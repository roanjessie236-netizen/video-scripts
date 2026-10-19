#!/usr/bin/env python3
"""v4 engine = Sapiens render_core.py/render.py + tools/patch_engine.py (Homo Deus v1/v2 additions) + this patch.
Adds: clean 'plates' (shots rebuilt from the v2 master, see tools/extract_plates.py) loaded without re-crop/re-grade,
grades 'none'/'ash', a placeholder for images that are not delivered yet, two-line captions ('/'), cool-grey English
subtitles, per-label fade times, a 'punch' camera ease and a glow amount for lights_on.
Usage: python3 tools/patch_v4.py engine_dir   (patches render_core.py and render.py in place, idempotent)"""
import os, sys
D = sys.argv[1]
rc_p, rd_p = os.path.join(D, 'render_core.py'), os.path.join(D, 'render.py')
rc, rd = open(rc_p, encoding='utf-8').read(), open(rd_p, encoding='utf-8').read()
if 'HOMO-DEUS-V4' in rc:
    sys.exit('already patched')


def rep(s, a, b):
    assert a in s, 'missing: ' + a[:80]
    return s.replace(a, b, 1)


rc = rep(rc, "ASSETS = os.path.join(HERE, 'assets')\n",
         "ASSETS = os.path.join(HERE, 'assets')\nPLATES = os.path.join(HERE, 'plates')\n")
rc = rep(rc, "    if kind == 'lin':\n        return u\n",
         "    if kind == 'lin':\n        return u\n    if kind == 'punch':  # fast push on a hit, then a slow drift\n"
         "        return 0.7 * (1 - (1 - min(1.0, u / 0.18)) ** 3) + 0.3 * u\n")
rc = rep(rc, "\n\ndef grade(img, g):\n",
         """
GRADES.update({
    'none': None,   # plates: already carry the v2 grade
    'ash': dict(exp=1.0, con=.30, sat=.42, sh=(.02, .012, .0), hi=(.05, .035, .01), lift=(.03, .026, .022)),
    'sodium': dict(exp=1.0, con=.28, sat=.85, sh=(-.01, .01, .04), hi=(.07, .04, -.02), lift=(.014, .012, .018)),
})


def grade(img, g):
    if g is None:
        return img
""")
rc = rep(rc, """    img = cv2.imread(os.path.join(ASSETS, shot['image']))
    prep = shot['prep']
""", """    prep = shot['prep']
    img = cv2.imread(os.path.join(PLATES if prep.get('plate') else ASSETS, shot['image']))
    if img is None:
        img = placeholder(shot)
    if prep.get('plate'):
        up = img if img.shape[:2] == (SH, SW) else cv2.resize(img, (SW, SH), interpolation=cv2.INTER_LANCZOS4)
        if prep.get('sharp'):
            bl = cv2.GaussianBlur(up, (0, 0), 1.2)
            up = cv2.addWeighted(up, 1 + prep['sharp'], bl, -prep['sharp'], 0)
        out = grade(up, GRADES[shot['grade']])
        if len(_src) > 6:
            _src.pop(next(iter(_src)))
        _src[key] = (out, (0, 0, 1.0, 1.0))
        return _src[key]
""")
rc = rep(rc, "\n\n_src = {}\n", '''

def placeholder(shot):
    """Stand-in for an image that has not been delivered yet (marked 待补图 in previews)."""
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    r = np.sqrt(((xx - SW / 2) / SW) ** 2 + ((yy - SH / 2) / SH) ** 2)
    base = np.clip(70 - r * 90, 18, 70)
    img = np.dstack([base * 1.15, base * 1.0, base * 0.85]).astype(np.uint8)
    pil = Image.fromarray(img[..., ::-1].copy())
    d = ImageDraw.Draw(pil)
    for txt, sz, y in [('待补图', 150, SH * 0.36), (shot['image'], 70, SH * 0.52), (shot.get('desc', '')[:60], 44, SH * 0.62)]:
        f = font('Medium', sz)
        d.text(((SW - f.getlength(txt)) / 2, y), txt, font=f, fill=(150, 150, 150))
    return np.asarray(pil)[..., ::-1].copy()


_src = {}
''')
rc = rep(rc, "EN_SUB = (226, 218, 202)", "EN_SUB = (214, 222, 236)  # v4: cool grey (user's choice)")
rc = rep(rc, "def caption_layer(text, en=''):\n",
         """def caption_layer(text, en=''):
    if '/' in text and not en:  # v4: two-line caption
        def mkm():
            parts = [caption_layer(p) for p in text.split('/')]
            return stack(parts, [-int(parts[0].shape[0] * 0.40)] * (len(parts) - 1))
        return cached(('capm', text), mkm)
""")
rc = rep(rc, "            zh = caption_layer(text)\n            e = text_layer(en, font('Light', 42), (214, 222, 236), shadow=(8, 0.8, 2), whole=True)\n            return stack([zh, e], [-int(zh.shape[0] * 0.22) - int(e.shape[0] * 0.25)])", "            zh = caption_layer(text)\n            e = text_layer(en, font('Light', 42), (214, 222, 236), shadow=(8, 0.8, 2), whole=True)\n            one = caption_layer('字').shape[0]  # v4: gap from a single caption line (two-line captions)\n            return stack([zh, e], [-int(one * 0.22) - int(e.shape[0] * 0.25)])")
rc += '\n# HOMO-DEUS-V4\n'
rd = rep(rd, "out = cv2.addWeighted(out, 1.0, q, 0.7 * k, 0)", "out = cv2.addWeighted(out, 1.0, q, p.get('glow', 0.7) * k, 0)")
rd = rep(rd, "alow = max([window(t, s, e, 0.6, 0.6) for s, e, _, _ in TL['labels']] +",
         "alow = max([window(t, L[0], L[1], *([L[4]] * 2 if len(L) > 4 else [0.6, 0.6])) for L in TL['labels']] +")
rd = rep(rd, """    for s, e, l1, l2 in TL['labels']:
        a = window(t, s, e, 0.6, 0.6)
""", """    for s, e, l1, l2, *fd in TL['labels']:
        fd = fd[0] if fd else 0.6
        a = window(t, s, e, fd, fd)
""")
rd = rep(rd, '    sc, sl, st = max(0.62 * ach, 0.62 * ati, 0.3 * aen), 0.5 * alow, 0.35 * acap\n',
         "    kb = max([k for a_, b_, k in TL.get('scrim_boost', []) if a_ <= t < b_] + [1.0])  # v4: bright plates\n    sc, sl, st = max(0.62 * ach, 0.62 * ati, 0.3 * aen), min(0.95, 0.5 * alow * kb), min(0.95, 0.35 * acap * kb)\n")
rd += '\n# HOMO-DEUS-V4\n'
open(rc_p, 'w', encoding='utf-8').write(rc)
open(rd_p, 'w', encoding='utf-8').write(rd)
print('patched', D)

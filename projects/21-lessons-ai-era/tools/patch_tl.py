#!/usr/bin/env python3
"""Film 3 engine patch. Copies the film-2 engine (render_core.py / render.py, already patched by
homo-deus-future/tools/patch_engine.py) into this folder and adds:
  grades grey/warm, warm-gold typography, film-3 title/end card text, fx 'reveal',
  global floating dust + opening embers, light leaks, the chapter-1 timeline overlay, 1.6 s final fade.
Usage: python3 tools/patch_tl.py /path/to/film2_engine_dir
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/data/hd'
for f in ('render_core.py', 'render.py'):
    shutil.copy(os.path.join(SRC, f), os.path.join(HERE, f))


def patch(fn, reps):
    p = os.path.join(HERE, fn)
    s = open(p, encoding='utf-8').read()
    for old, new, allow_multi in reps:
        n = s.count(old)
        assert n >= 1, (fn, old[:60])
        assert allow_multi or n == 1, (fn, old[:60], n)
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)


CORE_ADD = r'''

# ====================================================================== FILM-3 ADDITIONS
GRADES.update({
    'grey': dict(exp=1.0, con=.26, sat=.60, sh=(-.01, .008, .035), hi=(.01, .02, .03), lift=(.014, .018, .026)),
    'warm': dict(exp=1.04, con=.22, sat=.94, sh=(.012, .008, 0), hi=(.06, .04, .005), lift=(.026, .021, .015)),
})
QW, QH = W // 4, H // 4
_PR = np.random.default_rng(5)
DN = 230
D_X, D_Y = _PR.uniform(0, 1, DN), _PR.uniform(0, 1, DN)
D_D = _PR.uniform(0.25, 1, DN) ** 1.5
D_VX, D_VY = _PR.normal(0.004, 0.006, DN), _PR.normal(-0.006, 0.004, DN)
D_PH = _PR.uniform(0, 6.283, DN)
D_BIG = _PR.random(DN) < 0.07
EN = 150
E_X, E_Y = _PR.uniform(0, 1, EN), _PR.uniform(0, 1, EN)
E_D = _PR.uniform(0.3, 1, EN)
E_VX, E_VY = _PR.normal(0.0, 0.012, EN), _PR.uniform(-0.11, -0.05, EN)
E_PH = _PR.uniform(0, 6.283, EN)
_LX = np.linspace(0, 1, QW, dtype=np.float32)[None, :]
_LY = np.linspace(0, 1, QH, dtype=np.float32)[:, None]


def tab(table, t):
    for a, b in zip(table, table[1:]):
        if a[0] <= t <= b[0]:
            k = (t - a[0]) / max(1e-6, b[0] - a[0])
            return [x + (y - x) * k for x, y in zip(a[1:], b[1:])]
    return list(table[-1][1:])


def particles(frame, t):
    du = tab(TL['dust'], t)
    eg = tab(TL['embers_g'], t)[0]
    if du[0] < 0.01 and eg < 0.01:
        return frame
    acc = np.zeros((QH, QW, 3), np.float32)
    if du[0] >= 0.01:
        q = np.zeros((QH, QW), np.float32)
        x = (D_X + D_VX * t * D_D + 0.012 * np.sin(0.3 * t + D_PH)) % 1
        y = (D_Y + D_VY * t * D_D + 0.010 * np.cos(0.23 * t + D_PH)) % 1
        tw = 0.6 + 0.4 * np.sin(1.3 * t + D_PH * 3)
        for xi, yi, d, b, w in zip(x * QW, y * QH, D_D, D_BIG, tw):
            r = (4 + 5 * d) if b else (0.6 + 1.5 * d)
            cv2.circle(q, (int(xi * 16), int(yi * 16)), max(1, int(r * 16)), float(d * w * (0.3 if b else 1.0)), -1,
                       cv2.LINE_AA, 4)
        q = cv2.GaussianBlur(q, (0, 0), 1.0)
        acc += q[..., None] * (np.array(du[1:4], np.float32) * du[0] * 0.95)
    if eg >= 0.01:
        q = np.zeros((QH, QW), np.float32)
        x = (E_X + E_VX * t + 0.02 * np.sin(1.1 * t + E_PH)) % 1
        y = (E_Y + E_VY * t * E_D) % 1
        fl = 0.55 + 0.45 * np.sin(9.0 * t + E_PH * 5)
        for xi, yi, d, w in zip(x * QW, y * QH, E_D, fl):
            cv2.circle(q, (int(xi * 16), int(yi * 16)), max(1, int((0.7 + 1.6 * d) * 16)), float(d * w), -1,
                       cv2.LINE_AA, 4)
        q = cv2.GaussianBlur(q, (0, 0), 1.3)
        acc += q[..., None] * (np.array([50, 150, 255], np.float32) * eg)
    L = cv2.resize(np.clip(acc, 0, 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_LINEAR)
    return cv2.add(frame, L)


def leaks(frame, t):
    acc = None
    for s, d, col, dr, st in TL['leaks']:
        u = (t - s) / d
        if 0 <= u <= 1:
            cx = -0.3 + 1.6 * u if dr > 0 else 1.3 - 1.6 * u
            g = np.exp(-(((_LX - cx) / 0.34) ** 2 + ((_LY - 0.40) / 0.8) ** 2))
            g2 = np.exp(-(((_LX - cx - 0.06 * dr) / 0.05) ** 2)) * (0.5 + 0.5 * np.exp(-((_LY - 0.4) / 0.5) ** 2))
            k = math.sin(math.pi * u) ** 1.5 * st
            Lc = (g + 0.45 * g2)[..., None] * np.array(col, np.float32) * k
            acc = Lc if acc is None else acc + Lc
    if acc is None:
        return frame
    L = cv2.resize(np.clip(acc, 0, 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_LINEAR)
    return cv2.add(frame, L)


def fx_global(frame, t):
    return leaks(particles(frame, t), t)


def tl_label(l1, l2):
    def mk():
        a = text_layer(l1, font('SemiBold', 44), GOLD, tracking=4, shadow=(6, 0.85, 3))
        b = text_layer(l2, font('Regular', 32), WARMW, tracking=8, shadow=(5, 0.85, 2))
        return stack([a, b], [-44])
    return cached(('tln', l1, l2), mk)


TLGOLD = (120, 196, 236)   # BGR


def draw_timeline(frame, t):
    tl = TL.get('timeline')
    if not tl:
        return
    a0, a1 = tl['win']
    if t < a0 or t > a1:
        return
    a = min(smooth((t - a0) / 0.8), smooth((a1 - t) / 0.8))
    p = smooth((t - tl['grow'][0]) / (tl['grow'][1] - tl['grow'][0]))
    y, x0, xe = tl['y'], tl['x0'], tl['x1']
    y0, y1 = y - 50, y + 50
    roi = frame[y0:y1].copy()
    ov = roi.copy()
    cv2.line(ov, (x0 - 60, 50), (xe + 60, 50), (150, 150, 150), 1, cv2.LINE_AA)
    xx = int(x0 + (xe - x0) * p)
    if xx > x0:
        cv2.line(ov, (x0, 50), (xx, 50), TLGOLD, 6, cv2.LINE_AA)
        ov = cv2.addWeighted(ov, 0.5, roi, 0.5, 0)
        cv2.line(ov, (x0, 50), (xx, 50), (210, 236, 255), 2, cv2.LINE_AA)
        cv2.circle(ov, (xx, 50), 5, (235, 248, 255), -1, cv2.LINE_AA)
    for nt, nx, l1, l2 in tl['nodes']:
        if t < nt:
            continue
        na = smooth((t - nt) / 0.5)
        cv2.circle(ov, (nx, 50), int(4 + 6 * na), (225, 242, 255), -1, cv2.LINE_AA)
        u = (t - nt) / 1.4
        if u < 1:
            cv2.circle(ov, (nx, 50), int(12 + 30 * u), TLGOLD, 2, cv2.LINE_AA)
    frame[y0:y1] = cv2.addWeighted(ov, a, roi, 1 - a, 0)
    for nt, nx, l1, l2 in tl['nodes']:
        if t >= nt:
            na = smooth((t - nt) / 0.7)
            blit_center(frame, tl_label(l1, l2), nx, y - 95 + 12 * (1 - na), a * na)
'''

patch('render_core.py', [
    ('GOLD_T, GOLD_B, GOLD = (240, 247, 255), (118, 166, 222), (168, 206, 242)',
     'GOLD_T, GOLD_B, GOLD = (255, 247, 228), (222, 180, 108), (236, 206, 146)', False),
    ('\u672a\u6765\u7b80\u53f2',
     '\u4eca\u65e5\u7b80\u53f2', True),
    ('\u4eba\u7c7b\u4e4b\u540e\uff0c\u4f1a\u662f\u8c01\uff1f',
     'AI\u65f6\u4ee3\uff0c\u4eba\u7c7b\u5982\u4f55\u91cd\u65b0\u5b9a\u4e49\u81ea\u5df1', True),
    ('HOMO DEUS  \u00b7  A BRIEF HISTORY OF TOMORROW',
     '21 LESSONS FOR THE 21ST CENTURY', False),
    ("font('Black', 200), tracking=46", "font('Black', 190), tracking=40", False),
    ('glow=((120, 190, 255), 10, 0.25)', 'glow=((255, 200, 130), 10, 0.22)', True),
    ('glow=((90, 165, 255), 20, 0.32)', 'glow=((255, 176, 90), 20, 0.28)', False),
    ('glow=((90, 160, 255), 30, 0.42)', 'glow=((255, 176, 96), 30, 0.36)', False),
])
open(os.path.join(HERE, 'render_core.py'), 'a', encoding='utf-8').write(CORE_ADD)

patch('render.py', [
    ("    if 'dim' in fx:\n",
     "    if 'reveal' in fx:\n        p = fx['reveal']\n        k = smooth((t - p['t0']) / (p['t1'] - p['t0']))\n"
     "        out = cv2.convertScaleAbs(out, alpha=p['a0'] + (1 - p['a0']) * k)\n    if 'dim' in fx:\n", False),
    ('    # ---- typography\n', '    frame = fx_global(frame, t)\n    # ---- typography\n', False),
    ('    draw_ticker(frame, t)\n', '    draw_ticker(frame, t)\n    draw_timeline(frame, t)\n', False),
])
p = os.path.join(HERE, 'render.py')
s = open(p, encoding='utf-8').read()
import re
s2 = re.sub(r'DUR - 3\.0', 'DUR - 1.6', s)
s2 = s2.replace('/ 3.0)', '/ 1.6)') if s2 != s else s2
open(p, 'w', encoding='utf-8').write(s2)
print('patched; fade edits:', s != s2)

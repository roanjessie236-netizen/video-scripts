#!/usr/bin/env python3
"""Patch the Film-1 engine (render_core.py / render.py from projects/sapiens-70000-years) for
《未来简史：人类之后，会是谁？》: cool silver-blue typography, future grades, data-stream / bloom fx,
a 'digital' block transition and a duration-independent fade-out. Idempotent: run once on fresh copies."""
import os
HD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def patch(fn, reps):
    p = os.path.join(HD, fn)
    s = open(p, encoding='utf-8').read()
    if 'HOMO-DEUS-PATCHED' in s:
        print(fn, 'already patched')
        return
    for a, b, allow_many in reps:
        n = s.count(a)
        assert n >= 1 and (allow_many or n == 1), (fn, a[:60], n)
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8').write(s + '\n# HOMO-DEUS-PATCHED\n')
    print('patched', fn, len(reps), 'edits')


GRADES_NEW = '''
GRADES.update({
    'void': dict(exp=1.0, con=.24, sat=1.0, sh=(0, .006, .025), hi=(0, .01, .02), lift=(.003, .006, .014)),
    'cyan': dict(exp=1.03, con=.26, sat=.92, sh=(-.015, .012, .05), hi=(0, .03, .05), lift=(.008, .016, .03)),
    'lab': dict(exp=1.03, con=.24, sat=.88, sh=(-.01, .015, .04), hi=(.02, .035, .04), lift=(.01, .018, .026)),
    'tender': dict(exp=1.02, con=.22, sat=.92, sh=(-.005, .01, .03), hi=(.04, .03, .01), lift=(.012, .014, .02)),
    'dawn': dict(exp=1.03, con=.26, sat=.95, sh=(-.01, .008, .04), hi=(.06, .035, -.01), lift=(.012, .014, .022)),
    'amber': dict(exp=1.0, con=.28, sat=.90, sh=(-.01, .01, .035), hi=(.06, .035, -.02), lift=(.014, .014, .02)),
})


def grade(img, g):'''

FX_NEW = '''

# ------------------------------------------------------------------ future fx (Homo Deus)
_DR = np.random.default_rng(9)
DS_N = 1200
DS_U, DS_L = _DR.random(DS_N), _DR.normal(0, 1, DS_N)
DS_S, DS_P = _DR.uniform(0.5, 1.6, DS_N), _DR.uniform(0, 6.28, DS_N)
DS_B = _DR.uniform(0.3, 1.0, DS_N) ** 2


def datastream(img, t, p):
    """Streams of light particles flowing across the frame like a galaxy of data."""
    n, yc, sp = min(DS_N, p.get('n', 600)), p.get('y', 0.55) * H, p.get('spread', 0.12) * H
    amp, v, tilt = p.get('amp', 0.08) * H, p.get('speed', 0.16), p.get('tilt', 0.0)
    col, a = np.array(p.get('col', [255, 200, 90]), np.float32), p.get('alpha', 1.0)
    if a <= 0.01:
        return img
    layer = np.zeros((H // 2, W // 2, 3), np.uint8)
    for i in range(n):
        x = ((DS_U[i] + v * DS_S[i] * t) % 1.2 - 0.1) * W
        xp = x - v * DS_S[i] * W * 0.07

        def yy(q):
            return yc + DS_L[i] * sp + amp * math.sin(q / W * 8.2 + DS_P[i] * 0.35 + t * 0.4) + tilt * (q - W / 2)
        c = col * DS_B[i] * a
        cv2.line(layer, (int(xp / 2), int(yy(xp) / 2)), (int(x / 2), int(yy(x) / 2)),
                 (int(c[0]), int(c[1]), int(c[2])), 1, cv2.LINE_AA)
    layer = cv2.add(cv2.GaussianBlur(layer, (0, 0), 0.7), cv2.GaussianBlur(layer, (0, 0), 3.0))
    return cv2.add(img, cv2.resize(layer, (W, H), interpolation=cv2.INTER_LINEAR))


def bloom(img, amt, thr=165):
    q = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    q = cv2.GaussianBlur(cv2.subtract(q, (thr, thr, thr, 0)), (0, 0), 9)
    return cv2.addWeighted(img, 1.0, cv2.resize(q, (W, H), interpolation=cv2.INTER_LINEAR), amt * 2.2, 0)
'''

patch('render_core.py', [
    ('\n\ndef grade(img, g):', GRADES_NEW, False),
    ('GOLD_T, GOLD_B, GOLD = (252, 230, 172), (190, 136, 64), (228, 192, 122)\nWARMW = (247, 239, 224)',
     'GOLD_T, GOLD_B, GOLD = (240, 247, 255), (118, 166, 222), (168, 206, 242)\nWARMW = (242, 245, 250)', False),
    ('(255, 196, 110)', '(120, 190, 255)', True),
    ('(255, 180, 90)', '(90, 165, 255)', True),
    ('(255, 170, 80)', '(90, 160, 255)', True),
    ('(255, 190, 110)', '(120, 190, 255)', True),
    ('(232, 214, 176)', '(196, 216, 240)', True),
    ('(240, 224, 192)', '(222, 234, 250)', True),
    ('(226, 206, 166)', '(186, 206, 232)', True),
    ('人类简史', '未来简史', True),
    ('七万年的文明觉醒', '人类之后，会是谁？', True),
    ('70,000 YEARS OF AWAKENING', 'HOMO DEUS  ·  A BRIEF HISTORY OF TOMORROW', False),
    ("    return f'公元前 {-y} 年' if y < 0 else f'公元 {y} 年'\n",
     "    return f'公元前 {-y} 年' if y < 0 else f'公元 {y} 年'\n" + FX_NEW, False),
])

DIGITAL = '''    elif kind == 'digital':
        bl = cv2.resize(BLK, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
        p = u * 1.3 - 0.15
        m = (bl < p).astype(np.float32)
        edge = ((bl >= p) & (bl < p + 0.12)).astype(np.float32) * math.sin(math.pi * u)
        As = np.roll(Af, int(48 * math.sin(math.pi * u)), axis=1)
        out = As * (1 - m) + Bf * m + edge * np.array([255, 190, 60], np.float32) * 0.45
    elif kind == 'burn':'''

patch('render.py', [
    ('297.0', '(DUR - 3.0)', True),
    ("    if 'routes' in fx:\n        out = draw_routes(out, t, M, xf)\n    return out",
     "    if 'datastream' in fx:\n        p = fx['datastream']\n"
     "        out = datastream(out, t, dict(p, alpha=p.get('alpha', 1.0) * smooth((t - s['start']) / 1.5)))\n"
     "    if 'bloom' in fx:\n        out = bloom(out, fx['bloom'])\n"
     "    if 'routes' in fx:\n        out = draw_routes(out, t, M, xf)\n    return out", False),
    ('_gy /= 360.0\n', '_gy /= 360.0\nBLK = np.random.default_rng(21).random((18, 32)).astype(np.float32)\n', False),
    ("    elif kind == 'burn':", DIGITAL, False),
    ('人类简史', '未来简史', True),
    ('七万年的文明觉醒', '人类之后，会是谁？', True),
])

"""Core helpers for render.py: still preparation, grading, camera, effects, typography."""
import os, math, json, random
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

cv2.setNumThreads(2)
HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, 'shotlist.json'), encoding='utf-8'))
W, H, FPS, DUR = TL['width'], TL['height'], TL['fps'], TL['duration']
SW, SH = 2944, 1656  # working resolution of every still (16:9, ~1.15x output for camera moves)
ASSETS = os.path.join(HERE, 'assets')
FONT_DIR = '/usr/share/fonts/google-noto-cjk'


def clip01(x):
    return min(1.0, max(0.0, x))


def smooth(x):
    x = clip01(x)
    return x * x * (3 - 2 * x)


def ease(u, kind):
    u = clip01(u)
    if kind == 'lin':
        return u
    if kind == 'in':
        return u ** 3
    if kind == 'out':
        return 1 - (1 - u) ** 2.5
    return 0.5 - 0.5 * math.cos(math.pi * u)


# ------------------------------------------------------------------ grading (tints are RGB)
GRADES = {
    'cosmos': dict(exp=1.0, con=.22, sat=1.05, sh=(0, .005, .02), hi=(.01, .01, 0), lift=(.004, .006, .012)),
    'ember': dict(exp=1.0, con=.30, sat=.80, sh=(.04, .015, -.02), hi=(.05, .02, -.04), lift=(.03, .018, .01)),
    'parch': dict(exp=1.0, con=.18, sat=.90, sh=(.03, .015, 0), hi=(.02, .01, -.02), lift=(.02, .012, .006)),
    'earth': dict(exp=1.02, con=.28, sat=.86, sh=(.03, .015, -.01), hi=(.05, .03, -.03), lift=(.026, .018, .01)),
    'gold': dict(exp=1.03, con=.28, sat=.92, sh=(0, .01, .02), hi=(.06, .035, -.03), lift=(.02, .016, .014)),
    'goldblue': dict(exp=1.02, con=.28, sat=.90, sh=(-.01, .01, .035), hi=(.05, .035, -.01), lift=(.014, .016, .022)),
    'steel': dict(exp=1.0, con=.30, sat=.82, sh=(-.01, .01, .04), hi=(.04, .03, 0), lift=(.012, .016, .024)),
    'future': dict(exp=1.02, con=.26, sat=.80, sh=(-.01, .008, .045), hi=(.03, .035, .04), lift=(.01, .016, .028)),
    'mars': dict(exp=1.0, con=.26, sat=.85, sh=(0, .005, .03), hi=(.04, .03, .02), lift=(.014, .014, .02)),
}


def grade(img, g):
    x = img.astype(np.float32) / 255.0 * g['exp']
    lum = x[..., 0] * .114 + x[..., 1] * .587 + x[..., 2] * .299
    x = lum[..., None] + (x - lum[..., None]) * g['sat']
    x = np.clip(x, 0, 1)
    x = x + g['con'] * (x * x * (3 - 2 * x) - x)
    lum = x[..., 0] * .114 + x[..., 1] * .587 + x[..., 2] * .299
    x = x + ((1 - lum) ** 2)[..., None] * np.array(g['sh'][::-1], np.float32) \
        + (lum ** 2)[..., None] * np.array(g['hi'][::-1], np.float32)
    lift = np.array(g['lift'][::-1], np.float32)
    x = lift + x * (1 - lift)
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)


# ------------------------------------------------------------------ still preparation
def autocrop_box(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = g.shape

    def bar(v):
        return np.percentile(v, 99.5) < 20
    t, b, l, r = 0, h, 0, w
    while t < 80 and bar(g[t]):
        t += 1
    while h - b < 80 and bar(g[b - 1]):
        b -= 1
    while l < 120 and bar(g[:, l]):
        l += 1
    while w - r < 120 and bar(g[:, r - 1]):
        r -= 1
    t, l = (t + 2 if t else 0), (l + 2 if l else 0)
    b, r = (b - 2 if b < h else h), (r - 2 if r < w else w)
    return l, t, r, b


def blur_rects(img, rects):
    big = cv2.GaussianBlur(img, (0, 0), 11)
    m = np.zeros(img.shape[:2], np.float32)
    for x0, y0, x1, y1 in rects:
        m[y0:y1, x0:x1] = 1
    m = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
    return (img * (1 - m) + big * m).astype(np.uint8)


_src = {}


def get_src(shot):
    key = (shot['image'], json.dumps(shot['prep'], sort_keys=True), shot['grade'])
    if key in _src:
        return _src[key]
    img = cv2.imread(os.path.join(ASSETS, shot['image']))
    prep = shot['prep']
    if prep.get('blur'):
        img = blur_rects(img, prep['blur'])
    if prep.get('crop'):
        l, t, r, b = prep['crop']
    else:
        l, t, r, b = autocrop_box(img)
    cw, ch = r - l, b - t
    if cw / ch > 16 / 9:
        nw = int(round(ch * 16 / 9))
        l += (cw - nw) // 2
        cw = nw
    else:
        nh = int(round(cw * 9 / 16))
        t += (ch - nh) // 2
        ch = nh
    crop = img[t:t + ch, l:l + cw]
    up = cv2.resize(crop, (SW, SH), interpolation=cv2.INTER_LANCZOS4)
    bl = cv2.GaussianBlur(up, (0, 0), 1.6)
    up = cv2.addWeighted(up, 1.45, bl, -0.45, 0)
    out = grade(up, GRADES[shot['grade']])
    xf = (l, t, SW / cw, SH / ch)
    if len(_src) > 6:
        _src.pop(next(iter(_src)))
    _src[key] = (out, xf)
    return out, xf


_aux = {}


def painted_version(shot):
    """Ochre cave-painting rendition of a still, multiplied with the cave rock texture."""
    if 'painted' in _aux:
        return _aux['painted']
    src, _ = get_src(shot)
    small = cv2.resize(src, (SW // 2, SH // 2), interpolation=cv2.INTER_AREA)
    sty = cv2.stylization(small, sigma_s=60, sigma_r=0.45)
    g = cv2.cvtColor(sty, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    g = np.clip((g - 0.12) / 0.7, 0, 1)[..., None]
    dark = np.array([18, 28, 45], np.float32)
    ochre = np.array([62, 125, 205], np.float32)
    light = np.array([150, 200, 235], np.float32)
    pal = np.where(g < 0.6, dark + (ochre - dark) * (g / 0.6), ochre + (light - ochre) * ((g - 0.6) / 0.4))
    cave_shot = next(s for s in TL['shots'] if s['id'] == 'cave')
    cave, _ = get_src(cave_shot)
    rock = cv2.cvtColor(cv2.resize(cave, (SW // 2, SH // 2)), cv2.COLOR_BGR2GRAY).astype(np.float32)
    rock = np.clip(rock / np.percentile(rock, 92), 0, 1.1)[..., None]
    out = np.clip(pal * (0.45 + 0.55 * rock), 0, 255).astype(np.uint8)
    out = cv2.resize(out, (SW, SH), interpolation=cv2.INTER_CUBIC)
    _aux['painted'] = out
    return out


def lights_mask(shot):
    if 'lights' in _aux:
        return _aux['lights']
    src, _ = get_src(shot)
    lum = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    m = np.clip((lum - 0.62) / 0.3, 0, 1)
    m = cv2.GaussianBlur(m * m * (3 - 2 * m), (0, 0), 3)
    _aux['lights'] = (m * 255).astype(np.uint8)
    return _aux['lights']


def lights_wide(shot):
    """Wider, soft mask covering the whole lamp halo (used to switch lamps 'off')."""
    if 'lights_w' in _aux:
        return _aux['lights_w']
    src, _ = get_src(shot)
    lum = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    m = np.clip((lum - 0.42) / 0.3, 0, 1)
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    m = np.clip(cv2.GaussianBlur(m, (0, 0), 14) * 1.25, 0, 1)
    _aux['lights_w'] = (m * 255).astype(np.uint8)
    return _aux['lights_w']


# ------------------------------------------------------------------ camera
def cam_matrix(cam, u, kind, shake=(0.0, 0.0)):
    a, b = cam
    e = ease(u, kind)
    z, cx, cy, rot = [a[i] + (b[i] - a[i]) * e for i in range(4)]
    hw = 0.5 / z
    cx = min(max(cx, hw), 1 - hw)
    cy = min(max(cy, hw), 1 - hw)
    s = W * z / SW
    th = math.radians(rot)
    c, sn = math.cos(th), math.sin(th)
    px, py = cx * SW, cy * SH
    M = np.array([[s * c, -s * sn, W / 2 - s * (c * px - sn * py) + shake[0]],
                  [s * sn, s * c, H / 2 - s * (sn * px + c * py) + shake[1]]], np.float64)
    return M, z


def warp(img, M, interp=cv2.INTER_LINEAR):
    return cv2.warpAffine(img, M, (W, H), flags=interp, borderMode=cv2.BORDER_REFLECT)


def apply_pt(M, x, y):
    return M[0, 0] * x + M[0, 1] * y + M[0, 2], M[1, 0] * x + M[1, 1] * y + M[1, 2]


# ------------------------------------------------------------------ global textures
def _grain(n=8, sigma=6.5):
    r = np.random.default_rng(5)
    out = []
    for _ in range(n):
        g = r.normal(0, sigma, (H // 2, W // 2)).astype(np.float32)
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
        g = np.clip(g + 128, 0, 255).astype(np.uint8)
        out.append(cv2.merge([g, g, g]))
    return out


GRAIN = _grain()
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_d = np.sqrt(((_xx - W / 2) / (W / 2)) ** 2 + ((_yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
VIG = (1 - 0.5 * np.clip((_d - 0.3) / 0.7, 0, 1) ** 1.6).astype(np.float32)
del _yy, _xx, _d
_p = cv2.resize(cv2.imread(os.path.join(ASSETS, 'parchment.jpg')), (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
_pl = _p[..., 0] * .114 + _p[..., 1] * .587 + _p[..., 2] * .299
PARCH = np.clip(_p / np.percentile(_pl, 98), 0, 1).astype(np.float32)
del _p, _pl
_mm = {}


def _ell(cx, cy, sx, sy):
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    e = np.exp(-(((xx * 4 - cx) / sx) ** 2 + ((yy * 4 - cy) / sy) ** 2) * 0.5)
    return cv2.resize(e, (W, H), interpolation=cv2.INTER_LINEAR)


SCRIM_C = _ell(W / 2, H / 2, 0.24 * W, 0.17 * H)      # behind title / chapter / end cards
SCRIM_L = _ell(470, H - 320, 560, 150)                 # behind lower-left labels
SCRIM_T = _ell(W / 2, 0.27 * H, 0.22 * W, 0.08 * H)    # behind the closing questions
SCRIM_B = _ell(W / 2, H - 150, 0.26 * W, 70)          # behind subtitles


def mulmap(a, sc=0.0, sl=0.0, st=0.0, sb=0.0):
    q = lambda v, s: round(v / s) * s
    key = (q(a, 0.02), q(sc, 0.05), q(sl, 0.05), q(st, 0.05), q(sb, 0.05))
    if key not in _mm:
        if len(_mm) > 6:
            _mm.pop(next(iter(_mm)))
        k, c, l, tt, b = key
        m = VIG * (1 - c * SCRIM_C) * (1 - l * SCRIM_L) * (1 - tt * SCRIM_T) * (1 - b * SCRIM_B)
        m = m[..., None] * (1 - k + k * PARCH)
        _mm[key] = (np.clip(m, 0, 1) * 255).astype(np.uint8)
    return _mm[key]


def _fbm(seed, w=640, h=360):
    r = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    for (gw, gh), amp in zip([(8, 5), (16, 9), (32, 18), (64, 36), (128, 72)], [1, .55, .3, .17, .1]):
        acc += amp * cv2.resize(r.random((gh, gw)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    flat = acc.ravel()
    ranks = np.empty_like(flat)
    ranks[np.argsort(flat)] = np.linspace(0, 1, flat.size, dtype=np.float32)
    return ranks.reshape(h, w)


NOISE_R = _fbm(11)
NOISE_B = _fbm(12)

# ------------------------------------------------------------------ effects
_SR = np.random.default_rng(3)
NST = 1400
ST_XY = _SR.uniform(-1, 1, (NST, 2)) * np.array([1.8, 1.0])
ST_Z = _SR.uniform(0, 1, NST)
ST_M = _SR.uniform(0.25, 1, NST) ** 2


def stars3d(img, t, k1, k2, t0, alpha=1.0):
    def dist(x):
        return k1 * x + k2 * x * x
    tt = t - t0
    d, dp = dist(tt), dist(max(tt - 1.5 / FPS, 0))
    z = (ST_Z - d) % 1.0 * 0.98 + 0.02
    zp = (ST_Z - dp) % 1.0 * 0.98 + 0.02
    f = 0.32 * W
    x, y = W / 2 + ST_XY[:, 0] / z * f, H / 2 + ST_XY[:, 1] / z * f
    xp, yp = W / 2 + ST_XY[:, 0] / zp * f, H / 2 + ST_XY[:, 1] / zp * f
    b = ST_M * np.clip((1 - z) * 1.6, 0, 1) ** 1.5 * alpha
    ok = (zp >= z) & (x > -40) & (x < W + 40) & (y > -40) & (y < H + 40) & (b > 0.03)
    layer = np.zeros((H // 2, W // 2, 3), np.uint8)
    for i in np.nonzero(ok)[0]:
        c = min(1.0, b[i])
        col = (int(255 * c), int(240 * c), int(222 * c))
        cv2.line(layer, (int(xp[i] / 2), int(yp[i] / 2)), (int(x[i] / 2), int(y[i] / 2)), col,
                 1 if z[i] > 0.3 else 2, cv2.LINE_AA)
    layer = cv2.GaussianBlur(layer, (0, 0), 0.8)
    return cv2.add(img, cv2.resize(layer, (W, H), interpolation=cv2.INTER_LINEAR))


def embers(img, t, M, z, p, shot):
    fx, fy = apply_pt(M, p['src'][0] * SW, p['src'][1] * SH)
    rate, spread = p['rate'], p['spread']
    base = shot['start'] - 4.0
    i0 = max(0, int((t - 4.5 - base) * rate))
    i1 = int((t - base) * rate) + 1
    layer = np.zeros((H // 2, W // 2, 3), np.uint8)
    salt = sum(map(ord, shot['id'])) * 1000
    for i in range(i0, i1):
        r = random.Random(salt + i)
        birth = base + i / rate + r.uniform(0, 1 / rate)
        age, life = t - birth, r.uniform(1.8, 4.2)
        if age < 0 or age > life:
            continue
        x = fx + r.gauss(0, spread) * z + r.gauss(0, 25) * z * age \
            + r.uniform(10, 35) * z * math.sin(r.uniform(1.5, 3.5) * age + r.uniform(0, 6.28))
        y = fy - r.uniform(90, 260) * z * age
        fade = min(1.0, age / 0.25) * max(0.0, 1 - age / life) ** 1.2 * r.uniform(0.5, 1.0)
        size = r.uniform(1.0, 3.2) * z
        hue = r.uniform(0, 1)
        col = (int((30 + 60 * hue) * fade), int((130 + 90 * hue) * fade), int(255 * fade))
        cv2.circle(layer, (int(x / 2), int(y / 2)), max(1, int(size / 2 + 0.5)), col, -1, cv2.LINE_AA)
    layer = cv2.add(cv2.GaussianBlur(layer, (0, 0), 1.0), cv2.GaussianBlur(layer, (0, 0), 4.0))
    return cv2.add(img, cv2.resize(layer, (W, H), interpolation=cv2.INTER_LINEAR))


def flicker_gain(t, amp):
    return 1 + amp * (0.5 * math.sin(2 * math.pi * 5.1 * t) + 0.3 * math.sin(2 * math.pi * 8.7 * t + 1)
                      + 0.2 * math.sin(2 * math.pi * 13.3 * t + 2))


def shake_offset(p, t, end):
    t0, pk = p['t0'], p['peak']
    if t < t0:
        return 0.0, 0.0
    amp = 14 * smooth((t - t0) / (pk - t0)) if t < pk else 3 + 11 * math.exp(-(t - pk) / 2.5)
    return (amp * (0.6 * math.sin(2 * math.pi * 17 * t) + 0.4 * math.sin(2 * math.pi * 29 * t + 1)),
            amp * (0.6 * math.cos(2 * math.pi * 23 * t) + 0.4 * math.sin(2 * math.pi * 13 * t + 2)))


# ------------------------------------------------------------------ typography (premultiplied BGR + alpha, float32)
_fc = {}


def font(weight, size):
    k = (weight, size)
    if k not in _fc:
        path = f'{FONT_DIR}/NotoSerifCJK-{weight}.ttc'
        f = None
        for idx in range(8):
            try:
                ff = ImageFont.truetype(path, size, index=idx)
            except Exception:
                break
            if 'SC' in ff.getname()[0]:
                f = ff
                break
        _fc[k] = f or ImageFont.truetype(path, size, index=2)
    return _fc[k]


def text_layer(text, fnt, color=(255, 255, 255), tracking=0, grad=None, glow=None, shadow=None):
    pad = int(fnt.size * 0.6)
    if glow:
        pad = max(pad, int(glow[1] * 3))
    if shadow:
        pad = max(pad, int(shadow[0] * 3 + shadow[2]))
    widths = [fnt.getlength(c) for c in text]
    tw = sum(widths) + tracking * max(0, len(text) - 1)
    asc, desc = fnt.getmetrics()
    w, h = int(math.ceil(tw)) + 2 * pad, asc + desc + 2 * pad
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    x = pad
    for c, cw in zip(text, widths):
        d.text((x, pad), c, font=fnt, fill=255)
        x += cw + tracking
    a = np.asarray(m, np.float32) / 255
    if grad:
        rows = np.nonzero(a.max(axis=1) > 0.1)[0]
        y0, y1 = (rows[0], rows[-1]) if len(rows) else (0, h)
        tt = np.clip((np.arange(h) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
        col = np.array(grad[0], np.float32) * (1 - tt) + np.array(grad[1], np.float32) * tt
        rgb = np.broadcast_to(col, (h, w, 3))
    else:
        rgb = np.broadcast_to(np.array(color, np.float32), (h, w, 3))
    P = rgb * a[..., None]
    A = a.copy()
    if glow:
        gcol, rad, k = glow
        g = np.clip(cv2.GaussianBlur(a, (0, 0), rad) * k, 0, 1)
        P = P + np.array(gcol, np.float32) * (g * (1 - A))[..., None]
        A = A + g * (1 - A)
    if shadow:
        rad, k, off = shadow
        s = np.clip(np.roll(cv2.GaussianBlur(a, (0, 0), rad), off, axis=0) * k, 0, 1)
        A = A + s * (1 - A)
    return np.dstack([P[..., ::-1], A]).astype(np.float32)


def stack(layers, gaps, align='center'):
    w = max(L.shape[1] for L in layers)
    ys, y = [], 0
    for i, L in enumerate(layers):
        ys.append(y)
        y += L.shape[0] + (gaps[i] if i < len(gaps) else 0)
    h = max(ys[i] + layers[i].shape[0] for i in range(len(layers)))
    out = np.zeros((h, w, 4), np.float32)
    for L, yy in zip(layers, ys):
        x = (w - L.shape[1]) // 2 if align == 'center' else 0
        reg = out[yy:yy + L.shape[0], x:x + L.shape[1]]
        reg[:] = L + reg * (1 - L[..., 3:4])
    return out


def ornament(width, color, alpha=0.9):
    h = 28
    a = np.zeros((h, width), np.float32)
    prof = np.sin(np.linspace(0, np.pi, width)) ** 0.8
    a[h // 2 - 1:h // 2 + 1, :] = prof * alpha
    cv2.fillConvexPoly(a, np.array([[width // 2, h // 2 - 8], [width // 2 + 8, h // 2], [width // 2, h // 2 + 8],
                                    [width // 2 - 8, h // 2]], np.int32), float(alpha), cv2.LINE_AA)
    a[:, width // 2 - 40:width // 2 - 12] = 0
    a[:, width // 2 + 12:width // 2 + 40] = 0
    cv2.fillConvexPoly(a, np.array([[width // 2, h // 2 - 8], [width // 2 + 8, h // 2], [width // 2, h // 2 + 8],
                                    [width // 2 - 8, h // 2]], np.int32), float(alpha), cv2.LINE_AA)
    P = np.array(color[::-1], np.float32) * a[..., None]
    return np.dstack([P, a]).astype(np.float32)


def blit(frame, L, x, y, alpha=1.0):
    if alpha <= 0.001:
        return
    h, w = L.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    Ls = L[y0 - y:y1 - y, x0 - x:x1 - x]
    roi = frame[y0:y1, x0:x1].astype(np.float32)
    roi = roi * (1 - Ls[..., 3:4] * alpha) + Ls[..., :3] * alpha
    frame[y0:y1, x0:x1] = np.clip(roi, 0, 255).astype(np.uint8)


def blit_center(frame, L, cx, cy, alpha=1.0):
    blit(frame, L, cx - L.shape[1] / 2, cy - L.shape[0] / 2, alpha)


GOLD_T, GOLD_B, GOLD = (252, 230, 172), (190, 136, 64), (228, 192, 122)
WARMW = (247, 239, 224)
_lc = {}


def cached(key, fn):
    if key not in _lc:
        if len(_lc) > 400:
            _lc.clear()
        _lc[key] = fn()
    return _lc[key]


def subtitle_layer(text):
    return cached(('sub', text), lambda: text_layer(text, font('Medium', 56), WARMW, tracking=3, shadow=(7, 0.9, 3)))


def chapter_layer(num, name, eng):
    def mk():
        l1 = text_layer(num, font('SemiBold', 46), GOLD_T, tracking=22, glow=((255, 196, 110), 10, 0.25),
                        shadow=(7, 0.85, 2))
        l2 = text_layer(name, font('Bold', 124), tracking=28, grad=(GOLD_T, GOLD_B), glow=((255, 180, 90), 20, 0.32),
                        shadow=(12, 0.55, 6))
        orn = ornament(max(560, int(l2.shape[1] * 0.62)), GOLD)
        l3 = text_layer(eng, font('Medium', 30), (232, 214, 176), tracking=10, shadow=(6, 0.85, 2))
        return stack([l1, l2, orn, l3], [-40, -60, -6])
    return cached(('ch', name), mk)


def title_layer():
    def mk():
        l1 = text_layer('人类简史', font('Black', 200), tracking=46, grad=(GOLD_T, GOLD_B),
                        glow=((255, 170, 80), 30, 0.42), shadow=(16, 0.6, 8))
        orn = ornament(760, GOLD)
        l2 = text_layer('七万年的文明觉醒', font('Regular', 62), (240, 224, 192), tracking=26,
                        glow=((255, 190, 110), 12, 0.25), shadow=(8, 0.7, 4))
        l3 = text_layer('70,000 YEARS OF AWAKENING', font('Medium', 30), (226, 206, 166), tracking=14,
                        shadow=(5, 0.7, 2))
        return stack([l1, orn, l2, l3], [-110, -20, -40])
    return cached(('title',), mk)


def caption_layer(text):
    return cached(('cap', text), lambda: text_layer(text, font('Light', 92), (238, 242, 250), tracking=30,
                                                    glow=((150, 190, 255), 22, 0.32), shadow=(12, 0.5, 5)))


def endcard_layer():
    def mk():
        l1 = text_layer('人类简史', font('Bold', 140), tracking=36, grad=((246, 246, 250), (176, 190, 212)),
                        glow=((140, 180, 255), 24, 0.35), shadow=(12, 0.5, 6))
        orn = ornament(560, (210, 220, 236))
        l2 = text_layer('七万年的文明觉醒', font('Regular', 50), (226, 232, 242), tracking=22)
        l3 = text_layer('灵感来自尤瓦尔·赫拉利《人类简史》', font('Light', 30), (190, 198, 212), tracking=8)
        return stack([l1, orn, l2, l3], [-80, -16, -10])
    return cached(('end',), mk)


def lower_layer(l1, l2):
    def mk():
        a = text_layer(l1, font('SemiBold', 58), GOLD, tracking=3, shadow=(6, 0.75, 3))
        b = text_layer(l2, font('Regular', 32), WARMW, tracking=6, shadow=(5, 0.75, 2))
        pa, pb = int(58 * 0.6), int(32 * 0.6)
        b2 = np.zeros((b.shape[0], b.shape[1] + pa - pb, 4), np.float32)
        b2[:, pa - pb:] = b
        out = stack([a, b2], [-pa - pb + 6], align='left')
        y0, y1 = pa + 6, out.shape[0] - pb - 4
        x0 = max(0, pa - 26)
        bar = out[y0:y1, x0:x0 + 4]
        col = np.array(GOLD[::-1], np.float32)
        bar[..., :3] = col * 0.95 + bar[..., :3] * (1 - 0.95)
        bar[..., 3] = 0.95 + bar[..., 3] * 0.05
        return out
    return cached(('low', l1, l2), mk)


def map_label_layer(text):
    return cached(('map', text), lambda: text_layer(text, font('SemiBold', 36), (72, 40, 20), tracking=2,
                                                    glow=((244, 230, 198), 7, 1.8)))


def year_str(y):
    y = int(round(y))
    if y == 0:
        y = 1
    return f'公元前 {-y} 年' if y < 0 else f'公元 {y} 年'

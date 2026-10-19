"""v2 motion toolkit for 《明天属于谁》 (imported by render.py):
2.5D depth parallax (Depth-Anything-V2 maps in depth/), handheld drift, atmosphere overlays (fog, motes = dust/snow/ash,
rain, sparks, god rays, anamorphic flare, glitch) and modern transitions (whip, zoom, leak, glitch, luma, slide, dip,
flash). Shot fx keys: par (parallax gain, 0 = off), hand (handheld px), fog, motes, rain, sparks, rays, flare, glitch."""
import os, math, random
import cv2
import numpy as np
from PIL import Image
from render_core import W, H, SW, SH, HERE, ASSETS, smooth, clip01, ease, apply_pt, _fbm

DEPTH = os.path.join(HERE, 'depth')
W4, H4 = W // 4, H // 4
_gy4, _gx4 = np.mgrid[0:H4, 0:W4].astype(np.float32)
PX4, PY4 = (_gx4 + 0.5) * 4 - 0.5, (_gy4 + 0.5) * 4 - 0.5     # full-res coords of the low-res pixel centres
CX, CY = W / 2.0, H / 2.0
_dep = {}


def depth_plate(s, xf):
    """depth (1 = near) resampled into the shot's plate space at quarter res (SW/4 x SH/4); None if absent."""
    key = (s['image'], tuple(xf))
    if key in _dep:
        return _dep[key]
    n = os.path.splitext(s['image'])[0]
    p = os.path.join(DEPTH, n + '.png')
    d = None
    if not s['prep'].get('plate') and os.path.exists(p):
        d = cv2.imread(p, -1).astype(np.float32) / 65535
        iw, ih = Image.open(os.path.join(ASSETS, s['image'])).size
        l, t, sx, sy = xf
        kx, ky = d.shape[1] / iw, d.shape[0] / ih
        A = np.array([[kx * 4 / sx, 0, kx * l], [0, ky * 4 / sy, ky * t]], np.float32)
        d = cv2.warpAffine(d, A, (SW // 4, SH // 4), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                           borderMode=cv2.BORDER_REPLICATE)
    if len(_dep) > 8:
        _dep.pop(next(iter(_dep)))
    _dep[key] = d
    return d


def handheld(s, t):
    a = s['fx'].get('hand', 0.0)
    if not a:
        return 0.0, 0.0
    ph = (sum(map(ord, s['id'])) % 97) * 0.37
    x = 0.55 * math.sin(2 * math.pi * 0.23 * t + ph) + 0.30 * math.sin(2 * math.pi * 0.61 * t + 2 * ph) \
        + 0.15 * math.sin(2 * math.pi * 1.37 * t + 3 * ph)
    y = 0.55 * math.sin(2 * math.pi * 0.19 * t + 1.7 * ph) + 0.30 * math.sin(2 * math.pi * 0.53 * t + ph) \
        + 0.15 * math.sin(2 * math.pi * 1.11 * t + 0.5 * ph)
    return a * x, a * y


def base_warp(src, s, M, u, z, xf):
    """camera warp + depth parallax: near layers travel / scale further than far ones (centred on mid-shot)."""
    k = s['fx'].get('par', 1.0)
    d = depth_plate(s, xf) if k else None
    if d is None:
        return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), None
    M4 = M.copy()
    M4[:, 2] /= 4.0
    dd = cv2.warpAffine(d, M4, (W4, H4), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    a, b = s['cam']
    e = ease(u, s['ease']) - 0.5
    dz = b[0] / a[0] - 1.0
    if abs(dz) < 0.03 and abs(b[1] - a[1]) < 0.01 and abs(b[2] - a[2]) < 0.01:
        dz = 0.03 if dz >= 0 else -0.03            # near-static shot: still give it a gentle depth breath
    tx, ty = -(b[1] - a[1]) * W * z, -(b[2] - a[2]) * H * z
    g = (dd - 0.5) * (k * e)
    Dx = g * (0.6 * tx + 1.25 * dz * (PX4 - CX))
    Dy = g * (0.6 * ty + 1.25 * dz * (PY4 - CY))
    qx, qy = PX4 - Dx, PY4 - Dy
    Mi = cv2.invertAffineTransform(M)
    mx = (Mi[0, 0] * qx + Mi[0, 1] * qy + Mi[0, 2]).astype(np.float32)
    my = (Mi[1, 0] * qx + Mi[1, 1] * qy + Mi[1, 2]).astype(np.float32)
    mx = cv2.resize(mx, (W, H), interpolation=cv2.INTER_LINEAR)
    my = cv2.resize(my, (W, H), interpolation=cv2.INTER_LINEAR)
    out = cv2.remap(src, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return out, dd


# ------------------------------------------------------------------ atmosphere
FOG1, FOG2 = _fbm(31, 640, 360), _fbm(32, 640, 360)
_gy, _gx = np.mgrid[0:360, 0:640].astype(np.float32)
_gy /= 360.0
_gx /= 640.0


def _shift(a, dx, dy=0.0):
    return cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_WRAP)


def fog(img, t, p, dd):
    a, sp = p.get('a', 0.3), p.get('sp', 0.02)
    col = np.array(p.get('col', [205, 205, 200]), np.float32)
    f = 0.6 * _shift(FOG1, t * sp * 640) + 0.4 * _shift(FOG2, -t * sp * 1.6 * 640, t * sp * 60)
    m = np.clip((f - p.get('thr', 0.35)) / 0.5, 0, 1) ** 1.3
    y0 = p.get('y', None)              # vertical bias: fog hugs the lower part of the frame
    if y0 is not None:
        m *= np.clip((_gy - y0) / 0.35 + 0.5, 0, 1)
    if dd is not None and p.get('far', True):
        m *= 1.0 - 0.7 * cv2.resize(dd, (640, 360))
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)[..., None] * a
    o = img.astype(np.float32)
    return np.clip(o + (col - o) * m, 0, 255).astype(np.uint8)


_mo = {}


def motes(img, t, p, s):
    """floating particles: dust in light beams, snow, ash. v = drift px/s (full res), z = per-particle depth."""
    key = s['id']
    if key not in _mo:
        r = np.random.default_rng(sum(map(ord, key)))
        n = p.get('n', 90)
        _mo[key] = dict(x=r.uniform(0, W, n), y=r.uniform(0, H, n), z=r.uniform(0.25, 1.0, n) ** 1.5,
                        ph=r.uniform(0, 6.28, n), fr=r.uniform(0.3, 1.1, n), b=r.uniform(0.4, 1.0, n))
    q = _mo[key]
    vx, vy = p.get('v', [6.0, -5.0])
    wob = p.get('wob', 14.0)
    tt = t - s['start']
    x = (q['x'] + vx * q['z'] * tt + wob * q['z'] * np.sin(q['fr'] * tt + q['ph'])) % (W + 80) - 40
    y = (q['y'] + vy * q['z'] * tt + wob * q['z'] * np.cos(0.8 * q['fr'] * tt + q['ph'])) % (H + 80) - 40
    size = p.get('size', [1.2, 6.0])
    col = np.array(p.get('col', [205, 228, 255]), np.float32)
    a = p.get('a', 0.65) * smooth(tt / 0.6)
    near = np.zeros((H // 2, W // 2, 3), np.uint8)
    far = np.zeros((H // 2, W // 2, 3), np.uint8)
    for i in range(len(x)):
        zz = q['z'][i]
        br = a * q['b'][i] * (0.75 + 0.25 * math.sin(2.3 * tt + q['ph'][i]))
        c = tuple(int(v) for v in np.clip(col * br, 0, 255))
        rad = max(1, int((size[0] + (size[1] - size[0]) * zz) / 2 + 0.5))
        cv2.circle(near if zz > 0.55 else far, (int(x[i] / 2), int(y[i] / 2)), rad, c, -1, cv2.LINE_AA)
    lay = cv2.add(cv2.GaussianBlur(far, (0, 0), 0.9), cv2.GaussianBlur(near, (0, 0), 2.6))
    return cv2.add(img, cv2.resize(lay, (W, H), interpolation=cv2.INTER_LINEAR))


_rn = {}


def rain(img, t, p, s):
    key = s['id']
    n = p.get('n', 260)
    if key not in _rn:
        r = np.random.default_rng(7 + sum(map(ord, key)))
        _rn[key] = (r.uniform(0, 1, n), r.uniform(0, 1, n), r.uniform(0.4, 1.0, n))
    X, Y, Z = _rn[key]
    sp, ang, ln = p.get('speed', 1500.0), p.get('ang', 0.12), p.get('len', 70.0)
    a = p.get('a', 0.22)
    lay = np.zeros((H // 2, W // 2, 3), np.uint8)
    for i in range(n):
        y = (Y[i] * (H + 200) + sp * Z[i] * t) % (H + 200) - 100
        x = (X[i] * (W + 300) + ang * sp * Z[i] * t) % (W + 300) - 150
        L = ln * Z[i]
        c = int(255 * a * Z[i])
        cv2.line(lay, (int(x / 2), int(y / 2)), (int((x - ang * L) / 2), int((y - L) / 2)), (c, c, c), 1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 0.7)
    return cv2.add(img, cv2.resize(lay, (W, H), interpolation=cv2.INTER_LINEAR))


def sparks(img, t, M, z, p, s):
    """burst of hot sparks with gravity from a plate-space point."""
    fx_, fy_ = apply_pt(M, p['src'][0] * SW, p['src'][1] * SH)
    rate = p.get('rate', 45.0)
    t0 = p.get('t0', s['start'])
    if t < t0:
        return img
    lay = np.zeros((H // 2, W // 2, 3), np.uint8)
    i0, i1 = max(0, int((t - t0 - 1.4) * rate)), int((t - t0) * rate) + 1
    salt = sum(map(ord, s['id'])) * 7919
    for i in range(i0, i1):
        r = random.Random(salt + i)
        birth = t0 + i / rate
        age, life = t - birth, r.uniform(0.35, 1.3)
        if age < 0 or age > life:
            continue
        ang = r.uniform(*p.get('ang', [-2.6, -0.5]))
        v = r.uniform(250, 900) * z
        vx, vy = v * math.cos(ang), v * math.sin(ang)
        g = 1400 * z
        x, y = fx_ + vx * age, fy_ + vy * age + 0.5 * g * age * age
        xp, yp = fx_ + vx * (age - 0.03), fy_ + vy * (age - 0.03) + 0.5 * g * (age - 0.03) ** 2
        f = (1 - age / life) ** 1.3
        col = (int(90 * f), int(190 * f), int(255 * f))
        cv2.line(lay, (int(xp / 2), int(yp / 2)), (int(x / 2), int(y / 2)), col, 1, cv2.LINE_AA)
    lay = cv2.add(lay, cv2.GaussianBlur(lay, (0, 0), 3.0))
    return cv2.add(img, cv2.resize(lay, (W, H), interpolation=cv2.INTER_LINEAR))


def rays(img, t, M, p):
    """volumetric god rays: bright pixels radially smeared away from the light source."""
    W8, H8 = W // 8, H // 8
    sm = cv2.resize(img, (W8, H8), interpolation=cv2.INTER_AREA).astype(np.float32)
    thr = p.get('thr', 170)
    br = np.clip((sm.max(axis=2, keepdims=True) - thr) / (255 - thr), 0, 1) * sm
    cx, cy = apply_pt(M, p['src'][0] * SW, p['src'][1] * SH)
    cx, cy = cx / 8, cy / 8
    acc, wsum = br.copy(), 1.0
    for i in range(1, 12):
        sc = 1 - 0.045 * i
        A = np.float32([[sc, 0, cx * (1 - sc)], [0, sc, cy * (1 - sc)]])
        wt = 0.9 ** i
        acc += wt * cv2.warpAffine(br, A, (W8, H8), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                                   borderMode=cv2.BORDER_CONSTANT)
        wsum += wt
    acc = cv2.GaussianBlur(acc / wsum, (0, 0), 1.2)
    a = p.get('a', 0.5) * (1 + 0.08 * math.sin(1.7 * t))
    up = cv2.resize(acc, (W, H), interpolation=cv2.INTER_LINEAR) * a
    return np.clip(img.astype(np.float32) + up, 0, 255).astype(np.uint8)


_fl = {}


def flare(img, t, M, p):
    cx, cy = apply_pt(M, p['src'][0] * SW, p['src'][1] * SH)
    if 'k' not in _fl:
        yy, xx = np.mgrid[0:H4, 0:W4 * 2].astype(np.float32)
        xx -= W4
        yy -= H4 / 2
        streak = np.exp(-(yy / 1.6) ** 2) * np.exp(-np.abs(xx) / (W4 * 0.35))
        glow = np.exp(-(xx ** 2 + yy ** 2) / (2 * 22.0 ** 2))
        _fl['k'] = (streak, glow)
    streak, glow = _fl['k']
    a = p.get('a', 0.5) * (1 + 0.06 * math.sin(2.1 * t))
    sc = np.array(p.get('col', [255, 190, 120]), np.float32)
    sh = np.float32([[1, 0, cx / 4 - W4], [0, 1, cy / 4 - H4 / 2]])
    s1 = cv2.warpAffine(streak, sh, (W4, H4))
    g1 = cv2.warpAffine(glow, sh, (W4, H4))
    lay = (s1[..., None] * sc + g1[..., None] * np.array([200, 225, 255], np.float32) * 0.6) * a
    up = cv2.resize(lay, (W, H), interpolation=cv2.INTER_LINEAR)
    return np.clip(img.astype(np.float32) + up, 0, 255).astype(np.uint8)


def glitch_frame(img, k, seed, dirn=1):
    """RGB split + displaced bands; k in 0..1."""
    if k <= 0.01:
        return img
    r = np.random.default_rng(seed)
    o = img.copy()
    sh = int(26 * k) * dirn
    o[..., 0] = np.roll(img[..., 0], sh, axis=1)
    o[..., 2] = np.roll(img[..., 2], -sh, axis=1)
    for _ in range(int(3 + 9 * k)):
        y0 = int(r.integers(0, H - 10))
        h = int(r.integers(6, 30 + int(110 * k)))
        dx = int(r.integers(-160, 160) * k)
        o[y0:y0 + h] = np.roll(o[y0:y0 + h], dx, axis=1)
    if k > 0.5:
        o = cv2.addWeighted(o, 1.0, np.full_like(o, (40, 18, 0)), 0.3 * k, 0)
    return o


def atmos(out, s, t, M, z, dd):
    fx = s['fx']
    if 'fog' in fx:
        out = fog(out, t, fx['fog'], dd)
    if 'rays' in fx:
        out = rays(out, t, M, fx['rays'])
    if 'flare' in fx:
        out = flare(out, t, M, fx['flare'])
    if 'motes' in fx:
        out = motes(out, t, fx['motes'], s)
    if 'rain' in fx:
        out = rain(out, t, fx['rain'], s)
    if 'sparks' in fx:
        out = sparks(out, t, M, z, fx['sparks'], s)
    if 'glitch' in fx:
        g = fx['glitch']
        for t0 in g['t']:
            if t0 <= t < t0 + g.get('d', 0.3):
                out = glitch_frame(out, math.sin(math.pi * (t - t0) / g.get('d', 0.3)), int(t * 24))
    return out


# ------------------------------------------------------------------ transitions
TRANS = {'whip', 'zoom', 'leak', 'glitch', 'luma', 'slide', 'dip', 'flash'}
LEAK = _fbm(41, 640, 360)


def _cubic(u):
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def _mblur(img, k, vertical=False):
    if k < 2:
        return img
    sm = cv2.resize(img, (W4, H4), interpolation=cv2.INTER_AREA)
    sm = cv2.blur(sm, (1, int(k)) if vertical else (int(k), 1))
    return cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR)


def transition2(A, B, s, t, u):
    kind, fx = s['trans'], s['fx']
    if kind in ('whip', 'slide'):
        vert = kind == 'slide'
        dirn = fx.get('dir', 1)
        e = _cubic(u)
        sp = (_cubic(min(1, u + 0.02)) - _cubic(max(0, u - 0.02))) / 0.04      # 0..3
        if vert:
            strip = np.vstack([A, B] if dirn > 0 else [B, A])
            o = int(e * H) if dirn > 0 else int((1 - e) * H)
            out = strip[o:o + H]
        else:
            strip = np.hstack([A, B] if dirn > 0 else [B, A])
            o = int(e * W) if dirn > 0 else int((1 - e) * W)
            out = strip[:, o:o + W]
        bl = _mblur(out, sp * (28 if not vert else 18), vert)
        m = clip01(sp / (1.4 if not vert else 2.2))
        return cv2.addWeighted(out, 1 - m, bl, m, 0)
    if kind == 'zoom':
        c = fx.get('zc', [0.5, 0.5])
        cx, cy = c[0] * W, c[1] * H
        if u < 0.5:
            img, k = A, (2 * u) ** 2.2
        else:
            img, k = B, (2 * (1 - u)) ** 2.2
        sc = 1 + 0.9 * k
        Mz = np.float32([[sc, 0, cx * (1 - sc)], [0, sc, cy * (1 - sc)]])
        out = cv2.warpAffine(img, Mz, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if k > 0.05:
            sm = cv2.resize(out, (W4, H4), interpolation=cv2.INTER_AREA).astype(np.float32)
            acc = sm.copy()
            for i in range(1, 6):
                q = 1 + 0.035 * i * k
                Mq = np.float32([[q, 0, cx / 4 * (1 - q)], [0, q, cy / 4 * (1 - q)]])
                acc += cv2.warpAffine(sm, Mq, (W4, H4), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            bl = cv2.resize(np.clip(acc / 6, 0, 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_LINEAR)
            out = cv2.addWeighted(out, 1 - min(1, k * 1.2), bl, min(1, k * 1.2), 0)
        return cv2.convertScaleAbs(out, alpha=1 + 0.25 * k)
    if kind == 'leak':
        e = ease(u, 'io')
        base = cv2.addWeighted(A, 1 - e, B, e, 0).astype(np.float32)
        col = np.array(fx.get('leak', [60, 150, 255]), np.float32)
        x = u * 1.6 - 0.3
        m = np.clip(1 - np.abs(_gx - x) / 0.45, 0, 1) ** 1.5 * (0.55 + 0.45 * LEAK) * math.sin(math.pi * u) ** 1.2
        m = cv2.resize(m.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)[..., None] * 0.95
        lk = col * m
        return np.clip(255 - (255 - base) * (255 - lk) / 255, 0, 255).astype(np.uint8)
    if kind == 'glitch':
        k = math.sin(math.pi * u)
        img = A if u < 0.5 else B
        return glitch_frame(img, k, int(t * 24) + 3)
    if kind == 'luma':
        lum = cv2.cvtColor(cv2.resize(B, (W4, H4), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
        lum = cv2.GaussianBlur(lum / 255, (0, 0), 3)
        thr = 1.05 - 1.35 * ease(u, 'io')
        m = np.clip((lum - thr) / 0.25, 0, 1)
        m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
        return np.clip(A * (1 - m) + B * m, 0, 255).astype(np.uint8)
    if kind == 'dip':
        if u < 0.5:
            return cv2.convertScaleAbs(A, alpha=(1 - smooth(u * 2)))
        return cv2.convertScaleAbs(B, alpha=smooth(u * 2 - 1))
    if kind == 'flash':
        e = smooth((u - 0.35) / 0.3)
        base = cv2.addWeighted(A, 1 - e, B, e, 0)
        k = math.sin(math.pi * u) ** 2 * fx.get('flash_a', 0.6)
        return cv2.addWeighted(base, 1 - k, np.full_like(base, (235, 245, 255)), k, 0)
    return B

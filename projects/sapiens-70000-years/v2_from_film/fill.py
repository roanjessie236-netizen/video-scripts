"""Pass-2 helpers: re-render the band under the v1 subtitles from the clean plates, through the exact v1 pipeline,
and blend it with the directly inverted pixels."""
import os, math
import numpy as np, cv2
import core as C
from core import W, H, R, smooth, BY0
from render_core import ease, clip01, NOISE_R, NOISE_B

PL = '/data/v2f/plates'
_pl = {}
MARG = 64


def plate(key):
    if key not in _pl:
        if len(_pl) > 5:
            _pl.pop(next(iter(_pl)))
        z = np.load(os.path.join(PL, key + '.npz'))
        _pl[key] = dict(plate=z['plate'].astype(np.float32), wt=z['wt'].astype(np.float32), bb=z['bb'])
    return _pl[key]


def fill_crop(t):
    xs = []
    for i, a in C.subs_at(t):
        L, lx, ly = C.sub_place(i)
        xs += [lx, lx + L.shape[1]]
    if not xs:
        return None
    return max(0, min(xs) - MARG), BY0, min(W, max(xs) + MARG), H


def _wp(key, Mx, crop):
    x0, y0, x1, y1 = crop
    P = plate(key)
    ox, oy = int(P['bb'][0]), int(P['bb'][1])
    Mp = C.shift(Mx, ox, oy, x0, y0)
    img = cv2.warpAffine(P['plate'], Mp, (x1 - x0, y1 - y0), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    wt = cv2.warpAffine(P['wt'], Mp, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                        borderValue=0)
    return img, wt


def shot_band(s, t, crop):
    x0, y0, x1, y1 = crop
    M, z = C.cam(s, t)
    fx = s['fx']
    sid = s['id']
    if 'painted' in fx and t < fx['painted']['t1']:
        p = fx['painted']
        k = smooth((t - p['t0']) / (p['t1'] - p['t0']))
        out, wt = _wp(sid + '_painted', M, crop)
        if k > 0:
            n, nw = _wp(sid, M, crop)
            out, wt = out * (1 - k) + n * k, np.minimum(wt, nw)
    else:
        out, wt = _wp(sid, M, crop)
    if 'zoomblur' in fx and t > fx['zoomblur']['t0']:
        t0 = fx['zoomblur']['t0']
        k = smooth((t - t0) / (s['end'] - t0))
        acc = out.copy()
        for i in range(1, 5):
            sc = 1 + 0.05 * i * k
            S = np.array([[sc, 0, (1 - sc) * W / 2], [0, sc, (1 - sc) * H / 2]])
            acc += _wp(sid, R.compose(S, M), crop)[0]
        out = acc / 5
    out = np.clip(out * C.gain_fx(s, t), 0, 255)
    lay = C.additive_layers(s, t, M, z)
    if lay is not None:
        out = np.clip(out + lay[y0:y1, x0:x1], 0, 255)
    if 'routes' in fx:
        _, xf = R.get_src(s)
        cv = np.zeros((H, W, 3), np.uint8)
        cv[y0:y1, x0:x1] = np.clip(out + 0.5, 0, 255).astype(np.uint8)
        cv = R.draw_routes(cv, t, M, xf)
        out = cv[y0:y1, x0:x1].astype(np.float32)
    return out, wt


def _up_crop(a, crop):
    x0, y0, x1, y1 = crop
    return cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)[y0:y1, x0:x1, None]


def trans_band(A, B, s, t, crop):
    kind, dur = s['trans'], s['tdur']
    if kind in ('cut', 'none') or dur <= 0:
        return B
    u = clip01((t - s['start']) / dur)
    if u >= 1:
        return B
    if kind == 'inkmap':
        a = ease(u, 'io')
        return A * (1 - a) + B * ((1 - a) * A / 255 + a) * a
    if kind == 'radial':
        cx, cy = s['fx'].get('radial', {}).get('c', [0.5, 0.5])
        r = np.sqrt(((R._gx - cx) * 16 / 9) ** 2 + (R._gy - cy) ** 2)
        r = r / r.max() + 0.22 * (NOISE_R - 0.5)
        edge = u * 1.35 - 0.12
        m = np.clip((edge - r) / 0.07, 0, 1)
        g = np.exp(-((r - edge) / 0.03) ** 2) * math.sin(math.pi * u) * 0.8
        m, g = _up_crop(m, crop), _up_crop(g, crop)
        return np.clip(A * (1 - m) + B * m + g * np.array([110, 200, 255], np.float32), 0, 255)
    if kind == 'burn':
        p = u * 1.16 - 0.08
        n = NOISE_B
        m = np.clip((p - n) / 0.025, 0, 1)
        e = np.exp(-((n - p) / 0.02) ** 2)
        ch = np.clip(1 - (n - p) / 0.07, 0, 1) * (n > p)
        m, e, ch = _up_crop(m, crop), _up_crop(e, crop), _up_crop(ch, crop)
        return np.clip(A * (1 - m) * (1 - 0.75 * ch) + B * m + e * np.array([40, 150, 255], np.float32) * 1.1, 0, 255)
    e = ease(u, 'io')
    return A * (1 - e) + B * e


def nconv(x, w, sig):
    num = cv2.GaussianBlur(x * w[..., None], (0, 0), sig)
    den = cv2.GaussianBlur(w, (0, 0), sig)
    return num, den


def clean_band(F, t, cgrain, debug=False):
    """returns (crop, cleaned float32 BGR band without the v1 subtitles) or None"""
    crop = fill_crop(t)
    if crop is None:
        return None
    x0, y0, x1, y1 = crop
    Fc = F[y0:y1, x0:x1].astype(np.float32)
    aA, aP, gm = C.sub_maps(t, x0, y0, x1, y1, glyph=True)
    hl = C.halo(gm)
    inv = 1 - aA
    xinv = (Fc - aP) / np.maximum(inv, 0.2)[..., None]
    fr, wt = None, None
    for s in C.visible(t):
        img, w = shot_band(s, t, crop)
        if fr is None:
            fr, wt = img, w
        else:
            fr = trans_band(fr, img, s, t, crop)
            wt = np.minimum(wt, w)
    g, beta, scr = C.post_params(t)
    mm = C.mm_known(scr, x0, y0, x1, y1)
    y = np.clip(g * fr + beta, 0, 255) * mm[..., None]
    # low-frequency ratio correction (parchment texture, residual gain) from trustworthy inverted pixels
    wr = np.clip((inv - 0.3) / 0.5, 0, 1) ** 2 * (1 - C.halo(gm, sig=4.0))
    nx, d1 = nconv(xinv, wr, 10)
    ny, _ = nconv(y, wr, 10)
    nx2, d2 = nconv(xinv, wr, 40)
    ny2, _ = nconv(y, wr, 40)
    r1 = (nx + 1) / (ny + 1)
    r2 = (nx2 + 1) / (ny2 + 1)
    a = np.clip(d1 / 0.25, 0, 1)[..., None]
    ratio = np.clip(r1 * a + r2 * (1 - a), 0.6, 1.6)
    yc = y * ratio + C.grain_mix(cgrain, x0, y0, x1, y1)
    c = (np.clip((inv - 0.4) / 0.4, 0, 1) * (1 - hl))[..., None]
    out = c * xinv + (1 - c) * yc
    if debug:
        return crop, out, dict(xinv=xinv, y=y, yc=yc, aA=aA, wt=wt, ratio=ratio)
    return crop, out

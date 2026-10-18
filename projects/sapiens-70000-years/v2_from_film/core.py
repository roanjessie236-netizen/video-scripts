"""Shared model of the v1 render (exact camera / post / typography) used to clean the user's film.
The user's film = v1 render (24 fps) -> editor export 30 fps by frame duplication: user frame k shows v1 frame floor(0.8k)
for k <= 7991 (t < 266.4 s); after that the editor sped up the ending (blended frames)."""
import sys, os, json, math, subprocess
sys.path.insert(0, '/data/v2f/v1core')
import numpy as np
import cv2
import render as R
from render_core import (W, H, SW, SH, VIG, SCRIM_C, SCRIM_L, SCRIM_T, SCRIM_B, GRAIN, smooth, cam_matrix,
                         shake_offset, flicker_gain, stars3d, embers, subtitle_layer, caption_layer, apply_pt)

TL1 = R.TL
TL2 = json.load(open('/data/v2f/v2core/shotlist.json', encoding='utf-8'))
SHOTS = R.SHOTS
BY = {s['id']: s for s in SHOTS}
SRC = '/data/film/src.mp4'
K_LAST_A = 7991          # last user frame of the normally-timed part
J_LAST_A = 6392          # last output frame (24 fps) taken from it: k = ceil(1.25 j)
N_OUT = 6819             # 284.125 s at 24 fps
BY0 = 1200               # top row of the subtitle work band
window = R.window


def k_of_j(j):
    if j <= J_LAST_A:
        return -(-j * 5 // 4)
    return 7992 + int(round((j - (J_LAST_A + 1)) * 1.25))


# ------------------------------------------------------------------ v1 typography
def sub_place(i, tl=TL1):
    s, e, text, *rest = tl['subtitles'][i]
    L = subtitle_layer(text)
    h, w = L.shape[:2]
    return L, int(round(W / 2 - w / 2)), int(round(H - 150 - h / 2))


def subs_at(t, tl=TL1):
    out = []
    for i, (s, e, *_) in enumerate(tl['subtitles']):
        a = window(t, s, e, 0.35, 0.35)
        if a > 0:
            out.append((i, a))
    return out


def sub_maps(t, x0, y0, x1, y1, glyph=False):
    """alpha*A and alpha*P (premultiplied BGR) of the v1 subtitles inside screen crop [y0:y1, x0:x1]."""
    aA = np.zeros((y1 - y0, x1 - x0), np.float32)
    aP = np.zeros((y1 - y0, x1 - x0, 3), np.float32)
    if glyph:
        gm = np.zeros((y1 - y0, x1 - x0), np.float32)
    for i, a in subs_at(t):
        L, lx, ly = sub_place(i)
        h, w = L.shape[:2]
        ax0, ay0, ax1, ay1 = max(x0, lx), max(y0, ly), min(x1, lx + w), min(y1, ly + h)
        if ax1 <= ax0 or ay1 <= ay0:
            continue
        Ls = L[ay0 - ly:ay1 - ly, ax0 - lx:ax1 - lx]
        A = aA[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0]
        P = aP[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0]
        # sequential 'over' compositing, same as blit()
        P[:] = P * (1 - Ls[..., 3:4] * a) + Ls[..., :3] * a
        A[:] = 1 - (1 - A) * (1 - Ls[..., 3] * a)
        if glyph:
            G = gm[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0]
            np.maximum(G, Ls[..., 1] / 239.0 * a, out=G)
    if glyph:
        return aA, aP, gm
    return aA, aP


_K11 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))


def halo(gm, thr=0.03, sig=2.0):
    """soft mask of the glyphs grown by ~5 px: compression ringing / smear around the white text lives here."""
    m = cv2.dilate((gm > thr).astype(np.uint8), _K11).astype(np.float32)
    return np.clip(cv2.GaussianBlur(m, (0, 0), sig) * 1.3, 0, 1)


# ------------------------------------------------------------------ v1 post()
def q(v, s):
    return round(v / s) * s


def post_params(t, tl=TL1, sub_alpha=None, cap_alpha=None):
    g, beta = 1.0, 0.0
    if t < 2.0:
        g *= smooth(t / 2.0)
    ach = max([window(t, c[0], c[1], 0.8, 0.8) for c in tl['chapters']] + [0])
    ati = window(t, tl['title_card'][0], tl['title_card'][1], 0.5, 0.9)
    aen = window(t, tl['endcard'][0], tl['endcard'][1], 1.2, 1.5)
    g *= (1 - 0.14 * ach) * (1 - 0.18 * ati)
    alow = max([window(t, s, e, 0.6, 0.6) for s, e, _, _ in tl['labels']] +
               [window(t, wa, wb, 0.8, 0.8) for wa, wb in tl['ticker']['windows']] + [0])
    acap = max([window(t, s, e, 1.0, 1.0) for s, e, *_ in tl['captions']] + [0]) if cap_alpha is None else cap_alpha
    asub = max([window(t, s, e, 0.35, 0.35) for s, e, *_ in tl['subtitles']] + [0]) if sub_alpha is None else sub_alpha
    sc, sl, st = max(0.62 * ach, 0.62 * ati, 0.3 * aen), 0.5 * alow, 0.35 * acap
    sb = 0.3 * asub
    for tf, amp, tau in tl['flashes']:
        d = t - tf
        if -0.12 <= d < 6 * tau:
            k = smooth((d + 0.12) / 0.12) if d < 0 else math.exp(-d / tau)
            beta += amp * k * 230
            g *= 1 + 0.3 * amp * k
    return g, beta, (q(sc, 0.05), q(sl, 0.05), q(st, 0.05), q(sb, 0.05))


def mm_known(sc_sl_st_sb, x0, y0, x1, y1):
    c, l, tt, b = sc_sl_st_sb
    sl_ = (slice(y0, y1), slice(x0, x1))
    m = VIG[sl_].copy()
    if c:
        m *= 1 - c * SCRIM_C[sl_]
    if l:
        m *= 1 - l * SCRIM_L[sl_]
    if tt:
        m *= 1 - tt * SCRIM_T[sl_]
    if b:
        m *= 1 - b * SCRIM_B[sl_]
    return m


# ------------------------------------------------------------------ shots
def visible(t):
    return [s for s in SHOTS if s['start'] <= t < s['end']]


def cam(s, t):
    u = (t - s['start']) / (s['end'] - s['start'])
    fx = s['fx']
    sh = shake_offset(fx['shake'], t, s['end']) if 'shake' in fx else (0.0, 0.0)
    return cam_matrix(s['cam'], u, s['ease'], sh)


def shift(M, ox, oy, cx=0, cy=0):
    """M maps source->screen. Return matrix mapping (plate coords + (ox,oy)) -> (screen - (cx,cy))."""
    N = M.copy()
    N[:, 2] = M[:, :2] @ np.array([ox, oy], np.float64) + M[:, 2] - np.array([cx, cy], np.float64)
    return N


def additive_layers(s, t, M, z):
    """stars3d + embers layers (full frame, uint8) that shot_frame adds on top, or None."""
    fx = s['fx']
    lay = None
    if 'stars3d' in fx:
        lay = stars3d(np.zeros((H, W, 3), np.uint8), t, fx['stars3d']['k1'], fx['stars3d']['k2'], s['start'])
    if 'embers' in fx:
        e = embers(np.zeros((H, W, 3), np.uint8), t, M, z, fx['embers'], s)
        lay = e if lay is None else cv2.add(lay, e)
    return lay


def gain_fx(s, t):
    fx = s['fx']
    g = 1.0
    if 'flicker' in fx:
        g *= flicker_gain(t, fx['flicker']['amp'])
    if 'dim' in fx:
        g *= fx['dim']
    return g


def phase(s, t):
    """which plate a frame of shot s belongs to ('' normal, 'painted'); None = not usable for accumulation."""
    fx = s['fx']
    if 'painted' in fx:
        p = fx['painted']
        if t < p['t0']:
            return 'painted'
        if t < p['t1']:
            return None
    if 'zoomblur' in fx and t > fx['zoomblur']['t0']:
        return None
    if 'lights_on' in fx and fx['lights_on']['t0'] - 0.05 < t < fx['lights_on']['t1'] + 0.05:
        return None
    if 'routes' in fx:
        return ''
    return ''


# ------------------------------------------------------------------ grain
_GH = None


def grain_hp(y0, y1):
    global _GH
    if _GH is None or _GH[0] != (y0, y1):
        gs = []
        for i in range(8):
            g = GRAIN[i][y0:y1, :, 0].astype(np.float32)
            gs.append(g - cv2.GaussianBlur(g, (0, 0), 4))
        _GH = ((y0, y1), np.stack(gs))
    return _GH[1]


def fit_grain(F, y0=900, y1=1200, step=2):
    """least-squares weights of the 8 v1 grain frames still present in user frame F (after two lossy encodes)."""
    G = grain_hp(y0, y1)[:, ::step, ::step]
    g = cv2.cvtColor(F[y0:y1], cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = (g - cv2.GaussianBlur(g, (0, 0), 4))[::step, ::step]
    A = G.reshape(8, -1)
    c, *_ = np.linalg.lstsq(A.T, g.ravel(), rcond=None)
    return np.clip(c, -0.2, 1.0)


def grain_mix(c, x0, y0, x1, y1):
    acc = np.zeros((y1 - y0, x1 - x0), np.float32)
    for i in range(8):
        if abs(c[i]) > 0.01:
            acc += c[i] * (GRAIN[i][y0:y1, x0:x1, 0].astype(np.float32) - 128)
    return acc[..., None]


# ------------------------------------------------------------------ decoding
def frames(k0=0, k1=None):
    """sequential decode of user frames k0..k1-1 -> (k, frame)"""
    cmd = ['ffmpeg', '-v', 'error', '-ss', '%.4f' % max(0, k0 / 30 - 0.0005), '-i', SRC, '-f', 'rawvideo',
           '-pix_fmt', 'bgr24', '-']
    if k1 is not None:
        cmd[-1:-1] = ['-frames:v', str(k1 - k0)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)
    n = W * H * 3
    k = k0
    try:
        while True:
            b = p.stdout.read(n)
            if len(b) < n:
                break
            yield k, np.frombuffer(b, np.uint8).reshape(H, W, 3)
            k += 1
            if k1 is not None and k >= k1:
                break
    finally:
        p.stdout.close()
        p.kill()
        p.wait()

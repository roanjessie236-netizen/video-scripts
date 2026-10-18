"""v3 picture: the v2 2K picture re-timed with the v3 time warp (warp.py).
Output frame j (24 fps) at new time u = j/24 -> v1 time t = Winv(u) -> nearest v1 frame m (user frame ceil(1.25 m)).
 - v1 subtitles removed on the source frame (fill.clean_band, as v2f)
 - sub-frame motion: the cleaned frame is re-projected with the exact v1 camera of the dominant shot,
   D = A(t) * A(m/24)^-1 (smooth slow/fast motion instead of repeated/skipped frames); the screen-space v1 typography
   (labels, year ticker, chapter / title cards) is pasted back un-warped through its exact alpha so it stays still
 - v1 bottom scrim -> v2 scrim of the new subtitle timing, mild luma sharpening, v2 bilingual subtitles at the new times
 - the user's own ending cut (from v1 266.375 s) is kept frame-exact, only shifted (warp.OFF_END)
usage: python3 render_v3.py SEG [SEG ...] | test J0 J1 OUT.mp4
"""
import sys, os, json, time, subprocess
sys.path.insert(0, '/data/v2f'); sys.path.insert(0, '/data/v3')
import numpy as np, cv2
import core as C
import fill
import render_v2f as RV
import warp as WP
from core import W, H, SCRIM_B, q, window, R
from render_core import cam_matrix, lower_layer, chapter_layer, title_layer, endcard_layer, caption_layer, smooth

TL3 = json.load(open('/data/v3/shotlist_v3.json', encoding='utf-8'))
SEGLEN = 480
RB0 = RV.RB0
OUT = '/data/v3/segs'
rc2 = RV.rc2
CAP_ZH_H = caption_layer('字').shape[0]
N_SEG = -(-WP.N_NEW // SEGLEN)


def src_of(j):
    """-> (user frame k, v1 frame m or None, v1 time t or None)"""
    if j >= WP.J_END_NEW:
        return 7992 + int(round((j - WP.J_END_NEW) * 1.25)), None, None
    t = WP.Winv(j / 24.0)
    m = min(int(round(t * 24)), C.J_LAST_A)
    if abs(t * 24 - m) < 1e-6:
        t = m / 24.0
    return -(-m * 5 // 4), m, t


# ------------------------------------------------------------------ camera re-projection
def dom_shot(t):
    vs = sorted(C.visible(t), key=lambda s: s['start'])
    if not vs:
        return None
    if len(vs) == 1:
        return vs[0]
    A, B = vs[-2], vs[-1]
    td = B.get('tdur') or 0
    return B if td <= 0 or (t - B['start']) / td >= 0.5 else A


def delta(t_src, t_out):
    s = dom_shot(t_out)
    if s is None:
        return None
    def cam(tt):   # v1 camera without the rocket shake (the jitter itself is not interpolated)
        return np.vstack([cam_matrix(s['cam'], (tt - s['start']) / (s['end'] - s['start']), s['ease'])[0], [0, 0, 1]])
    A0, A1 = cam(t_src), cam(t_out)
    D = (A1 @ np.linalg.inv(A0))[:2]
    P = np.array([[0, 0], [W, 0], [0, H], [W, H]], np.float64)
    if np.abs(P @ D[:, :2].T + D[:, 2] - P).max() < 0.03:
        return None
    return D


# ------------------------------------------------------------------ v1 screen-space typography (exact alpha)
def typo_layers(t):
    TL = C.TL1
    out = []
    for s, e, num, name, eng in TL['chapters']:
        a = window(t, s, e, 0.8, 0.8)
        if a:
            L = chapter_layer(num, name, eng)
            out.append((L, W / 2 - L.shape[1] / 2, H / 2 - 20 + 16 * (1 - smooth((t - s) / 1.6)) - L.shape[0] / 2, a))
    ts_, te = TL['title_card']
    a = window(t, ts_, te, 0.5, 0.9)
    if a:
        L = title_layer()
        out.append((L, W / 2 - L.shape[1] / 2, H / 2 - 30 + 10 * (1 - smooth((t - ts_) / 2.0)) - L.shape[0] / 2, a))
    for s, e, l1, l2 in TL['labels']:
        a = window(t, s, e, 0.6, 0.6)
        if a:
            L = lower_layer(l1, l2)
            out.append((L, R.LX, R.LBOT - L.shape[0], a))
    got = []
    orig = R.draw_lower
    R.draw_lower = lambda frame, L, a: got.append((L, R.LX, R.LBOT - L.shape[0], a))
    try:
        R.draw_ticker(None, t)
    finally:
        R.draw_lower = orig
    out += [g for g in got if g[3] > 0.001]
    for s, e, text, *en in TL['captions']:
        a = window(t, s, e, 1.0, 1.0)
        if a:
            L = caption_layer(text, en[0] if en else '')
            out.append((L, W / 2 - L.shape[1] / 2, H * 0.27 - CAP_ZH_H / 2, a))
    es, ee = TL['endcard']
    a = window(t, es, ee, 1.2, 1.5)
    if a:
        L = endcard_layer()
        out.append((L, W / 2 - L.shape[1] / 2, H / 2 - L.shape[0] / 2, a))
    return out


def typo_mask(t):
    """(bbox, alpha) of all v1 screen-space typography at v1 time t (1 px grown), or None"""
    lays = typo_layers(t)
    if not lays:
        return None
    boxes = []
    for L, x, y, a in lays:
        x, y = int(round(x)), int(round(y))
        h, w = L.shape[:2]
        boxes.append((max(0, x), max(0, y), min(W, x + w), min(H, y + h), L, x, y, a))
    X0 = max(0, min(b[0] for b in boxes) - 2); Y0 = max(0, min(b[1] for b in boxes) - 2)
    X1 = min(W, max(b[2] for b in boxes) + 2); Y1 = min(H, max(b[3] for b in boxes) + 2)
    keep = np.ones((Y1 - Y0, X1 - X0), np.float32)
    for x0, y0, x1, y1, L, x, y, a in boxes:
        if x1 > x0 and y1 > y0:
            keep[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] *= 1 - L[y0 - y:y1 - y, x0 - x:x1 - x, 3] * a
    M = cv2.dilate(1 - keep, np.ones((3, 3), np.uint8))
    return (X0, Y0, X1, Y1), M


# ------------------------------------------------------------------ per frame
def clean_src(F, m):
    t = m / 24.0
    G = F.copy()
    cg = None
    if C.subs_at(t):
        cg = C.fit_grain(F)
        r = fill.clean_band(F, t, cg)
        if r is not None:
            (x0, y0, x1, y1), out = r
            Bf = G[RB0:].astype(np.float32)
            Bf[y0 - RB0:y1 - RB0, x0:x1] = out
            G[RB0:] = np.clip(Bf + 0.5, 0, 255).astype(np.uint8)
    return G, cg, q(0.3 * RV.asub(t, C.TL1), 0.05)


def finish(j, F, G, cg, sb1, m, t):
    u = j / 24.0
    D = delta(m / 24.0, t) if t != m / 24.0 else None
    if D is not None:
        G2 = cv2.warpAffine(G, D, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        tm = typo_mask(m / 24.0)
        if tm is not None:
            (X0, Y0, X1, Y1), Mk = tm
            Mk = Mk[..., None]
            G2[Y0:Y1, X0:X1] = np.clip(G2[Y0:Y1, X0:X1] * (1 - Mk) + G[Y0:Y1, X0:X1] * Mk + 0.5, 0, 255).astype(np.uint8)
    else:
        G2 = G.copy()
    v2 = [(s, e, zh, en) for s, e, zh, _, en in TL3['subtitles'] if window(u, s, e, 0.35, 0.35) > 0]
    sb2 = q(0.3 * RV.asub(u, TL3), 0.05)
    if sb1 != sb2:
        Bf = G2[RB0:].astype(np.float32)
        Bf *= ((1 - sb2 * SCRIM_B[RB0:]) / (1 - sb1 * SCRIM_B[RB0:]))[..., None]
        G2[RB0:] = np.clip(Bf + 0.5, 0, 255).astype(np.uint8)
    G2 = RV.sharpen(G2)
    if v2:
        if cg is None:
            cg = C.fit_grain(F)
        Bf = G2[RB0:].astype(np.float32)
        gr = C.grain_mix(cg, 0, RB0, W, H)
        for s, e, zh, en in v2:
            a = window(u, s, e, 0.35, 0.35)
            L = rc2.subtitle_layer(zh, en)
            RV.comp(Bf, L, W / 2 - L.shape[1] / 2, H - 150 - RV.SUB_ZH_H / 2, a, gr)
        G2[RB0:] = np.clip(Bf + 0.5, 0, 255).astype(np.uint8)
    return G2


def encoder(path):
    """= render_v2f.encoder (x264 High, CRF, bt709) with a smaller lookahead / thread pool (2 renders fit in 4 GB)"""
    vf = 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p'
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H), '-r', '24',
           '-i', '-', '-vf', vf, '-c:v', 'libx264', '-preset', RV.PRESET, '-crf', RV.CRF, '-profile:v', 'high',
           '-threads', os.environ.get('X264_THREADS', '2'),
           '-x264-params', 'keyint=48:min-keyint=24:rc-lookahead=%s' % os.environ.get('LOOKAHEAD', '20'),
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def render_seg(si, j0=None, j1=None, path=None):
    j0 = si * SEGLEN if j0 is None else j0
    j1 = min(WP.N_NEW, j0 + SEGLEN) if j1 is None else j1
    path = path or os.path.join(OUT, 'seg_%02d.mp4' % si)
    if os.path.exists(path):
        print('skip', path)
        return
    tmp = path + '.part.mp4'
    want = {}
    for j in range(j0, j1):
        k, m, t = src_of(j)
        want.setdefault(k, []).append((j, m, t))
    ks = sorted(want)
    enc = encoder(tmp)
    t0 = time.time(); n = 0
    for k, F in C.frames(ks[0], ks[-1] + 1):
        if k not in want:
            continue
        lst = want[k]
        if lst[0][1] is None:   # ending: identical to v2f
            for j, _, _ in lst:
                G = RV.process(j - WP.J_END_NEW + WP.J_END_OLD, k, F)
                enc.stdin.write(G.tobytes()); n += 1
        else:
            G, cg, sb1 = clean_src(F, lst[0][1])
            for j, m, t in lst:
                enc.stdin.write(finish(j, F, G, cg, sb1, m, t).tobytes()); n += 1
        if n % 120 < len(lst):
            print('  seg %d: %d/%d  %.1fs' % (si, n, j1 - j0, time.time() - t0), flush=True)
    enc.stdin.close()
    enc.wait()
    assert n == j1 - j0, (n, j1 - j0)
    os.rename(tmp, path)
    print('done seg %d (%d frames) %.1fs' % (si, n, time.time() - t0), flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'test':
        render_seg(-1, int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    else:
        for a in sys.argv[1:]:
            render_seg(int(a))

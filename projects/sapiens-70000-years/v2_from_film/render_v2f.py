"""Pass 2: build the v2 picture from the user's full film (2560x1440).
 - output 24 fps, 6819 frames (284.125 s); output frame j <- user frame k_of_j(j)
 - t < 266.4 s: remove the burned-in v1 Chinese subtitles (exact v1 model + clean plates, fill.clean_band),
   swap the v1 subtitle scrim for the v2 one and draw the v2 bilingual subtitles (zh + en) exactly as render.py v2
 - ending (user's own re-timed cut): keep the baked zh closing questions, add the v2 English line with the measured alpha
usage: python3 render_v2f.py SEG [SEG ...]   (segments of SEGLEN frames, resumable: existing segs/seg_XX.mp4 are skipped)
"""
import sys, os, json, time, subprocess, importlib.util
import numpy as np, cv2
import core as C
import fill
from core import W, H, SCRIM_B, q, window

spec = importlib.util.spec_from_file_location('rc2', '/data/sp/render_core.py')
rc2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc2)

SEGLEN = 480
RB0 = 1000                      # rows touched by subtitles / bottom scrim
CRF = os.environ.get('CRF', '17')
PRESET = os.environ.get('PRESET', 'medium')
VF = os.environ.get('VF', '')   # optional extra ffmpeg filter
SHARP = float(os.environ.get('SHARP', '0.35'))   # luma unsharp amount (radius SHARP_SIG); 0 = off
SHARP_SIG = float(os.environ.get('SHARP_SIG', '2.0'))
OUT = '/data/v2f/segs'

SUB_ZH_H = rc2.subtitle_layer('字').shape[0]
TL2 = C.TL2


def asub(t, tl):
    return max([window(t, s, e, 0.35, 0.35) for s, e, *_ in tl['subtitles']] + [0])


def comp(Bf, L, x, y, a, gr):
    """premultiplied layer L composited into float band Bf (rows RB0..) with grain under the glyphs"""
    h, w = L.shape[:2]
    x, y = int(round(x)), int(round(y)) - RB0
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(Bf.shape[0], y + h)
    Ls = L[y0 - y:y1 - y, x0 - x:x1 - x]
    A = Ls[..., 3:4] * a
    roi = Bf[y0:y1, x0:x1]
    roi[:] = roi * (1 - A) + Ls[..., :3] * a + (A * gr[y0:y1, x0:x1] if gr is not None else 0)


# ---- ending: English line under the baked closing questions
CAP = json.load(open('/data/v2f/cap_alpha.json'))
CAPK = {r[0]: r for r in CAP}
CAPWIN = [(8130, 8245), (8262, 8348)]


def cap_alpha_k(k):
    """measured alpha of the baked zh questions (normalised plateau/baseline, 3-tap smoothed)"""
    out = []
    for c in (0, 1):
        vals = [float(np.clip((CAPK[kk][1 + 2 * c] - 0.05) / 0.93, 0, 1)) for kk in (k - 1, k, k + 1) if kk in CAPK]
        v = float(np.mean(vals)) if vals else 0.0
        if not (CAPWIN[c][0] <= k <= CAPWIN[c][1]):   # outside the caption's life (8349 = user's hard cut)
            v = 0.0
        out.append(v if v > 0.02 else 0.0)
    return out


EN_CAPS = []
for (s, e, zh, en) in TL2['captions']:
    Lzh = rc2.caption_layer(zh)
    Le = rc2.text_layer(en, rc2.font('Light', 42), (214, 222, 236), shadow=(8, 0.8, 2), whole=True)
    Lst = rc2.caption_layer(zh, en)
    gap = -int(Lzh.shape[0] * 0.22) - int(Le.shape[0] * 0.25)
    top = H * 0.27 - rc2.caption_layer('字').shape[0] / 2
    x = int(round(W / 2 - Lst.shape[1] / 2)) + (Lst.shape[1] - Le.shape[1]) // 2
    y = int(round(top)) + Lzh.shape[0] + gap
    EN_CAPS.append((Le, x, y))


def sharpen(G):
    """mild luma-only unsharp mask (the film's assets are soft upscales; this restores some local contrast)"""
    if SHARP <= 0:
        return G
    Y = cv2.cvtColor(G, cv2.COLOR_BGR2GRAY).astype(np.float32)
    d = (Y - cv2.GaussianBlur(Y, (0, 0), SHARP_SIG)) * SHARP
    return np.clip(G.astype(np.float32) + d[..., None] + 0.5, 0, 255).astype(np.uint8)


def process(j, k, F):
    t = j / 24.0
    G = F.copy()
    if j <= C.J_LAST_A:
        v1 = C.subs_at(t)
        v2 = [(s, e, zh, en[0] if en else '') for s, e, zh, _, *en in TL2['subtitles'] if window(t, s, e, 0.35, 0.35) > 0]
        sb1 = q(0.3 * asub(t, C.TL1), 0.05)
        sb2 = q(0.3 * asub(t, TL2), 0.05)
        cg = C.fit_grain(F) if (v1 or v2) else None
        if v1 or sb1 != sb2:
            Bf = G[RB0:].astype(np.float32)
            if v1:
                r = fill.clean_band(F, t, cg)
                if r is not None:
                    (x0, y0, x1, y1), out = r
                    Bf[y0 - RB0:y1 - RB0, x0:x1] = out
            if sb1 != sb2:
                Bf *= ((1 - sb2 * SCRIM_B[RB0:]) / (1 - sb1 * SCRIM_B[RB0:]))[..., None]
            G[RB0:] = np.clip(Bf + 0.5, 0, 255).astype(np.uint8)
        G = sharpen(G)
        if v2:
            Bf = G[RB0:].astype(np.float32)
            gr = C.grain_mix(cg, 0, RB0, W, H)
            for s, e, zh, en in v2:
                a = window(t, s, e, 0.35, 0.35)
                L = rc2.subtitle_layer(zh, en)
                comp(Bf, L, W / 2 - L.shape[1] / 2, H - 150 - SUB_ZH_H / 2, a, gr)
            G[RB0:] = np.clip(Bf + 0.5, 0, 255).astype(np.uint8)
        return G
    G = sharpen(G)
    al = cap_alpha_k(k)
    if max(al) > 0:
        cg = C.fit_grain(F, 700, 1000)
        y0, y1 = 300, 700
        Bf = G[y0:y1].astype(np.float32)
        gr = C.grain_mix(cg, 0, y0, W, y1)
        for (Le, x, y), a in zip(EN_CAPS, al):
            if a > 0:
                comp_rows(Bf, Le, x, y - y0, a, gr)
        G[y0:y1] = np.clip(Bf + 0.5, 0, 255).astype(np.uint8)
    return G


def comp_rows(Bf, L, x, y, a, gr):
    h, w = L.shape[:2]
    x, y = int(round(x)), int(round(y))
    Ls = L
    A = Ls[..., 3:4] * a
    roi = Bf[y:y + h, x:x + w]
    roi[:] = roi * (1 - A) + Ls[..., :3] * a + A * gr[y:y + h, x:x + w]


def encoder(path):
    vf = 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p'
    if VF:
        vf = VF + ',' + vf
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H), '-r', '24',
           '-i', '-', '-vf', vf, '-c:v', 'libx264', '-preset', PRESET, '-crf', CRF, '-profile:v', 'high',
           '-x264-params', 'keyint=48:min-keyint=24', '-color_primaries', 'bt709', '-color_trc', 'bt709',
           '-colorspace', 'bt709', '-movflags', '+faststart', path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def render_seg(si, j0=None, j1=None, path=None):
    j0 = si * SEGLEN if j0 is None else j0
    j1 = min(C.N_OUT, j0 + SEGLEN) if j1 is None else j1
    path = path or os.path.join(OUT, 'seg_%02d.mp4' % si)
    if os.path.exists(path):
        print('skip', path)
        return
    tmp = path + '.part.mp4'
    want = {C.k_of_j(j): j for j in range(j0, j1)}
    k0, k1 = C.k_of_j(j0), C.k_of_j(j1 - 1) + 1
    enc = encoder(tmp)
    t0 = time.time(); n = 0
    for k, F in C.frames(k0, k1):
        if k in want:
            G = process(want[k], k, F)
            enc.stdin.write(G.tobytes())
            n += 1
            if n % 120 == 0:
                print('  seg %d: %d/%d  %.1fs' % (si, n, j1 - j0, time.time() - t0), flush=True)
    enc.stdin.close()
    enc.wait()
    assert n == j1 - j0, (n, j1 - j0)
    os.rename(tmp, path)
    print('done seg %d (%d frames) %.1fs' % (si, n, time.time() - t0), flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'test':
        j0, j1 = int(sys.argv[2]), int(sys.argv[3])
        render_seg(-1, j0, j1, sys.argv[4])
    else:
        for a in sys.argv[1:]:
            render_seg(int(a))

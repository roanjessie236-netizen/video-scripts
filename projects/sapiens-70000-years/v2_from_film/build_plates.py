"""Pass 1: per shot, accumulate a clean source-space plate of everything that ever sits under a v1 subtitle.
Each user frame is undone through the exact v1 pipeline (subtitle blit, post gain/flash/vignette/scrims, additive fx,
flicker) and inverse-warped by the exact camera matrix. Output: plates/<shot>[_painted].npz"""
import sys, os, time, json
import numpy as np, cv2
import core as C
from core import W, H, SW, SH, BY0
from overlays import overlay_alpha

OUT = '/data/v2f/plates'
MARG = 64


def fill_crop(t):
    xs = []
    for i, a in C.subs_at(t):
        L, lx, ly = C.sub_place(i)
        xs += [lx, lx + L.shape[1]]
    if not xs:
        return None
    return max(0, min(xs) - MARG), BY0, min(W, max(xs) + MARG), H


def plan():
    """plates needed: key -> dict(shot, phase, bbox in source coords, fill frames)"""
    P = {}
    for j in range(0, C.J_LAST_A + 1):
        t = j / 24
        cr = fill_crop(t)
        if cr is None:
            continue
        x0, y0, x1, y1 = cr
        for s in C.visible(t):
            ph = C.phase(s, t)
            if ph is None:  # inside painted/zoomblur transition: needs the normal plate (+painted for bison)
                phs = ['', 'painted'] if 'painted' in s['fx'] else ['']
            else:
                phs = [ph]
            M, z = C.cam(s, t)
            Mi = cv2.invertAffineTransform(M)
            pts = np.array([[x0, y0], [x1, y0], [x0, y1], [x1, y1]], np.float64)
            src = pts @ Mi[:, :2].T + Mi[:, 2]
            for ph in phs:
                key = s['id'] + ('_' + ph if ph else '')
                d = P.setdefault(key, dict(shot=s['id'], phase=ph, bb=[1e9, 1e9, -1e9, -1e9], fills=[]))
                d['fills'].append(j)
                bb = d['bb']
                bb[0] = min(bb[0], src[:, 0].min()); bb[1] = min(bb[1], src[:, 1].min())
                bb[2] = max(bb[2], src[:, 0].max()); bb[3] = max(bb[3], src[:, 1].max())
    for key, d in P.items():
        bb = d['bb']
        d['bb'] = [int(max(0, np.floor(bb[0]) - 8)), int(max(0, np.floor(bb[1]) - 8)),
                   int(min(SW, np.ceil(bb[2]) + 8)), int(min(SH, np.ceil(bb[3]) + 8))]
        s = C.BY[d['shot']]
        d['acc'] = [j for j in range(int(np.ceil(s['start'] * 24)), int(np.ceil(s['end'] * 24)))
                    if j <= C.J_LAST_A and [x['id'] for x in C.visible(j / 24)] == [s['id']]
                    and C.phase(s, j / 24) == d['phase']]
    return P


def accumulate(d, j, F, acc):
    s = C.BY[d['shot']]
    t = j / 24
    ox, oy, bx1, by1 = d['bb']
    bw, bh = bx1 - ox, by1 - oy
    M, z = C.cam(s, t)
    pts = np.array([[ox, oy], [bx1, oy], [ox, by1], [bx1, by1]], np.float64) @ M[:, :2].T + M[:, 2]
    x0, y0 = int(max(0, np.floor(pts[:, 0].min()) - 3)), int(max(0, np.floor(pts[:, 1].min()) - 3))
    x1, y1 = int(min(W, np.ceil(pts[:, 0].max()) + 3)), int(min(H, np.ceil(pts[:, 1].max()) + 3))
    if x1 - x0 < 8 or y1 - y0 < 8:
        return
    Fc = F[y0:y1, x0:x1].astype(np.float32)
    aA, aP, gm = C.sub_maps(t, x0, y0, x1, y1, glyph=True)
    hl = C.halo(gm)
    inv = 1 - aA
    x = (Fc - aP) / np.maximum(inv, 0.2)[..., None]
    g, beta, scr = C.post_params(t)
    if g < 0.08:
        return
    mm = C.mm_known(scr, x0, y0, x1, y1)
    x = (x / mm[..., None] - beta) / g
    lay = C.additive_layers(s, t, M, z)
    if lay is not None:
        x -= lay[y0:y1, x0:x1].astype(np.float32)
    gf = C.gain_fx(s, t)
    x /= gf
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    ov = overlay_alpha(t, x0, y0, x1, y1, s, M)
    w = (np.clip(inv - 0.2, 0, 1) / 0.8) ** 2 * (1 - ov) * (1 - hl) * (g * gf * mm) ** 2
    w[(Fc.max(2) > 252)] *= 0.05
    Mp = C.shift(M, ox, oy, x0, y0)  # plate coords -> crop coords
    fl = cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP
    ww = cv2.warpAffine(w, Mp, (bw, bh), flags=fl, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    xw = cv2.warpAffine(x * w[..., None], Mp, (bw, bh), flags=fl, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    acc['S'] += xw
    acc['W'] += ww
    acc['n'] += 1


def push_pull(img, wt, thr=0.3):
    """fill low-weight pixels from a weighted image pyramid (smooth, temporally stable fallback)."""
    levels = []
    I, Wt = img * wt[..., None], wt.copy()
    while min(Wt.shape) > 4:
        levels.append((I, Wt))
        I = cv2.pyrDown(I)
        Wt = cv2.pyrDown(Wt)
    est = I / np.maximum(Wt, 1e-6)[..., None]
    for I, Wt in reversed(levels):
        up = cv2.resize(est, (Wt.shape[1], Wt.shape[0]), interpolation=cv2.INTER_LINEAR)
        a = np.clip(Wt / thr, 0, 1)[..., None]
        est = (I / np.maximum(Wt, 1e-6)[..., None]) * a + up * (1 - a)
    return est


def finalize(key, d, acc):
    S, Wt = acc['S'], acc['W']
    mean = S / np.maximum(Wt, 1e-6)[..., None]
    # weight in "effective clean frames"
    filled = push_pull(np.where(Wt[..., None] > 1e-4, mean, 0), np.clip(Wt / 2.0, 0, 1), thr=1.0)
    np.savez_compressed(os.path.join(OUT, key + '.npz'), plate=filled.astype(np.float16), wt=Wt.astype(np.float16),
                        bb=np.array(d['bb']), n=acc['n'])
    cov = float((Wt > 0.5).mean())
    print(f'  saved {key}: bb={d["bb"]} acc={acc["n"]} frames, coverage(w>0.5)={cov:.3f}', flush=True)
    return cov


def main():
    only = set(sys.argv[1].split(',')) if len(sys.argv) > 1 else None
    P = plan()
    if only:
        P = {k: v for k, v in P.items() if k in only}
    todo = {k: v for k, v in P.items() if not os.path.exists(os.path.join(OUT, k + '.npz'))}
    json.dump({k: dict(bb=v['bb'], fills=[v['fills'][0], v['fills'][-1], len(v['fills'])], acc=len(v['acc']))
               for k, v in P.items()}, open(os.path.join(OUT, 'plan.json'), 'w'), indent=1)
    print(len(P), 'plates planned,', len(todo), 'to build', flush=True)
    if not todo:
        return
    need = {}
    for key, d in todo.items():
        for j in d['acc']:
            need.setdefault(j, []).append(key)
    last = {key: max(d['acc']) if d['acc'] else -1 for key, d in todo.items()}
    accs = {}
    jmin, jmax = min(need), max(need)
    k0, k1 = C.k_of_j(jmin), C.k_of_j(jmax) + 1
    t0 = time.time()
    for k, F in C.frames(k0, k1):
        j = (4 * k) // 5
        if C.k_of_j(j) != k or j not in need:
            continue
        for key in need[j]:
            d = todo[key]
            if key not in accs:
                bw, bh = d['bb'][2] - d['bb'][0], d['bb'][3] - d['bb'][1]
                accs[key] = dict(S=np.zeros((bh, bw, 3), np.float32), W=np.zeros((bh, bw), np.float32), n=0)
            accumulate(d, j, F, accs[key])
            if j == last[key]:
                finalize(key, d, accs.pop(key))
        if j % 240 == 0:
            print(f'j={j} t={j / 24:.1f}s  {time.time() - t0:.0f}s elapsed', flush=True)
    for key in list(accs):
        finalize(key, todo[key], accs.pop(key))
    print('done', time.time() - t0, flush=True)


if __name__ == '__main__':
    main()

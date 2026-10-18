#!/usr/bin/env python3
"""Renders 《人类简史：七万年的文明觉醒》 from shotlist.json + assets/.

  python3 timeline.py                                   # regenerate shotlist.json
  python3 render.py --stills 3,12,58 [--sheet]          # QA stills -> frames/
  python3 render.py --video out/video.mp4 [--start 0 --end 300 --preset medium --crf 20]
  ffmpeg -i out/video.mp4 -i out/score.wav -c:v copy -c:a aac -b:a 256k -shortest out/final.mp4
"""
import argparse, math, os, subprocess, sys, time
import cv2
import numpy as np
from render_core import *

SHOTS = TL['shots']
for i, s in enumerate(SHOTS):
    s['tdur'] = max(0.0, SHOTS[i - 1]['end'] - s['start']) if i else 0.0


# ------------------------------------------------------------------ migration map
def catmull(pts, n=14):
    P = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = [np.array(q, np.float64) for q in P[i - 1:i + 3]]
        for s in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * (2 * p1 + (p2 - p0) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s
                              + (3 * p1 - p0 - 3 * p2 + p3) * s ** 3))
    out.append(np.array(pts[-1], np.float64))
    return np.array(out)


RD = []
for r in TL['routes']:
    segs, cur = [], []
    for p in r[2] + [None]:
        if p is None:
            if len(cur) > 1:
                segs.append(catmull(cur))
            cur = []
        else:
            cur.append(p)
    lens = [np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(sg, axis=0), axis=1))]) for sg in segs]
    RD.append((segs, lens, sum(L[-1] for L in lens)))


def draw_routes(img, t, M, xf):
    l, tp, sx, sy = xf

    def dst(arr):
        X, Y = (arr[:, 0] - l) * sx, (arr[:, 1] - tp) * sy
        return np.stack([M[0, 0] * X + M[0, 1] * Y + M[0, 2], M[1, 0] * X + M[1, 1] * Y + M[1, 2]], 1)
    glow = np.zeros((H // 2, W // 2, 3), np.uint8)
    heads, labels = [], []
    for r, (segs, lens, total) in zip(TL['routes'], RD):
        t0, t1, _, label, off, anchor = r
        if t < t0:
            continue
        rem = smooth((t - t0) / (t1 - t0)) * total
        head = None
        for sg, L in zip(segs, lens):
            if rem <= 0:
                break
            k = int(np.searchsorted(L, rem))
            d = dst(sg[:min(len(sg), k + 1)])
            rem -= L[-1]
            if len(d) >= 2:
                cv2.polylines(glow, [(d / 2).astype(np.int32)], False, (40, 120, 235), 6, cv2.LINE_AA)
                cv2.polylines(img, [(d * 4).astype(np.int32)], False, (26, 34, 128), 4, cv2.LINE_AA, 2)
            head = d[-1]
        if head is not None and t < t1:
            heads.append(head)
        s0 = dst(segs[0][:1])[0]
        cv2.circle(img, (int(s0[0]), int(s0[1])), 7, (26, 34, 128), -1, cv2.LINE_AA)
        if anchor == 'start':
            ph = ((t - t0) * 0.7) % 1.0
            cv2.circle(glow, (int(s0[0] / 2), int(s0[1] / 2)), int(6 + 30 * ph), (60, 150, 255), 2, cv2.LINE_AA)
        ap = s0 if anchor == 'start' else dst(segs[-1][-1:])[0]
        if anchor == 'end':
            cv2.circle(img, (int(ap[0]), int(ap[1])), 6, (26, 34, 128), -1, cv2.LINE_AA)
        la = smooth((t - (t0 if anchor == 'start' else t1)) / 0.6)
        if la > 0:
            labels.append((label, ap[0] + off[0], ap[1] + off[1], la))
    for hd in heads:
        cv2.circle(glow, (int(hd[0] / 2), int(hd[1] / 2)), 9, (120, 210, 255), -1, cv2.LINE_AA)
    glow = cv2.GaussianBlur(glow, (0, 0), 4)
    img = cv2.add(img, cv2.resize(glow, (W, H), interpolation=cv2.INTER_LINEAR))
    for hd in heads:
        cv2.circle(img, (int(hd[0]), int(hd[1])), 5, (200, 240, 255), -1, cv2.LINE_AA)
    for label, x, y, la in labels:
        blit_center(img, map_label_layer(label), x, y, la)
    return img


# ------------------------------------------------------------------ shots and transitions
def compose(M2, M1):
    """Affine M2 applied after M1."""
    A = M2[:, :2] @ M1[:, :2]
    b = M2[:, :2] @ M1[:, 2] + M2[:, 2]
    return np.hstack([A, b[:, None]])


def shot_frame(s, t):
    src, xf = get_src(s)
    fx = s['fx']
    u = (t - s['start']) / (s['end'] - s['start'])
    sh = shake_offset(fx['shake'], t, s['end']) if 'shake' in fx else (0.0, 0.0)
    M, z = cam_matrix(s['cam'], u, s['ease'], sh)
    out = warp(src, M)
    if 'painted' in fx:
        p = fx['painted']
        k = smooth((t - p['t0']) / (p['t1'] - p['t0']))
        if k < 1:
            out = cv2.addWeighted(warp(painted_version(s), M), 1 - k, out, k, 0)
    if 'zoomblur' in fx and t > fx['zoomblur']['t0']:
        t0 = fx['zoomblur']['t0']
        k = smooth((t - t0) / (s['end'] - t0))
        acc = out.astype(np.float32)
        for i in range(1, 5):
            sc = 1 + 0.05 * i * k
            S = np.array([[sc, 0, (1 - sc) * W / 2], [0, sc, (1 - sc) * H / 2]])
            acc += warp(src, compose(S, M))
        out = np.clip(acc / 5, 0, 255).astype(np.uint8)
    if 'lights_on' in fx:
        p = fx['lights_on']
        uu = (t - p['t0']) / (p['t1'] - p['t0'])
        k = smooth(uu)
        if 0 < uu < 0.7:
            k *= 0.55 + 0.45 * (math.sin(41 * t) > -0.2)
        m = warp(lights_mask(s), M)
        if k < 1:
            m3 = (warp(lights_wide(s), M).astype(np.float32) / 255)[..., None]
            factor = (0.55 + 0.45 * k) * (1 - m3) + (0.2 + 0.8 * k) * m3
            out = np.clip(out.astype(np.float32) * factor, 0, 255).astype(np.uint8)
        if k > 0:
            q = cv2.resize(cv2.multiply(out, cv2.merge([m, m, m]), scale=1 / 255), (W // 4, H // 4),
                           interpolation=cv2.INTER_AREA)
            q = cv2.GaussianBlur(q, (0, 0), 7).astype(np.float32)
            mq = cv2.resize(m, (W // 4, H // 4), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
            mq = cv2.GaussianBlur(mq, (0, 0), 16)[..., None]
            q = q * np.array([0.42, 0.78, 1.08], np.float32) + mq * np.array([22, 92, 210], np.float32)
            q = cv2.resize(np.clip(q, 0, 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_LINEAR)
            out = cv2.addWeighted(out, 1.0, q, 0.7 * k, 0)
    if 'flicker' in fx:
        out = cv2.convertScaleAbs(out, alpha=flicker_gain(t, fx['flicker']['amp']))
    if 'dim' in fx:
        out = cv2.convertScaleAbs(out, alpha=fx['dim'])
    if 'stars3d' in fx:
        out = stars3d(out, t, fx['stars3d']['k1'], fx['stars3d']['k2'], s['start'])
    if 'embers' in fx:
        out = embers(out, t, M, z, fx['embers'], s)
    if 'routes' in fx:
        out = draw_routes(out, t, M, xf)
    return out


_gy, _gx = np.mgrid[0:360, 0:640].astype(np.float32)
_gx /= 640.0
_gy /= 360.0


def up(a):
    return cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]


def transition(A, B, s, t):
    kind, dur = s['trans'], s['tdur']
    if kind in ('cut', 'none') or dur <= 0:
        return B
    u = clip01((t - s['start']) / dur)
    if u >= 1:
        return B
    if kind == 'fade':
        e = ease(u, 'io')
        return cv2.addWeighted(A, 1 - e, B, e, 0)
    Af, Bf = A.astype(np.float32), B.astype(np.float32)
    if kind == 'inkmap':
        a = ease(u, 'io')
        out = Af * (1 - a) + Bf * ((1 - a) * Af / 255 + a) * a
    elif kind == 'radial':
        cx, cy = s['fx'].get('radial', {}).get('c', [0.5, 0.5])
        r = np.sqrt(((_gx - cx) * 16 / 9) ** 2 + (_gy - cy) ** 2)
        r = r / r.max() + 0.22 * (NOISE_R - 0.5)
        edge = u * 1.35 - 0.12
        m = np.clip((edge - r) / 0.07, 0, 1)
        g = np.exp(-((r - edge) / 0.03) ** 2) * math.sin(math.pi * u) * 0.8
        m, g = up(m), up(g)
        out = Af * (1 - m) + Bf * m + g * np.array([110, 200, 255], np.float32)
    elif kind == 'burn':
        p = u * 1.16 - 0.08
        n = NOISE_B
        m = np.clip((p - n) / 0.025, 0, 1)
        e = np.exp(-((n - p) / 0.02) ** 2)
        ch = np.clip(1 - (n - p) / 0.07, 0, 1) * (n > p)
        m, e, ch = up(m), up(e), up(ch)
        out = Af * (1 - m) * (1 - 0.75 * ch) + Bf * m + e * np.array([40, 150, 255], np.float32) * 1.1
    else:
        e = ease(u, 'io')
        return cv2.addWeighted(A, 1 - e, B, e, 0)
    return np.clip(out, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ global post
def window(t, s, e, fi, fo):
    if t < s or t > e:
        return 0.0
    return min(smooth((t - s) / fi), smooth((e - t) / fo))


def interp(table, t):
    for (t0, a0), (t1, a1) in zip(table, table[1:]):
        if t0 <= t <= t1:
            return a0 + (a1 - a0) * (t - t0) / max(1e-6, t1 - t0)
    return table[-1][1]


LX, LBOT = 116, H - 236


def draw_lower(frame, L, a):
    blit(frame, L, LX, LBOT - L.shape[0], a)


def draw_ticker(frame, t):
    tk = TL['ticker']
    for wa, wb in tk['windows']:
        if wa <= t <= wb:
            break
    else:
        return
    a = window(t, wa, wb, 0.8, 0.8)
    keys = [k for k in tk['keys'] if wa - 0.01 <= k[0] <= wb]
    idx = max([i for i, k in enumerate(keys) if k[0] <= t], default=None)
    if idx is None:
        return
    cur, prev = keys[idx], (keys[idx - 1] if idx else None)
    dt = t - cur[0]
    v = prev[1] + (cur[1] - prev[1]) * (1 - (1 - dt / 1.4) ** 3) if prev and dt < 1.4 else cur[1]
    ys = year_str(v)
    if prev and dt < 0.5:
        pa = smooth(dt / 0.5)
        draw_lower(frame, lower_layer(ys, prev[2]), a * (1 - pa))
        draw_lower(frame, lower_layer(ys, cur[2]), a * pa)
    else:
        draw_lower(frame, lower_layer(ys, cur[2]), a)


def post(frame, t, fidx):
    g, beta = 1.0, 0.0
    if t < 2.0:
        g *= smooth(t / 2.0)
    if t > DUR - 3.0:
        g *= 1 - smooth((t - (DUR - 3.0)) / 3.0)
    ach = max([window(t, c[0], c[1], 0.8, 0.8) for c in TL['chapters']] + [0])
    ati = window(t, TL['title_card'][0], TL['title_card'][1], 0.5, 0.9)
    aen = window(t, TL['endcard'][0], TL['endcard'][1], 1.2, 1.5)
    g *= (1 - 0.14 * ach) * (1 - 0.18 * ati)
    alow = max([window(t, s, e, 0.6, 0.6) for s, e, _, _ in TL['labels']] +
               [window(t, wa, wb, 0.8, 0.8) for wa, wb in TL['ticker']['windows']] + [0])
    acap = max([window(t, s, e, 1.0, 1.0) for s, e, *_ in TL['captions']] + [0])
    asub = max([window(t, s, e, 0.35, 0.35) for s, e, *_ in TL['subtitles']] + [0])
    sc, sl, st = max(0.62 * ach, 0.62 * ati, 0.3 * aen), 0.5 * alow, 0.35 * acap
    sb = 0.3 * asub
    for tf, amp, tau in TL['flashes']:
        d = t - tf
        if -0.12 <= d < 6 * tau:
            k = smooth((d + 0.12) / 0.12) if d < 0 else math.exp(-d / tau)
            beta += amp * k * 230
            g *= 1 + 0.3 * amp * k
    if g != 1.0 or beta:
        frame = cv2.convertScaleAbs(frame, alpha=g, beta=beta)
    frame = cv2.multiply(frame, mulmap(interp(TL['parchment'], t), sc, sl, st, sb), scale=1 / 255)
    # ---- typography
    for s, e, text, _, *en in TL['subtitles']:
        a = window(t, s, e, 0.35, 0.35)
        if a:
            Ls = subtitle_layer(text, en[0] if en else '')
            blit(frame, Ls, W / 2 - Ls.shape[1] / 2, H - 150 - SUB_ZH_H / 2, a)
    for s, e, num, name, eng in TL['chapters']:
        a = window(t, s, e, 0.8, 0.8)
        if a:
            blit_center(frame, chapter_layer(num, name, eng), W / 2, H / 2 - 20 + 16 * (1 - smooth((t - s) / 1.6)), a)
    ts, te = TL['title_card']
    a = window(t, ts, te, 0.5, 0.9)
    if a:
        blit_center(frame, title_layer(), W / 2, H / 2 - 30 + 10 * (1 - smooth((t - ts) / 2.0)), a)
    for s, e, l1, l2 in TL['labels']:
        a = window(t, s, e, 0.6, 0.6)
        if a:
            draw_lower(frame, lower_layer(l1, l2), a)
    draw_ticker(frame, t)
    for s, e, text, *en in TL['captions']:
        a = window(t, s, e, 1.0, 1.0)
        if a:
            Lc = caption_layer(text, en[0] if en else '')
            blit(frame, Lc, W / 2 - Lc.shape[1] / 2, H * 0.27 - CAP_ZH_H / 2, a)
    es, ee = TL['endcard']
    a = window(t, es, ee, 1.2, 1.5)
    if a:
        blit_center(frame, endcard_layer(), W / 2, H / 2, a)
    return cv2.addWeighted(frame, 1.0, GRAIN[fidx % len(GRAIN)], 1.0, -128)


def render_frame(fidx):
    t = fidx / FPS
    frame = None
    for s in SHOTS:
        if s['start'] <= t < s['end']:
            img = shot_frame(s, t)
            frame = img if frame is None else transition(frame, img, s, t)
    if frame is None:
        frame = np.zeros((H, W, 3), np.uint8)
    return post(frame, t, fidx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stills')
    ap.add_argument('--sheet', action='store_true')
    ap.add_argument('--video')
    ap.add_argument('--start', type=float, default=0.0)
    ap.add_argument('--end', type=float, default=DUR)
    ap.add_argument('--preset', default='medium')
    ap.add_argument('--crf', type=float, default=20)
    ap.add_argument('--out-dir', default=os.path.join(HERE, 'frames'))
    a = ap.parse_args()
    if a.stills:
        os.makedirs(a.out_dir, exist_ok=True)
        times = [float(x) for x in a.stills.split(',')]
        tiles = []
        for tt in times:
            t0 = time.time()
            f = render_frame(int(round(tt * FPS)))
            small = cv2.resize(f, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
            p = os.path.join(a.out_dir, f's_{tt:06.1f}.jpg')
            cv2.imwrite(p, small, [cv2.IMWRITE_JPEG_QUALITY, 88])
            tiles.append((tt, small))
            print(f'{tt:7.2f}s -> {p}  ({time.time() - t0:.2f}s)', flush=True)
        if a.sheet:
            for i in range(0, len(tiles), 4):
                grp = tiles[i:i + 4]
                sheet = np.zeros((1080, 1920, 3), np.uint8)
                for j, (tt, im) in enumerate(grp):
                    tile = cv2.resize(im, (960, 540), interpolation=cv2.INTER_AREA)
                    cv2.putText(tile, f'{tt:.1f}s', (14, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 2)
                    sheet[(j // 2) * 540:(j // 2 + 1) * 540, (j % 2) * 960:(j % 2 + 1) * 960] = tile
                p = os.path.join(a.out_dir, f'sheet_{i // 4:02d}.jpg')
                cv2.imwrite(p, sheet, [cv2.IMWRITE_JPEG_QUALITY, 90])
                print('sheet', p)
        return
    if a.video:
        f0, f1 = int(round(a.start * FPS)), int(round(a.end * FPS))
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
               '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', a.preset, '-crf', str(a.crf),
               '-maxrate', '9M', '-bufsize', '18M', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
               '-tag:v', 'avc1', '-movflags', '+faststart', a.video]
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for fi in range(f0, f1):
            pr.stdin.write(render_frame(fi).tobytes())
            n = fi - f0 + 1
            if n % 48 == 0 or fi == f1 - 1:
                el = time.time() - t0
                print(f'frame {fi} ({fi / FPS:6.1f}s)  {n / el:5.2f} fps  eta {(f1 - f0 - n) / (n / el) / 60:5.1f} min',
                      flush=True)
        pr.stdin.close()
        pr.wait()
        print('done', a.video, 'rc', pr.returncode, flush=True)


SUB_ZH_H = subtitle_layer('字').shape[0]
CAP_ZH_H = caption_layer('字').shape[0]


if __name__ == '__main__':
    main()

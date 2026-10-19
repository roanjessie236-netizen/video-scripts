#!/usr/bin/env python3
"""Rebuild clean source plates (SW x SH, graded) from the rendered v2 film when the original stills are lost.

For every frame in a shot's clean interval (no dissolve, no flash, no zoom-blur/lights-on ramp):
  undo grain (exact, deterministic) -> undo vignette/scrims/card dimming (exact mulmap) ->
  mask every text layer box -> inverse camera warp into source space.
Per source pixel take the median of the valid samples (removes text, particles, moving stars, codec noise).
Holes no frame ever saw clean are inpainted; finally the largest centred 16:9 region that the camera
actually covered is resized back to SW x SH.
Usage: python3 extract_plates.py VIDEO ENGINE_DIR OUT_DIR [shot_id ...]
"""
import sys, os, json, math, subprocess
import numpy as np, cv2

VIDEO, ENG, OUT = sys.argv[1:4]
ONLY = set(sys.argv[4:])
sys.path.insert(0, ENG); os.chdir(ENG)
import render_core as rc
TL = rc.TL; W, H, FPS, DUR = rc.W, rc.H, rc.FPS, rc.DUR; SW, SH = rc.SW, rc.SH
os.makedirs(OUT, exist_ok=True)
SUB_H = rc.subtitle_layer('字').shape[0]
CAP_H = rc.caption_layer('字').shape[0]
win = lambda t, s, e, fi, fo: 0.0 if (t < s or t > e) else min(rc.smooth((t - s) / fi), rc.smooth((e - t) / fo))
MARG = 34


def boxes(t):
    B = []
    for s, e, text, *_ in TL['subtitles']:
        if s - 0.05 <= t <= e + 0.05:
            L = rc.subtitle_layer(text); w, h = L.shape[1], L.shape[0]
            x0, y0 = W / 2 - w / 2, H - 150 - SUB_H / 2
            B.append((x0 - MARG, y0 - MARG, x0 + w + MARG, y0 + h + MARG))
    for s, e, num, name, eng in TL['chapters']:
        if s - 0.05 <= t <= e + 0.05:
            L = rc.chapter_layer(num, name, eng); w, h = L.shape[1], L.shape[0]
            B.append((W / 2 - w / 2 - 60, H / 2 - 20 - h / 2 - 60, W / 2 + w / 2 + 60, H / 2 - 20 + h / 2 + 76))
    ts, te = TL['title_card']
    if ts - 0.05 <= t <= te + 0.05:
        L = rc.title_layer(); w, h = L.shape[1], L.shape[0]
        B.append((W / 2 - w / 2 - 70, H / 2 - 30 - h / 2 - 70, W / 2 + w / 2 + 70, H / 2 - 30 + h / 2 + 80))
    for s, e, l1, l2 in TL['labels']:
        if s - 0.05 <= t <= e + 0.05:
            L = rc.lower_layer(l1, l2); w, h = L.shape[1], L.shape[0]
            B.append((116 - MARG, H - 236 - h - MARG, 116 + w + MARG, H - 236 + MARG))
    for s, e, text, *_ in TL['captions']:
        if s - 0.05 <= t <= e + 0.05:
            L = rc.caption_layer(text); w, h = L.shape[1], L.shape[0]
            B.append((W / 2 - w / 2 - 70, H * 0.27 - CAP_H / 2 - 70, W / 2 + w / 2 + 70, H * 0.27 - CAP_H / 2 + h + 70))
    es, ee = TL['endcard']
    if es - 0.05 <= t <= ee + 0.05:
        L = rc.endcard_layer(); w, h = L.shape[1], L.shape[0]
        B.append((W / 2 - w / 2 - 70, H / 2 - h / 2 - 70, W / 2 + w / 2 + 70, H / 2 + h / 2 + 70))
    return B


def post_params(t):
    g = 1.0
    if t < 2.0 or t > DUR - 3.0:
        return None
    for tf, amp, tau in TL['flashes']:
        if -0.15 <= t - tf < 7 * tau:
            return None
    ach = max([win(t, c[0], c[1], 0.8, 0.8) for c in TL['chapters']] + [0])
    ati = win(t, TL['title_card'][0], TL['title_card'][1], 0.5, 0.9)
    aen = win(t, TL['endcard'][0], TL['endcard'][1], 1.2, 1.5)
    g *= (1 - 0.14 * ach) * (1 - 0.18 * ati)
    alow = max([win(t, s, e, 0.6, 0.6) for s, e, _, _ in TL['labels']] + [0])
    acap = max([win(t, s, e, 1.0, 1.0) for s, e, *_ in TL['captions']] + [0])
    asub = max([win(t, s, e, 0.35, 0.35) for s, e, *_ in TL['subtitles']] + [0])
    m = rc.mulmap(0.0, max(0.62 * ach, 0.62 * ati, 0.3 * aen), 0.5 * alow, 0.35 * acap, 0.3 * asub)
    return g, m


def read_frames(t0, t1, n):
    """decode frames whose index is in [t0*FPS, t1*FPS) and keep ~n evenly spaced ones"""
    f0, f1 = int(math.ceil(t0 * FPS)), int(math.floor(t1 * FPS))
    idx = sorted(set(np.linspace(f0, f1 - 1, n).round().astype(int).tolist())) if f1 - f0 > n else list(range(f0, f1))
    cmd = ['ffmpeg', '-v', 'error', '-ss', '%.4f' % (f0 / FPS - 0.5), '-i', VIDEO, '-ss', '0.5', '-frames:v', str(f1 - f0),
           '-f', 'rawvideo', '-pix_fmt', 'bgr24', 'pipe:']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out = []
    for k in range(f1 - f0):
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        if f0 + k in idx:
            out.append((f0 + k, np.frombuffer(buf, np.uint8).reshape(H, W, 3)))
    p.stdout.close(); p.wait()
    return out


def clean_interval(k):
    s = TL['shots'][k]
    a, b = s['start'], s['end']
    if k > 0: a = max(a, TL['shots'][k - 1]['end'])
    if k + 1 < len(TL['shots']): b = min(b, TL['shots'][k + 1]['start'])
    fx = s['fx']
    if 'zoomblur' in fx: b = min(b, fx['zoomblur']['t0'])
    if 'lights_on' in fx: a = max(a, fx['lights_on']['t1'] + 0.05)
    if 'datastream' in fx: a = max(a, s['start'] + 1.5)
    return a + 0.02, b - 0.02


def extract(k, nmax=26):
    s = TL['shots'][k]
    a, b = clean_interval(k)
    frames = read_frames(a, b, nmax)
    stack, valid = [], []
    border = np.ones((H, W), np.float32); border[:3] = border[-3:] = 0; border[:, :3] = border[:, -3:] = 0
    used = 0
    for fi, F in frames:
        t = fi / FPS
        pp = post_params(t)
        if pp is None:
            continue
        g, m = pp
        x = F.astype(np.float32) - (rc.GRAIN[fi % len(rc.GRAIN)].astype(np.float32) - 128)
        x = x / np.maximum(m.astype(np.float32) / 255, 1e-3) / g
        if 'dim' in s['fx']:
            x /= s['fx']['dim']
        mk = border.copy()
        for x0, y0, x1, y1 in boxes(t):
            mk[max(0, int(y0)):min(H, int(math.ceil(y1))), max(0, int(x0)):min(W, int(math.ceil(x1)))] = 0
        u = (t - s['start']) / (s['end'] - s['start'])
        sh = rc.shake_offset(s['fx']['shake'], t, s['end']) if 'shake' in s['fx'] else (0.0, 0.0)
        M, z = rc.cam_matrix(s['cam'], u, s['ease'], sh)
        Mi = cv2.invertAffineTransform(M)
        src = cv2.warpAffine(np.clip(x, 0, 255).astype(np.uint8), Mi, (SW, SH), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_CONSTANT)
        v = cv2.warpAffine(mk, Mi, (SW, SH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT) > 0.999
        stack.append(src); valid.append(v); used += 1
    if not stack:
        print(s['id'], 'NO FRAMES'); return
    S = np.stack(stack); V = np.stack(valid)
    plate = np.zeros((SH, SW, 3), np.uint8); cnt = V.sum(0)
    for r0 in range(0, SH, 184):
        r1 = min(SH, r0 + 184)
        blk = S[:, r0:r1].astype(np.float32)
        blk[~V[:, r0:r1]] = np.nan
        with np.errstate(all='ignore'):
            med = np.nanmedian(blk, axis=0)
        plate[r0:r1] = np.nan_to_num(med, nan=0).clip(0, 255).astype(np.uint8)
    # coverage = pixels the camera ever showed (text or not); holes = covered but never clean
    cov = np.zeros((SH, SW), bool)
    for fi, F in frames[::max(1, len(frames) // 8)] + frames[-1:]:
        t = fi / FPS; u = (t - s['start']) / (s['end'] - s['start'])
        sh = rc.shake_offset(s['fx']['shake'], t, s['end']) if 'shake' in s['fx'] else (0.0, 0.0)
        M, z = rc.cam_matrix(s['cam'], u, s['ease'], sh)
        cov |= cv2.warpAffine(border, cv2.invertAffineTransform(M), (SW, SH), borderMode=cv2.BORDER_CONSTANT) > 0.999
    hole = cov & (cnt == 0)
    nh = int(hole.sum())
    if nh:
        plate = cv2.inpaint(plate, hole.astype(np.uint8) * 255, 7, cv2.INPAINT_TELEA)
    # largest centred-ish 16:9 rectangle inside the coverage
    ys, xs = np.where(cov)
    cy, cx = ys.mean(), xs.mean()
    best = None
    for sc in np.linspace(1.0, 0.5, 101):
        w, h = SW * sc, SH * sc
        for dx in np.linspace(-0.15, 0.15, 13) * SW:
            for dy in np.linspace(-0.15, 0.15, 13) * SH:
                x0 = int(round(min(max(cx + dx - w / 2, 0), SW - w))); y0 = int(round(min(max(cy + dy - h / 2, 0), SH - h)))
                x1, y1 = int(x0 + w), int(y0 + h)
                if cov[y0, x0] and cov[y0, x1 - 1] and cov[y1 - 1, x0] and cov[y1 - 1, x1 - 1] and cov[y0:y1, x0:x1].all():
                    best = (x0, y0, x1, y1); break
            if best: break
        if best: break
    x0, y0, x1, y1 = best
    crop = plate[y0:y1, x0:x1]
    final = cv2.resize(crop, (SW, SH), interpolation=cv2.INTER_LANCZOS4) if crop.shape[1] != SW else crop
    name = os.path.splitext(s['image'])[0]
    cv2.imwrite(os.path.join(OUT, name + '.jpg'), final, [cv2.IMWRITE_JPEG_QUALITY, 96])
    hm = (hole[y0:y1, x0:x1].astype(np.uint8) * 255)
    cv2.imwrite(os.path.join(OUT, name + '_holes.png'), cv2.resize(hm, (SW // 4, SH // 4), interpolation=cv2.INTER_AREA))
    info = dict(id=s['id'], image=s['image'], frames=used, interval=[round(a, 2), round(b, 2)], holes_px=nh,
                holes_in_crop=int(hole[y0:y1, x0:x1].sum()), crop=[x0, y0, x1, y1], upscale=round(SW / (x1 - x0), 3))
    print(json.dumps(info), flush=True)
    return info


if __name__ == '__main__':
    res = []
    for k, s in enumerate(TL['shots']):
        if ONLY and s['id'] not in ONLY:
            continue
        if s['id'] == 'end':
            continue
        r = extract(k)
        if r: res.append(r)
    with open(os.path.join(OUT, 'plates_%s.json' % ('all' if not ONLY else '_'.join(sorted(ONLY))[:40])), 'w') as f:
        json.dump(res, f, indent=1)

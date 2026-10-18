"""今日简史 v2 — burn English subtitles under the existing (already burned) Chinese subtitles.
Typography is copied verbatim from projects/sapiens-70000-years/render_core.py (Sapiens v2 bilingual subtitles):
  subtitle EN = Noto Serif CJK SC Regular 36, (226,218,202), shadow (6,0.9,2), stacked 50 px into the zh line box,
  zh box top at H-150-SUB_ZH_H/2, fade 0.35/0.35 s;  caption EN = Light 42, (214,222,236), shadow (8,0.8,2), fade 1.0/1.0 s.
The zh layer is rendered only to get the identical stack geometry and is left transparent (zh is already in the picture).
Usage: python3 en_overlay.py SRC.mp4 subs.json OUT.mp4 [--crf 18 --preset medium] | --stills 33.5,82.5,214,218 OUTDIR
"""
import argparse, json, math, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 2560, 1440, 24
FONT_DIR = '/usr/share/fonts/google-noto-cjk'
_fc = {}
WARMW = (247, 239, 224)
EN_SUB = (226, 218, 202)


def clip01(x):
    return min(1.0, max(0.0, x))


def smooth(x):
    x = clip01(x)
    return x * x * (3 - 2 * x)


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


def text_layer(text, fnt, color=(255, 255, 255), tracking=0, grad=None, glow=None, shadow=None, whole=False):
    pad = int(fnt.size * 0.6)
    if glow:
        pad = max(pad, int(glow[1] * 3))
    if shadow:
        pad = max(pad, int(shadow[0] * 3 + shadow[2]))
    widths = [fnt.getlength(c) for c in text]
    tw = sum(widths) + tracking * max(0, len(text) - 1)
    if whole:  # draw the run in one call so Latin text keeps its kerning
        tw = fnt.getlength(text)
    asc, desc = fnt.getmetrics()
    w, h = int(math.ceil(tw)) + 2 * pad, asc + desc + 2 * pad
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    x = pad
    if whole:
        d.text((x, pad), text, font=fnt, fill=255)
    else:
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


def window(t, s, e, fi, fo):
    if t < s or t > e:
        return 0.0
    return min(smooth((t - s) / fi), smooth((e - t) / fo))


def zh_sub(text):
    return text_layer(text, font('Medium', 56), WARMW, tracking=3, shadow=(7, 0.9, 3))


def zh_cap(text):
    return text_layer(text, font('Light', 92), (238, 242, 250), tracking=30, glow=((150, 190, 255), 22, 0.32), shadow=(12, 0.5, 5))


def en_sub_layer(zh, en):  # = Sapiens v2 subtitle_layer(zh, en) with the zh part transparent
    z = zh_sub(zh); e = text_layer(en, font('Regular', 36), EN_SUB, shadow=(6, 0.9, 2), whole=True)
    return stack([np.zeros_like(z), e], [-50])


def en_cap_layer(zh, en):  # = Sapiens v2 caption_layer(zh, en) with the zh part transparent
    z = zh_cap(zh); e = text_layer(en, font('Light', 42), (214, 222, 236), shadow=(8, 0.8, 2), whole=True)
    return stack([np.zeros_like(z), e], [-int(z.shape[0] * 0.22) - int(e.shape[0] * 0.25)])


def build(subs):
    SUB_ZH_H = zh_sub('字').shape[0]; CAP_ZH_H = zh_cap('字').shape[0]; items = []
    for k, s in sorted(subs.items(), key=lambda kv: int(kv[0])):
        cap = int(k) >= 42
        L = en_cap_layer(s['zh'], s['en']) if cap else en_sub_layer(s['zh'], s['en'])
        y = H * 0.27 - CAP_ZH_H / 2 if cap else H - 150 - SUB_ZH_H / 2
        items.append((s['s'], s['e'], (1.0, 1.0) if cap else (0.35, 0.35), L, W / 2 - L.shape[1] / 2, y))
    return items


def draw(frame, t, items):
    for s, e, (fi, fo), L, x, y in items:
        a = window(t, s, e, fi, fo)
        if a: blit(frame, L, x, y, a)
    return frame


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('subs'); ap.add_argument('out')
    ap.add_argument('--crf', default='18'); ap.add_argument('--preset', default='medium'); ap.add_argument('--stills', default='')
    a = ap.parse_args(); items = build(json.load(open(a.subs, encoding='utf-8')))
    if a.stills:
        os.makedirs(a.out, exist_ok=True)
        for t in map(float, a.stills.split(',')):
            n = int(round(t * FPS)); raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', '%.4f' % (n / FPS), '-i', a.src,
                  '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'bgr24', 'pipe:'])
            f = np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy()
            cv2.imwrite(os.path.join(a.out, 'en_%.1f.png' % t), draw(f, n / FPS, items))
        return
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', a.src, '-f', 'rawvideo', '-pix_fmt', 'bgr24', 'pipe:'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H), '-r', str(FPS),
                            '-i', 'pipe:', '-i', a.src, '-map', '0:v', '-map', '1:a', '-c:a', 'copy',
                            '-c:v', 'libx264', '-preset', a.preset, '-crf', a.crf, '-maxrate', '14M', '-bufsize', '28M',
                            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
    n = 0; FB = W * H * 3
    while True:
        b = dec.stdout.read(FB)
        if len(b) < FB: break
        t = n / FPS
        if any(window(t, s, e, *f) for s, e, f, *_ in items):
            fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(); b = draw(fr, t, items).tobytes()
        enc.stdin.write(b); n += 1
        if n % 240 == 0: print('frame', n, flush=True)
    enc.stdin.close(); enc.wait(); dec.wait(); print('done frames', n)


if __name__ == '__main__':
    main()

"""Conservative alpha masks of the v1 overlays that we keep (labels, ticker, cards, routes) -> excluded from plates."""
import numpy as np, cv2
import core as C
from core import R, W, H, smooth, window
from render_core import lower_layer, chapter_layer, title_layer, endcard_layer, caption_layer, year_str

LX, LBOT = R.LX, R.LBOT
_tick_w = max(lower_layer(year_str(k[1]), k[2]).shape[1] for k in C.TL1['ticker']['keys'])
_tick_h = lower_layer(year_str(-9500), 'x').shape[0]


def rects(t, tl=C.TL1):
    out = []  # (x0, y0, x1, y1, alpha)
    for s, e, l1, l2 in tl['labels']:
        a = window(t, s, e, 0.6, 0.6)
        if a:
            L = lower_layer(l1, l2)
            out.append((LX, LBOT - L.shape[0], LX + L.shape[1], LBOT, a))
    for wa, wb in tl['ticker']['windows']:
        a = window(t, wa, wb, 0.8, 0.8)
        if a:
            out.append((LX, LBOT - _tick_h, LX + _tick_w, LBOT, a))
    for s, e, num, name, eng in tl['chapters']:
        a = window(t, s, e, 0.8, 0.8)
        if a:
            L = chapter_layer(num, name, eng)
            cy = H / 2 - 20 + 16 * (1 - smooth((t - s) / 1.6))
            out.append((W / 2 - L.shape[1] / 2, cy - L.shape[0] / 2 - 4, W / 2 + L.shape[1] / 2, cy + L.shape[0] / 2 + 4, a))
    ts, te = tl['title_card']
    a = window(t, ts, te, 0.5, 0.9)
    if a:
        L = title_layer()
        out.append((W / 2 - L.shape[1] / 2, H / 2 - 30 - L.shape[0] / 2, W / 2 + L.shape[1] / 2, H / 2 - 20 + L.shape[0] / 2, a))
    es, ee = tl['endcard']
    a = window(t, es, ee, 1.2, 1.5)
    if a:
        L = endcard_layer()
        out.append((W / 2 - L.shape[1] / 2, H / 2 - L.shape[0] / 2, W / 2 + L.shape[1] / 2, H / 2 + L.shape[0] / 2, a))
    for s, e, text, *_ in tl['captions']:
        a = window(t, s, e, 1.0, 1.0)
        if a:
            L = caption_layer(text)
            out.append((W / 2 - L.shape[1] / 2, H * 0.27 - L.shape[0] / 2, W / 2 + L.shape[1] / 2, H * 0.27 + L.shape[0] / 2, a))
    return out


def overlay_alpha(t, x0, y0, x1, y1, s=None, M=None):
    m = np.zeros((y1 - y0, x1 - x0), np.float32)
    for a0, b0, a1, b1, a in rects(t):
        a0, b0, a1, b1 = int(max(x0, a0)), int(max(y0, b0)), int(min(x1, a1)), int(min(y1, b1))
        if a1 > a0 and b1 > b0:
            m[b0 - y0:b1 - y0, a0 - x0:a1 - x0] = np.maximum(m[b0 - y0:b1 - y0, a0 - x0:a1 - x0], 1.0 if a > 0.02 else a * 50)
    if s is not None and 'routes' in s['fx']:
        _, xf = R.get_src(s)
        z = R.draw_routes(np.zeros((H, W, 3), np.uint8), t, M, xf)
        r = (z[y0:y1, x0:x1].max(2) > 2).astype(np.uint8)
        r = cv2.dilate(r, np.ones((7, 7), np.uint8)).astype(np.float32)
        m = np.maximum(m, r)
    return m

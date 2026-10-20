#!/usr/bin/env python3
"""Graphic plates for 《明天属于谁》(2944x1656, drawn 2x then downscaled): historical-materialism diagram (2 build
states) and the 'contradiction' chart. usage: diagrams.py OUT_DIR"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
S = 2; W, H = 2944 * S, 1656 * S
FD = '/usr/share/fonts/google-noto-cjk'
_fc = {}
def F(w, size):
    k = (w, size)
    if k not in _fc:
        p = f'{FD}/NotoSerifCJK-{w}.ttc'
        for i in range(8):
            f = ImageFont.truetype(p, size * S, index=i)
            if 'SC' in f.getname()[0]: break
        _fc[k] = f
    return _fc[k]
GOLD, GOLDT, WARM, DIM, EMBER = (228, 192, 122), (252, 230, 172), (240, 228, 206), (120, 104, 84), (236, 120, 64)
def background():
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    r = np.sqrt(((xx - W / 8) / (W / 4)) ** 2 + ((yy - H / 8) / (H / 4) * 0.8) ** 2)
    k = np.clip(1 - r * 1.25, 0, 1) ** 1.6
    c0, c1 = np.array([7, 6, 5], np.float32), np.array([36, 28, 20], np.float32)
    img = c0 + (c1 - c0) * k[..., None]
    img += np.random.default_rng(3).normal(0, 2.2, img.shape)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    d = ImageDraw.Draw(im)
    for x in range(0, W, 92 * S):   # faint engraved grid
        d.line([(x, 0), (x, H)], fill=(30, 25, 19), width=1)
    for y in range(0, H, 92 * S):
        d.line([(0, y), (W, y)], fill=(30, 25, 19), width=1)
    return im.convert('RGBA')
def text(d, xy, s, f, fill, anchor='mm', tracking=0):
    if not tracking:
        d.text(xy, s, font=f, fill=fill, anchor=anchor); return
    widths = [f.getlength(c) for c in s]; tw = sum(widths) + tracking * S * (len(s) - 1)
    x = xy[0] - (tw / 2 if anchor[0] == 'm' else 0 if anchor[0] == 'l' else tw)
    for c, w_ in zip(s, widths):
        d.text((x, xy[1]), c, font=f, fill=fill, anchor='l' + anchor[1]); x += w_ + tracking * S
def glow(im, layer, rad=18, amt=0.8):
    g = layer.filter(ImageFilter.GaussianBlur(rad * S))
    a = np.asarray(g).astype(np.float32); a[..., 3] *= amt
    im.alpha_composite(Image.fromarray(a.clip(0, 255).astype(np.uint8)))
    im.alpha_composite(layer)
def arrow(d, x0, y0, x1, y1, col, w=5, head=26):
    d.line([(x0, y0), (x1, y1)], fill=col, width=w * S)
    v = np.array([x1 - x0, y1 - y0], np.float32); v /= np.linalg.norm(v); n = np.array([-v[1], v[0]])
    p = np.array([x1, y1]); h = head * S
    d.polygon([tuple(p + v * h * 0.2), tuple(p - v * h + n * h * 0.55), tuple(p - v * h - n * h * 0.55)], fill=col)
TIERS = [('上层建筑', 'SUPERSTRUCTURE', '国家 · 法律 · 观念'), ('生产关系', 'RELATIONS OF PRODUCTION', '所有制 · 分工 · 分配'),
         ('生产力', 'PRODUCTIVE FORCES', '工具 · 技术 · 劳动者')]
def tiers(lit):
    im = background(); L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    cx, bw, bh, gap = W / 2, 1360 * S, 236 * S, 96 * S
    y0 = H / 2 - (3 * bh + 2 * gap) / 2 + 30 * S
    for k, (zh, en, sub) in enumerate(TIERS):
        on = lit[k]; a = 255 if on else 70
        top = y0 + k * (bh + gap); col = GOLD + (a,)
        d.rounded_rectangle([cx - bw / 2, top, cx + bw / 2, top + bh], radius=18 * S, outline=col, width=4 * S,
                            fill=(40, 30, 18, 150 if on else 60))
        text(d, (cx - bw / 2 + 120 * S, top + bh * 0.40), zh, F('Bold', 96), GOLDT + (a,), 'lm', tracking=14)
        text(d, (cx - bw / 2 + 122 * S, top + bh * 0.76), en, F('Medium', 30), WARM + (int(a * 0.8),), 'lm', tracking=6)
        text(d, (cx + bw / 2 - 110 * S, top + bh * 0.50), sub, F('Regular', 46), WARM + (int(a * 0.9),), 'rm', tracking=4)
        if k < 2 and lit[k] and lit[k + 1]:
            yb, yt = top + bh + gap - 14 * S, top + bh + 14 * S      # up arrow (determines) / down (reacts back)
            arrow(d, cx - 160 * S, yb, cx - 160 * S, yt, GOLDT + (255,), 6, 30)
            text(d, (cx - 200 * S, (yb + yt) / 2), '基础' if k == 0 else '决定', F('SemiBold', 40), GOLDT + (255,), 'rm')  # v3
            arrow(d, cx + 160 * S, yt + 6 * S, cx + 160 * S, yb - 6 * S, DIM + (255,), 3, 22)
            text(d, (cx + 200 * S, (yb + yt) / 2), '反作用', F('Regular', 36), (176, 160, 136, 255), 'lm')
    if all(lit):   # bracket: economic base = the SUM OF THE RELATIONS OF PRODUCTION only (Marx, Preface 1859)
        top = y0 + (bh + gap) - 6 * S; bot = top + bh + 12 * S; x = cx + bw / 2 + 50 * S; ym = (top + bot) / 2
        d.line([(x, top), (x + 30 * S, top), (x + 30 * S, bot), (x, bot)], fill=GOLD + (220,), width=3 * S)
        d.line([(x + 30 * S, ym), (x + 52 * S, ym)], fill=GOLD + (220,), width=3 * S)
        text(d, (x + 76 * S, ym - 52 * S), '经济基础', F('Bold', 50), GOLDT + (240,), 'lm')
        text(d, (x + 78 * S, ym + 8 * S), '＝ 生产关系的总和', F('Regular', 34), WARM + (230,), 'lm')
        text(d, (x + 78 * S, ym + 58 * S), 'ECONOMIC BASE', F('Medium', 22), WARM + (190,), 'lm', tracking=4)
        text(d, (W / 2, 168 * S), '「这些生产关系的总和构成社会的经济结构，即有法律的和政治的上层建筑竖立其上的现实基础。」',
             F('Regular', 36), WARM + (215,), 'mm')
        text(d, (W / 2, 232 * S), '马克思 ·《〈政治经济学批判〉序言》· 1859', F('Medium', 28), (190, 172, 140, 210), 'mm', tracking=3)
    glow(im, L, 14, 0.55)
    return im
def conflict(full=True):
    im = background(); L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    x0, x1 = 760 * S, 2480 * S
    text(d, (W / 2, 300 * S), '矛  盾', F('Bold', 84), GOLDT + (255,), 'mm', tracking=30)
    text(d, (W / 2, 392 * S), 'THE CONTRADICTION', F('Medium', 28), WARM + (210,), 'mm', tracking=12)
    y1, y2 = 760 * S, 1150 * S
    text(d, (x0 - 60 * S, y1), '生产力', F('Bold', 74), GOLDT + (255,), 'rm', tracking=8)
    text(d, (x0 - 60 * S, y1 + 74 * S), 'PRODUCTIVE FORCES', F('Medium', 22), WARM + (200,), 'rm', tracking=4)
    arrow(d, x0, y1, x1, y1, GOLDT + (255,), 10, 54)
    for fx, lab, yr in [(0.10, '蒸汽机', '1769'), (0.36, '电力', '1879'), (0.62, '计算机', '1946'), (0.90, '人工智能', '2020s')]:
        x = x0 + (x1 - x0) * fx
        d.ellipse([x - 16 * S, y1 - 16 * S, x + 16 * S, y1 + 16 * S], fill=GOLDT + (255,))
        text(d, (x, y1 - 92 * S), lab, F('SemiBold', 46), WARM + (255,), 'mm')
        text(d, (x, y1 - 44 * S), yr, F('Regular', 28), (200, 184, 156, 255), 'mm')
    if not full:
        glow(im, L, 14, 0.6)
        return im
    text(d, (x0 - 60 * S, y2), '生产关系', F('Bold', 74), GOLDT + (255,), 'rm', tracking=8)
    text(d, (x0 - 60 * S, y2 + 74 * S), 'RELATIONS OF PRODUCTION', F('Medium', 22), WARM + (200,), 'rm', tracking=4)
    xe = x0 + (x1 - x0) * 0.24
    d.rounded_rectangle([x0, y2 - 22 * S, xe, y2 + 22 * S], radius=10 * S, fill=DIM + (255,))
    text(d, ((x0 + xe) / 2, y2 + 80 * S), '所有制 · 分配方式', F('Regular', 40), (190, 174, 150, 255), 'mm')
    for k in range(9):    # dashed gap to the arrow tip
        xa = xe + 40 * S + k * ((x1 - xe - 60 * S) / 9)
        d.line([(xa, y2), (xa + 46 * S, y2)], fill=EMBER + (220,), width=4 * S)
    xm = (xe + x1) / 2
    d.line([(xe + 30 * S, y2 - 70 * S), (xe + 30 * S, y2 - 110 * S), (x1, y2 - 110 * S), (x1, y2 - 70 * S)],
           fill=EMBER + (200,), width=3 * S)
    text(d, (xm, y2 - 168 * S), '差距越拉越大', F('SemiBold', 48), EMBER + (255,), 'mm')
    glow(im, L, 14, 0.6)
    return im
def save(im, name):
    im.convert('RGB').resize((W // S, H // S), Image.LANCZOS).save(os.path.join(OUT, name), quality=95, subsampling=0)
save(tiers([False, False, True]), 'dg_hm_a.jpg')
save(tiers([True, True, True]), 'dg_hm_b.jpg')
save(conflict(False), 'dg_conflict_a.jpg')
save(conflict(), 'dg_conflict.jpg')
print('ok')

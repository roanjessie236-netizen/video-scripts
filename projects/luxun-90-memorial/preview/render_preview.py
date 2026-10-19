# 样片渲染：序章 + 第一章（S0-01—S1-07），1920x1080/25fps，无声，旁白与原文以字幕显示
import math, subprocess, sys, re, yaml, csv
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops
W, H, FPS = 1920, 1080, 25
ROOT = '/data/luxun90/'; SRC = ROOT + 'preview/src/'
def SERIF(s, w='Regular'): return ImageFont.truetype(f'/usr/share/fonts/google-noto-cjk/NotoSerifCJK-{w}.ttc', s, index=2)
def SANS(s, w='Medium'): return ImageFont.truetype(f'/usr/share/fonts/google-noto-cjk/NotoSansSC-{w}.otf', s)
BLACK = (0, 0, 0)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def lerp(a, b, t): return a + (b - a) * t

# ---------- 素材 ----------
def load(name, crop=None, tone='warm', oval=False):
    im = Image.open(SRC + name).convert('RGB')
    if crop:
        iw, ih = im.size; a, b, c, d = crop
        im = im.crop((int(a * iw), int(b * ih), int(c * iw), int(d * ih)))
    if tone:
        g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=0.5)
        im = ImageOps.colorize(g, black=(14, 12, 10), white=(236, 228, 212)) if tone == 'warm' else \
             ImageOps.colorize(g, black=(8, 12, 20), white=(190, 205, 222))
    if oval:
        m = Image.new('L', im.size, 0); iw, ih = im.size
        ImageDraw.Draw(m).ellipse((iw * .06, ih * .05, iw * .94, ih * .95), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(iw * .02))
        im = Image.composite(im, Image.new('RGB', im.size, BLACK), m)
    return im
def prescale(im, mode, zmax):
    iw, ih = im.size
    s0 = max(W / iw, H / ih) if mode == 'cover' else min(W / iw, H / ih)
    f = min(1.0, s0 * zmax * 1.15)
    if f < 0.98: im = im.resize((max(1, int(iw * f)), max(1, int(ih * f))), Image.LANCZOS)
    return im
def kb(im, z, cx, cy, mode='cover', dx=0, dy=0):
    iw, ih = im.size
    s = (max(W / iw, H / ih) if mode == 'cover' else min(W / iw, H / ih)) * z
    vw, vh = W / s, H / s
    cxp = min(max(cx * iw, vw / 2), iw - vw / 2) if vw <= iw else iw / 2
    cyp = min(max(cy * ih, vh / 2), ih - vh / 2) if vh <= ih else ih / 2
    x0, y0 = cxp - vw / 2 + dx / s, cyp - vh / 2 + dy / s
    return im.transform((W, H), Image.AFFINE, (1 / s, 0, x0, 0, 1 / s, y0), resample=Image.BILINEAR, fillcolor=BLACK)
def KB(name, z0, z1, c0, c1, mode='cover', crop=None, tone='warm', oval=False, img=None, shake=None):
    im = img if img is not None else load(name, crop, tone, oval)
    im = prescale(im, mode, max(z0, z1))
    def fn(t, d):
        u = ease(t / d) if d > 0 else 0
        dx = dy = 0
        if shake and shake[0] <= t <= shake[0] + 0.28:
            k = int((t - shake[0]) * FPS); dx, dy = [(14, -9), (-11, 7), (6, -4), (-3, 2), (1, 0), (0, 0), (0, 0), (0, 0)][min(k, 7)]
        return kb(im, lerp(z0, z1, u), lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u), mode, dx, dy)
    return fn

# ---------- 文字 ----------
def text_rgba(txt, font, fill, stroke=0, sfill=(0, 0, 0)):
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    im = Image.new('RGBA', (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, 2 - t), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return im
VMAP = {'，': '︐', '。': '︒', '、': '︑', '；': '︔', '：': '︓', '—': '︱', '！': '︕', '？': '︖', '“': '﹁', '”': '﹂'}
def vcol(txt, font, cell, fill, blank=()):
    """竖排一列：逐字居中放进方格"""
    fs = font.size; im = Image.new('RGBA', (int(fs * 1.4), int(cell * len(txt)) + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, ch in enumerate(txt):
        if i in blank: continue
        g = VMAP.get(ch, ch)
        l, t, r, b = d.textbbox((0, 0), g, font=font)
        x = (im.width - (r - l)) / 2 - l; y = i * cell + (cell - (b - t)) / 2 - t
        if ch in '，。、': x += fs * 0.25; y -= fs * 0.25
        d.text((x, y), g, font=font, fill=fill)
    return im
def paste_a(base, rgba, pos, a):
    if a <= 0.003: return
    m = rgba.getchannel('A')
    if a < 0.997: m = m.point(lambda v: int(v * a))
    base.paste(rgba.convert('RGB'), (int(pos[0]), int(pos[1])), m)

# ---------- 时间线 ----------
SB = yaml.safe_load(open(ROOT + 'storyboard.yaml', encoding='utf-8'))
Q = {r[0]: r[1] for r in csv.reader(open(ROOT + 'quotes_src.tsv', encoding='utf-8'), delimiter='\t')}
SH = {}; T = 0.0
for ch in SB['chapters'][:2]:
    for s in ch['shots']: SH[s['id']] = (T, s); T += s['dur']
TOTAL_MAIN = T; CRED = 7.0; TOTAL = T + CRED
def at(sid, t): return SH[sid][0] + t
clips, overlays, subs = [], [], []
def clip(sid, t0, t1, fn, fin=0.8, fout=0.0): clips.append((at(sid, t0), at(sid, t1), fn, fin, fout))
def ov(sid, t0, t1, fn, fin=0.6, fout=0.6): overlays.append((at(sid, t0), at(sid, t1), fn, fin, fout))
def solid(c=BLACK):
    im = Image.new('RGB', (W, H), c); return lambda t, d: im

# 字幕：按语速切块
VR, QR, GAP = SB['meta']['vo_rate'], SB['meta']['quote_rate'], SB['meta']['gap']
def chunks(txt, n=18):
    parts = re.findall(r'[^，。；：！？、—]+[，。；：！？、]*(?:——)?|——', txt)
    out, cur = [], ''
    for p in parts:
        if cur and len(cur) + len(p) > n: out.append(cur); cur = p
        else: cur += p
    if cur: out.append(cur)
    return [c.rstrip('，。；、').rstrip('—') or c for c in out]
SKIP = {('S0-02', 'Q71'), ('S0-02', 'Q01'), ('S1-06', 'Q06'), ('S1-06', 'vo')}
FV = SANS(42); FQ = SERIF(44, 'SemiBold')
for sid, (t0, s) in SH.items():
    t = 0.4
    for a in s.get('audio', []):
        if 'vo' in a: kind, txt, rate = 'vo', a['vo'], VR
        elif 'q' in a: kind, txt, rate = a['q'], Q[a['q']], QR
        else: continue
        n = len(re.sub(r'[，。；：！？、—“”（）\s]', '', txt)); dur = n / rate
        if (sid, kind) not in SKIP and (sid, 'vo' if kind == 'vo' else kind) not in SKIP:
            cs = chunks(txt); tot = sum(len(c) for c in cs); u = t
            for c in cs:
                dd = dur * len(c) / tot
                if (sid, kind) == ('S0-03', 'Q02') and u < 3.0: u += dd; continue
                img = text_rgba(c, FV if kind == 'vo' else FQ, (255, 255, 255) if kind == 'vo' else (238, 224, 192), 3)
                subs.append((t0 + u, t0 + u + dd - 0.08, img)); u += dd
        t += dur + GAP

# ---------- S0-01 钢笔与“死” ----------
clip('S0-01', 0, 3.6, KB('m01_pen.jpg', 1.0, 1.35, (0.56, 0.5), (0.5, 0.58), crop=(0, 0.125, 1, 0.875), tone=None), fin=1.2)
paper = load('m01_pen.jpg', crop=(0.02, 0.17, 0.42, 0.7), tone=None).filter(ImageFilter.GaussianBlur(1.2))
clip('S0-01', 3.2, 6.6, KB(None, 1.0, 1.06, (0.5, 0.5), (0.5, 0.5), img=paper), fin=0.5, fout=0.5)
si = text_rgba('死', SERIF(330, 'Bold'), (30, 22, 16, 255))
bleeds = [si.filter(ImageFilter.GaussianBlur(r)) for r in (2, 5, 9, 14, 20)]
def si_fn(t):
    im = Image.new('RGBA', (si.width + 120, si.height + 120), (0, 0, 0, 0))
    k = min(4, int(clamp((t - 0.8) / 2.2) * 5))
    if t > 0.8: im.alpha_composite(bleeds[k], (60, 60))
    im.alpha_composite(si, (60, 60)); return im
def si_ov(t):
    im = si_fn(t); a = clamp(t / 0.9)
    m = im.getchannel('A').point(lambda v: int(v * a)); im.putalpha(m)
    return im, (W / 2 - im.width / 2, H / 2 - im.height / 2 - 20)
ov('S0-01', 3.5, 6.6, si_ov, fin=0.01, fout=0.5)
dt = text_rgba('1936年9月5日', SERIF(34), (70, 58, 44, 255))
ov('S0-01', 4.4, 6.6, lambda t: (dt, (W - dt.width - 150, H - 150)), fin=0.8, fout=0.5)

# ---------- S0-02 / S0-03 《死》手稿与竖排原文 ----------
clip('S0-02', 0, 5.8, KB('qj2028-000.jpg', 1.0, 1.55, (0.5, 0.5), (0.62, 0.32), mode='fit'), fin=0.8)
ITEMS = [['一，不得因为丧事，收受任何人的', '一文钱。——但老朋友的，不在此例。'], ['二，赶快收敛，埋掉，拉倒。'], ['三，不要做任何关于纪念的事情。'],
         ['四，忘记我，管自己生活。', '——倘不，那就真是胡涂虫。'], ['五，孩子长大，倘无才能，可寻点', '小事情过活，万不可去做空头文学', '家或美术家。'],
         ['六，别人应许给你的事物，不可当真。'], ['七，损着别人的牙眼，却反对报复，', '主张宽容的人，万勿和他接近。']]
FS, CELL, CW, TOP = 40, 47, 74, 120
FT = SERIF(FS); BR, DM = (240, 232, 214, 255), (240, 232, 214, 255)
cols = []; x = 0
for i, it in enumerate(ITEMS):
    for j, c in enumerate(it): cols.append((i, j, c, x)); x += CW
    x += 22
x0 = W / 2 + (x - 22) / 2 - CW
layer = []
for i, j, c, xx in cols:
    blank = (2, 3, 4) if (i, j) == (3, 0) else ()
    full = vcol(c, FT, CELL, BR); br = vcol(c, FT, CELL, BR, blank); dm = full.filter(ImageFilter.GaussianBlur(1.6))
    layer.append((i, br, dm, (x0 - xx - (br.width - CW) / 2, TOP), full))
WJW = vcol('忘记我', SERIF(400), 470, BR)  # 放大用
pos_w = [L[3] for L in layer if L[0] == 3][0]
def item_alpha(i, T):  # 返回(亮,暗)透明度；T 为全局时间
    s2, s3 = SH['S0-02'][0], SH['S0-03'][0]
    q71, q01 = s2 + 5.5, s2 + 9.0
    if T < s3:
        base = clamp((T - (s2 + 5.0)) / 1.0)
        hl = (i == 1 and T >= q71) or (i == 2 and T >= q01)
        b = clamp((T - (q71 if i == 1 else q01)) / 0.5) if hl else 0
        return base * b, base * 0.30 * (1 - b)
    t = T - s3
    if i == 3: return clamp(t / 0.6) * (1 - clamp((t - 3.0) / 1.0)), 0.30 * (1 - clamp(t / 0.6))
    fade = 1 - clamp((t - 1.0) / 1.5)
    if i in (1, 2): return fade, 0
    return 0, 0.30 * fade
def card_fn(t, d):
    T = at('S0-02', 0) + 5.0 + t
    im = Image.new('RGB', (W, H), BLACK)
    s3 = SH['S0-03'][0]
    for i, br, dm, p, full in layer:
        a, b = item_alpha(i, T)
        paste_a(im, dm, p, b); paste_a(im, br if T >= s3 else full, p, a)
    # “忘记我”
    if T >= s3:
        t3 = T - s3; a = clamp(t3 / 0.6)
        u = ease((t3 - 3.6) / 3.9)
        sc = lerp(FS / 400, 1.02, u * u)
        w_, h_ = max(1, int(WJW.width * sc)), max(1, int(WJW.height * sc))
        im2 = WJW.resize((w_, h_), Image.LANCZOS)
        cx0 = pos_w[0] + WJW.width * (FS / 400) / 2; cy0 = TOP + CELL * 2 + CELL * 1.5
        cx, cy = lerp(cx0, W / 2, ease((t3 - 3.6) / 2.5)), lerp(cy0, H / 2, ease((t3 - 3.6) / 2.5))
        paste_a(im, im2, (cx - w_ / 2, cy - h_ / 2), a)
    return im
clip('S0-02', 5.0, 14 + 8, card_fn, fin=1.0, fout=0.7)

# ---------- S0-04 1936年10月留影 + 日历纸 ----------
clip('S0-04', 0, 15.3, KB('hz231.png', 1.0, 2.35, (0.5, 0.5), (0.5, 0.235), mode='fit', crop=(0.02, 0.07, 0.76, 0.87)), fin=1.0)
cal = Image.new('RGBA', (300, 420), (232, 224, 206, 255)); d = ImageDraw.Draw(cal)
d.rectangle((0, 0, 300, 92), fill=(146, 32, 26, 255))
d.text((150, 46), '十 月', font=SERIF(46, 'Bold'), fill=(245, 236, 220), anchor='mm')
d.text((150, 210), '十九', font=SERIF(150, 'Black'), fill=(24, 20, 16), anchor='mm')
d.text((150, 330), '星期一', font=SERIF(34), fill=(60, 50, 40), anchor='mm')
d.text((150, 380), '民国二十五年', font=SERIF(26), fill=(110, 95, 80), anchor='mm')
for k in range(0, 300, 12): d.ellipse((k + 3, 4, k + 9, 10), fill=(90, 20, 16, 255))
cal = cal.rotate(-5, expand=True, resample=Image.BICUBIC)
ov('S0-04', 6.5, 15.2, lambda t: (cal, (W - cal.width - 120 + int(30 * (1 - ease(t / 1.2))), 250)), fin=1.0, fout=0.6)

# ---------- S0-05 殡仪 → 葬礼 → “民族魂” ----------
clip('S0-05', 0, 6.0, KB('qj6081-000.jpg', 1.02, 1.22, (0.42, 0.5), (0.58, 0.45)), fin=0.8)
clip('S0-05', 5.4, 10.8, KB('hz233.png', 1.0, 1.35, (0.5, 0.5), (0.45, 0.42), mode='fit', crop=(0.12, 0.155, 0.88, 0.86)), fin=0.7)
mzh = text_rgba('民族魂', SERIF(230, 'Black'), (244, 238, 226, 255))
mzs = text_rgba('覆在灵柩上的白旗　沈钧儒书', SERIF(34), (160, 152, 140, 255))
def mz_card(t, d):
    im = Image.new('RGB', (W, H), BLACK)
    paste_a(im, mzh, (W / 2 - mzh.width / 2, H / 2 - mzh.height / 2 - 60), clamp(t / 1.0))
    paste_a(im, mzs, (W / 2 - mzs.width / 2, H / 2 + 120), clamp((t - 1.0) / 0.8)); return im
clip('S0-05', 10.2, 14.0, mz_card, fin=0.7, fout=0.6)

# ---------- S0-06 片名 ----------
title = load('m02_title.jpg', tone=None)
sub = text_rgba('鲁迅逝世九十周年　1936—2026', SERIF(44), (196, 188, 172, 255))
def title_fn(t, d):
    im = kb(title, 1.0 + 0.04 * t / d, 0.5, 0.48)
    paste_a(im, sub, (W / 2 - sub.width / 2, 800), clamp((t - 2.0) / 1.0)); return im
clip('S0-06', 0.2, 11.0, title_fn, fin=1.6, fout=1.0)

# ---------- S1-01 章节卡 + 绍兴城 ----------
c1 = text_rgba('一｜绍兴', SERIF(124, 'Bold'), (240, 232, 214, 255)); c2 = text_rgba('1881—1898　坠入困顿', SERIF(46), (176, 168, 152, 255))
def chap(t, d):
    im = Image.new('RGB', (W, H), BLACK)
    paste_a(im, c1, (W / 2 - c1.width / 2, 400), clamp(t / 0.7)); paste_a(im, c2, (W / 2 - c2.width / 2, 580), clamp((t - 0.5) / 0.7)); return im
clip('S1-01', 0, 3.4, chap, fin=0.6)
clip('S1-01', 2.6, 6.6, KB('hz4.png', 1.05, 1.18, (0.4, 0.55), (0.56, 0.5), crop=(0, 0.40, 1, 0.97)), fin=0.9)
# ---------- S1-02 老宅 → 翰林匾 → 祖父 ----------
clip('S1-02', 0, 5.2, KB('hz6.png', 1.0, 1.14, (0.5, 0.4), (0.5, 0.5), crop=(0, 0, 1, 0.755)), fin=0.6)
clip('S1-02', 4.6, 8.8, KB('hz7.png', 1.0, 1.0, (0.7, 0.5), (0.3, 0.5), crop=(0, 0, 1, 0.305)), fin=0.6)
clip('S1-02', 8.2, 13.4, KB('hz9.png', 1.0, 1.75, (0.5, 0.5), (0.5, 0.22), mode='fit', crop=(0.11, 0.14, 0.93, 0.73)), fin=0.6)
# ---------- S1-03 高墙铁锁 → 父亲 ----------
clip('S1-03', 0, 8.6, KB('m03_wall.jpg', 2.0, 1.55, (0.47, 0.22), (0.47, 0.62), tone=None, shake=(4.3,)), fin=0.6)
clip('S1-03', 7.8, 15.4, KB('hz10.png', 1.0, 1.15, (0.5, 0.5), (0.5, 0.45), mode='fit', crop=(0.715, 0.515, 0.915, 0.725), tone='cold', oval=True), fin=1.0)
# ---------- S1-04 当铺 → 药店 → 当铺 ----------
clip('S1-04', 0, 10.2, KB('m04a_pawn.jpg', 1.85, 1.75, (0.33, 0.6), (0.52, 0.3), tone=None), fin=0.8)
clip('S1-04', 9.6, 14.4, KB('m04b_pharm.jpg', 1.25, 1.45, (0.38, 0.5), (0.33, 0.47), tone=None), fin=0.6)
clip('S1-04', 13.8, 21.4, KB('m04a_pawn.jpg', 1.6, 1.25, (0.36, 0.62), (0.52, 0.42), tone=None), fin=0.6)
# ---------- S1-05 药引 → 油灯熄灭 ----------
clip('S1-05', 0, 9.6, KB('m05a_herbs.jpg', 1.8, 1.8, (0.2, 0.47), (0.8, 0.42), tone=None), fin=0.7)
lamp = KB('m05b_lamp.jpg', 1.0, 1.28, (0.5, 0.5), (0.62, 0.64), mode='fit', crop=(0.33, 0.065, 0.67, 0.945), tone=None)
blk = Image.new('RGB', (W, H), BLACK)
def lamp_fn(t, d):
    im = lamp(t, d); k = clamp((t - 4.4) / 0.7)
    return Image.blend(im, blk, ease(k) * 0.97) if k > 0 else im
clip('S1-05', 9.0, 15.0, lamp_fn, fin=0.7, fout=0.4)
# ---------- S1-06 原文逐字 → 转身卡 ----------
QF = SERIF(60); L1, L2 = '有谁从小康人家而坠入困顿的么，', '我以为在这途路中，大概可以看见世人的真面目'
glyphs = []
for li, line in enumerate((L1, L2)):
    wl = QF.getlength(line); x = W / 2 - wl / 2; y = 420 + li * 110
    for ch in line: glyphs.append((text_rgba(ch, QF, (240, 230, 206, 255)), x, y)); x += QF.getlength(ch)
t1a = text_rgba('第一次转身', SERIF(40), (170, 160, 140, 255)); t1b = text_rgba('在柜台前，他看见了人心', SERIF(84, 'Bold'), (244, 236, 220, 255))
def s16(t, d):
    im = Image.new('RGB', (W, H), BLACK)
    if t < 11.8:
        fa = 1 - clamp((t - 11.0) / 0.7); n = len(glyphs)
        for k, (g, x, y) in enumerate(glyphs):
            paste_a(im, g, (x, y + 6 - g.height / 2), clamp((t - 0.4 - k * 10.4 / n) / 0.35) * fa)
    else:
        u = t - 11.8
        paste_a(im, t1a, (W / 2 - t1a.width / 2, 400), clamp(u / 0.6)); paste_a(im, t1b, (W / 2 - t1b.width / 2, 500), clamp((u - 0.5) / 0.8))
    return im
clip('S1-06', 0, 17.0, s16, fin=0.6, fout=0.7)
# ---------- S1-07 维新报刊 → 《离家》 → 母亲 → 乌篷船 ----------
clip('S1-07', 0, 6.4, KB('hz11.png', 1.0, 1.16, (0.35, 0.5), (0.6, 0.5), crop=(0, 0.525, 1, 0.895)), fin=0.8)
clip('S1-07', 5.8, 12.8, KB('art05.jpg', 1.0, 1.35, (0.5, 0.5), (0.5, 0.62), mode='fit', crop=(0.03, 0.02, 0.97, 0.935), tone='warm'), fin=0.7)
clip('S1-07', 12.2, 20.0, KB('hz10.png', 1.0, 1.12, (0.5, 0.5), (0.5, 0.45), mode='fit', crop=(0.715, 0.225, 0.915, 0.445), oval=True), fin=0.9)
clip('S1-07', 19.4, 23.0, KB('m06_boat.jpg', 1.12, 1.2, (0.4, 0.5), (0.62, 0.5), tone=None), fin=0.9, fout=1.4)
# ---------- 片尾说明 ----------
CR = ['样片｜序章＋第一章（B站母版 00:00—02:58）', '未加配音、配乐与音效；旁白与鲁迅原文以字幕显示', '',
      '图片：林贤治《鲁迅画传》；《鲁迅全集》2005年版文前彩插；赵延年木刻《离家》', '木刻风画面、片名书法、钢笔特写：AI 生成（正式版片尾与平台均作标注）', '鲁迅原文均据《鲁迅全集》2005年版']
crs = [text_rgba(c, SERIF(40 if i == 0 else 32), (236, 228, 212, 255) if i == 0 else (176, 168, 152, 255)) if c else None for i, c in enumerate(CR)]
def cred(t, d):
    im = Image.new('RGB', (W, H), BLACK); y = 330
    for i, c in enumerate(crs):
        if c: paste_a(im, c, (W / 2 - c.width / 2, y), clamp((t - 0.3 - i * 0.15) / 0.8))
        y += 80 if i == 0 else 58
    return im
clips.append((TOTAL_MAIN + 0.4, TOTAL, cred, 0.8, 0.8))
WM = text_rgba('样片 · 无配音', SANS(24, 'Light'), (255, 255, 255, 255))

# ---------- 逐帧合成 ----------
def frame(Tg):
    base = Image.new('RGB', (W, H), BLACK)
    for (t0, t1, fn, fin, fout) in clips:
        if not (t0 <= Tg < t1): continue
        img = fn(Tg - t0, t1 - t0)
        a = min(clamp((Tg - t0) / fin) if fin > 0 else 1, clamp((t1 - Tg) / fout) if fout > 0 else 1)
        base = img if a >= 0.999 else Image.blend(base, img, a)
    for (t0, t1, fn, fin, fout) in overlays:
        if not (t0 <= Tg < t1): continue
        rgba, pos = fn(Tg - t0)
        paste_a(base, rgba, pos, min(clamp((Tg - t0) / fin), clamp((t1 - Tg) / fout)))
    for (t0, t1, img) in subs:
        if t0 <= Tg < t1:
            paste_a(base, img, (W / 2 - img.width / 2, H - 78 - img.height), min(clamp((Tg - t0) / 0.15), clamp((t1 - Tg) / 0.15)))
    if Tg < TOTAL_MAIN: paste_a(base, WM, (40, 32), 0.45)
    return base

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else ROOT + 'preview/luxun90_preview_S0-S1.mp4'
    if '--stills' in sys.argv:
        for tt in [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]:
            frame(tt).save(f'/tmp/still_{tt:06.1f}.jpg', quality=85)
        sys.exit(0)
    N = int(TOTAL * FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(N):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 250 == 0: print(f, '/', N, flush=True)
    p.stdin.close(); p.wait(); print('done', out, TOTAL)

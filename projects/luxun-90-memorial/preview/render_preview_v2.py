# 样片 v2：序章（冷开场）+ 第一章，国产2D动画电影风，2–4 秒一换，1920x1080/25fps，无声，旁白与原文以字幕显示
# 用法：python3 render_preview_v2.py [--stills 1,2,3] [--part k/n out.mp4]
import math, sys, re, csv, random, datetime, subprocess, yaml
from collections import OrderedDict
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
W, H, FPS = 1920, 1080, 25
ROOT = '/data/luxun90/'; S2 = ROOT + 'preview/src2/'
def SERIF(s, w='Regular'): return ImageFont.truetype(f'/usr/share/fonts/google-noto-cjk/NotoSerifCJK-{w}.ttc', s, index=2)
def SANS(s, w='Medium'): return ImageFont.truetype(f'/usr/share/fonts/google-noto-cjk/NotoSansSC-{w}.otf', s)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, t): return a + (b - a) * t
INK = (34, 27, 22); CREAM = (250, 242, 224)

# ---------- 图像缓存 ----------
_IM, _DER = OrderedDict(), OrderedDict()
def IMG(n):
    if n in _IM: _IM.move_to_end(n); return _IM[n]
    im = Image.open(S2 + n + '.jpg').convert('RGB'); _IM[n] = im
    if len(_IM) > 12: _IM.popitem(last=False)
    return im
def DER(key, make):
    if key in _DER: _DER.move_to_end(key); return _DER[key]
    v = make(); _DER[key] = v
    if len(_DER) > 24: _DER.popitem(last=False)
    return v
def graded(n, g):
    if not g: return IMG(n)
    def mk():
        im = IMG(n)
        if g == 'cold':
            d = ImageEnhance.Color(im).enhance(0.3); return Image.blend(d, Image.new('RGB', im.size, (60, 80, 110)), 0.16)
        if g == 'sepia':
            s = ImageOps.colorize(ImageOps.grayscale(im), (34, 24, 16), (252, 238, 212)); return Image.blend(s, im, 0.35)
        if g == 'blur':
            sm = im.resize((800, round(800 * im.height / im.width)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(9))
            return ImageEnhance.Brightness(sm).enhance(0.8)
    return DER((n, g), mk)
def kb(im, z, cx, cy, dx=0, dy=0):
    iw, ih = im.size; s = max(W / iw, H / ih) * z; vw, vh = W / s, H / s
    cxp = min(max(cx * iw, vw / 2), iw - vw / 2); cyp = min(max(cy * ih, vh / 2), ih - vh / 2)
    x0, y0 = cxp - vw / 2 + dx / s, cyp - vh / 2 + dy / s
    return im.transform((W, H), Image.AFFINE, (1 / s, 0, x0, 0, 1 / s, y0), resample=Image.BILINEAR), (s, x0, y0)
def KB(n, z0, z1, c0, c1, g=None, shake=None, post=None, e='lin'):
    def fn(t, d):
        u = t / d if e == 'lin' else ease(t / d) if e == 'io' else eout(t / d)
        dx = dy = 0
        if shake is not None and shake <= t <= shake + 0.32:
            k = int((t - shake) * FPS); dx, dy = [(18, -12), (-14, 9), (9, -6), (-5, 3), (2, -1), (0, 0), (0, 0), (0, 0), (0, 0)][min(k, 8)]
        im, M = kb(graded(n, g), lerp(z0, z1, u), lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u), dx, dy)
        if post: post(im, t, d, M, graded(n, g).size)
        return im
    return fn
def to_screen(M, size, px, py):
    s, x0, y0 = M; return ((px * size[0] - x0) * s, (py * size[1] - y0) * s)

# ---------- 文字 ----------
def text_rgba(txt, font, fill, stroke=0, sfill=(0, 0, 0), shadow=0):
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    p = 6 + shadow * 2
    im = Image.new('RGBA', (r - l + 2 * p, b - t + 2 * p), (0, 0, 0, 0))
    if shadow:
        m = Image.new('L', im.size, 0); ImageDraw.Draw(m).text((p - l + 3, p - t + 4), txt, font=font, fill=200, stroke_width=stroke + 2)
        m = m.filter(ImageFilter.GaussianBlur(shadow)); im.paste((10, 6, 4, 255), (0, 0), m)
    ImageDraw.Draw(im).text((p - l, p - t), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return im
def paste_a(base, rgba, pos, a=1.0):
    if a <= 0.003: return
    m = rgba.getchannel('A')
    if a < 0.997: m = m.point(lambda v, a=a: int(v * a))
    base.paste(rgba.convert('RGB'), (int(pos[0]), int(pos[1])), m)
class Pop:
    """逐字弹出的大字：lines=[(text, font, fill, cx, cy, t_start, per_char)]"""
    def __init__(self, lines, shadow=8, back=False):
        self.g = []; self.back = None
        for txt, font, fill, cx, cy, ts, pc in lines:
            wl = font.getlength(txt); x = cx - wl / 2
            for i, ch in enumerate(txt):
                cw = font.getlength(ch); im = text_rgba(ch, font, fill, shadow=shadow)
                self.g.append((im, x + cw / 2, cy, ts + i * pc)); x += cw
        if back:
            x0 = min(c - im.width / 2 for im, c, _, _ in self.g); x1 = max(c + im.width / 2 for im, c, _, _ in self.g)
            y0 = min(c - im.height / 2 for im, _, c, _ in self.g); y1 = max(c + im.height / 2 for im, _, c, _ in self.g); m = 120
            bm = Image.new('L', (int(x1 - x0) + 2 * m, int(y1 - y0) + 2 * m), 0); ImageDraw.Draw(bm).rounded_rectangle((m * .6, m * .6, bm.width - m * .6, bm.height - m * .6), 60, fill=125)
            b = Image.new('RGBA', bm.size, (14, 10, 8, 255)); b.putalpha(bm.filter(ImageFilter.GaussianBlur(40))); self.back = (b, x0 - m, y0 - m, min(ti for *_, ti in self.g))
    def draw(self, base, t, alpha=1.0):
        if self.back: b, bx, by, bt = self.back; paste_a(base, b, (bx, by), alpha * clamp((t - bt + 0.2) / 0.4))
        for im, cx, cy, ti in self.g:
            u = clamp((t - ti) / 0.28)
            if u <= 0: continue
            sc = lerp(1.7, 1.0, eout(u)); g = im if sc == 1.0 else im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
            paste_a(base, g, (cx - g.width / 2, cy - g.height / 2), clamp(u * 1.6) * alpha)
def make_label(main, sub=None):
    a = text_rgba(main, SERIF(50, 'Bold'), CREAM, shadow=6); b = text_rgba(sub, SANS(28, 'Regular'), (236, 226, 204), shadow=4) if sub else None
    w = max(a.width, b.width if b else 0) + 30; h = a.height + (b.height - 6 if b else 0) + 10
    im = Image.new('RGBA', (w + 40, h + 30), (0, 0, 0, 0))
    bg = Image.new('L', im.size, 0); ImageDraw.Draw(bg).rounded_rectangle((0, 6, w + 10, h + 4), 14, fill=96); im.paste((14, 10, 8, 255), (0, 0), bg.filter(ImageFilter.GaussianBlur(14)))
    sh = Image.new('L', (w, h), 0); ImageDraw.Draw(sh).rectangle((6, 14, 12, h - 12), fill=180); im.paste((10, 6, 4, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(3)))
    ImageDraw.Draw(im).rectangle((4, 12, 9, h - 14), fill=(214, 70, 46, 255))
    im.alpha_composite(a, (16, 0))
    if b: im.alpha_composite(b, (18, a.height - 8))
    return im
def tag_rgba(txt):
    f = SERIF(56, 'Bold'); n = len(txt); w, h = 104, n * 70 + 50
    im = Image.new('RGBA', (w + 30, h + 30), (0, 0, 0, 0))
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rectangle((14, 18, w + 14, h + 18), fill=150); im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(im).rectangle((8, 8, w + 8, h + 8), fill=(178, 48, 34, 255))
    ImageDraw.Draw(im).rectangle((16, 16, w, h), outline=(240, 214, 170, 255), width=2)
    for i, ch in enumerate(txt): ImageDraw.Draw(im).text((8 + w / 2, 8 + 25 + 35 + i * 70), ch, font=f, fill=(250, 236, 206), anchor='mm')
    return im

# ---------- 相片卡 ----------
def make_card(cn, hpx, rot, maxw=None):
    im = Image.open(S2 + 'card_' + cn + '.jpg').convert('RGB')
    s = hpx / im.height
    if maxw and im.width * s > maxw: s = maxw / im.width
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    bd, pad = 16, 46; cw, ch = im.width + 2 * bd, im.height + 2 * bd
    c = Image.new('RGBA', (cw + 2 * pad, ch + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('L', c.size, 0); ImageDraw.Draw(sh).rectangle((pad + 10, pad + 16, pad + cw + 10, pad + ch + 16), fill=160)
    c.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(c).rectangle((pad, pad, pad + cw, pad + ch), fill=(248, 243, 231, 255)); c.paste(im, (pad + bd, pad + bd))
    return c.rotate(rot, expand=True, resample=Image.BICUBIC)
def CARDS(bg, cards, z=(1.04, 1.12), c=(.5, .5), post=None):
    """cards: (名, cx, cy, 高, 旋转, 入场时刻, 来向dx, 来向dy[, 最大宽])"""
    def fn(t, d):
        im, M = kb(graded(bg, 'blur'), lerp(z[0], z[1], t / d), c[0], c[1])
        for cd in cards:
            cn, cx, cy, hp, rot, tin, fx, fy = cd[:8]; mw = cd[8] if len(cd) > 8 else None
            if t < tin: continue
            r = DER(('card', cn, hp, rot, mw), lambda: make_card(cn, hp, rot, mw))
            u = eout((t - tin) / 0.55); sc = lerp(1.18, 1.0, u)
            g = r if u >= 1 else r.resize((int(r.width * sc), int(r.height * sc)), Image.BILINEAR)
            drift = (t - tin) * 7
            paste_a(im, g, (cx + fx * (1 - u) + drift - g.width / 2, cy + fy * (1 - u) - g.height / 2), clamp((t - tin) / 0.2))
        if post: post(im, t, d)
        return im
    return fn

# ---------- 纸张 ----------
def make_paper():
    rnd = random.Random(3)
    base = Image.new('RGB', (W, H), (240, 230, 208))
    lo = Image.effect_noise((W // 16, H // 16), 30).resize((W, H), Image.BICUBIC)
    hi = Image.effect_noise((W, H), 18).filter(ImageFilter.GaussianBlur(0.6))
    base = Image.composite(Image.new('RGB', (W, H), (226, 212, 184)), base, lo.point(lambda v: int(clamp((v - 110) / 120) * 140)))
    base = Image.blend(base, Image.merge('RGB', (hi, hi, hi)), 0.05)
    vg = Image.new('L', (W, H), 0); ImageDraw.Draw(vg).ellipse((-W * .2, -H * .25, W * 1.2, H * 1.25), fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(base, Image.new('RGB', (W, H), (206, 186, 150)), vg)
PAPER = make_paper()

# ---------- 时间线 ----------
clips, ovs, subs, tags = [], [], [], []
def clip(t0, t1, fn, tr='fade', td=0.35): clips.append((t0, t1, fn, tr, td))
def ov(t0, t1, draw, fin=0.3, fout=0.3): ovs.append((t0, t1, draw, fin, fout))
def LABEL(t0, t1, main, sub=None, pos=(96, 84)):
    im = make_label(main, sub)
    def dr(base, t, a):
        u = eout(t / 0.6); w = max(1, int(im.width * u))
        paste_a(base, im.crop((0, 0, w, im.height)), (pos[0] + (1 - u) * -20, pos[1]), a)
    ov(t0, t1, dr, 0.15, 0.35)
def TAG(t0, t1, txt, pos=(W - 250, 150)):
    im = tag_rgba(txt)
    def dr(base, t, a):
        u = eout(t / 0.4); g = im.resize((im.width, max(1, int(im.height * u))), Image.BILINEAR)
        paste_a(base, g, pos, a)
    ov(t0, t1, dr, 0.1, 0.3)
def POP(t0, t1, pop, fin=0.01, fout=0.4): ov(t0, t1, lambda b, t, a: pop.draw(b, t + t0, a), fin, fout)

# 字幕
SB = yaml.safe_load(open(ROOT + 'storyboard.yaml', encoding='utf-8'))
Q = {r[0]: r[1] for r in csv.reader(open(ROOT + 'quotes_src.tsv', encoding='utf-8'), delimiter='\t')}
VR, QR, GAP = SB['meta']['vo_rate'], SB['meta']['quote_rate'], SB['meta']['gap']
SHOT = {s['id']: s for ch in SB['chapters'][:2] for s in ch['shots']}
def vo_of(sid): return [a['vo'] for a in SHOT[sid]['audio'] if 'vo' in a][0]
def nchar(txt): return len(re.sub(r'[，。；：！？、—“”（）\s]', '', txt))
def chunks(txt, n=18):
    parts = re.findall(r'[^，。；：！？、—]+[，。；：！？、]*(?:——)?|——', txt); out, cur = [], ''
    for p in parts:
        if cur and len(cur) + len(p) > n: out.append(cur); cur = p
        else: cur += p
    if cur: out.append(cur)
    return [c.rstrip('，。；、').rstrip('—') or c for c in out]
SRCNAME = {'Q02': '鲁迅《死》', 'Q71': '鲁迅《死》', 'Q01': '鲁迅《死》'}
FV, FQ, FT = SANS(44), SERIF(46, 'SemiBold'), SERIF(28)
def SUB(t0, kind, txt=None):
    q = kind != 'vo'; txt = txt or Q[kind]; dur = nchar(txt) / (QR if q else VR)
    cs = chunks(txt); tot = sum(len(c) for c in cs); u = t0
    for c in cs:
        dd = dur * len(c) / tot
        subs.append((u, u + dd - 0.08, text_rgba(c, FQ if q else FV, (252, 236, 196) if q else (255, 255, 255), 3, (20, 14, 10))))
        u += dd
    if q:
        tg = text_rgba('——' + SRCNAME.get(kind, '鲁迅《〈呐喊〉自序》'), FT, (250, 236, 206), 2, (20, 14, 10))
        tags.append((t0, t0 + dur, tg))
    return t0 + dur
S05 = vo_of('S0-05'); S06 = vo_of('S0-06'); S06a, S06b = S06.split('。', 1)[0] + '。', S06.split('。', 1)[1]
SUB(7.0, 'vo', S05); SUB(19.2, 'vo', S06a); SUB(29.0, 'vo', vo_of('S0-02')); SUB(33.9, 'Q71'); SUB(42.3, 'vo', vo_of('S0-04')); SUB(58.2, 'vo', S06b)
T = 68.0
for sid in ['S1-01', 'S1-02', 'S1-03', 'S1-04', 'S1-05', 'S1-06', 'S1-07']:
    s = SHOT[sid]; t = T + 0.4
    for a in s.get('audio', []):
        if 'vo' in a: kind, txt = 'vo', a['vo']
        elif 'q' in a: kind, txt = a['q'], Q[a['q']]
        else: continue
        if (sid, kind) == ('S1-06', 'vo'): t += nchar(txt) / VR + GAP; continue
        t = SUB(t, kind, txt) + GAP
    T += s['dur']
TOTAL_MAIN = 178.0; CRED = 7.0; TOTAL = TOTAL_MAIN + CRED
assert abs(T - TOTAL_MAIN) < 1e-6, T

# ================= 序章 =================
# 冷开场 0–6.8：笔尖 → 鲁迅伏案，“忘记我，管自己生活。——倘不，那就真是胡涂虫。”
clip(0.0, 2.5, KB('p01_brush', 1.06, 1.32, (.6, .6), (.6, .66)), 'black', 0.3)
clip(2.3, 6.9, KB('p02_luxun_desk', 1.02, 1.16, (.55, .45), (.6, .38)), 'fade', 0.35)
GRAD = Image.new('RGBA', (W, H), (0, 0, 0, 0))
_m = Image.linear_gradient('L').rotate(90, expand=True).resize((W, H)); _m = _m.point(lambda v: int(clamp((v - 70) / 185) * 150))
GRAD.paste((12, 8, 6, 255), (0, 0), _m)
ov(0.0, 6.6, lambda b, t, a: paste_a(b, GRAD, (0, 0), a), 0.3, 0.4)
pre = text_rgba('1936年9月5日，鲁迅在遗嘱里写：', SERIF(40), (244, 232, 210), shadow=6)
ov(0.3, 6.5, lambda b, t, a: paste_a(b, pre, (120, 300), a * clamp(t / 0.5)), 0.01, 0.4)
F1, F2 = SERIF(150, 'Bold'), SERIF(76, 'SemiBold')
POP(0.9, 6.5, Pop([('忘记我', F1, CREAM, 470, 500, 0.9, 0.18)]), 0.01, 0.4)
POP(2.1, 3.9, Pop([('管自己生活。', F2, CREAM, 470, 680, 2.1, 0.09)]), 0.01, 0.25)
POP(3.8, 6.5, Pop([('——倘不，那就真是胡涂虫。', F2, (255, 214, 160), 600, 680, 3.8, 0.07)]), 0.01, 0.4)
# 出殡 6.8–19.0
clip(6.8, 9.5, KB('p03_procession', 1.04, 1.16, (.5, .55), (.55, .5)), 'whip', 0.4)
clip(9.3, 11.6, CARDS('p03_procession', [('qj6081', 960, 520, 700, -3, 0.0, 0, 700)]))
LABEL(9.5, 11.5, '1936年10月22日', '上海 · 万国殡仪馆 出殡')
clip(11.4, 13.8, KB('p04_mourners', 1.08, 1.16, (.3, .5), (.6, .5)), 'whip', 0.35)
clip(13.6, 15.6, CARDS('p04_mourners', [('qj6081', 640, 540, 560, -4, -0.6, 0, 0), ('hz233', 1320, 540, 700, 3, 0.0, 900, 0)]))
def flag_post(im, t, d, M, size):
    if t < 1.5: return
    x, y = to_screen(M, size, .53, .5); s = M[0] / (W / size[0])
    k = DER(('mzh', round(s, 2)), lambda: text_rgba('民族魂', SERIF(int(150 * s), 'Black'), (28, 24, 22, 255)).filter(ImageFilter.GaussianBlur(1.1)))
    paste_a(im, k, (x - k.width / 2, y - k.height / 2), clamp((t - 1.5) / 0.7) * 0.92)
clip(15.4, 19.1, KB('p05_coffin', 1.0, 1.22, (.52, .5), (.53, .5), post=flag_post), 'fade', 0.35)
LABEL(17.2, 19.0, '民族魂', '覆在灵柩上的白旗')
# 九十年 19.0–23.0 → 片名 23.0
clip(19.0, 23.1, KB('p06_statue', 1.0, 1.14, (.5, .5), (.5, .4)), 'flash', 0.4)
def counter(t0, t1, y0, y1, pos, font=SERIF(210, 'Bold'), dur=None):
    def dr(b, t, a):
        u = ease(t / (dur or (t1 - t0) * 0.8)); im = text_rgba(str(round(lerp(y0, y1, u))), font, CREAM, shadow=10)
        paste_a(b, im, (pos[0] - im.width / 2, pos[1] - im.height / 2), a)
    return dr
ov(19.2, 23.0, counter(19.2, 23.0, 1936, 2026, (460, 300), dur=2.6), 0.3, 0.2)
TM = Image.open(S2 + 'title_mask.png').convert('L').resize((round(1376 * 1.42), round(768 * 1.42)), Image.LANCZOS)
TINK = Image.new('RGBA', TM.size, INK + (255,)); TINK.putalpha(TM)
tsub = text_rgba('鲁迅逝世九十周年　1936—2026', SERIF(46), (92, 64, 44, 255))
def title_fn(t, d):
    im = PAPER.copy(); u = eout(t / 0.35); sc = lerp(1.35, 1.0, u) * (1 + 0.03 * t / d)
    g = TINK.resize((int(TINK.width * sc), int(TINK.height * sc)), Image.BILINEAR)
    dx, dy = ((14, -10), (-10, 7), (6, -4), (-3, 2), (0, 0))[min(4, max(0, int((t - 0.35) * FPS)))] if t > 0.35 else (0, 0)
    paste_a(im, g, (W / 2 - g.width / 2 + dx, H / 2 - g.height / 2 - 40 + dy), clamp(t / 0.12))
    paste_a(im, tsub, (W / 2 - tsub.width / 2, 840), clamp((t - 1.2) / 0.8)); return im
clip(23.0, 28.8, title_fn, 'flash', 0.25)
# 遗嘱 28.6–42.2
clip(28.6, 31.6, KB('p07_lane_autumn', 1.06, 1.2, (.55, .35), (.6, .25)), 'whip', 0.35)
LABEL(28.9, 31.4, '上海 · 大陆新村', '1936年 秋')
clip(31.4, 34.0, KB('p08_desk_ots', 1.0, 1.22, (.5, .5), (.44, .58)), 'fade', 0.3)
clip(33.8, 37.4, CARDS('p08_desk_ots', [('qj2028', 760, 540, 860, -3, 0.0, 0, 800)]))
LABEL(34.1, 37.2, '《死》手稿', '1936年9月5日')
# 竖排遗嘱（纸上）：先亮第二、三条，再亮“忘记我”
VMAP = {'，': '︐', '。': '︒', '、': '︑', '；': '︔', '：': '︓', '—': '︱', '！': '︕', '？': '︖', '“': '﹁', '”': '﹂'}
def vcol(txt, font, cell, fill):
    fs = font.size; im = Image.new('RGBA', (int(fs * 1.4), int(cell * len(txt)) + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, ch in enumerate(txt):
        g = VMAP.get(ch, ch); l, t, r, b = d.textbbox((0, 0), g, font=font)
        x = (im.width - (r - l)) / 2 - l; y = i * cell + (cell - (b - t)) / 2 - t
        if ch in '，。、': x += fs * 0.25; y -= fs * 0.25
        d.text((x, y), g, font=font, fill=fill)
    return im
ITEMS = [['一，不得因为丧事，收受任何人的', '一文钱。——但老朋友的，不在此例。'], ['二，赶快收敛，埋掉，拉倒。'], ['三，不要做任何关于纪念的事情。'],
         ['四，忘记我，管自己生活。', '——倘不，那就真是胡涂虫。'], ['五，孩子长大，倘无才能，可寻点', '小事情过活，万不可去做空头文学', '家或美术家。'],
         ['六，别人应许给你的事物，不可当真。'], ['七，损着别人的牙眼，却反对报复，', '主张宽容的人，万勿和他接近。']]
FS, CELL, CW, TOP = 42, 50, 78, 100
cols, x = [], 0
for i, it in enumerate(ITEMS):
    for j, c in enumerate(it): cols.append((i, c, x)); x += CW
    x += 24
X0 = W / 2 + (x - 24) / 2 - CW
VL = [(i, vcol(c, SERIF(FS, 'SemiBold'), CELL, INK + (255,)), vcol(c, SERIF(FS, 'SemiBold'), CELL, (168, 44, 30, 255)), X0 - xx) for i, c, xx in cols]
def will_fn(t, d):
    im, _ = kb(PAPER, 1.0 + 0.05 * t / d, .5, .5)
    for i, ink, red, xx in VL:
        a = 0.22 + 0.78 * (clamp((t - 0.2) / 0.5) if i == 1 else clamp((t - 0.3) / 0.5) if i == 2 else clamp((t - 2.6) / 0.6) if i == 3 else 0)
        paste_a(im, red if (i == 3 and t > 2.6) else ink, (xx - (ink.width - CW) / 2, TOP), a * clamp(t / 0.4))
    return im
clip(37.2, 42.2, will_fn, 'fade', 0.4)
# 第四十四天 42.0–57.6
WK = '一二三四五六日'
def cal_card(day):
    dt = datetime.date(1936, 9, 5) + datetime.timedelta(days=day)
    c = Image.new('RGBA', (420, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rectangle((0, 0, 419, 559), fill=(246, 238, 220, 255)); d.rectangle((0, 0, 419, 120), fill=(176, 42, 30, 255))
    d.text((210, 62), ('九月' if dt.month == 9 else '十月'), font=SERIF(60, 'Bold'), fill=(250, 238, 220), anchor='mm')
    d.text((210, 290), str(dt.day), font=SERIF(220, 'Black'), fill=(28, 22, 18), anchor='mm')
    d.text((210, 455), '星期' + WK[dt.weekday()], font=SERIF(42), fill=(70, 56, 44), anchor='mm')
    d.text((210, 515), '民国二十五年', font=SERIF(32), fill=(120, 100, 80), anchor='mm')
    for k in range(0, 420, 15): d.ellipse((k + 4, 6, k + 11, 13), fill=(110, 26, 20, 255))
    return c
CAL = [None] * 45
def cal_fn(t, d):
    im, _ = kb(graded('p08_desk_ots', 'blur'), 1.1, .5, .5)
    v = ease((t - 0.6) / 3.2) * 44; k = min(44, int(v)); fr = v - k if k < 44 else 0
    for kk in (k, min(44, k + 1)):
        if CAL[kk] is None: CAL[kk] = cal_card(kk)
    cx, cy = W / 2, H / 2 - 30
    if k < 44: paste_a(im, CAL[k + 1], (cx - 210, cy - 280))
    top = CAL[k] if fr < 0.02 else CAL[k].rotate(-10 * fr, expand=True, resample=Image.BILINEAR)
    paste_a(im, top, (cx - top.width / 2 + 60 * fr, cy - top.height / 2 - 520 * fr * fr), 1 - fr)
    return im
clip(42.0, 47.0, cal_fn, 'fade', 0.35)
nd = text_rgba('第 44 天', SERIF(64, 'Bold'), CREAM, shadow=8)
ov(45.2, 47.0, lambda b, t, a: paste_a(b, nd, (W / 2 + 280, H / 2 - 60), a), 0.3, 0.3)
clip(46.8, 50.0, KB('p09_clock', 1.05, 1.5, (.33, .3), (.33, .25)), 'fade', 0.35)
LABEL(47.6, 49.8, '清晨 5:25')
clip(49.8, 53.2, KB('p10_lane_dawn', 1.04, 1.16, (.4, .45), (.3, .4)), 'fade', 0.35)
LABEL(50.0, 53.0, '上海 · 大陆新村9号')
clip(53.0, 57.8, CARDS('p10_lane_dawn', [('hz231', 960, 540, 900, -2, 0.0, 0, 120)], z=(1.06, 1.14)), 'fade', 0.5)
LABEL(54.2, 57.4, '鲁迅', '1881—1936')
# 回信 57.6–62.4 → 时光倒流 62.4–66.8
clip(57.6, 62.6, KB('p11_letter', 1.0, 1.18, (.5, .55), (.46, .7)), 'fade', 0.6)
RW = ['p06_statue', 'p10_lane_dawn', 'p09_clock', 'p05_coffin', 'p03_procession', 'p02_luxun_desk', 'c35_boat_leave', 'c34_mother_cry',
      'c29_backlit', 'c25_lamp', 'c19_tears', 'c14_hands', 'c10_snow_bridge', 'c07_lock', 'c04_baby']
R0, R1 = 62.4, 66.6; RD = (R1 - R0) / len(RW)
for i, n in enumerate(RW): clip(R0 + i * RD, R0 + (i + 1) * RD + 0.04, KB(n, 1.14, 1.0, (.5, .5), (.5, .5), g='sepia'), 'flash' if i == 0 else 'cut', 0.2 if i == 0 else 0)
ov(62.6, 68.3, counter(62.6, 68.3, 2026, 1881, (W / 2, H / 2), SERIF(240, 'Bold'), dur=3.9), 0.2, 0.5)

# ================= 第一章 =================
clip(66.6, 72.0, KB('c01_aerial', 1.0, 1.28, (.5, .4), (.5, .55)), 'flash', 0.3)
POP(68.4, 71.8, Pop([('一｜绍兴', SERIF(132, 'Bold'), CREAM, W / 2, 440, 68.4, 0.12), ('1881—1898　坠入困顿', SERIF(50), (250, 232, 204), W / 2, 590, 68.9, 0.05)], back=True), 0.01, 0.4)
clip(71.8, 73.6, KB('c02_boat', 1.1, 1.24, (.35, .55), (.45, .55)), 'whip', 0.35)
clip(73.4, 75.0, CARDS('c02_boat', [('hz4', 960, 540, 760, -2, 0.0, 0, 600, 1300)]))
LABEL(73.6, 74.9, '绍兴旧影')
clip(74.8, 77.4, KB('c03_gate', 1.0, 1.14, (.4, .45), (.38, .5)), 'fade', 0.3)
LABEL(75.0, 77.2, '1881.9.25', '浙江 · 绍兴')
clip(77.2, 79.6, KB('c04_baby', 1.04, 1.24, (.5, .5), (.47, .55)), 'fade', 0.3)
clip(79.4, 81.4, CARDS('c03_gate', [('hz6', 960, 540, 800, 2, 0.0, 0, 700, 1300)]))
LABEL(79.6, 81.3, '东昌坊口 · 周家新台门')
clip(81.2, 82.8, lambda t, d: kb(graded('c04_baby', 'blur'), 1.1 + 0.03 * t, .5, .5)[0])
POP(81.3, 82.8, Pop([('本名', SERIF(44), (250, 232, 204), W / 2, 400, 81.3, 0.05), ('周樟寿', SERIF(170, 'Bold'), CREAM, W / 2, 560, 81.4, 0.12)]), 0.01, 0.2)
clip(82.6, 85.0, KB('c05_beijing', 1.0, 1.1, (.45, .55), (.3, .55)), 'whip', 0.35)
LABEL(82.9, 84.8, '祖父 周福清', '翰林 · 京官')
clip(84.8, 87.2, CARDS('c05_beijing', [('hz9', 700, 560, 780, -3, 0.0, -500, 0), ('hz7', 1340, 760, 300, 3, 0.35, 600, 0, 760)]))
# 1893
clip(87.0, 89.6, KB('c06_bribe', 1.05, 1.22, (.55, .5), (.6, .45)), 'whip', 0.35)
LABEL(87.2, 89.4, '1893', '科场案')
clip(89.4, 91.6, KB('c07_lock', 1.3, 1.12, (.55, .5), (.55, .5), shake=1.0), 'fade', 0.2)
clip(91.4, 93.0, KB('c03_gate', 1.16, 1.0, (.4, .5), (.45, .5), g='cold'), 'fade', 0.3)
LABEL(91.6, 92.9, '家道中落')
def father_card(im, t, d, M, size):
    if t < 0.7: return
    r = DER(('card', 'hz10f', 380, 4), lambda: make_card('hz10f', 380, 4))
    u = eout((t - 0.7) / 0.5); paste_a(im, r, (1380 + 300 * (1 - u), 120), clamp((t - 0.7) / 0.2))
clip(92.8, 95.0, KB('c08_father_ill', 1.0, 1.14, (.4, .45), (.35, .42), post=father_card), 'fade', 0.3)
LABEL(93.6, 94.9, '父亲 周伯宜', '1894年冬 病倒')
clip(94.8, 97.4, KB('c09_doorway', 1.1, 1.3, (.4, .4), (.39, .3)), 'fade', 0.3)
clip(97.2, 100.0, KB('c10_snow_bridge', 1.12, 1.18, (.42, .35), (.6, .35)), 'whip', 0.35)
clip(99.8, 104.0, KB('c11_rain', 1.04, 1.22, (.55, .5), (.58, .55)), 'fade', 0.4)
# 质铺和药店 102.4–123
clip(103.8, 106.4, KB('c12_pawn_facade', 1.25, 1.12, (.42, .8), (.5, .35), e='io'), 'fade', 0.3)
clip(106.2, 108.0, KB('c13_pawn_counter', 1.12, 1.26, (.5, .5), (.55, .45)), 'whip', 0.3)
TAG(106.4, 108.0, '质铺')
clip(107.8, 109.6, KB('c17_pharmacy', 1.08, 1.2, (.5, .5), (.45, .45)), 'whip', 0.3)
TAG(108.0, 109.6, '药店')
clip(109.4, 111.6, KB('c18_dusk', 1.05, 1.16, (.35, .5), (.32, .5)), 'fade', 0.35)
def same_h(im, t, d, M, size):
    if t < 1.0: return
    u = eout((t - 1.0) / 0.6); x0, y = to_screen(M, size, .27, .51); x1, _ = to_screen(M, size, .56, .51)
    dd = ImageDraw.Draw(im); xe = lerp(x0, x1, u); x = x0
    while x < xe: dd.line((x, y, min(x + 26, xe), y), fill=(255, 226, 120), width=6); x += 44
    if u > 0.9: paste_a(im, SAMEH, (x0 + 30, y - SAMEH.height - 24), clamp((t - 1.5) / 0.4))
SAMEH = text_rgba('一样高', SERIF(58, 'Bold'), (255, 230, 140), shadow=6)
clip(111.4, 115.8, KB('c17_pharmacy', 1.42, 1.56, (.36, .5), (.37, .5), post=same_h), 'fade', 0.35)
clip(115.6, 117.6, KB('c14_hands', 1.04, 1.16, (.45, .5), (.45, .4)), 'whip', 0.3)
TWICE = make_label('比我高一倍')
ov(116.0, 117.6, lambda b, t, a: paste_a(b, TWICE, (1200, 700 - 40 * eout(t / 0.5)), a), 0.25, 0.2)
clip(117.4, 119.6, KB('c15_clerk', 1.0, 1.16, (.5, .55), (.5, .45)), 'fade', 0.3)
clip(119.4, 121.4, KB('c16_coins', 1.06, 1.2, (.5, .5), (.5, .62)), 'fade', 0.3)
clip(121.2, 123.4, KB('c19_tears', 1.0, 1.12, (.45, .5), (.43, .45)), 'fade', 0.3)
# 药引 123–138
clip(123.2, 125.0, KB('c20_reeds', 1.05, 1.16, (.5, .5), (.55, .55)), 'whip', 0.3); TAG(123.4, 124.9, '芦根')
clip(124.8, 127.0, KB('c21_cane', 1.05, 1.18, (.45, .55), (.55, .55)), 'whip', 0.3); TAG(125.0, 126.9, '甘蔗')
clip(126.8, 128.8, KB('c22_crickets', 1.05, 1.18, (.45, .5), (.48, .55)), 'whip', 0.3); TAG(127.0, 128.7, '蟋蟀')
clip(128.6, 130.8, KB('c23_berries', 1.05, 1.18, (.6, .5), (.6, .45)), 'whip', 0.3); TAG(128.8, 130.7, '平地木')
def grid_fn(t, d):
    def mk():
        g = PAPER.copy()
        for k, n in enumerate(['c20_reeds', 'c21_cane', 'c22_crickets', 'c23_berries']):
            im = IMG(n).resize((924, 520), Image.LANCZOS); g.paste(im, (24 + (k % 2) * 948, 14 + (k // 2) * 540 + 6))
        return g
    return kb(DER('grid', mk), 1.0 + 0.04 * t / d, .5, .5)[0]
clip(130.6, 131.8, grid_fn, 'fade', 0.25)
clip(131.6, 134.4, KB('c24_bedside', 1.0, 1.16, (.45, .45), (.45, .4)), 'fade', 0.35)
LABEL(131.8, 134.2, '1896年10月')
def lamp_fn(t, d):
    im = KB('c25_lamp', 1.0, 1.16, (.5, .55), (.5, .6))(t, d); k = clamp((t - 2.0) / 0.5)
    return Image.blend(im, Image.new('RGB', (W, H), (8, 6, 5)), ease(k) * 0.8) if k > 0 else im
clip(134.2, 138.2, lamp_fn, 'fade', 0.35)
# 世人的真面目 138–155
clip(138.0, 140.8, KB('c26_gossip', 1.0, 1.12, (.5, .55), (.5, .5)), 'fade', 0.4)
clip(140.6, 143.0, KB('c27_relatives', 1.0, 1.16, (.5, .45), (.5, .4)), 'whip', 0.3)
clip(142.8, 145.2, KB('c28_puddle', 1.05, 1.2, (.5, .5), (.5, .55)), 'fade', 0.35)
clip(145.0, 146.2, KB('c15_clerk', 1.45, 1.6, (.48, .36), (.48, .36)), 'cut', 0)
clip(146.0, 147.2, KB('c27_relatives', 1.7, 1.85, (.6, .38), (.6, .38)), 'cut', 0)
clip(147.0, 148.6, KB('c26_gossip', 1.9, 2.05, (.9, .5), (.9, .5)), 'cut', 0)
POP(146.0, 148.6, Pop([('世人的真面目', SERIF(120, 'Bold'), CREAM, W / 2, H / 2 - 30, 146.0, 0.08)], back=True), 0.01, 0.3)
clip(148.4, 155.2, KB('c29_backlit', 1.0, 1.12, (.5, .5), (.52, .45)), 'flash', 0.4)
POP(149.6, 154.8, Pop([('第一次转身', SERIF(46), (255, 228, 180), W / 2, 330, 149.6, 0.06), ('在柜台前，他看见了人心', SERIF(86, 'Bold'), CREAM, W / 2, 450, 150.0, 0.1)], back=True), 0.01, 0.5)
# 离家 155–178
clip(155.0, 157.8, KB('c30_reading', 1.05, 1.2, (.45, .45), (.45, .4)), 'fade', 0.4)
LABEL(155.2, 157.6, '1898')
clip(157.6, 160.4, CARDS('c30_reading', [('hz11', 960, 540, 640, -2, 0.0, 0, 600, 1300)]))
LABEL(157.8, 160.2, '维新报刊')
clip(160.2, 163.4, KB('c31_bridge_dawn', 1.7, 1.45, (.52, .42), (.52, .42)), 'fade', 0.35)
clip(163.2, 166.6, KB('c31_bridge_dawn', 1.12, 1.0, (.5, .4), (.5, .45)), 'fade', 0.4)
clip(166.4, 169.4, KB('c32_mother_coins', 1.04, 1.22, (.6, .45), (.55, .62)), 'fade', 0.35)
clip(169.2, 171.4, KB('c33_hands_coins', 1.0, 1.14, (.5, .5), (.48, .55)), 'fade', 0.3)
LABEL(169.4, 171.2, '八元川资')
clip(171.2, 173.8, KB('c34_mother_cry', 1.04, 1.2, (.6, .45), (.68, .4)), 'fade', 0.35)
clip(173.6, 175.6, CARDS('c34_mother_cry', [('hz10m', 960, 540, 760, 2, 0.0, 0, 500)]))
LABEL(173.8, 175.4, '母亲 鲁瑞')
clip(175.4, 178.4, KB('c35_boat_leave', 1.0, 1.12, (.55, .5), (.62, .5)), 'fade', 0.4)
# 片尾
CR = ['样片 v2｜序章＋第一章（B站母版 00:00—02:58）', '未加配音、配乐与音效；旁白与鲁迅原文以字幕显示', '',
      '动画画面：AI 生成（正式版片尾与平台均作标注）', '历史照片：林贤治《鲁迅画传》；《鲁迅全集》2005年版文前彩插', '鲁迅原文均据《鲁迅全集》2005年版']
CRS = [text_rgba(c, SERIF(42 if i == 0 else 32, 'SemiBold' if i == 0 else 'Regular'), INK + (255,) if i == 0 else (96, 74, 56, 255)) if c else None for i, c in enumerate(CR)]
def cred(t, d):
    im = PAPER.copy(); y = 330
    for i, c in enumerate(CRS):
        if c: paste_a(im, c, (W / 2 - c.width / 2, y), clamp((t - 0.3 - i * 0.15) / 0.8))
        y += 84 if i == 0 else 60
    return im
clip(178.0, TOTAL, cred, 'fade', 0.6)
WM = text_rgba('样片 v2 · 无配音', SANS(24, 'Light'), (255, 255, 255, 255), 1, (0, 0, 0))
# 浮尘
rnd = random.Random(11)
DUST = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(-14, 14), rnd.uniform(-22, -6), rnd.choice([3, 4, 5, 7]), rnd.uniform(0, 6.28)) for _ in range(46)]
SPR = {}
for r in (3, 4, 5, 7):
    m = Image.new('L', (r * 6, r * 6), 0); ImageDraw.Draw(m).ellipse((r * 2, r * 2, r * 4, r * 4), fill=255); m = m.filter(ImageFilter.GaussianBlur(r * 0.8))
    s = Image.new('RGBA', m.size, (255, 236, 196, 255)); s.putalpha(m); SPR[r] = s
DUSTR = [(0, 6.8), (15.4, 19.0), (31.4, 34.0), (53, 62.4), (102, 123.4), (131.6, 138.2), (148.4, 155.2), (155.0, 157.8)]
def dust(base, T):
    a = max([clamp((T - a0) / 0.5) * clamp((a1 - T) / 0.5) for a0, a1 in DUSTR] + [0])
    if a <= 0: return
    for x0, y0, vx, vy, r, ph in DUST:
        paste_a(base, SPR[r], ((x0 + vx * T) % W, (y0 + vy * T) % H), a * (0.35 + 0.35 * math.sin(T * 1.7 + ph)))

# ---------- 合成 ----------
WHITE = Image.new('RGB', (W, H), (255, 250, 240)); BLACK = Image.new('RGB', (W, H), (0, 0, 0))
def mblur(im, s):
    if s < 0.12: return im
    k = int(2 + s * 26); return im.resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
def frame(T):
    base = BLACK
    for t0, t1, fn, tr, td in clips:
        if not (t0 <= T < t1): continue
        img = fn(T - t0, t1 - t0)
        if tr == 'cut' or td <= 0 or T - t0 >= td: base = img; continue
        a = (T - t0) / td
        if tr in ('fade', 'black'): base = Image.blend(base, img, ease(a))
        elif tr == 'flash':
            base = Image.blend(Image.blend(base, img, ease(a)), WHITE, 0.85 * (1 - abs(2 * a - 1)))
        elif tr == 'whip':
            u = ease(a); sp = math.sin(math.pi * a); off = int(W * u)
            c = Image.new('RGB', (W, H)); c.paste(mblur(base, sp), (-off, 0)); c.paste(mblur(img, sp), (W - off, 0)); base = c
    if base is BLACK: base = BLACK.copy()
    dust(base, T)
    for t0, t1, dr, fin, fout in ovs:
        if t0 <= T < t1: dr(base, T - t0, min(clamp((T - t0) / fin), clamp((t1 - T) / fout)))
    for t0, t1, im in subs:
        if t0 <= T < t1: paste_a(base, im, (W / 2 - im.width / 2, H - 70 - im.height), min(clamp((T - t0) / 0.12), clamp((t1 - T) / 0.12)))
    for t0, t1, im in tags:
        if t0 <= T < t1: paste_a(base, im, (W - 64 - im.width, H - 150 - im.height), 0.9 * min(clamp((T - t0) / 0.4), clamp((t1 - T) / 0.4)))
    if T < TOTAL_MAIN: paste_a(base, WM, (W - 40 - WM.width, 30), 0.5)
    return base

if __name__ == '__main__':
    if '--stills' in sys.argv:
        for tt in [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]:
            frame(tt).save(f'/tmp/v2_{tt:06.1f}.jpg', quality=85)
        sys.exit(0)
    k, n = map(int, sys.argv[sys.argv.index('--part') + 1].split('/')); out = sys.argv[sys.argv.index('--part') + 2]
    N = int(TOTAL * FPS); a, b = N * k // n, N * (k + 1) // n
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(frame(f / FPS).tobytes())
        if (f - a) % 250 == 0: print(k, f - a, '/', b - a, flush=True)
    p.stdin.close(); p.wait(); print('done', k)

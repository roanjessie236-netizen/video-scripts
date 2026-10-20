# 样片 v3：序章（冷开场）+ 第一章。真实素材为主（历史照片、手稿、书刊、版画、实拍），少年时期用 AI 情景再现（D 写实，不露正脸）
# 影视剧、AI、当代实拍统一“冷调旧胶片·中档”；老照片保持黑白原样。1920x1080/25fps，无声，旁白与原文以字幕显示
# 先运行 prep_v3.py 生成 preview/src3/。用法：python3 render_preview_v3.py [--plan] [--stills 1,2,3] [--part k/n out.mp4]
import math, sys, re, csv, random, datetime, subprocess, yaml
from collections import OrderedDict
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops
W, H, FPS = 1920, 1080, 25
ROOT = '/data/luxun90/'; S3 = ROOT + 'preview/src3/'
FD = '/usr/share/fonts/google-noto-cjk/'
def SERIF(s, w='Regular'): return ImageFont.truetype(FD + f'NotoSerifCJK-{w}.ttc', s, index=2)
def SANS(s, w='Regular'): return ImageFont.truetype(FD + f'NotoSansSC-{w}.otf', s)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, t): return a + (b - a) * t
INK = (30, 28, 26); CREAM = (244, 240, 230); RED = (168, 58, 44)

# ---------- 图像缓存 ----------
_IM, _DER = OrderedDict(), OrderedDict()
def IMG(n):
    if n in _IM: _IM.move_to_end(n); return _IM[n]
    im = Image.open(S3 + n + '.jpg').convert('RGB'); _IM[n] = im
    if len(_IM) > 14: _IM.popitem(last=False)
    return im
def DER(key, make):
    if key in _DER: _DER.move_to_end(key); return _DER[key]
    v = make(); _DER[key] = v
    if len(_DER) > 40: _DER.popitem(last=False)
    return v
def kb(im, z, cx, cy):
    iw, ih = im.size; s = max(W / iw, H / ih) * z; vw, vh = W / s, H / s
    cxp = min(max(cx * iw, vw / 2), iw - vw / 2); cyp = min(max(cy * ih, vh / 2), ih - vh / 2)
    x0, y0 = cxp - vw / 2, cyp - vh / 2
    return im.transform((W, H), Image.AFFINE, (1 / s, 0, x0, 0, 1 / s, y0), resample=Image.BILINEAR), (s, x0, y0)
def to_screen(M, px, py, size):
    s, x0, y0 = M; return ((px * size[0] - x0) * s, (py * size[1] - y0) * s)
def KB(n, z0, z1, c0, c1, post=None, gray=None):
    """慢推/慢移：线性插值，保证叠化处运动连续"""
    def fn(t, d):
        u = t / d; src = IMG(n)
        im, M = kb(src, lerp(z0, z1, u), lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u))
        if gray: k = gray(t, d); im = Image.blend(im, ImageOps.grayscale(im).convert('RGB'), k) if k > 0 else im
        if post: im = post(im, t, d, M, src.size) or im
        return im
    return fn

# ---------- 文字 ----------
def text_rgba(txt, font, fill, shadow=0, salpha=190, glow=0):
    l, t, r, b = font.getbbox(txt); p = 8 + shadow * 2 + glow * 2
    im = Image.new('RGBA', (r - l + 2 * p, b - t + 2 * p), (0, 0, 0, 0))
    if glow:
        m = Image.new('L', im.size, 0); ImageDraw.Draw(m).text((p - l, p - t + 2), txt, font=font, fill=150, stroke_width=3)
        im.paste((0, 0, 0, 255), (0, 0), m.filter(ImageFilter.GaussianBlur(glow)))
    if shadow:
        m = Image.new('L', im.size, 0); ImageDraw.Draw(m).text((p - l + 1, p - t + 3), txt, font=font, fill=salpha)
        im.paste((0, 0, 0, 255), (0, 0), m.filter(ImageFilter.GaussianBlur(shadow)))
    ImageDraw.Draw(im).text((p - l, p - t), txt, font=font, fill=fill)
    return im
def paste_a(base, rgba, pos, a=1.0):
    if a <= 0.003: return
    m = rgba.getchannel('A')
    if a < 0.997: m = m.point(lambda v, a=a: int(v * a))
    base.paste(rgba.convert('RGB'), (int(round(pos[0])), int(round(pos[1]))), m)
class Pop:
    """逐字浮现的大字：lines=[(text, font, fill, cx, cy, t_start, per_char)]"""
    def __init__(self, lines, shadow=6, back=False):
        self.g = []; self.back = None
        for txt, font, fill, cx, cy, ts, pc in lines:
            x = cx - font.getlength(txt) / 2
            for i, ch in enumerate(txt):
                cw = font.getlength(ch); self.g.append((text_rgba(ch, font, fill, shadow=shadow), x + cw / 2, cy, ts + i * pc)); x += cw
        if back:
            x0 = min(c - im.width / 2 for im, c, _, _ in self.g); x1 = max(c + im.width / 2 for im, c, _, _ in self.g)
            y0 = min(c - im.height / 2 for im, _, c, _ in self.g); y1 = max(c + im.height / 2 for im, _, c, _ in self.g); m = 140
            bm = Image.new('L', (int(x1 - x0) + 2 * m, int(y1 - y0) + 2 * m), 0)
            ImageDraw.Draw(bm).rounded_rectangle((m * .6, m * .6, bm.width - m * .6, bm.height - m * .6), 60, fill=140)
            b = Image.new('RGBA', bm.size, (8, 10, 12, 255)); b.putalpha(bm.filter(ImageFilter.GaussianBlur(46)))
            self.back = (b, x0 - m, y0 - m, min(ti for *_, ti in self.g))
    def draw(self, base, t, alpha=1.0):
        if self.back: b, bx, by, bt = self.back; paste_a(base, b, (bx, by), alpha * clamp((t - bt + 0.2) / 0.5))
        for im, cx, cy, ti in self.g:
            u = clamp((t - ti) / 0.45)
            if u <= 0: continue
            sc = lerp(1.25, 1.0, eout(u)); g = im if u >= 1 else im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
            paste_a(base, g, (cx - g.width / 2, cy - g.height / 2), clamp(u * 1.4) * alpha)

# ---------- 统一介绍卡 / 标签 ----------
def info_rgba(kind, title, meta=None, src=None):
    f1, f2, f3 = SANS(22, 'Medium'), SERIF(40, 'SemiBold'), SANS(24)
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    w = int(max(d0.textlength(x, font=f) for x, f in [(kind, f1), (title, f2), (meta or '', f3), (src or '', f3)]) + 64)
    h = 196 if meta else 122
    im = Image.new('RGBA', (w, h), (16, 20, 24, 178)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 5, h), fill=RED + (255,))
    d.text((30, 22), kind, font=f1, fill=(196, 120, 104, 255)); d.text((30, 52), title, font=f2, fill=(242, 242, 238, 255))
    if meta: d.text((30, 112), meta, font=f3, fill=(210, 213, 210, 255))
    if src: d.text((30, 150), src, font=f3, fill=(160, 166, 166, 255))
    return im
def tag_rgba(t):
    f = SANS(24); w = int(f.getlength(t)) + 28
    im = Image.new('RGBA', (w, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 39), 6, fill=(20, 24, 28, 150)); d.text((w - 14, 20), t, font=f, fill=(225, 228, 226, 255), anchor='rm')
    return im
AITAG_IM = tag_rgba('AI 情景再现')

# ---------- 纸张 ----------
def make_paper():
    base = Image.new('RGB', (W, H), (228, 223, 210))
    lo = Image.effect_noise((W // 16, H // 16), 30).resize((W, H), Image.BICUBIC)
    hi = Image.effect_noise((W, H), 18).filter(ImageFilter.GaussianBlur(0.6))
    base = Image.composite(Image.new('RGB', (W, H), (212, 204, 186)), base, lo.point(lambda v: int(clamp((v - 110) / 120) * 140)))
    base = Image.blend(base, Image.merge('RGB', (hi, hi, hi)), 0.05)
    vg = Image.new('L', (W, H), 0); ImageDraw.Draw(vg).ellipse((-W * .2, -H * .25, W * 1.2, H * 1.25), fill=255)
    return Image.composite(base, Image.new('RGB', (W, H), (180, 172, 156)), vg.filter(ImageFilter.GaussianBlur(160)))
PAPER = make_paper()

# ---------- 时间线 ----------
clips, ovs, subs, SHAKES = [], [], [], []
def clip(t0, t1, fn, tr='fade', td=1.0): clips.append((t0, t1, fn, tr, td))
def X(a, b, fn, tr='fade'):
    """名义区间 [a,b)；默认约 1 秒叠化（前后各 0.5 秒），闪白 0.5 秒"""
    if tr == 'flash': clip(a - 0.25, b + 0.5, fn, 'flash', 0.5)
    elif tr == 'black': clip(a, b + 0.5, fn, 'black', 1.0)
    else: clip(a - 0.5, b + 0.5, fn, 'fade', 1.0)
def ov(t0, t1, draw, fin=0.4, fout=0.4): ovs.append((t0, t1, draw, fin, fout))
def INFO(t0, t1, kind, title, meta=None, src=None, pos=(72, 72)):
    im = info_rgba(kind, title, meta, src)
    def dr(base, t, a):
        u = eout(t / 0.7); paste_a(base, im, (pos[0] - 24 * (1 - u), pos[1]), a)
    ov(t0, t1, dr, 0.5, 0.4)
def AITAG(a, b): ov(a - 0.3, b + 0.3, lambda base, t, al: paste_a(base, AITAG_IM, (W - 56 - AITAG_IM.width, 48), al), 0.6, 0.6)
def POP(t0, t1, pop, fin=0.01, fout=0.5): ov(t0, t1, lambda b, t, a: pop.draw(b, t + t0, a), fin, fout)

# 相片卡（白边、轻旋转、投影），背景为照片自身的模糊压暗冷调版
def make_card(cn, hpx, rot, maxw=None):
    im = IMG('card_' + cn); s = hpx / im.height
    if maxw and im.width * s > maxw: s = maxw / im.width
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    bd, pad = 18, 50; cw, ch = im.width + 2 * bd, im.height + 2 * bd
    c = Image.new('RGBA', (cw + 2 * pad, ch + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('L', c.size, 0); ImageDraw.Draw(sh).rectangle((pad + 12, pad + 18, pad + cw + 12, pad + ch + 18), fill=150)
    c.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
    ImageDraw.Draw(c).rectangle((pad, pad, pad + cw, pad + ch), fill=(233, 234, 230, 255)); c.paste(im, (pad + bd, pad + bd))
    return c.rotate(rot, expand=True, resample=Image.BICUBIC)
def CARDS(bg, cards, z=(1.03, 1.10), c=(.5, .5), post=None, grow=0.035, aim=None):
    """cards: (名, cx, cy, 高, 旋转, 入场时刻[, 最大宽])；卡片从下方飞入，随后极慢推近（grow：推近幅度；aim=(锚点纵向位置, 目标屏幕y)：推近时把锚点移向目标）"""
    def fn(t, d):
        im, M = kb(IMG('bg_' + bg), lerp(z[0], z[1], t / d), c[0], c[1])
        for cd in cards:
            cn, cx, cy, hp, rot, tin = cd[:6]; mw = cd[6] if len(cd) > 6 else None
            if t < tin: continue
            r = DER(('card', cn, hp, rot, mw), lambda: make_card(cn, hp, rot, mw))
            u = eout((t - tin) / 0.8); gk = 1 + grow * (t - tin) / max(0.1, d - tin); sc = lerp(1.10, 1.0, u) * gk
            g = r.resize((int(r.width * sc), int(r.height * sc)), Image.BILINEAR)
            yc = cy
            if aim: ay, ty = aim; yc = lerp(cy + (ay - 0.5) * r.height, ty, ease((t - tin) / max(0.1, d - tin))) - (ay - 0.5) * g.height
            paste_a(im, g, (cx - g.width / 2, yc + 240 * (1 - u) - g.height / 2), clamp((t - tin) / 0.3))
        if post: post(im, t, d)
        return im
    return fn

# ---------- 字幕 ----------
SB = yaml.safe_load(open(ROOT + 'storyboard.yaml', encoding='utf-8'))
Q = {r[0]: r[1] for r in csv.reader(open(ROOT + 'quotes_src.tsv', encoding='utf-8'), delimiter='\t')}
QS = {r[0]: r[2] for r in csv.reader(open(ROOT + 'quotes_src.tsv', encoding='utf-8'), delimiter='\t')}
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
    res = []
    for c in out:
        s = c
        while s and s[-1] in '，。；、—': s = s[:-1]
        res.append(s or c)
    return res
FS, FA = SERIF(44, 'Medium'), SERIF(26)
SUBLOG = []
def SUB(t0, kind, txt=None):
    q = kind != 'vo'; txt = txt or Q[kind]; dur = nchar(txt) / (QR if q else VR)
    cs = chunks(txt); tot = sum(len(c) for c in cs); u = t0
    attr = (text_rgba('——鲁迅' + QS[kind], FA, (214, 216, 214, 255), shadow=3, salpha=230, glow=6), text_rgba('——鲁迅' + QS[kind], FA, (96, 90, 82, 255))) if q else None
    for c in cs:
        dd = dur * len(c) / tot
        subs.append((u, u + dd - 0.08, (text_rgba(c, FS, (248, 240, 222, 255) if q else (244, 244, 240, 255), shadow=3, salpha=230, glow=8),
                                        text_rgba(c, FS, (40, 36, 32, 255))), attr))
        SUBLOG.append((round(u, 2), round(u + dd, 2), c)); u += dd
    return t0 + dur
S06 = vo_of('S0-06'); S06a, S06b = S06.split('。', 1)[0] + '。', S06.split('。', 1)[1]
SUB(7.2, 'vo', vo_of('S0-05')); SUB(19.8, 'vo', S06a); SUB(29.2, 'vo', vo_of('S0-02')); SUB(34.0, 'Q71'); SUB(38.2, 'Q01')
SUB(42.6, 'vo', vo_of('S0-04')); SUB(58.2, 'vo', S06b)
T = 68.0
for sid in ['S1-01', 'S1-02', 'S1-03', 'S1-04', 'S1-05', 'S1-06', 'S1-07']:
    s = SHOT[sid]; t = T + 0.4
    for a in s.get('audio', []):
        if 'vo' in a: kind, txt = 'vo', a['vo']
        elif 'q' in a: kind, txt = a['q'], Q[a['q']]
        else: continue
        if (sid, kind) == ('S1-06', 'vo'): t += nchar(txt) / VR + GAP; continue   # 由“第一次转身”字卡呈现
        t = SUB(t, kind, txt) + GAP
    T += s['dur']
TOTAL_MAIN = 179.5; CRED = 7.0; TOTAL = TOTAL_MAIN + CRED

# ================= 序章 =================
# P1 0–7 冷开场：《死》手稿（全集彩插）暗场慢移 + 大字
def p1_fn(t, d):
    im, _ = kb(IMG('bg_qj2028'), 1.04 + 0.04 * t / d, .5, .5)
    pg = DER('p1page', lambda: ImageOps.contain(IMG('card_qj2028'), (900, 1240), Image.LANCZOS).convert('RGBA'))
    pg2 = pg.copy(); pg2.putalpha(150)
    paste_a(im, pg2, (1080 - 18 * t, -60 - 10 * t), 0.75); return im
X(0, 7, p1_fn, 'black')
pre = text_rgba('1936年9月5日，鲁迅在《死》里写下遗嘱：', SERIF(38), (230, 230, 226, 255), shadow=6)
ov(0.4, 6.8, lambda b, t, a: paste_a(b, pre, (110, 300), a * clamp(t / 0.6)), 0.01, 0.5)
F1, F2 = SERIF(150, 'Bold'), SERIF(66, 'SemiBold')
POP(1.0, 6.8, Pop([('忘记我', F1, CREAM, 430, 500, 1.0, 0.2)]))
POP(2.3, 6.8, Pop([('管自己生活。', F2, CREAM, 360, 680, 2.3, 0.1)]))
POP(3.8, 6.8, Pop([('——倘不，那就真是胡涂虫。', F2, (228, 200, 170), 540, 790, 3.8, 0.08)]))
# P2/P3 出殡：沙飞摄《鲁迅葬仪》、《新中华》丧仪照
X(7, 11.6, CARDS('w0201', [('w0201', 1100, 470, 620, -1.6, 0.25)]))
INFO(7.7, 11.6, '史料 · 照片', '鲁迅葬仪', '1936年10月22日 · 上海', '摄影：沙飞')
X(11.6, 16, CARDS('w0202', [('w0202', 1110, 470, 640, 1.4, 0.25)]))
INFO(12.1, 15.9, '史料 · 期刊', '《鲁迅先生的丧仪》', '1936年10月 · 上海', '出处：《新中华》1936年第4卷第21期')
# P4 “民族魂”白旗字卡
def make_flag():
    y, x = np.mgrid[0:H + 80, 0:W + 140].astype(np.float32)
    fold = 0.06 * np.sin(x / 210 + 0.6 * np.sin(y / 330)) + 0.035 * np.sin(x / 67 + y / 400)
    a = np.clip(0.80 + fold + np.random.default_rng(5).normal(0, 0.012, x.shape), 0, 1)
    rgb = np.stack([a * 232, a * 232, a * 226], -1).astype(np.uint8); im = Image.fromarray(rgb)
    k = text_rgba('民族魂', SERIF(260, 'Black'), (26, 24, 24, 255)).filter(ImageFilter.GaussianBlur(1.2))
    paste_a(im, k, (im.width / 2 - k.width / 2, im.height / 2 - k.height / 2 - 40), 0.93)
    return im
FLAG = make_flag()
FLAGT = text_rgba('覆在灵柩上的白旗　沈钧儒书', SANS(30), (70, 70, 70, 255))
def flag_fn(t, d):
    im, _ = kb(FLAG, 1.0 + 0.06 * t / d, .5, .5); paste_a(im, FLAGT, (W / 2 - FLAGT.width / 2, 800), clamp((t - 1.0) / 0.8)); return im
X(16, 19.6, flag_fn, 'flash'); SHAKES.append(16.3)
# P5 九十年：上海鲁迅墓（实拍）+ 年份
X(19.6, 24, KB('m_tomb', 1.0, 1.12, (.5, .5), (.5, .42)))
INFO(20.0, 23.8, '今日 · 实拍', '上海 · 鲁迅墓')
def counter(y0, y1, pos, font, dur):
    def dr(b, t, a):
        im = text_rgba(str(round(lerp(y0, y1, ease(t / dur)))), font, CREAM, shadow=10)
        paste_a(b, im, (pos[0] - im.width / 2, pos[1] - im.height / 2), a)
    return dr
ov(20.2, 23.9, counter(1936, 2026, (420, 520), SERIF(200, 'Bold'), 2.6), 0.4, 0.3)
# P6 片名
TM = Image.open(S3 + 'title_mask.png').convert('L'); TM = TM.resize((1100, round(TM.height * 1100 / TM.width)), Image.LANCZOS)
TINK = Image.new('RGBA', TM.size, INK + (255,)); TINK.putalpha(TM)
tsub = text_rgba('鲁迅逝世九十周年　1936—2026', SERIF(44), (88, 80, 72, 255))
def title_fn(t, d):
    im, _ = kb(PAPER, 1.0 + 0.03 * t / d, .5, .5); u = eout(t / 0.4); sc = lerp(1.25, 1.0, u) * (1 + 0.025 * t / d)
    g = TINK.resize((int(TINK.width * sc), int(TINK.height * sc)), Image.BILINEAR)
    paste_a(im, g, (W / 2 - g.width / 2, H / 2 - g.height / 2 - 50), clamp(t / 0.15))
    paste_a(im, tsub, (W / 2 - tsub.width / 2, 820), clamp((t - 1.2) / 0.8)); return im
X(24, 29, title_fn, 'flash'); SHAKES.append(24.35)
# P7 遗嘱：大陆新村9号（实拍）
X(29, 33.8, KB('m_house', 1.0, 1.1, (.5, .5), (.46, .46)))
INFO(29.4, 33.7, '今日 · 实拍', '上海 · 大陆新村9号')
# P8 《死》手稿（七条遗嘱页）
X(33.8, 38, CARDS('w01', [('w01', 1160, 470, 780, -1.6, 0.25)]))
INFO(34.3, 37.9, '史料 · 手稿', '《死》手稿', '1936年9月5日 · 上海', '出处：上观新闻 2018年展览报道配图')
# P9 竖排七条遗嘱，高亮第二、三条
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
VFS, CELL, CW, TOP = 42, 50, 78, 100
cols, xx = [], 0
for i, it in enumerate(ITEMS):
    for c in it: cols.append((i, c, xx)); xx += CW
    xx += 24
X0 = W / 2 + (xx - 24) / 2 - CW
VL = [(i, vcol(c, SERIF(VFS, 'SemiBold'), CELL, INK + (255,)), vcol(c, SERIF(VFS, 'SemiBold'), CELL, (160, 50, 36, 255)), X0 - x) for i, c, x in cols]
def will_fn(t, d):
    im, _ = kb(PAPER, 1.0 + 0.05 * t / d, .5, .5)
    for i, ink, red, x in VL:
        a = 0.2 + 0.8 * (0.75 if i == 1 else clamp((t - 0.3) / 0.6) if i == 2 else 0)
        paste_a(im, red if (i == 2 and t > 0.3) else ink, (x - (ink.width - CW) / 2, TOP), a * clamp(t / 0.5))
    return im
X(38, 42.4, will_fn)
# P10 第四十四天：日历翻页（背景为故居卧室虚化）
WK = '一二三四五六日'
def cal_card(day):
    dt = datetime.date(1936, 9, 5) + datetime.timedelta(days=day)
    c = Image.new('RGBA', (420, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rectangle((0, 0, 419, 559), fill=(236, 233, 224, 255)); d.rectangle((0, 0, 419, 120), fill=(140, 52, 42, 255))
    d.text((210, 62), ('九月' if dt.month == 9 else '十月'), font=SERIF(60, 'Bold'), fill=(240, 232, 220), anchor='mm')
    d.text((210, 290), str(dt.day), font=SERIF(220, 'Black'), fill=(30, 28, 26), anchor='mm')
    d.text((210, 455), '星期' + WK[dt.weekday()], font=SERIF(42), fill=(70, 66, 60), anchor='mm')
    d.text((210, 515), '民国二十五年', font=SERIF(32), fill=(120, 114, 104), anchor='mm')
    for k in range(0, 420, 15): d.ellipse((k + 4, 6, k + 11, 13), fill=(90, 30, 24, 255))
    return c
CAL = [None] * 45
def cal_fn(t, d):
    im, _ = kb(IMG('bg_m_bed'), 1.05 + 0.04 * t / d, .5, .5)
    v = ease((t - 0.6) / 3.0) * 44; k = min(44, int(v)); fr = v - k if k < 44 else 0
    for kk in (k, min(44, k + 1)):
        if CAL[kk] is None: CAL[kk] = cal_card(kk)
    cx, cy = W / 2 - 160, H / 2 - 40
    if k < 44: paste_a(im, CAL[k + 1], (cx - 210, cy - 280))
    top = CAL[k] if fr < 0.02 else CAL[k].rotate(-10 * fr, expand=True, resample=Image.BILINEAR)
    paste_a(im, top, (cx - top.width / 2 + 60 * fr, cy - top.height / 2 - 520 * fr * fr), 1 - fr)
    return im
X(42.4, 47, cal_fn)
nd = text_rgba('第 44 天', SERIF(72, 'Bold'), CREAM, shadow=8)
ov(45.6, 47.4, lambda b, t, a: paste_a(b, nd, (W / 2 + 160, H / 2 - 90), a), 0.4, 0.4)
# P11 故居卧室（今貌）  P12 1936年10月留影 → 缓推到眼睛
X(47, 51.8, KB('m_bed', 1.04, 1.16, (.5, .5), (.42, .5)))
INFO(47.4, 51.7, '今日 · 实拍', '上海鲁迅故居 · 二楼卧室')
X(51.8, 58, CARDS('hz231', [('hz231', 1140, 450, 700, -1.6, 0.2)], grow=0.45, aim=(0.22, 420)))   # 极慢推近到眼睛
INFO(52.2, 56.4, '史料 · 照片', '1936年10月的鲁迅', '上海', '出处：林贤治《鲁迅画传》')
# P13 “先生：”信笺字卡
LET = text_rgba('先生：', SERIF(92, 'SemiBold'), INK + (255,))
LDATE = text_rgba('二〇二六年十月十九日', SERIF(36), (90, 84, 76, 255))
def letter_fn(t, d):
    def mk():
        im = PAPER.copy(); dd = ImageDraw.Draw(im); x0, y0, x1, y1 = 420, 150, 1500, 930
        sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rectangle((x0 + 10, y0 + 16, x1 + 10, y1 + 16), fill=120)
        im.paste((60, 56, 50), (0, 0), sh.filter(ImageFilter.GaussianBlur(16)))
        dd.rectangle((x0, y0, x1, y1), fill=(238, 235, 226))
        for k in range(9): yy = y0 + 150 + k * 80; dd.line((x0 + 70, yy, x1 - 70, yy), fill=(196, 150, 140), width=2)
        return im
    im, _ = kb(DER('letter', mk), 1.0 + 0.06 * t / d, .5, .42)
    u = clamp((t - 0.5) / 1.4); w = max(1, int(LET.width * u))
    paste_a(im, LET.crop((0, 0, w, LET.height)), (520, 205), 1.0)
    paste_a(im, LDATE, (1360 - LDATE.width, 830), clamp((t - 2.2) / 0.8)); return im
X(58, 63, letter_fn)
# P14 时光倒流：绍兴水巷（实拍）逐渐褪成黑白 + 年份 2026→1881
X(63, 68, KB('m_water', 1.16, 1.0, (.5, .5), (.5, .5), gray=lambda t, d: ease((t - 1.0) / (d - 1.5)) * 0.9))
ov(63.4, 68.2, counter(2026, 1881, (W / 2, H / 2 - 20), SERIF(230, 'Bold'), 3.6), 0.4, 0.3)

# ================= 第一章 =================
# C1 章节卡 + 绍兴城远景
def dim(k0, k1, t0=0.0, t1=1.0):
    def post(im, t, d, M, size):
        k = lerp(k0, k1, ease((t - t0) / max(0.01, t1 - t0))); return Image.blend(im, Image.new('RGB', (W, H), (6, 8, 10)), k) if k > 0 else im
    return post
X(68, 74, KB('card_hz4', 1.0, 1.14, (.5, .45), (.5, .55), post=dim(0.55, 0.0, 3.4, 4.4)), 'flash')
POP(68.4, 71.8, Pop([('一｜绍兴', SERIF(132, 'Bold'), CREAM, W / 2, 450, 68.4, 0.12), ('1881—1898　坠入困顿', SERIF(50), (232, 228, 218), W / 2, 600, 68.9, 0.05)], back=True))
INFO(72.0, 74.4, '史料 · 照片', '绍兴城远景', '浙江绍兴 · 旧影', '出处：林贤治《鲁迅画传》')
X(74, 78.6, KB('m_taimen', 1.0, 1.12, (.42, .5), (.4, .46)))
INFO(74.4, 78.5, '今日 · 实拍', '绍兴 · 周家新台门')
X(78.6, 82.8, CARDS('hz6', [('hz6', 1140, 470, 760, -1.6, 0.2)]))
INFO(79.0, 82.7, '史料 · 照片', '周家老宅', '浙江绍兴 · 东昌坊口', '出处：林贤治《鲁迅画传》')
X(82.8, 85.2, CARDS('hz9', [('hz9', 1140, 470, 720, 1.4, 0.2)]))
INFO(83.2, 85.2, '史料 · 照片', '祖父周福清', '翰林 · 京官', '出处：林贤治《鲁迅画传》')
X(85.2, 87.6, CARDS('hz7', [('hz7', 1100, 480, 420, -1.2, 0.2, 1240)]))
INFO(85.6, 87.6, '史料 · 实物', '周家“翰林”匾', '浙江绍兴', '出处：林贤治《鲁迅画传》')
# C5 1893 科场案：府狱铁锁（AI）
X(87.6, 92, KB('a01', 1.16, 1.02, (.5, .45), (.5, .45))); AITAG(87.6, 92); SHAKES.append(88.4)
X(92, 96.6, CARDS('hz10f', [('hz10f', 1140, 470, 700, 1.6, 0.2)]))
INFO(92.4, 96.5, '史料 · 照片', '父亲周伯宜', '1894年冬病倒 · 1896年病逝', '出处：林贤治《鲁迅画传》')
X(96.6, 102, KB('a03', 1.02, 1.14, (.55, .5), (.6, .5))); AITAG(96.6, 102)
# 质铺和药店（引文按分句对齐画面）
def at(sub):
    for a, b, c in SUBLOG:
        if sub in c: return a
    raise KeyError(sub)
tQ2, tQ4 = at('几乎是每天'), at('药店的柜台')
tQ5 = at('质铺的是比我高一倍')
X(102, tQ2 + 0.4, KB('a04', 1.0, 1.12, (.4, .5), (.36, .52))); AITAG(102, tQ2 + 0.4)
X(tQ2 + 0.4, tQ4 - 1.5, KB('a06', 1.04, 1.16, (.45, .5), (.52, .55))); AITAG(tQ2 + 0.4, tQ4 - 1.5)
X(tQ4 - 1.5, tQ5 - 0.3, KB('a07', 1.02, 1.12, (.4, .5), (.45, .55))); AITAG(tQ4 - 1.5, tQ5 - 0.3)
X(tQ5 - 0.3, 123, KB('a05', 1.04, 1.18, (.55, .7), (.62, .4))); AITAG(tQ5 - 0.3, 123)
# 药引：缓摇，逐个标注
HERB = [('芦根', .13, .62, 230), ('甘蔗', .39, .51, 150), ('蟋蟀', .465, .50, 150), ('平地木', .585, .47, 150)]
HL = {k: text_rgba(k, SERIF(40, 'SemiBold'), CREAM, shadow=6) for k, *_ in HERB}
def at_char(k):
    for a, b, c in SUBLOG:
        if k in c: return a + (b - a) * c.index(k) / len(c)
    raise KeyError(k)
HT = {k: at_char(k) + 0.2 for k, *_ in HERB}
def herb_post(im, t, d, M, size):
    dd = ImageDraw.Draw(im)
    for k, px, py, off in HERB:
        a = clamp((t + 122.5 - HT[k]) / 0.5)
        if a <= 0: continue
        x, y = to_screen(M, px, py, size); y0 = y - off
        dd.line((x, y0 + 30, x, y0 + 30 + 70 * a), fill=(236, 232, 222), width=2)
        paste_a(im, HL[k], (x - HL[k].width / 2, y0 - HL[k].height / 2 - 8), a)
X(123, 131.6, KB('a08', 1.12, 1.12, (.36, .52), (.58, .52), post=herb_post)); AITAG(123, 131.6)
X(131.6, 138, KB('a09', 1.04, 1.16, (.6, .55), (.7, .6), post=dim(0.0, 0.82, 4.4, 6.2))); AITAG(131.6, 137.6)
tR = at('大概可以看见')
X(138, tR - 1.0, KB('a10', 1.0, 1.1, (.5, .5), (.5, .45))); AITAG(138, tR - 1.0)
X(tR - 1.0, 149.4, KB('a11', 1.0, 1.14, (.5, .4), (.55, .35))); AITAG(tR - 1.0, 149.4)
# 转身卡
X(149.4, 155, KB('bg_a05', 1.0, 1.08, (.5, .5), (.5, .5)), 'flash'); SHAKES.append(149.75)
POP(149.6, 155.2, Pop([('第一次转身', SERIF(46), (226, 196, 186), W / 2, 380, 149.6, 0.08), ('在柜台前，他看见了人心', SERIF(86, 'Bold'), CREAM, W / 2, 510, 150.0, 0.1)]))
# 离家
X(155, 160, CARDS('hz11', [('hz11', 1110, 480, 560, -1.4, 0.2, 1150)]))
INFO(155.4, 159.9, '史料 · 书影', '维新派报刊', '1890年代末', '出处：林贤治《鲁迅画传》')
X(160, 166.2, KB('a12', 1.0, 1.14, (.5, .5), (.47, .45))); AITAG(160, 166.2)
X(166.2, 170.2, CARDS('hz10m', [('hz10m', 1140, 470, 700, -1.6, 0.2)]))
INFO(166.6, 170.1, '史料 · 照片', '母亲鲁瑞', '1858—1943', '出处：林贤治《鲁迅画传》')
X(170.2, 174.6, KB('a13', 1.02, 1.14, (.55, .5), (.6, .5))); AITAG(170.2, 174.6)
X(174.6, 179.5, CARDS('art05', [('art05', 1140, 470, 800, 1.2, 0.2)]))
INFO(175.0, 179.4, '版画 · 木刻', '赵延年《离家》', '鲁迅作品木刻插图', '出处：赵延年木刻画册')
# 片尾
CR = [('样片 v3｜序章＋第一章（B站母版 00:00—02:58，无配音）', 40, 'SemiBold', INK),
      ('', 0, '', None),
      ('AI 情景再现：第一章少年时期部分镜头（画面右上角已标注）', 28, 'Regular', (70, 64, 58)),
      ('历史照片：林贤治《鲁迅画传》；《鲁迅全集》2005年版文前彩插', 28, 'Regular', (70, 64, 58)),
      ('葬礼照片：沙飞摄《鲁迅葬仪》；《新中华》1936年第4卷第21期（据中国作家网蔡涛文转引）', 28, 'Regular', (70, 64, 58)),
      ('《死》手稿：上观新闻2018年展览报道配图　木刻：赵延年《离家》', 28, 'Regular', (70, 64, 58)),
      ('实拍：上海鲁迅墓 ScareCriterion12（CC BY-SA 4.0）　大陆新村9号 Zhou Guanhuai（CC BY-SA 4.0）', 28, 'Regular', (70, 64, 58)),
      ('周家新台门 Gisling（CC BY-SA 3.0）　绍兴水巷 Taco Witte（CC BY 2.0）　故居卧室：上海市文化和旅游局', 28, 'Regular', (70, 64, 58)),
      ('鲁迅原文均据《鲁迅全集》2005年版', 28, 'Regular', (70, 64, 58))]
CRS = [text_rgba(c, SERIF(s, w), f + (255,)) if c else None for c, s, w, f in CR]
def cred(t, d):
    im = PAPER.copy(); y = 250
    for i, c in enumerate(CRS):
        if c: paste_a(im, c, (W / 2 - c.width / 2, y), clamp((t - 0.3 - i * 0.12) / 0.8))
        y += 80 if i == 0 else (30 if c is None else 58)
    return im
X(TOTAL_MAIN, TOTAL, cred)
WM = text_rgba('样片 v3 · 无配音', SANS(22, 'Light'), (255, 255, 255, 255), shadow=2)

# ---------- 浮尘（淡） ----------
rnd = random.Random(11)
DUST = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(-12, 12), rnd.uniform(-18, -5), rnd.choice([2, 3, 4, 6]), rnd.uniform(0, 6.28)) for _ in range(40)]
SPR = {}
for r in (2, 3, 4, 6):
    m = Image.new('L', (r * 6, r * 6), 0); ImageDraw.Draw(m).ellipse((r * 2, r * 2, r * 4, r * 4), fill=255); m = m.filter(ImageFilter.GaussianBlur(r * 0.8))
    s = Image.new('RGBA', m.size, (236, 236, 230, 255)); s.putalpha(m); SPR[r] = s
DUSTR = [(0, 7), (33.8, 38), (47, 58), (107, 123), (131.6, 137), (170.2, 174.6)]
def dust(base, T):
    a = max([clamp((T - a0) / 0.8) * clamp((a1 - T) / 0.8) for a0, a1 in DUSTR] + [0])
    if a <= 0: return
    for x0, y0, vx, vy, r, ph in DUST:
        paste_a(base, SPR[r], ((x0 + vx * T) % W, (y0 + vy * T) % H), a * (0.2 + 0.2 * math.sin(T * 1.7 + ph)))

# ---------- 胶片质感（逐帧：暗角 + 颗粒） ----------
_yy, _xx = np.mgrid[0:H, 0:W]; _d = np.sqrt(((_xx - W / 2) / (W / 2)) ** 2 + ((_yy - H / 2) / (H / 2)) ** 2)
VIG = Image.fromarray((255 * (1 - 0.35 * np.clip(_d - 0.55, 0, 1) ** 1.6)).astype(np.uint8)).convert('RGB')
_g = np.random.default_rng(7)
GRAIN = [Image.fromarray(np.clip(128 + _g.normal(0, 5.2, (H, W)), 0, 255).astype(np.uint8)).convert('RGB') for _ in range(6)]
del _yy, _xx, _d

# ---------- 合成 ----------
PAPER_T = [(16, 19.6), (24, 29), (38, 42.4), (58, 63)]   # 纸面/白旗镜头：字幕改用墨色
SUBGRAD = Image.new('RGBA', (W, 300), (0, 0, 0, 0)); SUBGRAD.putalpha(Image.linear_gradient('L').resize((W, 300)).point(lambda v: int((v / 255) ** 1.6 * 150)))
WHITE = Image.new('RGB', (W, H), (250, 250, 248)); BLACK = Image.new('RGB', (W, H), (0, 0, 0))
SHK = [(16, -10), (-12, 8), (8, -5), (-5, 3), (2, -1), (0, 0)]
def frame(T):
    base = BLACK
    for t0, t1, fn, tr, td in clips:
        if not (t0 <= T < t1): continue
        img = fn(T - t0, t1 - t0)
        if tr == 'cut' or td <= 0 or T - t0 >= td: base = img; continue
        a = (T - t0) / td
        if tr in ('fade', 'black'): base = Image.blend(base, img, ease(a))
        elif tr == 'flash': base = Image.blend(Image.blend(base, img, ease(a)), WHITE, 0.9 * (1 - abs(2 * a - 1)))
    if base is BLACK: base = BLACK.copy()
    dust(base, T)
    for ts in SHAKES:
        if ts <= T < ts + len(SHK) / FPS:
            dx, dy = SHK[int((T - ts) * FPS)]; s = 1.025
            base = base.transform((W, H), Image.AFFINE, (1 / s, 0, W * (1 - 1 / s) / 2 - dx / s, 0, 1 / s, H * (1 - 1 / s) / 2 - dy / s), resample=Image.BILINEAR)
    base = ImageChops.multiply(base, VIG)
    base = ImageChops.add(base, GRAIN[int(T * FPS) % len(GRAIN)], 1.0, -128)
    for t0, t1, dr, fin, fout in ovs:
        if t0 <= T < t1: dr(base, T - t0, min(clamp((T - t0) / fin), clamp((t1 - T) / fout)))
    pm = any(a <= T < b for a, b in PAPER_T)
    sa = max([min(clamp((T - t0 + 0.4) / 0.4), clamp((t1 - T + 0.4) / 0.4)) for t0, t1, *_ in subs] + [0])
    if sa > 0 and not pm: paste_a(base, SUBGRAD, (0, H - SUBGRAD.height), sa)
    for t0, t1, ims, attr in subs:
        if t0 <= T < t1:
            a = min(clamp((T - t0) / 0.15), clamp((t1 - T) / 0.15)); im = ims[pm]
            paste_a(base, im, (W / 2 - im.width / 2, H - 120 - im.height / 2), a)
            if attr: paste_a(base, attr[pm], (W / 2 - attr[pm].width / 2, H - 62 - attr[pm].height / 2), a)
    if T < TOTAL_MAIN: paste_a(base, WM, (W - 36 - WM.width, H - 40 - WM.height), 0.45)
    return base

if __name__ == '__main__':
    if '--plan' in sys.argv:
        for s in SUBLOG: print(*s)
        for c in clips: print(round(c[0], 2), round(c[1], 2), c[3])
        sys.exit(0)
    if '--stills' in sys.argv:
        for tt in [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]:
            frame(tt).save(f'/tmp/v3_{tt:06.1f}.jpg', quality=85)
        sys.exit(0)
    k, n = map(int, sys.argv[sys.argv.index('--part') + 1].split('/')); out = sys.argv[sys.argv.index('--part') + 2]
    N = int(round(TOTAL * FPS)); a, b = N * k // n, N * (k + 1) // n
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(frame(f / FPS).tobytes())
        if (f - a) % 250 == 0: print(k, f - a, '/', b - a, flush=True)
    p.stdin.close(); p.wait(); print('done', k)

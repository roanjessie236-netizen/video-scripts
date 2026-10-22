import math, sys, re, csv, random, datetime, subprocess, yaml
from collections import OrderedDict
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops
W, H, FPS = 1920, 1080, 25
ROOT = '/data/luxun90/'; S3 = ROOT + 'preview/src5/'   # 第五章素材目录（prep_ch5.py 输出；变量名沿用）
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
Q = {r[0]: r[1] for r in csv.reader(open(ROOT + 'quotes_src.tsv', encoding='utf-8'), delimiter='\t')}
QS = {r[0]: r[2] for r in csv.reader(open(ROOT + 'quotes_src.tsv', encoding='utf-8'), delimiter='\t')}
# r2 新增引文（已据《鲁迅全集》2005年版核对；v2.6 分镜时并入 quotes_src.tsv / quotes_checked.tsv）
Q.update({'Q94': '飞了一个小圈子，便又回来停在原地点', 'Q95': '我已经躬行我先前所憎恶，所反对的一切，拒斥我先前所崇仰，所主张的一切了。'})
QS.update({'Q94': '《在酒楼上》', 'Q95': '《孤独者》'})
# 第五章新增（已据《鲁迅全集》2005年版核对）：Q96 《而已集·题辞》（1926年10月14日夜作，1928年取作《而已集》题辞）；Q97 《写在〈坟〉后面》，比 Q60 多引前半句
Q.update({'Q96': '这半年我又看见了许多血和许多泪，然而我只有杂感而已。', 'Q97': '应该和光阴偕逝，逐渐消亡，至多不过是桥梁中的一木一石'})
QS.update({'Q96': '《而已集·题辞》', 'Q97': '《写在〈坟〉后面》'})
VR, QR, GAP, LEAD, TAIL = 4.2, 3.3, 0.6, 0.4, 0.5   # 旁白 4.2 字/秒，原文 3.3 字/秒；每个镜头在最后一句结束后 0.5 秒切走
def nchar(txt): return len(re.sub(r'[，。；：！？、—“”（）\s]', '', txt))
def chunks(txt, n=18):
    parts = re.findall(r'[^，。；：！？、—]+[，。；：！？、]*(?:——)?|——', txt); out, cur = [], ''
    for i in range(1, len(parts)):   # 后引号归前一句
        if parts[i].startswith('”'): parts[i - 1] += '”'; parts[i] = parts[i][1:]
    i = 0
    while i < len(parts) - 1:   # 极短分句（如“二，”）并入下一句
        if nchar(parts[i]) <= 1: parts[i + 1] = parts[i] + parts[i + 1]; parts.pop(i)
        else: i += 1
    for p in parts:
        if cur and (len(cur) + len(p) > n or (p.startswith('“') and cur.endswith('。'))): out.append(cur); cur = p
        else: cur += p
    if cur: out.append(cur)
    if len(out) >= 2 and nchar(out[-1]) <= 2 and len(out[-2]) + len(out[-1]) <= 24: _x = out.pop(); out[-1] += _x   # 句尾“他说——”之类并入上一行
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

# 样片 v3：第三、四章 北京（1912—1926 从沉默到呐喊；彷徨与反抗绝望）。框架与 render_ch2.py 相同（相片卡、介绍卡、字幕、调色、颗粒）
# 真实素材为主；补树书屋、抄碑、写作、同人群像用电视剧《觉醒年代》（2021）片段（右上角标注）；铁屋子、《过客》为 AI 意象（右上角标注）。1920x1080/25fps，无声
# 先运行 prep_v3.py、prep_ch34.py（--cards --film）生成 preview/src3/。用法：python3 render_ch34.py [--plan] [--stills 1,2,3] [--part k/n out.mp4]（k 从 0 开始）
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
SHOT = {s['id']: s for ch in SB['chapters'] for s in ch['shots']}
def vo_of(sid): return [a['vo'] for a in SHOT[sid]['audio'] if 'vo' in a][0]
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
# ---------- 第三、四章字幕（时序与 storyboard 一致；本章从 0 秒起算，B站母版对应 +346.5 秒） ----------
OFF = 346.5
T = 0.0; TURN = {}
for sid in ['S3-01', 'S3-02', 'S3-03', 'S3-04', 'S3-05', 'S3-06', 'S4-01', 'S4-02', 'S4-03', 'S4-04', 'S4-05', 'S4-06', 'S4-07', 'S4-08']:
    s = SHOT[sid]; t = T + 0.4
    for a in s.get('audio', []):
        if 'sil' in a: t += a['sil']; continue
        if 'vo' in a: kind, txt = 'vo', a['vo']
        elif 'q' in a: kind, txt = a['q'], Q[a['q']]
        else: continue                       # 音效在无声样片中略去
        if kind == 'vo' and '转身' in txt and '这是' in txt:   # “这是他的第N次转身……”由转身字卡呈现
            a1, a2 = txt.split('这是', 1)
            if a1: t = SUB(t, 'vo', a1) + GAP
            TURN[sid] = t; t += nchar('这是' + a2) / VR + GAP; continue
        t = SUB(t, kind, txt) + GAP
    T += s['dur']
assert abs(T - 263) < 0.01, T
TURN3, TURN4 = TURN['S3-06'], TURN['S4-06']
TOTAL_MAIN = 263.0; CRED = 7.0; TOTAL = TOTAL_MAIN + CRED
def at(sub):
    for a, b, c in SUBLOG:
        if sub in c: return a
    raise KeyError(sub)
def at_char(k):
    for a, b, c in SUBLOG:
        if k in c: return a + (b - a) * c.index(k) / len(c)
    raise KeyError(k)
def dim(k0, k1, t0=0.0, t1=1.0):
    def post(im, t, d, M, size):
        k = lerp(k0, k1, ease((t - t0) / max(0.01, t1 - t0))); return Image.blend(im, Image.new('RGB', (W, H), (6, 8, 10)), k) if k > 0 else im
    return post
SRC_HZ, SRC_QJ, SRC_WC = '出处：林贤治《鲁迅画传》', '出处：《鲁迅全集》2005年版', '出处：Wikimedia Commons'
DARK = Image.new('RGB', (W, H), (6, 8, 10))
HIDE = []   # 不显示底部字幕的区间（改为画面中央大字）

# ---------- 影视剧片段（《觉醒年代》，prep_ch34.py 已抽成 25fps 调色帧） ----------
import os
FILMN = {n: len(os.listdir(S3 + n)) for n in ('f_rub', 'f_hall', 'f_write', 'f_group')}
def FILM(n, z0=1.0, z1=1.04, c0=(.5, .5), c1=(.5, .5), speed=1.0, gray=None, post=None):
    def fn(t, d):
        k = min(FILMN[n] - 1, int(t * FPS * speed)); u = t / d
        src = Image.open(f'{S3}{n}/{k:04d}.jpg').convert('RGB')
        im = kb(src, lerp(z0, z1, u), lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u))[0]
        if gray: g = gray(t, d); im = Image.blend(im, ImageOps.grayscale(im).convert('RGB'), g) if g > 0 else im
        if post: im = post(im, t, d, None, src.size) or im
        return im
    return fn
FILMTAG_IM = tag_rgba('影视剧《觉醒年代》')
def FILMTAG(a, b): ov(a - 0.3, b + 0.3, lambda base, t, al: paste_a(base, FILMTAG_IM, (W - 56 - FILMTAG_IM.width, 48), al), 0.6, 0.6)
FILM_NOTE = '2021年 · 曹磊饰鲁迅　非历史影像'

# ================= 第三章　北京（1912—1922）从沉默到呐喊 =================
# S3-01 章节卡 → 蔡元培 → 绍兴县馆
t_sx = at_char('住进') - 0.3
X(0, t_sx, CARDS('hz54', [('hz54', 1140, 490, 660, -1.4, 3.3)]), 'flash')
POP(0.3, 3.6, Pop([('三｜北京', SERIF(120, 'Bold'), CREAM, W / 2, 450, 0.3, 0.09), ('1912—1922　从沉默到呐喊', SERIF(50), (232, 228, 218), W / 2, 600, 0.9, 0.05)], back=True))
INFO(3.7, t_sx - 0.1, '史料 · 照片', '蔡元培', '1912年任教育总长 · 邀鲁迅入教育部', SRC_HZ)
X(t_sx, 14, CARDS('hz56', [('hz56', 1140, 500, 820, 1.2, 0.2)]))
INFO(t_sx + 0.4, 13.9, '史料 · 照片', '绍兴县馆', '北京宣武门外南半截胡同 · 1912—1919年寓居', SRC_HZ)
# S3-02 袁世凯复辟 → 白天上班（京师图书馆）→ 夜里抄古碑（《觉醒年代》）→ 补树书屋 → 造像拓片
t_bt = at_char('他白天上班') - 0.3; t_cb = t_bt + 3.4; t_bs = t_cb + 3.8; t_tp = 28.2
X(14, t_bt, CARDS('hz55', [('hz55', 1140, 490, 780, -1.2, 0.2)]))
INFO(14.4, t_bt - 0.1, '史料 · 照片', '袁世凯', '1915年底复辟帝制 · 次年取消', SRC_HZ)
X(t_bt, t_cb, CARDS('hz57a', [('hz57a', 1150, 500, 700, 1.0, 0.2, 1500)]))
INFO(t_bt + 0.4, t_cb - 0.1, '史料 · 照片', '京师图书馆开馆纪念', '1917年1月 · 第二排左五为鲁迅（时任教育部佥事）', SRC_HZ)
X(t_cb, t_bs, FILM('f_rub', 1.02, 1.08, speed=0.85)); FILMTAG(t_cb, t_bs)
INFO(t_cb + 0.4, t_bs - 0.1, '影视剧片段', '《觉醒年代》第8集', FILM_NOTE)
X(t_bs, t_tp, CARDS('hz57b', [('hz57b', 1140, 490, 760, 1.2, 0.2)]))
INFO(t_bs + 0.4, t_tp - 0.1, '史料 · 照片', '补树书屋', '绍兴县馆内 · 《狂人日记》在此写成', SRC_HZ)
X(t_tp, 32, CARDS('w0806', [('w0806', 1140, 500, 840, -1.0, 0.2)]))
INFO(t_tp + 0.4, 31.9, '史料 · 拓片', '《王龙寺造像》拓片', '北京鲁迅博物馆藏', SRC_WC)
# S3-03 钱玄同夜谈（《觉醒年代》补树书屋）→ 铁屋子（AI 意象）
X(32, 39, FILM('f_hall', 1.0, 1.04)); FILMTAG(32, 39)
INFO(32.4, 38.9, '影视剧片段', '《觉醒年代》第13集', '补树书屋 · 曹磊饰鲁迅　非历史影像')
X(39, 50, KB('d01', 1.12, 1.24, (.5, .57), (.5, .6))); AITAG(39, 50)
INFO(39.6, 45.5, '意象画面', '“铁屋子”', '《〈呐喊〉自序》中的比喻 · AI 生成')
X(50, 60, KB('d02', 1.04, 1.14, (.55, .5), (.6, .46))); AITAG(50, 60)
# S3-04 写作（《觉醒年代》）→ 《新青年》4卷5号 → 《狂人日记》首页（红框“鲁迅”署名）→ 排字“仁义道德”/“吃人”
t_xq = at_char('发表在') - 0.2; t_dy = at_char('第一次署名') - 0.4; t_qm = at_char('署名') + 0.4; t_pai = at_char('歪歪斜斜') - 0.4
X(60, t_xq, FILM('f_write', 1.0, 1.05)); FILMTAG(60, t_xq)
INFO(60.4, t_xq - 0.1, '影视剧片段', '《觉醒年代》第15集', '写作《狂人日记》 · 非历史影像')
KR_HL = (0.655, 0.735, 0.715, 0.815)   # “鲁迅”署名在《狂人日记》原刊首页的位置（相对坐标）
def put_card(im, c, cx, cy, TT, tin, tend, grow=0.035):
    if TT < tin: return
    u = eout((TT - tin) / 0.8); sc = lerp(1.10, 1.0, u) * (1 + grow * (TT - tin) / max(0.1, tend - tin))
    g = c.resize((int(c.width * sc), int(c.height * sc)), Image.BILINEAR)
    paste_a(im, g, (cx - g.width / 2, cy + 240 * (1 - u) - g.height / 2), clamp((TT - tin) / 0.3))
def kr_fn(t, d):
    T0 = t_xq - 0.5; TT = T0 + t
    im, _ = kb(IMG('bg_w0701'), lerp(1.03, 1.09, t / d), .5, .5)
    put_card(im, DER('xqn', lambda: make_card('w0701', 720, 1.8)), 1450, 480, TT, t_xq - 0.3, T0 + d)
    def mk(hl):
        c = make_card('w0702', 840, 0)
        if hl:
            w, h = c.width - 136, c.height - 136; l, tp, r, b = KR_HL
            ImageDraw.Draw(c).rectangle((68 + l * w - 8, 68 + tp * h - 8, 68 + r * w + 8, 68 + b * h + 8), outline=RED + (255,), width=5)
        return c
    pg = DER('kr0', lambda: mk(False)); a = clamp((TT - t_qm) / 0.5)
    if a > 0: pg = Image.blend(pg, DER('kr1', lambda: mk(True)), eout(a))
    put_card(im, pg, 1010, 505, TT, t_dy, T0 + d, 0.06)
    return im
X(t_xq, t_pai, kr_fn)
INFO(t_xq + 0.3, t_dy - 0.1, '史料 · 刊物', '《新青年》第4卷第5号', '1918年5月', SRC_WC)
INFO(t_dy + 0.3, t_pai - 0.1, '史料 · 原刊', '《狂人日记》首页', '署名“鲁迅”——第一次用这个笔名', SRC_WC)
t_cr = at_char('吃人')
rr = random.Random(5)
RY_COLS = [(x + rr.uniform(-14, 14), 400 + rr.uniform(-46, 46), rr.uniform(-7, 7)) for x in range(1560, 300, -180)]
def col_img(txt, f, fill, gap):
    h = int(len(txt) * gap + 40); w = int(f.size * 1.5); im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for i, ch in enumerate(txt): im.alpha_composite(text_rgba(ch, f, fill, shadow=4), (int(w / 2 - f.size / 2 - 12), int(i * gap)))
    return im
def ry_fn(t, d):
    TT = t_pai - 0.5 + t
    im, _ = kb(IMG('bg_w0702'), lerp(1.06, 1.12, t / d), .5, .5); im = Image.blend(im, DARK, 0.82)
    kdim = 1 - 0.6 * ease((TT - t_cr) / 1.2)
    for i, (x, y, r) in enumerate(RY_COLS):
        a = clamp((TT - t_pai - 0.1 - i * 0.32) / 0.6) * kdim
        if a <= 0: continue
        c = DER(('ry', i), lambda r=r: col_img('仁义道德', SERIF(84, 'SemiBold'), (214, 204, 186, 255), 104).rotate(r, expand=True, resample=Image.BICUBIC))
        paste_a(im, c, (x - c.width / 2, y - c.height / 2 + 4 * math.sin(TT * 0.7 + i)), a)
    for i in range(len(RY_COLS) - 1):   # 字缝里的“吃人”
        a = clamp((TT - t_cr - i * 0.14) / 0.5)
        if a <= 0: continue
        x = (RY_COLS[i][0] + RY_COLS[i + 1][0]) / 2; y = 360 + 120 * math.sin(i * 2.1)
        c = DER(('cr', i), lambda: col_img('吃人', SERIF(64, 'Bold'), (196, 58, 44, 255), 78))
        paste_a(im, c, (x - c.width / 2, y - c.height / 2), a)
    return im
X(t_pai, 85, ry_fn)
# S3-05 “救救孩子……”（静默 3 秒，回声）
X(85, 95, KB('bg_w0702', 1.12, 1.16, (.5, .5), (.5, .5), post=dim(0.86, 0.94, 0, 9)))
t_jj = 91.0
JJ = text_rgba('救救孩子……', SERIF(100, 'Bold'), CREAM, shadow=8)
def echo(b, t, a):
    paste_a(b, JJ, (W / 2 - JJ.width / 2, 470 - JJ.height / 2), a * clamp(t / 0.8))
    for k in range(3):
        u = (t - 0.7 - k * 0.9) / 2.4
        if 0 < u < 1:
            s = 1 + 0.32 * u; g = JJ.resize((int(JJ.width * s), int(JJ.height * s)), Image.BILINEAR)
            paste_a(b, g, (W / 2 - g.width / 2, 470 - g.height / 2), a * 0.28 * (1 - u))
ov(t_jj, 95.3, echo, 0.01, 0.7)
# S3-06 《呐喊》初版 → 外文译本 → 1925 年像（“写出国人的魂灵”）→ 第三次转身
t_wy = at_char('一个个') - 0.3; t_66 = at_char('他一直在问') - 0.3; t_89 = at_char('我是否真能够') - 0.4
X(95, t_wy, CARDS('w2906', [('w2906', 1010, 500, 780, -1.4, 0.2), ('w2907', 1500, 520, 740, 1.6, 1.0)]))
INFO(95.4, t_wy - 0.1, '史料 · 书影', '《呐喊》初版', '1923年8月 · 北京新潮社　封面鲁迅设计', '出处：国家图书馆藏本（Commons）')
X(t_wy, t_66, CARDS('hz71a', [('hz71a', 1070, 560, 520, -1.2, 0.2), ('hz71b', 1620, 520, 600, 1.8, 0.7)]))
INFO(t_wy + 0.3, t_66 - 0.1, '史料 · 书影', '《阿Q正传》外文译本', '英译1926 · 俄译1929 · 法译载《欧罗巴》1926', SRC_HZ)
X(t_66, t_89, CARDS('qj6618', [('qj6618', 1140, 490, 800, 1.2, 0.2)]))
INFO(t_66 + 0.3, t_89 - 0.1, '史料 · 书影', '鲁迅作品的外文译本', '部分书影', SRC_QJ)
X(t_89, TURN3 + 0.7, CARDS('hz61', [('hz61', 1140, 480, 800, -1.0, 0.2)], grow=0.06))
INFO(t_89 + 0.4, TURN3 + 0.5, '史料 · 照片', '鲁迅', '1925年5月28日 · 为俄译本《阿Q正传》所摄', SRC_HZ)
X(TURN3 + 0.7, 118, KB('bg_hz61', 1.0, 1.08, (.5, .5), (.5, .5)), 'flash'); SHAKES.append(TURN3 + 1.05)
POP(TURN3 + 0.9, 118.2, Pop([('第三次转身', SERIF(46), (226, 196, 186), W / 2, 380, TURN3 + 0.9, 0.08),
                             ('沉默的抄碑人，发出了第一声呐喊', SERIF(84, 'Bold'), CREAM, W / 2, 510, TURN3 + 1.3, 0.08)]))

# ================= 第四章　北京（1923—1926）彷徨与反抗绝望 =================
# S4-01 章节卡 → 八道湾 → 西三条
t_xs = at_char('西三条') - 0.2
X(118, t_xs, CARDS('qj103', [('qj103', 1140, 500, 640, -1.2, 4.0)]))
POP(118.3, 121.3, Pop([('四｜北京', SERIF(120, 'Bold'), CREAM, W / 2, 450, 118.4, 0.09), ('1923—1926　彷徨与反抗绝望', SERIF(50), (232, 228, 218), W / 2, 600, 119.0, 0.05)], back=True))
INFO(121.7, t_xs - 0.1, '史料 · 照片', '八道湾11号', '1919年11月迁入 · 1923年8月搬出', SRC_QJ)
X(t_xs, 129, CARDS('hz80', [('hz80', 1140, 490, 780, 1.2, 0.2)]))
INFO(t_xs + 0.4, 128.9, '史料 · 照片', '西三条胡同21号', '1924年5月迁入 · 今北京鲁迅博物馆内', SRC_HZ)
# S4-02 《青年杂志》→ 同人星散（《觉醒年代》，渐灰）→ 《题〈彷徨〉》手迹 → 《彷徨》
t_59 = at_char('有的高升') - 0.3; t_24 = at_char('寂寞新文苑') - 0.4; t_ph = at_char('两间馀一卒') - 0.3
X(129, t_59, CARDS('hz62', [('hz62', 1140, 490, 800, -1.2, 0.2)]))
INFO(129.4, t_59 - 0.1, '史料 · 刊物', '《青年杂志》创刊号', '1915年9月 · 上海　次年改名《新青年》', SRC_HZ)
X(t_59, t_24, FILM('f_group', 1.0, 1.05, speed=0.9, gray=lambda t, d: 0.9 * ease(t / d), post=dim(0, 0.35, 1.0, 4.6))); FILMTAG(t_59, t_24)
INFO(t_59 + 0.3, t_24 - 0.1, '影视剧片段', '《觉醒年代》第13集', '《新青年》同人 · 非历史影像')
X(t_24, t_ph, CARDS('hz79', [('hz79', 1140, 490, 820, 1.0, 0.2)], grow=0.05))
INFO(t_24 + 0.3, t_ph - 0.1, '史料 · 手迹', '《题〈彷徨〉》', '1933年书赠山县初男', SRC_HZ)
X(t_ph, 145, CARDS('hz81', [('hz81', 1140, 490, 760, -1.2, 0.2)]))
INFO(t_ph + 0.3, 144.9, '史料 · 书影', '《彷徨》', '1926年8月 · 北新书局　陶元庆设计封面', SRC_HZ)
# S4-03 《华盖集》→ 《坟》→ 排字：两种时代的循环 → “第三样时代”
t_fen = at_char('《灯下漫笔》') - 0.4; t_ny = at_char('想做奴隶') - 0.6
t_l1, t_l2 = at_char('想做奴隶'), at_char('暂时做稳'); t_81 = at_char('而创造') - 0.1; t_3 = at_char('第三样时代'); t_qn = at_char('是现在的青年')
X(145, t_fen, CARDS('hz85h', [('hz85h', 1140, 490, 780, -1.2, 0.2)]))
INFO(145.4, t_fen - 0.1, '史料 · 书影', '《华盖集》', '1926年 · 北新书局　收1925年所作杂文', SRC_HZ)
X(t_fen, t_ny, CARDS('hz117', [('hz117', 1140, 490, 760, 1.2, 0.2)]))
INFO(t_fen + 0.3, t_ny - 0.1, '史料 · 书影', '《坟》', '1927年 · 未名社　收《灯下漫笔》（1925）', SRC_HZ)
L1 = text_rgba('想做奴隶而不得的时代', SERIF(78, 'SemiBold'), CREAM, shadow=6)
L2 = text_rgba('暂时做稳了奴隶的时代', SERIF(78, 'SemiBold'), CREAM, shadow=6)
DOT = Image.new('RGBA', (60, 60), (0, 0, 0, 0)); _m = Image.new('L', (60, 60), 0); ImageDraw.Draw(_m).ellipse((22, 22, 38, 38), fill=255)
DOT.paste((236, 200, 170, 255), (0, 0), _m.filter(ImageFilter.GaussianBlur(3)))
def ring_img(a):
    im = Image.new('RGBA', (1300, 420), (0, 0, 0, 0)); ImageDraw.Draw(im).ellipse((20, 20, 1280, 400), outline=(214, 200, 182, int(150 * a)), width=3)
    return im
def loop_fn(t, d):
    im, _ = kb(IMG('bg_hz117'), lerp(1.06, 1.12, t / d), .5, .5); return Image.blend(im, DARK, 0.8)
CY = 420
def loop_ov(b, t, a):
    TT = t_ny + t; br = ease((TT - t_81) / 2.4); fo = 1 - ease((TT - t_3 + 0.3) / 0.8)   # 循环被打破：两行分开、变淡，“第三样时代”出现时隐去
    k1 = clamp((TT - t_l1) / 0.6); k2 = clamp((TT - t_l2) / 0.6); t0 = t_l2 + 0.7
    th = 2 * math.pi * max(0, TT - t0) / 3.2 - math.pi / 2
    s1 = 0.55 + 0.45 * max(0, -math.sin(th)) if TT > t0 else 1; s2 = 0.55 + 0.45 * max(0, math.sin(th)) if TT > t0 else 1
    paste_a(b, L1, (W / 2 - L1.width / 2, CY - 70 - 150 * br - L1.height / 2), a * k1 * s1 * (1 - 0.7 * br) * fo)
    paste_a(b, L2, (W / 2 - L2.width / 2, CY + 70 + 150 * br - L2.height / 2), a * k2 * s2 * (1 - 0.7 * br) * fo)
    ra = clamp((TT - t0 + 0.6) / 0.8) * (1 - ease((TT - t_81) / 1.2))
    if ra > 0:
        sc = 1 + 0.25 * br; r = DER('ring', lambda: ring_img(1))
        g = r if br <= 0 else r.resize((int(r.width * sc), int(r.height * sc)), Image.BILINEAR)
        paste_a(b, g, (W / 2 - g.width / 2, CY - g.height / 2), a * ra * 0.8)
        x, y = W / 2 + 630 * sc * math.cos(th), CY + 190 * sc * math.sin(th); paste_a(b, DOT, (x - 30, y - 30), a * ra)
ov(t_ny, 175.3, loop_ov, 0.3, 0.6)
POP(t_3, 175.3, Pop([('第三样时代', SERIF(136, 'Bold'), CREAM, W / 2, CY, t_3, 0.12)]))
POP(t_qn, 175.3, Pop([('是现在的青年的使命', SERIF(54, 'SemiBold'), (228, 200, 170), W / 2, CY + 170, t_qn, 0.07)]))
X(t_ny, 175, loop_fn)
# S4-04 “老虎尾巴” → 《野草》
t_yc = at_char('散文诗集') - 0.3
X(175, t_yc, CARDS('qj497', [('qj497', 1140, 500, 640, -1.2, 0.2, 1500)]))
INFO(175.4, t_yc - 0.1, '史料 · 照片', '“老虎尾巴”', '西三条21号 · 北屋后接出的小书房', SRC_QJ)
X(t_yc, 186, CARDS('hz85y', [('hz85y', 1140, 490, 780, 1.2, 0.2)]))
INFO(t_yc + 0.4, 185.9, '史料 · 书影', '《野草》', '1927年7月 · 北新书局　孙福熙设计封面', SRC_HZ)
# S4-05 《过客》（AI 意象）
X(186, 198.4, KB('c01', 1.02, 1.12, (.45, .56), (.42, .56))); AITAG(186, 198.4)
INFO(186.6, 193.8, '意象画面', '《野草·过客》', '1925年作 · AI 生成')
X(198.4, 209, KB('c02', 1.04, 1.13, (.5, .5), (.56, .55))); AITAG(198.4, 209)
# S4-06 1925 年像（“看不见希望，也不向绝望下跪”）→ 第四次转身
X(209, TURN4 + 0.7, CARDS('hz94', [('hz94', 1140, 480, 800, -1.0, 0.2)], grow=0.07))
INFO(209.4, TURN4 - 0.2, '史料 · 照片', '鲁迅', '1925年7月 · 北京　为英译本《阿Q正传》所摄', SRC_HZ)
X(TURN4 + 0.7, 223, KB('bg_hz94', 1.0, 1.08, (.5, .5), (.5, .5)), 'flash'); SHAKES.append(TURN4 + 1.05)
POP(TURN4 + 0.9, 223.2, Pop([('第四次转身', SERIF(46), (226, 196, 186), W / 2, 380, TURN4 + 0.9, 0.08),
                             ('反抗绝望', SERIF(124, 'Bold'), CREAM, W / 2, 520, TURN4 + 1.3, 0.16)]))
# S4-07 朱安 → 许广平 → 书信
t_xg = at_char('1925年3月') - 0.3; t_xin = at_char('写来第一封信') - 0.3
X(223, t_xg, CARDS('zhuan', [('zhuan', 1140, 490, 740, -1.2, 0.2)]))
INFO(223.4, t_xg - 0.1, '史料 · 照片', '朱安', '1906年奉母命与鲁迅成婚', SRC_WC)
X(t_xg, t_xin, CARDS('hz95', [('hz95', 1140, 490, 800, 1.2, 0.2)]))
INFO(t_xg + 0.4, t_xin - 0.1, '史料 · 照片', '许广平', '北京女子师范大学学生', SRC_HZ)
X(t_xin, 237, CARDS('qj3653', [('qj3653', 1140, 500, 840, -1.0, 0.2)], grow=0.05))
INFO(t_xin + 0.4, 236.9, '史料 · 手迹', '鲁迅致许广平信', '1925年 · 二人通信后编为《两地书》', SRC_QJ)
# S4-08 三一八 → 刘和珍 → “真的猛士”（中央大字）
t_103 = at_char('到段祺瑞') - 0.3; t_kq = at_char('卫队开枪'); t_lh = at_char('在四十余') - 0.5; t_31 = at_char('真的猛士') - 0.3; t_face = t_lh + 3.0
X(237, t_103, CARDS('hz102', [('hz102', 1140, 500, 640, -1.0, 0.2, 1560)]))
INFO(237.4, t_103 - 0.1, '史料 · 照片', '三一八请愿', '1926年3月18日 · 北京', SRC_HZ)
def kq_post(im, t, d):
    k = 0.5 * eout((t - (t_kq - t_103 + 0.5)) / 0.35)
    if k > 0: im.paste(Image.blend(im, DARK, k))
X(t_103, t_lh, CARDS('hz103', [('hz103', 1140, 490, 800, 1.2, 0.2)], post=kq_post))
INFO(t_103 + 0.3, t_kq - 0.1, '史料 · 照片', '请愿群众与执政府卫队对峙', '1926年3月18日 · 北京', SRC_HZ)
X(t_lh, t_face, CARDS('hz104', [('hz104', 1140, 480, 800, -1.0, 0.2)]))
INFO(t_lh + 0.3, t_31 - 0.2, '史料 · 照片', '刘和珍（后排中）', '女师大学生自治会主席 · 1926年3月18日遇难', SRC_HZ)
X(t_face, t_31, KB('card_hz104', 1.22, 1.36, (.5, .2), (.5, .19)))
X(t_31, 263, KB('bg_hz104', 1.0, 1.04, (.5, .5), (.5, .5), post=dim(0.9, 0.95, 0, 10)))
HIDE.append((t_31 + 0.1, 263.6))
t_zm, t_zs = at_char('敢于直面'), at_char('敢于正视')
POP(t_31 + 0.3, 263.3, Pop([('真的猛士，', SERIF(84, 'Bold'), CREAM, W / 2, 330, t_31 + 0.4, 0.1)]))
POP(t_zm, 263.3, Pop([('敢于直面惨淡的人生，', SERIF(72, 'SemiBold'), CREAM, W / 2, 470, t_zm, 0.08)]))
POP(t_zs, 263.3, Pop([('敢于正视淋漓的鲜血。', SERIF(72, 'SemiBold'), CREAM, W / 2, 590, t_zs, 0.08)]))
ATT31 = text_rgba('——鲁迅《记念刘和珍君》', SERIF(36), (214, 210, 200, 255), shadow=4)
ov(t_zs + 1.6, 263.3, lambda b, t, a: paste_a(b, ATT31, (W / 2 + 200 - ATT31.width / 2, 720), a), 0.8, 0.5)
# 片尾
CR = [('样片 v3｜第三、四章 北京（B站母版 05:46—10:09，无配音）', 40, 'SemiBold', INK),
      ('', 0, '', None),
      ('AI 情景再现：铁屋子、《野草·过客》意象（画面右上角已标注）', 28, 'Regular', (70, 64, 58)),
      ('影视剧片段：电视剧《觉醒年代》（2021）第8、13、15集，曹磊饰鲁迅；已裁去原片字幕与台标，画面右上角已标注', 28, 'Regular', (70, 64, 58)),
      ('历史照片、手迹与书影：林贤治《鲁迅画传》；《鲁迅全集》2005年版文前彩插', 28, 'Regular', (70, 64, 58)),
      ('《新青年》第4卷第5号原刊、《呐喊》1923年初版（国家图书馆藏本，黑白扫描按原书暗红封面着色）', 28, 'Regular', (70, 64, 58)),
      ('《王龙寺造像》拓片、朱安像：Wikimedia Commons（公有领域）　鲁迅原文均据《鲁迅全集》2005年版', 28, 'Regular', (70, 64, 58))]
CRS = [text_rgba(c, SERIF(s, w), f + (255,)) if c else None for c, s, w, f in CR]
def cred(t, d):
    im = PAPER.copy(); y = 300
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
DUSTR = [(39, 60), (186, 209)]
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
PAPER_T = []   # 本章排字镜头均为暗底白字
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
    hid = any(a <= T < b for a, b in HIDE)
    sa = 0 if hid else max([min(clamp((T - t0 + 0.4) / 0.4), clamp((t1 - T + 0.4) / 0.4)) for t0, t1, *_ in subs] + [0])
    if sa > 0 and not pm: paste_a(base, SUBGRAD, (0, H - SUBGRAD.height), sa)
    for t0, t1, ims, attr in subs:
        if t0 <= T < t1 and not hid:
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

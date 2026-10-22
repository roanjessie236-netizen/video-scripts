import math, sys, re, csv, random, datetime, subprocess, yaml
from collections import OrderedDict
import numpy as np
# 样片 v3：第五章 厦门·广州（1926—1927 思路轰毁）。框架与 render_ch34.py 相同（相片卡、介绍卡、字幕、调色、颗粒、右上角来源标签）
# 影像为主：1917年北京正阳门东车站（纪录影像，AI 上色版）、北伐与1927年“清党”纪录影像（Internet Archive）、电影《鲁迅》（2005）；
# AI 情景再现：南下、厦门夜写、手术刀（“解剖我自己”）、进化的链子、桥梁中的一木一石、4·15 搜捕、投书告密、助官捕人、白云楼雨夜；历史事件再现另加小字“画面为情景再现”。
# “总以为将来必胜于过去，青年必胜于老人”：字幕浮起升到中央，被击中后裂纹蔓延、碎片翻转落下（接“我的思路因此轰毁”）。1920x1080/25fps，无声
# 先运行 prep_ch5.py（--cards --film）生成 preview/src5/。用法：python3 render_ch5.py [--plan] [--stills 1,2,3] [--part k/n out.mp4]（k 从 0 开始）
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
# ---------- 第五章时间线（按紧凑时长直接排；本章从 0 秒起算） ----------
OFF = 607.22   # 第三、四章 r2（332.75 + 274.47）之后，本章在 B站母版中的起点（v2.6 分镜同步）
SEQ = [('S5-01', [{'vo': '1926年8月，他和许广平一同南下。她去广州，他到了厦门大学。他在信里对她说——'}, {'q': 'Q61'}]),
 ('S5-02', [{'vo': '在厦门，他为文集《坟》写了后记。'}, {'q': 'Q30'}, {'q': 'Q29'}, {'q': 'Q97'}]),
 ('S5-03', [{'vo': '1927年1月，他来到“革命策源地”广州，在中山大学任教。'}, {'vo': '4月12日，“清党”从上海开始；4月15日，广州军警搜捕中大学生。他营救无果，愤而辞职。'}, {'q': 'Q53'}]),
 ('S5-04', [{'q': 'Q52', 'txt': '总以为将来必胜于过去，青年必胜于老人'}, {'sil': 1.0}, {'q': 'Q34'}, {'vo': '这一年的杂文，后来编成了《而已集》。题辞写道——'}, {'q': 'Q96'}]),
 ('S5-05', [{'vo': '9月底，他和许广平离开广州。'}, {'vo': '这是他的第五次转身：“青年必胜于老人”的信念碎了，可他没有离开青年——'}, {'q': 'Q54'}])]
EXTRA = {'S5-05': 0.6}   # 章末多留一点
T = 0.0; TURN, ST, EN = {}, {}, {}
for sid, aud in SEQ:
    ST[sid] = T; t = T + LEAD
    for a in aud:
        if 'sil' in a: t += a['sil']; continue
        kind, txt = ('vo', a['vo']) if 'vo' in a else (a['q'], a.get('txt') or Q[a['q']])
        if kind == 'vo' and '转身' in txt and '这是' in txt:   # “这是他的第N次转身……”由转身字卡呈现
            a1, a2 = txt.split('这是', 1)
            if a1: t = SUB(t, 'vo', a1) + GAP
            TURN[sid] = t; t += nchar('这是' + a2) / VR + GAP; continue
        if kind == 'Q52': Q52_T = (t, t + nchar(txt) / QR)   # 这一句不走底部字幕，做成“字幕浮起—碎裂”
        t = SUB(t, kind, txt) + GAP
    T = t - GAP + TAIL + EXTRA.get(sid, 0); EN[sid] = T
TURN5 = TURN['S5-05']
TOTAL_MAIN = round(T, 2); CRED = 7.0; TOTAL = TOTAL_MAIN + CRED
assert 100 < TOTAL_MAIN < 135, TOTAL_MAIN
def at(sub):
    for a, b, c in SUBLOG:
        if sub in c: return a
    raise KeyError(sub)
def at_char(k, after=-1.0):
    for a, b, c in SUBLOG:
        if k in c and a >= after - 1e-6: return a + (b - a) * c.index(k) / len(c)
    raise KeyError(k)
def dim(k0, k1, t0=0.0, t1=1.0):
    def post(im, t, d, M, size):
        k = lerp(k0, k1, ease((t - t0) / max(0.01, t1 - t0))); return Image.blend(im, Image.new('RGB', (W, H), (6, 8, 10)), k) if k > 0 else im
    return post
SRC_HZ, SRC_QJ, SRC_WC, SRC_IA = '出处：林贤治《鲁迅画传》', '出处：《鲁迅全集》2005年版', '出处：Wikimedia Commons', '出处：Internet Archive'
DARK = Image.new('RGB', (W, H), (6, 8, 10))
HIDE = []   # 不显示底部字幕的区间（改为画面中央大字）
def C(a, b, fn): clip(a, b + 0.5, fn, 'cut', 0)          # 硬切（后一镜头盖住前一镜头）
def XQ(a, b, fn): clip(a - 0.2, b + 0.5, fn, 'fade', 0.4)  # 快叠化 0.4 秒

# ---------- 右上角来源标签（同一标签相邻时合并，切换时 0.25 秒淡变） ----------
TAGL = []
def TAG(a, b, txt): TAGL.append((a, b, txt))
def AITAG(a, b): TAG(a, b, 'AI 情景再现')
T_JX, T_AQ, T_17, T_FR = '影视剧《觉醒年代》', '电影《阿Q正传》（1981）', '纪录影像 · 1917年北京', '纪录影像 · 1920年代'
def build_tags():
    m = []
    for a, b, t in sorted(TAGL):
        if m and m[-1][2] == t and a - m[-1][1] < 0.6: m[-1][1] = max(m[-1][1], b)
        else: m.append([a, b, t])
    for a, b, t in m:
        im = DER(('tag', t), lambda t=t: tag_rgba(t))
        ov(a - 0.1, b + 0.1, lambda base, tt, al, im=im: paste_a(base, im, (W - 56 - im.width, 48), al), 0.25, 0.25)

# ---------- 影像片段（prep_ch34.py 已抽成 25fps 调色帧；片段不够长时自动放慢，不定格） ----------
import os
FILMN, SLOW = {}, []
def FILM(n, z0=1.0, z1=1.04, c0=(.5, .5), c1=(.5, .5), speed=1.0, gray=None, post=None, off=0.0):
    if n not in FILMN: FILMN[n] = len(os.listdir(S3 + n))
    def fn(t, d):
        N = FILMN[n]; sp = min(speed, (N - 1 - off * FPS) / max(1.0, d * FPS))
        if (n, round(d, 2)) not in [x[:2] for x in SLOW]: SLOW.append((n, round(d, 2), round(sp, 2)))
        k = max(0, min(N - 1, int(off * FPS + t * FPS * sp))); u = t / d
        src = Image.open(f'{S3}{n}/{k:04d}.jpg').convert('RGB')
        im, M = kb(src, lerp(z0, z1, u), lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u))
        if gray: g = gray(t, d); im = Image.blend(im, ImageOps.grayscale(im).convert('RGB'), g) if g > 0 else im
        if post: im = post(im, t, d, M, src.size) or im
        return im
    return fn
JX_NOTE = '2021年 · 曹磊饰鲁迅　非历史影像'
AQ_NOTE = '上海电影制片厂 · 岑范导演　片头鲁迅为演员扮演 · 非历史影像'
A17_NOTE = 'Benjamin Brodsky 摄 · 经 AI 修复上色'

# ---------- 动态效果 ----------
def radial(R, power=1.6):
    y, x = np.mgrid[-R:R, -R:R]; d = np.sqrt(x * x + y * y) / R
    return Image.fromarray((255 * np.clip(1 - d, 0, 1) ** power).astype(np.uint8))
def flick(t, seed=0):
    return 0.5 + 0.5 * (0.55 * math.sin(t * 11.3 + seed) + 0.3 * math.sin(t * 6.7 + 1.3 + seed) + 0.15 * math.sin(t * 23.1 + seed * 2))
def lamp(p, R=300, amp=0.16, col=(255, 196, 128)):
    """油灯火苗闪烁：灯焰周围暖光随时间起伏，整幅画面亮度随之微动"""
    def post(im, t, d, M, size):
        x, y = to_screen(M, p[0], p[1], size); f = flick(t, p[0] * 10)
        m = DER(('rad', R), lambda: radial(R)); a = amp * (0.35 + 0.65 * f)
        im.paste(col, (int(x - R), int(y - R)), m.point(lambda v, a=a: int(v * a)))
        k = 0.03 * (f - 0.5)
        return Image.blend(im, DARK, -k * 2) if k < 0 else im
    return post
T_NE, T_412, T_LX = '纪录影像 · 北伐（1926—1928）', '纪录影像 · 1927年“清党”', '影视剧《鲁迅》（2005）'
LX_NOTE = '上海电影制片厂 · 丁荫楠导演 · 濮存昕饰鲁迅　非历史影像'
NOTE = text_rgba('画面为情景再现', SANS(24), (214, 216, 214, 255), shadow=3)
def RECON(a, b): ov(a, b, lambda base, t, al: paste_a(base, NOTE, (W - 56 - NOTE.width + 14, 94), al), 0.4, 0.4)
def chain(*ps):
    def post(im, t, d, M, size):
        for p in ps: im = p(im, t, d, M, size) or im
        return im
    return post
# 雾气 / 蒸汽缓缓飘移（站台白雾、河上晨雾）
_fr = np.random.default_rng(5)
FOGT = Image.fromarray((np.clip(_fr.normal(0.5, 0.22, (40, 160)), 0, 1) * 255).astype(np.uint8)).resize((W * 2, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30))
def fog(a=0.3, speed=45, col=(214, 220, 228)):
    lut = [int(clamp((v - 120) / 100) * 255 * a) for v in range(256)]
    def post(im, t, d, M, size):
        x = int(t * speed) % W; im.paste(col, (0, 0), FOGT.crop((x, 0, x + W, H)).point(lut))
    return post
# 雨丝：坐标在原图空间（随推镜放大），可限定在窗洞等区域内
rr2 = random.Random(4)
RAIN = [(rr2.uniform(0, 1), rr2.uniform(0, 1), rr2.uniform(0.9, 1.5), rr2.uniform(28, 64), rr2.uniform(0.25, 0.6)) for _ in range(400)]
def rain(regions=((0, 0, 1, 1),), a=1.0, ang=0.1, n=220, col=(196, 206, 220)):
    def post(im, t, d, M, size):
        lay = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(lay); k = 0
        for l, tp, r, b in regions:
            m = int(n * (r - l) * (b - tp)) + 10
            for x0, y0, sp, ln, al in RAIN[k:k + m]:
                v = (y0 + sp * t) % 1.0; x, y = to_screen(M, l + (r - l) * x0, tp + (b - tp) * v, size)
                dr.line((x, y, x - ang * ln, y - ln), fill=int(255 * al * a), width=2)
            k += m
        im.paste(col, (0, 0), lay.filter(ImageFilter.GaussianBlur(0.7)))
    return post
# 海船的轻微摇晃（旋转 + 起伏）
def ROLL(n, z0, z1, c0, c1, amp=0.45, per=4.6, bob=5):
    base = KB(n, z0, z1, c0, c1)
    def fn(t, d):
        im = base(t, d); th = math.radians(amp * math.sin(2 * math.pi * t / per)); s_ = 1.035
        dy = bob * math.sin(2 * math.pi * t / per + 1.1); a_, b_ = math.cos(th) / s_, math.sin(th) / s_; cx, cy = W / 2, H * 0.6
        return im.transform((W, H), Image.AFFINE, (a_, b_, cx - a_ * cx - b_ * cy, -b_, a_, cy + b_ * cx - a_ * cy + dy), resample=Image.BILINEAR)
    return fn

# ================= 第五章　厦门·广州（1926—1927）思路轰毁 =================
# S5-01 北京正阳门东车站（1917年纪录影像）+ 章节卡 → 站台背影 → 海船 → 厦门大学全景明信片 → 坟间留影 → “像一个皇帝”
s, e = ST['S5-01'], EN['S5-01']
t_n1 = 3.4; t_xm = at_char('他到了厦门') - 0.1; t_xin = at_char('他在信里') - 0.15; t_61 = at('是在草木丛中') - 0.1; t_hd = at_char('像一个皇帝') - 0.2
X(0, t_n1, FILM('a_stn', 1.0, 1.04), 'flash'); TAG(0, t_n1, T_17)
POP(0.3, t_n1 - 0.1, Pop([('五｜厦门·广州', SERIF(120, 'Bold'), CREAM, W / 2, 450, 0.3, 0.09), ('1926—1927　思路轰毁', SERIF(50), (232, 228, 218), W / 2, 600, 0.9, 0.05)], back=True))
XQ(t_n1, t_xm, KB('n01', 1.0, 1.07, (.5, .5), (.53, .5), post=fog(0.26, 40))); AITAG(t_n1, t_xin)
C(t_xm, t_xin, ROLL('n02', 1.03, 1.08, (.45, .5), (.47, .5)))
INFO(t_n1 + 0.3, t_xin - 0.1, '情景再现', '南下', '1926年8月26日离京 · 9月4日抵厦门')
XQ(t_xin, t_61, KB('card_qj3654', 1.04, 1.12, (.42, .5), (.6, .45)))
INFO(t_xin + 0.2, t_61 - 0.1, '史料 · 明信片', '厦门大学全景', '1926年9月寄许广平 · 有鲁迅题字', SRC_QJ)
XQ(t_61, t_hd, CARDS('qj855', [('qj855', 1140, 480, 760, -1.2, 0.2)]))
INFO(t_61 + 0.4, t_hd - 0.1, '史料 · 照片', '坟间留影', '1927年1月2日 · 厦门南普陀', SRC_QJ)
C(t_hd, e, KB('card_qj855', 1.0, 1.16, (.5, .5), (.5, .42)))
# S5-02 厦门灯下写《坟》后记 → 手术刀（“解剖我自己”）→ 链子中间的一环 → 雾中石桥 → 桥面一块石板
s, e = ST['S5-02'], EN['S5-02']
t_jp = at_char('我的确') - 0.3; t_gm = at_char('然而更多') - 0.1; t_29 = at_char('在进化') - 0.3; t_97 = at_char('应该和光阴') - 0.3; t_zd = at_char('至多不过') - 0.2
X(s, t_jp, KB('n03', 1.02, 1.12, (.42, .5), (.48, .52), post=lamp((0.545, 0.53), 240, 0.18))); AITAG(s, e)
INFO(s + 0.4, t_jp - 0.1, '情景再现', '《写在〈坟〉后面》', '1926年11月11日夜 · 厦门')
X(t_jp, t_gm, KB('n04', 1.04, 1.12, (.52, .55), (.56, .57), post=lamp((0.796, 0.17), 260, 0.2)))
C(t_gm, t_29, KB('n04', 1.5, 1.66, (.62, .6), (.64, .58), post=lamp((0.796, 0.17), 260, 0.2)))
X(t_29, t_97, KB('n05', 1.0, 1.3, (.5, .5), (.5, .5)))
X(t_97, t_zd, KB('n06', 1.02, 1.12, (.5, .5), (.53, .46), post=fog(0.3, 30)))
X(t_zd, e, KB('n07', 1.0, 1.12, (.5, .5), (.5, .6)))
# S5-03 北伐（纪录影像）→ 中山大学 → “清党”（纪录影像）→ 4月15日夜搜捕（情景再现）→ 白云楼 → 被捕者登记（纪录影像）→ 投书告密 / 助官捕人（情景再现）
s, e = ST['S5-03'], EN['S5-03']
t_zs = at_char('在中山大学') - 0.2; t_412 = at_char('4月12日') - 0.3; t_415 = at_char('4月15日') - 0.2; t_yj = at_char('他营救') - 0.2
t_gd = at_char('我在广东') - 0.3; t_ts = at_char('或则投书') - 0.2; t_zg = at_char('或则助官') - 0.1
X(s, t_zs, FILM('b_march', 1.0, 1.05)); TAG(s, t_zs, T_NE)
INFO(s + 0.4, t_zs - 0.1, '纪录影像', '北伐', '1926年7月 · 国民革命军自广州誓师北伐', SRC_IA)
X(t_zs, t_412, KB('card_hz120', 1.0, 1.06, (.5, .44), (.5, .4)))
INFO(t_zs + 0.2, t_412 - 0.1, '史料 · 照片', '国立中山大学', '1927年1月起任文学系主任兼教务主任', SRC_HZ)
C(t_412, t_415, FILM('p_arrest', 1.0, 1.05)); TAG(t_412, t_415, T_412)
INFO(t_412 + 0.3, t_415 - 0.1, '纪录影像', '“清党”', '1927年4月 · 军警搜捕工人、学生', SRC_IA)
X(t_415, t_yj, KB('n08', 1.02, 1.1, (.5, .5), (.47, .54), post=chain(rain(((0, 0, 1, 1),), 0.75), lamp((0.436, 0.61), 200, 0.2)))); AITAG(t_415, t_yj); RECON(t_415, t_yj)
INFO(t_415 + 0.3, t_yj - 0.1, '情景再现', '广州 · 1927年4月15日', '中山大学学生被捕')
X(t_yj, t_gd, CARDS('hz125', [('hz125', 1140, 480, 760, 1.2, 0.2)]))
INFO(t_yj + 0.3, t_gd - 0.1, '史料 · 照片', '广州白云楼', '1927年3月迁入 · 辞职后仍住在这里', SRC_HZ)
X(t_gd, t_ts, FILM('p_desk', 1.0, 1.05)); TAG(t_gd, t_ts, T_412)
C(t_ts, t_zg, KB('n09', 1.04, 1.14, (.5, .45), (.53, .42), post=lamp((0.974, 0.61), 240, 0.18))); AITAG(t_ts, e); RECON(t_ts, e)
C(t_zg, e, KB('n10', 1.02, 1.1, (.45, .5), (.5, .48), post=lamp((0.225, 0.39), 220, 0.2)))
# S5-04 “青年必胜于老人”：字幕浮起、升到中央 → 被击碎落下 → 白云楼雨夜 → 侧目而视（电影）→《而已集》→ 铁栅后的被捕者 → 书桌前
s, e = ST['S5-04'], EN['S5-04']; t52a, t52b = Q52_T
tc = t52b - 0.5; ts = tc + 0.55; t_n11 = ts + 1.25
t_hb = at_char('后来便') - 0.1; t_bz = at_char('不再无条件') - 0.15; t_ey = at_char('这一年的') - 0.3; t_96 = at_char('这半年') - 0.3; t_zy = at_char('然而我只有') - 0.2
X(s, t_n11, KB('bg_n11', 1.0, 1.06, (.5, .5), (.5, .5), post=dim(0.35, 0.55, 0, 6)))
N11P = rain(((0.49, 0, 0.745, 0.6), (0.275, 0, 0.36, 0.58)), 0.9)
X(t_n11, t_hb, KB('n11', 1.0, 1.07, (.5, .5), (.47, .48), post=N11P)); AITAG(t_n11, t_hb)
C(t_hb, t_bz, FILM('x_doubt', 1.0, 1.04)); TAG(t_hb, t_bz, T_LX)
INFO(t_hb + 0.3, t_bz - 0.2, '影视剧片段', '电影《鲁迅》（2005）', LX_NOTE)
C(t_bz, t_ey, KB('n11', 1.5, 1.6, (.44, .4), (.42, .38), post=N11P)); AITAG(t_bz, t_ey)
INFO(t_bz + 0.3, t_ey - 0.1, '情景再现', '白云楼 · 1927年', '辞职后在此编定《野草》《朝花夕拾》')
X(t_ey, t_96, CARDS('hz132', [('hz132', 1140, 470, 720, -1.2, 0.2)]))
INFO(t_ey + 0.3, t_96 - 0.1, '史料 · 书影', '《而已集》', '1928年10月上海北新书局初版 · 鲁迅设计封面', SRC_HZ)
C(t_96, t_zy, FILM('p_bars', 1.0, 1.05)); TAG(t_96, t_zy, T_412)
X(t_zy, e, FILM('x_desk', 1.0, 1.05)); TAG(t_zy, e, T_LX)

# ---- “思路轰毁”：这一句原文不走底部字幕。字幕从底部浮起，升到中央放大 → 回声 → 后一个“青”“年”之间被击中，裂纹蔓延 → 碎片翻转落下 ----
Q52TXT = SEQ[3][1][0]['txt']; HIDE.append((t52a - 0.45, t52b + 0.45))
F52 = SERIF(88, 'Medium'); YC = 470
T52 = text_rgba(Q52TXT, F52, (248, 240, 222, 255), shadow=5, salpha=230, glow=12)
A52 = text_rgba('——鲁迅' + QS['Q52'], SERIF(34), (214, 210, 200, 255), shadow=4)
_l, _t, _r, _b = F52.getbbox(Q52TXT); _p = 8 + 5 * 2 + 12 * 2
GX0, GY0 = W / 2 - T52.width / 2, YC - T52.height / 2
IMP = (GX0 + _p - _l + F52.getlength(Q52TXT[:Q52TXT.index('青年') + 1]), YC + 6)   # 撞击点（屏幕坐标）
rg = random.Random(52); NA = 18
ANG = sorted(2 * math.pi * i / NA + rg.uniform(-0.15, 0.15) for i in range(NA))
RING = [0, 26, 60, 110, 180, 280, 420, 620, 900, 1400]
VERT = [[(IMP[0] + r * rg.uniform(0.72, 1.28) * math.cos(a), IMP[1] + r * rg.uniform(0.72, 1.28) * math.sin(a)) if r else IMP for r in RING] for a in ANG]
def jag(p, q, n=3, amp=3.0):
    (x0, y0), (x1, y1) = p, q; L = math.hypot(x1 - x0, y1 - y0) or 1; nx, ny = -(y1 - y0) / L, (x1 - x0) / L; pts = [p]
    for k in range(1, n): u = k / n; o = rg.uniform(-amp, amp) * min(1, L / 40); pts.append((x0 + (x1 - x0) * u + nx * o, y0 + (y1 - y0) * u + ny * o))
    return pts + [q]
CRACK = []   # (点列, 各点到撞击点距离)
for i in range(NA):
    for j in range(len(RING) - 1):
        for p, q in ([(VERT[i][j], VERT[i][j + 1])] + ([(VERT[i][j], VERT[(i + 1) % NA][j])] if j == 1 or (j > 1 and rg.random() < 0.55) else [])):   # 同心裂纹只出现一部分，不成蛛网
            if min(math.dist(p, IMP), math.dist(q, IMP)) > 720: continue
            pts = jag(p, q, 4 if math.dist(p, q) > 30 else 1, 4.5); CRACK.append((pts, [math.dist(x, IMP) for x in pts]))
SHARDS = []
_A = T52.getchannel('A'); _DIL = _A.filter(ImageFilter.MaxFilter(7))
for i in range(NA):
    for j in range(len(RING) - 1):
        poly = [VERT[i][j], VERT[(i + 1) % NA][j], VERT[(i + 1) % NA][j + 1], VERT[i][j + 1]]
        pl = [(x - GX0, y - GY0) for x, y in poly]
        m = Image.new('L', T52.size, 0); ImageDraw.Draw(m).polygon(pl, fill=255)
        al = ImageChops.multiply(_A, m); bb = al.getbbox()
        if not bb or np.asarray(al.crop(bb)).sum() < 255 * 30: continue
        ed = Image.new('L', T52.size, 0); ImageDraw.Draw(ed).line(pl + [pl[0]], fill=200, width=2)
        ed = ImageChops.multiply(ImageChops.multiply(ed, _DIL), m)
        pc = T52.copy(); pc.putalpha(al); hl = Image.new('RGBA', T52.size, (255, 255, 252, 0)); hl.putalpha(ed); pc.alpha_composite(hl)
        pc = pc.crop(bb); cx, cy = GX0 + (bb[0] + bb[2]) / 2, GY0 + (bb[1] + bb[3]) / 2
        dx, dy = cx - IMP[0], cy - IMP[1]; dd = math.hypot(dx, dy) or 1; ux, uy = dx / dd, dy / dd
        v = 300 * (60 / (dd + 60)) ** 0.5 + rg.uniform(20, 90)
        SHARDS.append(dict(im=pc, cx=cx, cy=cy, ux=ux, uy=uy, vx=ux * v + rg.uniform(-30, 30), vy=uy * v * 0.6 - rg.uniform(80, 220),
                           g=1100 + rg.uniform(-100, 160), w=rg.uniform(-220, 220), fl=rg.uniform(2.0, 6.5), ph=rg.uniform(0, 1.2), dl=dd / 2600))
FLASH_R = radial(260, 2.2)
def q52_ov(b, t, a):
    T = t52a - 0.05 + t
    if T < tc:
        u = ease((T - t52a - 0.25) / 1.2); sc = lerp(0.5, 1.0, u); y = lerp(H - 120, YC, u)
        g = T52 if sc >= 0.999 else T52.resize((int(T52.width * sc), int(T52.height * sc)), Image.BILINEAR)
        paste_a(b, g, (W / 2 - g.width / 2, y - g.height / 2), a * clamp((T - t52a + 0.05) / 0.2))
        for k in range(2):                                     # 回声
            v = (T - t52a - 1.5 - k * 0.8) / 2.0
            if 0 < v < 1:
                s_ = 1 + 0.25 * v; gg = T52.resize((int(T52.width * s_), int(T52.height * s_)), Image.BILINEAR)
                paste_a(b, gg, (W / 2 - gg.width / 2, YC - gg.height / 2), a * 0.2 * (1 - v))
        paste_a(b, A52, (W / 2 + 420 - A52.width / 2, YC + 100), a * clamp((T - t52a - 1.6) / 0.6) * (1 - clamp((T - tc + 0.35) / 0.3)))
        return
    jx = jy = 0
    if T < tc + len(SHK) / FPS: jx, jy = SHK[int((T - tc) * FPS)]
    if T < ts + 0.3:                                           # 裂纹从撞击点蔓延
        R = 1000 * eout((T - tc) / 0.35); kc = 1 - clamp((T - ts) / 0.3); lay = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(lay)
        for wdt, base_a in ((5, 45), (2, 210)):
            for pts, ds in CRACK:
                if ds[0] > R and ds[-1] > R: continue
                for (p, q), d0, d1 in zip(zip(pts, pts[1:]), ds, ds[1:]):
                    if min(d0, d1) > R: continue
                    if max(d0, d1) > R:
                        f = (R - min(d0, d1)) / max(1e-3, abs(d1 - d0))
                        if d0 > d1: p, q = q, p
                        q = (p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f)
                    fa = int(base_a * kc * clamp(1 - min(d0, d1) / 720) ** 1.3)
                    dr.line((p[0] + jx, p[1] + jy, q[0] + jx, q[1] + jy), fill=fa, width=wdt)
        b.paste((240, 244, 250), (0, 0), lay)
    for sd in SHARDS:
        tau = T - ts - sd['dl']
        if tau <= 0:
            o = 2.5 * eout((T - tc) / 0.3); x, y = sd['cx'] + sd['ux'] * o + jx, sd['cy'] + sd['uy'] * o + jy; g = sd['im']; al = 1.0
        else:
            x = sd['cx'] + sd['vx'] * tau; y = sd['cy'] + sd['vy'] * tau + 0.5 * sd['g'] * tau * tau
            if y > H + 300: continue
            sx = max(0.18, abs(math.cos(sd['fl'] * tau + sd['ph']) / max(0.2, math.cos(sd['ph'])))); sx = min(sx, 1.0)
            g = sd['im']
            if sx < 0.97: g = g.resize((max(1, int(g.width * sx)), g.height), Image.BILINEAR)
            g = g.rotate(sd['w'] * tau, expand=True, resample=Image.BILINEAR); al = clamp(1 - (tau - 0.9) / 0.6)
        paste_a(b, g, (x - g.width / 2, y - g.height / 2), a * al)
    k = 1 - clamp((T - tc) / 0.35)                             # 撞击闪光
    if k > 0:
        b.paste(Image.blend(b, WHITE, 0.3 * k))
        b.paste((255, 252, 246), (int(IMP[0] - 260), int(IMP[1] - 260)), FLASH_R.point(lambda v, k=k: int(v * k)))
ov(t52a - 0.05, ts + 2.0, q52_ov, 0.01, 0.01); SHAKES.append(tc)
# S5-05 1927年9月11日合影 → 第五次转身 → 在青年中间（电影）
s, e = ST['S5-05'], EN['S5-05']; t_54 = at('然而此后') - 0.3
X(s, TURN5 + 0.7, CARDS('hz123', [('hz123', 1140, 470, 740, 1.0, 0.2)], grow=0.06))
INFO(s + 0.4, TURN5 + 0.5, '史料 · 照片', '与许广平、蒋径三合影', '1927年9月11日 · 广州', SRC_HZ)
X(TURN5 + 0.7, t_54, KB('bg_hz123', 1.0, 1.08, (.5, .5), (.5, .5)), 'flash'); SHAKES.append(TURN5 + 1.05)
POP(TURN5 + 0.9, t_54 + 0.3, Pop([('第五次转身', SERIF(46), (226, 196, 186), W / 2, 330, TURN5 + 0.9, 0.08),
                                ('“青年必胜于老人”的信念碎了', SERIF(64, 'SemiBold'), (232, 226, 214), W / 2, 460, TURN5 + 2.1, 0.06),
                                ('可他没有离开青年', SERIF(100, 'Bold'), CREAM, W / 2, 600, TURN5 + 4.9, 0.11)]))
X(t_54, e, FILM('x_youth', 1.0, 1.05)); TAG(t_54, e, T_LX)
build_tags()
# 片尾
def mmss(x): return f'{int(x // 60):02d}:{int(x % 60):02d}'
G_ = (70, 64, 58)
CR = [(f'样片 v3｜第五章 厦门·广州（B站母版 {mmss(OFF)}—{mmss(OFF + TOTAL_MAIN)}，无配音）', 40, 'SemiBold', INK),
      ('', 0, '', None),
      ('AI 情景再现：南下、厦门灯下写作、“解剖我自己”、“中间物”、“桥梁中的一木一石”、', 26, 'Regular', G_),
      ('1927年4月15日搜捕、“投书告密”“助官捕人”、白云楼雨夜（右上角已标注）', 26, 'Regular', G_),
      ('影视剧：电影《鲁迅》（2005，上海电影制片厂，丁荫楠导演，濮存昕饰鲁迅），非历史影像，已裁去转载台标', 26, 'Regular', G_),
      ('纪录影像：Benjamin Brodsky 摄1917年北京（AI 修复上色版）；《The Northern Expedition & The Unification Of China》；', 26, 'Regular', G_),
      ('《Chinese Coup d\'état of April 12 1927》——Internet Archive（已裁去原片字幕）', 26, 'Regular', G_),
      ('历史照片、明信片、书影：林贤治《鲁迅画传》；《鲁迅全集》2005年版文前彩插', 26, 'Regular', G_),
      ('鲁迅原文均据《鲁迅全集》2005年版', 26, 'Regular', G_)]
CRS = [text_rgba(c, SERIF(s, w), f + (255,)) if c else None for c, s, w, f in CR]
assert max(c.width for c in CRS if c) < W - 80, [c.width for c in CRS if c]
def cred(t, d):
    im = PAPER.copy(); y = 260
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
DUSTR = [(t_29, t_97)]   # “进化的链子”一镜带浮尘
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
PAPER_T = []   # 本章��字镜头均为暗底白字
SUBGRAD = Image.new('RGBA', (W, 300), (0, 0, 0, 0)); SUBGRAD.putalpha(Image.linear_gradient('L').resize((W, 300)).point(lambda v: int((v / 255) ** 1.6 * 150)))
WHITE = Image.new('RGB', (W, H), (250, 250, 248)); BLACK = Image.new('RGB', (W, H), (0, 0, 0))
SHK = [(16, -10), (-12, 8), (8, -5), (-5, 3), (2, -1), (0, 0)]
def frame(T):
    base = BLACK; act = [c for c in clips if c[0] <= T < c[1]]; k0 = 0
    for i in range(len(act) - 1, -1, -1):   # 从最上面一个完全不透明的镜头开始画，下面被盖住的不再计算
        t0, t1, fn, tr, td = act[i]
        if tr == 'cut' or td <= 0 or T - t0 >= td: k0 = i; break
    for t0, t1, fn, tr, td in act[k0:]:
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
        for sid, _ in SEQ: print(sid, round(ST[sid], 2), round(EN[sid] - ST[sid], 2), '母版', round(OFF + ST[sid], 2))
        print('TOTAL_MAIN', TOTAL_MAIN, 'TURN', round(TURN5, 2))
        for s in SUBLOG: print(*s)
        for c in clips: print(round(c[0], 2), round(c[1], 2), c[3])
        for tt in np.arange(0, TOTAL, 0.5): frame_check = [c for c in clips if c[0] <= tt < c[1]]; assert frame_check, tt
        for c in clips:
            if c[3] != 'flash': c[2](min(c[1] - c[0] - 0.01, c[1] - c[0]) * 0.999, c[1] - c[0])
        print('片段放慢：', [x for x in SLOW if x[2] < 0.999])
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

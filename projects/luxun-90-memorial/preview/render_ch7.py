import math, sys, re, csv, random, datetime, subprocess, yaml
from collections import OrderedDict
import numpy as np
# 样片 v3：尾声（1936）。框架与 render_ch6.py 相同（相片卡、介绍卡、字幕、调色、颗粒、右上角来源标签）
# 影像为主：电影《鲁迅》（2005）病中、木刻展、灵堂、丧仪与送葬段落；AI 情景再现：星夜窗前、木刻风《“这也是生活”……》四景（卧室街灯／书堆与画集／窗外屋顶／无数灯火）、
# 写便条的手、今日四景（故居门前背影、地铁读书的手、墓前鲜花、夏夜河畔）。史料照片：木刻展留影、大陆新村卧室、遗容、1936年鲁迅墓、今鲁迅墓。
# 动态：竖排逐字显影的《亥年残秋偶作》、街灯光从窗口铺进屋子并扫过墙壁、灯火闪烁、日文便条逐行浮现＋译文随读逐字点亮、“忘记我”旁逐字写出“没有忘”、萤火。1920x1080/25fps，无声
# 先运行 prep_ch7.py（--cards --film）生成 /tmp/src7/（preview/src7 为符号链接）。用法：python3 render_ch7.py [--plan] [--stills 1,2,3] [--part k/n out.mp4]（k 从 0 开始）
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops
W, H, FPS = 1920, 1080, 25
ROOT = '/data/luxun90/'; S3 = ROOT + 'preview/src7/'   # 尾声素材目录（prep_ch7.py 输出，实际在 /tmp/src7；变量名沿用）
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
        while s and s[-1] in '，。；：、—': s = s[:-1]
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
# ---------- 尾声时间线（按紧凑时长直接排；本章从 0 秒起算） ----------
OFF = 985.95   # 第六章（724.70 + 261.25）之后，尾声在 B站母版中的起点（v2.6 分镜同步）
SEQ = [('S7-01', [{'vo': '1935年底，他把一首七律书赠老友许寿裳，结尾是——'}, {'q': 'Q88'}, {'vo': '第二年，他的肺病越来越重。'}]),
 ('S7-02', [{'vo': '那年夏天，病得最重的一个夜里，他醒来，叫醒了许广平——'}, {'q': 'Q63'}, {'q': 'Q69'}]),
 ('S7-03', [{'vo': '10月8日，他去看了青年们的木刻展览，留下最后几张照片。'}, {'vo': '10月18日凌晨，气喘发作，他用日文给内山完造写下最后一张便条。'}, {'q': 'Q44'}]),
 ('S7-04', [{'vo': '1936年10月19日上午5时25分，他在上海大陆新村寓所逝世。'}]),
 ('S7-05', [{'vo': '他说——'}, {'q': 'Q71'}, {'vo': '可是先生，一个替我们看清了那么多黑暗，又不许我们绝望的人，怎么会被忘记呢？'}]),
 ('S7-06', [{'vo': '1940年，毛泽东在《新民主主义论》里称他是“中国文化革命的主将”，写道：“鲁迅的骨头是最硬的，他没有丝毫的奴颜和媚骨，这是殖民地半殖民地人民最可宝贵的性格。”'}]),
 ('S7-07', [{'vo': '先生，九十年过去了。'}, {'vo': '您让我们忘记您，管自己生活——'}, {'vo': '我们会好好生活。'}, {'vo': '只是在黑夜里，我们也想学着您：'}, {'q': 'Q23'}])]
EXTRA = {'S7-02': 1.2, 'S7-04': 1.5, 'S7-05': 0.6, 'S7-07': 2.5}   # 情感最高点、逝世、“怎么会被忘记呢”与全片结尾多留一点
T = 0.0; ST, EN, QT = {}, {}, {}
for sid, aud in SEQ:
    ST[sid] = T; t = T + LEAD
    for a in aud:
        kind, txt = ('vo', a['vo']) if 'vo' in a else (a['q'], a.get('txt') or Q[a['q']])
        QT[kind] = (t, t + nchar(txt) / (VR if kind == 'vo' else QR))
        t = SUB(t, kind, txt) + GAP
    T = t - GAP + TAIL + EXTRA.get(sid, 0); EN[sid] = T
TOTAL_MAIN = round(T, 2); CRED = 10.0; TOTAL = TOTAL_MAIN + CRED   # 尾声片尾即全片片尾字幕
assert 120 < TOTAL_MAIN < 200, TOTAL_MAIN
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
# ================= 尾声（1936） =================
def R_(A, a): return A - (a - 0.5)          # 绝对时刻 → 叠化镜头 X(a, …) 内的时刻
def BLK(t, d): return Image.new('RGB', (W, H), (6, 8, 10))
GY_, GX_ = np.mgrid[0:H, 0:W].astype(np.float32)   # 屏幕坐标网格（r5_tail 会删掉 _xx，另起名）
def PATHKB(n, keys, c0, post=None):
    """按关键帧 (绝对时刻, 缩放, cx, cy) 分段缓动的慢推/慢移；c0 为镜头起点的绝对时刻"""
    def fn(t, d):
        T = c0 + t; src = IMG(n); k = 0
        while k < len(keys) - 2 and T >= keys[k + 1][0]: k += 1
        (ta, za, xa, ya), (tb, zb, xb, yb) = keys[k], keys[k + 1]; u = ease((T - ta) / max(0.01, tb - ta))
        im, M = kb(src, lerp(za, zb, u), lerp(xa, xb, u), lerp(ya, yb, u))
        if post: im = post(im, t, d, M, src.size) or im
        return im
    return fn
def band(c0, t0, t1, x0, x1, amp=0.32, sig=210, slope=0.45, col=(240, 236, 224)):
    """一道斜的柔光带从 x0 扫到 x1（屏幕坐标），像街灯的光扫过墙壁"""
    U = GX_ + (GY_ - H / 2) * slope; LIT = Image.new('RGB', (W, H), col)
    def post(im, t, d, M, size):
        T = c0 + t; u = (T - t0) / (t1 - t0)
        if u <= 0 or u >= 1: return im
        a = amp * math.sin(math.pi * u) ** 0.6; pos = lerp(x0, x1, ease(u))
        m = Image.fromarray((np.exp(-((U - pos) / sig) ** 2) * 255 * a).astype(np.uint8))
        return Image.composite(LIT, im, m)
    return post
def reveal(c0, t_on, dur=2.6, k=0.8):
    """街灯光从窗口（右侧）铺进来：先整屋压暗，再由右向左亮起"""
    def post(im, t, d, M, size):
        T = c0 + t; u = clamp((T - t_on) / dur)
        if u >= 1: return im
        dk = Image.blend(im, DARK, k)
        if u <= 0: return dk
        edge = W * (1.15 - 1.5 * ease(u))
        m = Image.fromarray((np.clip((GX_ - edge) / 420, 0, 1) * 255).astype(np.uint8))
        return Image.composite(im, dk, m)
    return post

# S7-01 星夜窗前 + 章节卡 →《亥年残秋偶作》竖排逐字显影（末联随朗读点亮）→ 病床（电影）
s, e = ST['S7-01'], EN['S7-01']; t_sz = at('他把一首'); t88, t88e = QT['Q88']; t_de = at('第二年')
X(0, t_de, KB('b01', 1.0, 1.08, (.42, .5), (.4, .46)), 'flash'); AITAG(0, t_de)
POP(0.3, t_sz + 0.8, Pop([('尾声', SERIF(130, 'Bold'), CREAM, W / 2, 450, 0.3, 0.12), ('1936', SERIF(56), (232, 228, 218), W / 2, 600, 0.8, 0.06)], back=True))
INFO(t_sz + 0.9, t88 - 0.1, '史料 · 诗', '《亥年残秋偶作》', '1935年12月5日 · 书赠老友许寿裳', SRC_QJ)
POEM88 = '曾惊秋肃临天下，敢遣春温上笔端。尘海苍茫沉百感，金风萧瑟走千官。老归大泽菰蒲尽，梦坠空云齿发寒。竦听荒鸡偏阒寂，起看星斗正阑干。'
P88 = [x for x in re.split('[，。]', POEM88) if x]; assert ''.join(P88[6:]) == re.sub('[，。]', '', Q['Q88']) and len(P88) == 8
F88 = SERIF(60, 'Medium'); PC88 = (t88e - t88) / 14; GL88 = {}
def g88(ch, hi):
    if (ch, hi) not in GL88: GL88[(ch, hi)] = text_rgba(ch, F88, (248, 240, 222, 255) if hi else (222, 216, 204, 255), shadow=4, salpha=230, glow=10 if hi else 6)
    return GL88[(ch, hi)]
QX0, QDX, QY0, QDY = 1745, 100, 230, 82
A88 = text_rgba('——鲁迅' + QS['Q88'], SERIF(28), (214, 216, 214, 255), shadow=3, salpha=230, glow=6)
_bk = Image.new('L', (W, H), 0); ImageDraw.Draw(_bk).rounded_rectangle((QX0 - 7 * QDX - 110, QY0 - 110, QX0 + 110, QY0 + 6 * QDY + 110), 80, fill=140)
POEMBK88 = _bk.filter(ImageFilter.GaussianBlur(60))
def poem88(b, t, a):
    T = t_sz + 0.7 + t
    b.paste((6, 8, 10), (0, 0), POEMBK88.point(lambda v, a=a: int(v * a)))
    for k in range(8):
        x = QX0 - k * QDX
        for j, ch in enumerate(P88[k]):
            if k < 6: ti = t_sz + 0.9 + k * 0.5 + j * 0.05; al = 0.85 - 0.45 * ease((T - t88 + 0.3) / 0.6)
            else: ti = t88 + ((k - 6) * 7 + j) * PC88; al = 1.0
            u = clamp((T - ti) / 0.4)
            if u <= 0: continue
            g = g88(ch, k >= 6); sc = lerp(1.18, 1.0, eout(u))
            if sc > 1.001: g = g.resize((int(g.width * sc), int(g.height * sc)), Image.BILINEAR)
            paste_a(b, g, (x - g.width / 2, QY0 + j * QDY - g.height / 2), a * clamp(u * 1.4) * al)
    paste_a(b, A88, (W / 2 - A88.width / 2, H - 70 - A88.height / 2), a * clamp((T - t88 - 0.5) / 0.6) * (1 - clamp((T - t88e - 0.3) / 0.4)))
ov(t_sz + 0.7, t_de + 0.3, poem88, 0.4, 0.5); HIDE.append((t88 - 0.3, t88e + 0.4))
C(t_de, e, FILM('x_sick', 1.0, 1.05)); TAG(t_de, e, T_LX)

# S7-02 深夜（电影）→ 醒来 → 许广平 → 药瓶 → 许广平 → 木刻风：暗屋 → 街灯光从窗口铺进来 → 墙壁、棱线（光扫过）→ 书堆与未订的画集 → 窗外屋顶 → 无数灯火
s, e = ST['S7-02'], EN['S7-02']; t_wk = at_char('他醒来'); t_jx = at_char('叫醒了'); t63 = QT['Q63'][0]; t_kd = at_char('并且去开开电灯'); t_kk = at_char('给我看来看去')
t69, t69e = QT['Q69']; t_wl = at_char('我大略一看'); t_sd = at_char('熟识的书堆'); t_wm = at_char('外面的进行着的夜'); t_wq = at_char('无数的人们'); t_yg = at_char('都和我有关')
X(s, t_wk, FILM('x_night1', 1.0, 1.05)); C(t_wk, t_jx, FILM('x_wake', 1.0, 1.04)); C(t_jx, t63, FILM('x_xu', 1.0, 1.04))
C(t63, t_kd, FILM('x_bottle', 1.0, 1.05)); C(t_kd, t_kk, FILM('x_xu', 1.04, 1.08, off=2.6)); TAG(s, t_kk, T_LX)
INFO(s + 0.4, t_wk - 0.1, '影视剧片段', '电影《鲁迅》（2005）', LX_NOTE)
W01K = [(t_kk - 0.5, 1.3, .3, .62), (t69, 1.22, .34, .6), (t69 + 2.8, 1.02, .55, .5), (t_wl + 0.3, 1.05, .58, .45), (t_sd + 0.5, 1.5, .66, .3)]
X(t_kk, t_sd, PATHKB('w01', W01K, t_kk - 0.5, post=chain(reveal(t_kk - 0.5, t69 - 0.1), band(t_kk - 0.5, t_wl - 0.3, t_sd + 0.6, W + 300, -300))))
INFO(t_kk + 0.2, t69 - 0.1, '情景再现 · 木刻风', '《“这也是生活”……》', '1936年夏 · 病中的一个深夜')
X(t_sd, t_wm, KB('w02', 1.05, 1.2, (.42, .45), (.55, .6), post=band(t_sd - 0.5, t_sd - 0.3, t_wm + 0.4, W + 300, -300, 0.26)))
X(t_wm, t_wq, KB('w03', 1.0, 1.7, (.5, .5), (.36, .56)))   # 穿出窗外，推向远方
rT = random.Random(69); _g4 = np.asarray(IMG('w04').convert('L')); _h4, _w4 = _g4.shape
_cand = [(x, y) for y, x in zip(*np.where(_g4[int(_h4 * .42):int(_h4 * .97):3, ::3] > 215))]
CITY = [((x * 3) / _w4, (y * 3 + int(_h4 * .42)) / _h4, rT.choice([5, 6, 7, 9, 11]), rT.uniform(0, 6.28), rT.uniform(1.2, 3.4)) for x, y in rT.sample(_cand, min(320, len(_cand)))]
_cs = [(x, y) for y, x in zip(*np.where(_g4[:int(_h4 * .36):3, ::3] > 200))]
STARS = [((x * 3) / _w4, (y * 3) / _h4, rT.choice([3, 4]), rT.uniform(0, 6.28), rT.uniform(1.0, 2.6)) for x, y in rT.sample(_cs, min(90, len(_cs)))]
def glow_spr(r, col):
    m = radial(r * 3, 2.2); s_ = Image.new('RGBA', m.size, col + (255,)); s_.putalpha(m); return s_
SPW = {r: glow_spr(r, (255, 212, 146)) for r in (5, 6, 7, 9, 11)}; SPS = {r: glow_spr(r, (236, 240, 255)) for r in (3, 4)}
def twinkle(c0, t_up):
    def post(im, t, d, M, size):
        T = c0 + t; g = 0.55 + 0.45 * ease((T - t_up) / 1.5)
        for pts, spr, base in ((CITY, SPW, 0.9), (STARS, SPS, 0.5)):
            for px, py, r, ph, sp in pts:
                x, y = to_screen(M, px, py, size)
                if -30 < x < W + 30 and -30 < y < H + 30:
                    b = 0.5 + 0.5 * math.sin(T * sp + ph); g_ = spr[r]; paste_a(im, g_, (x - g_.width / 2, y - g_.height / 2), g * base * (0.35 + 0.65 * b * b))
    return post
X(t_wq, e, KB('w04', 1.7, 1.0, (.62, .62), (.5, .5), post=twinkle(t_wq - 0.5, t_yg))); AITAG(t_kk, e); RECON(t_kk, t_sd)
DUST_A = (t69, t_wm)

# S7-03 木刻展上与青年（电影）→ 最后的留影 → 深夜气喘（电影）→ 写便条的手 → 黑底字卡：日文原信逐行浮现，全集译文随朗读逐字点亮
s, e = ST['S7-03'], EN['S7-03']; t_lx = at_char('留下最后'); t_18 = at_char('10月18日'); t_ry = at_char('他用日文'); t44, t44e = QT['Q44']
X(s, t_lx, FILM('x_mkhall', 1.0, 1.05)); TAG(s, t_lx, T_LX)
INFO(s + 0.4, t_lx - 0.1, '史实', '第二回全国木刻流动展览会', '1936年10月8日 · 上海八仙桥青年会')
X(t_lx, t_18, CARDS('qj2024', [('qj2024', 1120, 540, 860, -1.0, 0.15)]))
INFO(t_lx + 0.2, t_18 - 0.05, '史料 · 照片', '最后的留影之一', '1936年10月8日 · 木刻展会场 · 沙飞摄', SRC_QJ)
C(t_18, t_ry, FILM('x_asthma', 1.0, 1.05)); TAG(t_18, t_ry, T_LX)
X(t_ry, t44, KB('c01', 1.45, 1.56, (.66, .6), (.68, .62))); AITAG(t_ry, t44); RECON(t_ry, t44)
FJ = ImageFont.truetype(FD + 'NotoSerifCJK-Regular.ttc', 38, index=0)   # 日文用 JP 字形
JL = [('老版几下：', 0), ('意外な事で夜中から又喘息がはじめました。', 2), ('だから、十時頃の約束がもう出來ないから甚だ濟みません。', 0),
      ('お賴み申します。電話で須藤先生に賴んで下さい。', 2), ('早速みて下さる様にと。草々頓首', 0), ('L拜　十月十八日', -1)]
JMAP = [0, 1, 1, 2, 2, 3]   # 日文行 → 译文行
CL = ['老版几下：', '没想到半夜又气喘起来。因此，十点钟的约会去不成了，很抱歉。', '拜托你给须藤先生挂个电话，请他速来看一下。']
assert ''.join(CL) == Q['Q44'], Q['Q44']
LX0, LX1, JY0, JDY, CY0, CDY = 380, 1540, 196, 62, 650, 78
JIM = [text_rgba(s_, FJ, (226, 222, 212, 255), shadow=3) for s_, _ in JL]
FCN = SERIF(44, 'Medium'); CG = []; _nk = 0
for i, line in enumerate(CL):
    x = LX0
    for ch in line:
        if not re.match(r'[，。；：！？、—“”（）\s]', ch): _nk += 1
        CG.append((i, text_rgba(ch, FCN, (250, 238, 214, 255), shadow=3, glow=6), x + FCN.getlength(ch) / 2, CY0 + i * CDY, t44 + (_nk - 1) / QR)); x += FCN.getlength(ch)
C_LINE_T = [min(c[4] for c in CG if c[0] == i) for i in range(3)] + [t44e + 0.3]
SIG = text_rgba('草草顿首　L拜　十月十八日', SERIF(34), (190, 186, 178, 255), shadow=3)
HDR = text_rgba('致内山完造（日文便条）　1936年10月18日', SERIF(32), (176, 172, 164, 255), shadow=3)
A44 = text_rgba('日文原信据《鲁迅全集》2005年版所录排字（不仿笔迹）　中文为全集译文', SANS(24), (150, 156, 156, 255))
def letter(c0):
    def fn(t, d):
        T = c0 + t; im = Image.new('RGB', (W, H), (8, 9, 11))
        paste_a(im, HDR, (W / 2 - HDR.width / 2, 92), clamp((T - t44 + 0.4) / 0.5))
        cur = max([i for i in range(4) if T >= C_LINE_T[i] - 0.2] + [-1])
        for j, (g, (s_, ind)) in enumerate(zip(JIM, JL)):
            ta = t44 - 0.3 + j * 0.55; u = clamp((T - ta) / 0.6)
            if u <= 0: continue
            hi = 1.0 if JMAP[j] == cur else 0.62
            x = LX1 - g.width + 8 if ind < 0 else LX0 - 8 + ind * 38
            paste_a(im, g, (x + 16 * (1 - eout(u)), JY0 + j * JDY - g.height / 2), u * hi)
        ImageDraw.Draw(im).line((LX0, 574, LX1, 574), fill=(84, 82, 78), width=2)
        for i, g, cx, cy, tc in CG:
            u = clamp((T - tc) / 0.25); al = lerp(0.16, 1.0, u) * clamp((T - t44 + 0.6) / 0.6)
            paste_a(im, g, (cx - g.width / 2, cy - g.height / 2), al)
        paste_a(im, SIG, (LX1 + 60 - SIG.width, CY0 + 3 * CDY - SIG.height / 2), clamp((T - t44e - 0.2) / 0.5))
        paste_a(im, A44, (W / 2 - A44.width / 2, H - 76), 0.85 * clamp((T - t44 - 0.6) / 0.6))
        return im
    return fn
X(t44, e, letter(t44 - 0.5)); HIDE.append((t44 - 0.3, t44e + 0.4))

# S7-04 黑场白字“1936年10月19日 上午5时25分”→ 大陆新村寓所卧室，极慢推
s, e = ST['S7-04'], EN['S7-04']; t_zs = at('他在上海')
X(s, t_zs, BLK); HIDE.append((s, t_zs - 0.05))
POP(s + 0.3, t_zs + 0.6, Pop([('1936年10月19日', SERIF(88, 'SemiBold'), CREAM, W / 2, 470, s + 0.4, 0.07), ('上午5时25分', SERIF(64), (226, 222, 212), W / 2, 610, s + 1.5, 0.08)]))
X(t_zs, e, KB('p2026', 1.0, 1.1, (.5, .5), (.56, .56)))
INFO(t_zs + 0.4, e - 0.3, '史料 · 照片', '上海大陆新村寓所卧室', '1933年4月—1936年10月 · 今山阴路132弄9号', SRC_QJ)

# S7-05 遗容 → 灵前烛光 →“鲁迅先生丧仪”→ 送葬的街道 →“民族魂”（电影）
s, e = ST['S7-05'], EN['S7-05']; t_ks = at('可是先生'); t_y5 = at_char('一个替我们'); t_bx = at_char('又不许'); t_zm = at_char('怎么会被忘记')
X(s, t_ks, KB('p6080', 1.0, 1.08, (.5, .5), (.46, .5)))
INFO(s + 0.3, t_ks - 0.1, '史料 · 照片', '遗容', '1936年10月19日', SRC_QJ)
C(t_ks, t_y5, FILM('x_ling', 1.0, 1.05)); C(t_y5, t_bx, FILM('x_sangyi', 1.0, 1.04)); C(t_bx, t_zm, FILM('x_songzang', 1.0, 1.05)); C(t_zm, e, FILM('x_mzh', 1.0, 1.05)); TAG(t_ks, e, T_LX)
INFO(t_y5 + 0.2, t_zm - 0.1, '史实', '1936年10月22日出殡', '万国殡仪馆 → 万国公墓 · 上海各界上万人送葬')

# S7-06 1936年的鲁迅墓 →“中国文化革命的主将”（送葬的人们，电影）→ 引文字卡：墓前鲜花 → 今日鲁迅墓
s, e = ST['S7-06'], EN['S7-06']; t_cz = at_char('称他是'); t_xd = at_char('写道'); t_gt = at_char('鲁迅的骨头'); t_my = at_char('他没有丝毫'); t_zx = at_char('这是殖民地')
X(s, t_cz, CARDS('hz234', [('hz234', 1160, 540, 820, 1.0, 0.2)]))
INFO(s + 0.3, t_cz - 0.1, '史料 · 照片', '1936年的鲁迅墓', '上海万国公墓 · 墓碑下部为周海婴题字', SRC_HZ)
X(t_cz, t_xd, FILM('x_crowd25', 1.0, 1.05, post=dim(0.45, 0.5))); TAG(t_cz, t_xd, T_LX)
POP(t_cz + 0.3, t_xd + 0.5, Pop([('中国文化革命的主将', SERIF(100, 'Bold'), CREAM, W / 2, 470, t_cz + 0.5, 0.1)], back=True))
X(t_xd, t_zx, KB('d01', 1.0, 1.08, (.5, .5), (.55, .5), post=dim(0.35, 0.35))); AITAG(t_xd, t_zx)
X(t_zx, e, KB('p6083', 1.0, 1.08, (.5, .5), (.5, .45), post=dim(0.4, 0.4)))
INFO(t_zx + 0.4, e - 0.1, '史料 · 照片', '鲁迅墓', '1956年迁葬虹口公园（今鲁迅公园）', SRC_QJ)
F_M1, F_M2 = SERIF(76, 'Bold'), SERIF(60, 'SemiBold')
MAO = Pop([('“鲁迅的骨头是最硬的，', F_M1, CREAM, W / 2, 360, t_gt, 1 / VR), ('他没有丝毫的奴颜和媚骨，', F_M2, (236, 230, 216), W / 2, 500, t_my, 1 / VR),
           ('这是殖民地半殖民地人民最可宝贵的性格。”', F_M2, (236, 230, 216), W / 2, 600, t_zx, 1 / VR)], back=True)
MSRC = [text_rgba('——毛泽东《新民主主义论》（1940年）', SERIF(34), (214, 216, 214, 255), shadow=3, glow=6),
        text_rgba('据《毛泽东选集》第二卷，人民出版社1991年第二版，第698页', SANS(24), (176, 180, 180, 255), shadow=3)]
def mao(b, t, a):
    T = t_xd + t; MAO.draw(b, T, a)
    for k, g in enumerate(MSRC): paste_a(b, g, (W / 2 - g.width / 2, 720 + 56 * k - g.height / 2), a * clamp((T - t_gt - 0.6) / 0.6))
ov(t_xd, e + 0.4, mao, 0.3, 0.6); HIDE.append((t_xd - 0.05, e + 0.5))

# S7-07 今日：故居门前背影 →“忘记我，管自己生活”→ 地铁里读书的手 → 夏夜河畔，萤火渐多 → 回到序章那张稿纸：“忘记我”旁写出“没有忘”
s, e = ST['S7-07'], EN['S7-07']; t_nr = at_char('您让我们'); t_hh = at_char('我们会好好'); t_zs7 = at_char('只是在黑夜里'); t23, t23e = QT['Q23']; t_jl = at_char('就令萤火'); t_bb = at_char('不必等候')
X(s, t_nr, KB('d02', 1.0, 1.06, (.5, .5), (.5, .46))); XQ(t_nr, t_hh, lambda t, d: wj(t_nr - 0.2, False)(t, d)); XQ(t_hh, t_zs7, KB('d03', 1.0, 1.07, (.5, .5), (.54, .5)))
VMAP = {'，': '︐', '。': '︒', '、': '︑', '；': '︔', '：': '︓', '—': '︱', '！': '︕', '？': '︖', '“': '﹁', '”': '﹂'}
WJ_TXT, WJ_F, WJ_CELL, WJ_TOP, WJ_X = '四，忘记我，管自己生活。', SERIF(56), 64, 118, W / 2 + 70
WJG = [text_rgba(VMAP.get(ch, ch), WJ_F, (240, 232, 214, 255), shadow=3) for ch in WJ_TXT]
MYW = [text_rgba(ch, SERIF(60, 'SemiBold'), (248, 208, 128, 255), shadow=0, glow=0) for ch in '没有忘']
MYG = [text_rgba(ch, SERIF(60, 'SemiBold'), (248, 208, 128, 255), shadow=4, glow=12) for ch in '没有忘']
def wipe(g, u, soft=22):
    h = g.height; y = u * (h + soft); col = np.clip((y - np.arange(h, dtype=np.float32)) / soft, 0, 1)
    m = Image.fromarray((np.repeat(col[:, None], g.width, 1) * 255).astype(np.uint8)); out = g.copy(); out.putalpha(ImageChops.multiply(g.getchannel('A'), m)); return out
rf = random.Random(23)
FF = [(rf.uniform(0, W), rf.uniform(0, H * 0.75), rf.uniform(-16, 16), rf.uniform(-12, 3), rf.choice([3, 4, 5, 6]), rf.uniform(0, 6.28), rf.uniform(0.6, 1.5)) for _ in range(110)]
FFS = {r: glow_spr(r, (226, 255, 150)) for r in (3, 4, 5, 6)}
def fireflies(c0, nfn):
    def post(im, t, d, M=None, size=None):
        T = c0 + t; n = nfn(T); u0 = T - t_zs7
        for i, (x0, y0, vx, vy, r, ph, sp) in enumerate(FF):
            a = clamp(n - i)
            if a <= 0: break
            x = (x0 + vx * u0 + 34 * math.sin(u0 * 0.5 * sp + ph)) % W; y = H * 0.25 + (y0 + vy * u0 + 20 * math.sin(u0 * 0.8 * sp + 1.7 * ph)) % (H * 0.75)
            b = (0.5 + 0.5 * math.sin(u0 * 2.4 * sp + ph)) ** 2; g = FFS[r]; paste_a(im, g, (x - g.width / 2, y - g.height / 2), a * (0.2 + 0.8 * b))
    return post
def nff(T): return 3 + 25 * ease((T - t23) / 2.5) + 72 * ease((T - t_jl) / 3.5)
def wj(c0, write):
    ff = fireflies(c0, lambda T: 40 * clamp((T - t_bb) / 1.5)) if write else None
    def fn(t, d):
        T = c0 + t; im = Image.new('RGB', (W, H), (6, 8, 10)); hi = ease((T - c0 - 0.5) / 0.6)
        for i, g in enumerate(WJG):
            a = 1.0 if 2 <= i <= 4 else lerp(1.0, 0.42, hi); y = WJ_TOP + i * WJ_CELL + WJ_CELL / 2
            dx, dy = (WJ_F.size * 0.25, -WJ_F.size * 0.25) if WJ_TXT[i] in '，。' else (0, 0)
            paste_a(im, g, (WJ_X - g.width / 2 + dx, y - g.height / 2 + dy), a * clamp((T - c0) / 0.5))
        if write:
            for k in range(3):
                u = clamp((T - (t_bb + 0.4 + k * 0.7)) / 0.6)
                if u <= 0: continue
                y = WJ_TOP + (2 + k) * WJ_CELL + WJ_CELL / 2; g = wipe(MYW[k], u) if u < 1 else MYW[k]
                paste_a(im, MYG[k], (WJ_X - 150 - MYG[k].width / 2, y - MYG[k].height / 2), 0.5 * ease(u))
                paste_a(im, g, (WJ_X - 150 - g.width / 2, y - g.height / 2), 1.0)
            ff(im, t, d)
        return im
    return fn
X(t_zs7, t_jl, KB('d05', 1.0, 1.12, (.5, .5), (.56, .48), post=fireflies(t_zs7 - 0.5, nff)))
X(t_jl, t_bb, KB('d05', 1.4, 1.6, (.32, .62), (.36, .6), post=fireflies(t_jl - 0.5, nff)))
AITAG(s, t_nr); AITAG(t_hh, t_bb)
X(t_bb, e, wj(t_bb - 0.5, True))
build_tags()

# 片尾（尾声即全片片尾字幕）
def mmss(x): return f'{int(x // 60):02d}:{int(x % 60):02d}'
G_ = (70, 64, 58)
CR = [(f'样片 v3｜尾声 1936（B站母版 {mmss(OFF)}—{mmss(OFF + TOTAL_MAIN)}，无配音）', 40, 'SemiBold', INK),
      ('', 0, '', None),
      ('参考书目：《鲁迅全集》（人民文学出版社2005年版）　林贤治《鲁迅画传》　钱理群《鲁迅作品十五讲》　孔庆东《正说鲁迅》', 26, 'Regular', G_),
      ('片中鲁迅原文均据《鲁迅全集》2005年版核对；毛泽东语据《毛泽东选集》第二卷（1991年第二版）第698页', 26, 'Regular', G_),
      ('历史照片：《鲁迅全集》2005年版文前彩插（木刻展留影、大陆新村寓所、遗容、鲁迅墓）；林贤治《鲁迅画传》（1936年的鲁迅墓）', 26, 'Regular', G_),
      ('影视剧：电影《鲁迅》（2005，上海电影制片厂，丁荫楠导演，濮存昕饰鲁迅），非历史影像，已裁去转载台标', 26, 'Regular', G_),
      ('AI 情景再现：星夜窗前、木刻风《“这也是生活”……》四景（卧室街灯／书堆与画集／窗外屋顶／无数灯火）、写便条的手；', 26, 'Regular', G_),
      ('今日：故居门前的背影、地铁里读书的手、墓前鲜花、夏夜河畔——均为 AI 生成，非实拍（右上角已标注）；萤火为程序生成', 26, 'Regular', G_),
      ('日文便条按全集所录排字，不仿笔迹；“没有忘”为印刷字体逐字显现，不仿鲁迅笔迹', 26, 'Regular', G_)]
CRS = [text_rgba(c, SERIF(s, w), f + (255,)) if c else None for c, s, w, f in CR]
assert max(c.width for c in CRS if c) < W - 80, [c.width for c in CRS if c]
def cred(t, d):
    im = PAPER.copy(); y = 240
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
DUSTR = [DUST_A]   # 街灯光里的浮尘
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
        print('TOTAL_MAIN', TOTAL_MAIN)
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

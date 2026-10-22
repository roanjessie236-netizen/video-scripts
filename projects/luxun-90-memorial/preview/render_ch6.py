import math, sys, re, csv, random, datetime, subprocess, yaml
from collections import OrderedDict
import numpy as np
# 样片 v3：第六章 上海（1927—1936 新的信念与横站）。框架与 render_ch5.py 相同（相片卡、介绍卡、字幕、调色、颗粒、右上角来源标签）
# 影像为主：1920—30年代上海与中国劳工纪录影像（Internet Archive）、电影《鲁迅》（2005）；AI 情景再现：灯下译书、“横站”、柔石取合同与被捕、
# 花园庄旅馆之夜、《惯于长夜过春时》诗意四景、长夜的路、足踏在地上、稿纸与译本、木刻风“匕首投枪”“血路”。历史事件再现另加小字“画面为情景再现”。
# 动态：“落伍者”印章砸下、两头飞来的箭、五烈士像依次亮起又熄灭、竖排逐字显影的诗、尽头渐亮的光、书影墙、“约三百万字”计数、冷暖分屏。1920x1080/25fps，无声
# 先运行 prep_ch6.py（--cards --film）生成 preview/src6/。用法：python3 render_ch6.py [--plan] [--stills 1,2,3] [--part k/n out.mp4]（k 从 0 开始）
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops
W, H, FPS = 1920, 1080, 25
ROOT = '/data/luxun90/'; S3 = ROOT + 'preview/src6/'   # 第六章素材目录（prep_ch6.py 输出；变量名沿用）
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
# ---------- 第六章时间线（按紧凑时长直接排；本章从 0 秒起算） ----------
OFF = 724.70   # 第五章（607.22 + 117.48）之后，本章在 B站母版中的起点（v2.6 分镜同步）
SEQ = [('S6-01', [{'vo': '1927年10月，他在上海定居，从此不再去大学任教，以写作和翻译为业。内山书店的老板内山完造，成了他的老朋友。'}]),
 ('S6-02', [{'vo': '到上海不久，创造社、太阳社的年轻人围攻他，说他是“落伍者”。他却由此去读马克思主义文艺理论，还动手翻译。他后来说——'}, {'q': 'Q82'}, {'q': 'Q83'}]),
 ('S6-03', [{'vo': '1929年，儿子海婴出生。有人笑他太宠孩子，他写诗回答——'}, {'q': 'Q41'}]),
 ('S6-04', [{'vo': '1930年3月，左联成立，他在成立大会上开口便说——'}, {'q': 'Q84'}, {'vo': '可此后，他常常要同时提防两面来的箭——'}, {'q': 'Q37'}]),
 ('S6-05', [{'vo': '1931年1月16日夜里，他最信任的青年朋友柔石来问出书的事，拿了合同抄件就走了。'}, {'q': 'Q74'},
            {'vo': '2月7日夜或8日晨，柔石、殷夫、胡也频、冯铿、李伟森在龙华被秘密杀害，都还不到三十岁。'}]),
 ('S6-06', [{'vo': '悼文无处发表。他在《北斗》创刊号上，选登了一幅珂勒惠支的木刻——'}, {'q': 'Q67'}]),
 ('S6-07', [{'vo': '他带着妻儿躲进客栈。在那些夜里，他写了一首诗。'}, {'q': 'Q68'}]),
 ('S6-08', [{'vo': '两年后，他终于写下《为了忘却的记念》，结尾是——'}, {'q': 'Q40'}]),
 ('S6-09', [{'vo': '血的教训，让他看清了自己和谁站在一起——'}, {'q': 'Q85'}, {'q': 'Q86'}]),
 ('S6-10', [{'vo': '他和瞿秋白一见如故，书赠一副清人的联语：人生得一知己足矣，斯世当以同怀视之。瞿秋白就义后，病中的他亲自编校亡友的译文集《海上述林》。'}]),
 ('S6-11', [{'vo': '十八年里，他写下小说、散文诗、回忆散文和十几本杂文集，写出《中国小说史略》，还编刊物、倡木刻、扶植青年；一生翻译的外国作品，约有三百万字。上海十年，他的武器是杂文——'}, {'q': 'Q87'}]),
 ('S6-12', [{'q': 'Q36'}, {'vo': '人们常记住前一句的冷，忘了后一句的暖。第六次转身：从进化论走到“新兴的无产者”，横站着，护着青年往前走。'}])]
EXTRA = {'S6-05': 1.6, 'S6-07': 0.6, 'S6-12': 0.6}   # 龙华、《惯于长夜》之后与章末多留一点
T = 0.0; TURN, ST, EN, QT = {}, {}, {}, {}
for sid, aud in SEQ:
    ST[sid] = T; t = T + LEAD
    for a in aud:
        if 'sil' in a: t += a['sil']; continue
        kind, txt = ('vo', a['vo']) if 'vo' in a else (a['q'], a.get('txt') or Q[a['q']])
        if kind == 'vo' and '次转身' in txt:   # “第N次转身……”由转身字卡呈现
            a1, a2 = txt[:txt.index('第六次转身')], txt[txt.index('第六次转身'):]
            if a1: t = SUB(t, 'vo', a1) + GAP
            TURN[sid] = t; t += nchar(a2) / VR + GAP; continue
        QT[kind] = (t, t + nchar(txt) / (VR if kind == 'vo' else QR))
        t = SUB(t, kind, txt) + GAP
    T = t - GAP + TAIL + EXTRA.get(sid, 0); EN[sid] = T
TURN6 = TURN['S6-12']
TOTAL_MAIN = round(T, 2); CRED = 7.0; TOTAL = TOTAL_MAIN + CRED
assert 230 < TOTAL_MAIN < 300, TOTAL_MAIN
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
# ================= 第六章　上海（1927—1936）新的信念与横站 =================
T_SH, T_32, T_30 = '纪录影像 · 1920年代上海', '纪录影像 · 1932年上海', '纪录影像 · 1930年代中国'
def R_(A, a): return A - (a - 0.5)          # 绝对时刻 → 叠化镜头 X(a, …) 内的时刻
def warm(k=1.0):
    g = np.array([1 + 0.10 * k, 1.0, 1 - 0.16 * k], np.float32); o = np.array([10, 4, -6], np.float32) * k
    def post(im, t, d, M, size): return Image.fromarray(np.clip(np.asarray(im).astype(np.float32) * g + o, 0, 255).astype(np.uint8))
    return post
def cold(k=1.0):
    def post(im, t, d, M, size):
        im = Image.blend(im, ImageOps.grayscale(im).convert('RGB'), 0.6 * k)
        return Image.fromarray(np.clip(np.asarray(im).astype(np.float32) * np.array([1 - 0.08 * k, 1 - 0.02 * k, 1 + 0.08 * k]), 0, 255).astype(np.uint8))
    return post
def ONB(basefn, cards, grow=0.03, fly=240, fin=0.6):
    """在任意底图（镜头函数）上飞入卡片：cards 同 CARDS"""
    def fn(t, d):
        im = basefn(t, d)
        for cd in cards:
            cn, cx, cy, hp, rot, tin = cd[:6]; mw = cd[6] if len(cd) > 6 else None
            if t < tin: continue
            r = DER(('card', cn, hp, rot, mw), lambda: make_card(cn, hp, rot, mw))
            u = eout((t - tin) / fin); sc = lerp(1.12, 1.0, u) * (1 + grow * (t - tin) / max(0.1, d - tin))
            g = r.resize((int(r.width * sc), int(r.height * sc)), Image.BILINEAR)
            paste_a(im, g, (cx - g.width / 2, cy + fly * (1 - u) - g.height / 2), clamp((t - tin) / 0.25))
        return im
    return fn
def DIMK(fn, k):
    def f(t, d): return Image.blend(fn(t, d), DARK, k)
    return f

# S6-01 1920年代上海街景（纪录影像）+ 章节卡 → 电车上 → 写作 → 内山书店（电影）→ 与内山完造合影
s, e = ST['S6-01'], EN['S6-01']
t1, t2, t3, t4 = at('从此不再'), at('以写作'), at('内山书店'), at('成了他的')
X(0, t1, FILM('d_tram', 1.0, 1.05), 'flash'); TAG(0, t1, T_SH)
POP(0.3, t1 - 0.1, Pop([('六｜上海', SERIF(120, 'Bold'), CREAM, W / 2, 450, 0.3, 0.09), ('1927—1936　新的信念与横站', SERIF(50), (232, 228, 218), W / 2, 600, 0.9, 0.05)], back=True))
C(t1, t2, FILM('x_tram', 1.0, 1.04)); C(t2, t3, FILM('x_write', 1.02, 1.07)); C(t3, t4, FILM('x_uchi', 1.0, 1.04)); TAG(t1, t4, T_LX)
INFO(t1 + 0.2, t4 - 0.1, '影视剧片段', '电影《鲁迅》（2005）', LX_NOTE)
X(t4, e, CARDS('hz141', [('hz141', 1140, 540, 840, -1.0, 0.2)]))
INFO(t4 + 0.3, e - 0.1, '史料 · 照片', '鲁迅与内山完造', '内山书店老板 · 鲁迅在上海的老朋友', SRC_HZ)

# S6-02 “革命文学”论争：三种刊物飞入 →“落伍者”印章砸下 → 灯下译书 → 读报（电影）→《艺术论》→ 进化的链子（回扣第五章）
s, e = ST['S6-02'], EN['S6-02']
t_tys = at_char('太阳社'); t_lw = at_char('落伍者'); t_yc = at('他却由此'); t82 = QT['Q82'][0]; t_ji = at('是他们'); t83 = QT['Q83'][0]; t_pp = at('的只信进化论')
X(s, t_yc, CARDS('w3201', [('w3201', 520, 610, 600, -3.0, 0.3), ('w3202', 960, 590, 620, 2.0, R_(t_tys, s)), ('hz146', 1400, 610, 600, -1.5, R_(t_tys + 0.6, s))]))
INFO(s + 0.4, t_lw - 0.1, '“革命文学”论争', '创造社 · 太阳社', '1928年 · 《创造月刊》《太阳月刊》《文化批判》', '出处：Wikimedia Commons；林贤治《鲁迅画传》')
def make_stamp(txt, size=150):
    f = SERIF(size, 'Black'); l, t, r, b = f.getbbox(txt); pad = 44
    w, h = int(r - l + 2 * pad), int(b - t + 2 * pad)
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    d.rounded_rectangle((8, 8, w - 9, h - 9), 16, outline=255, width=13); d.text((pad - l, pad - t), txt, font=f, fill=255)
    nz = Image.effect_noise((w, h), 70).filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 92 else int(v * 2.2))   # 印泥斑驳
    out = Image.new('RGBA', (w, h), (182, 36, 28, 255)); out.putalpha(ImageChops.multiply(m, nz))
    return out.rotate(-8, expand=True, resample=Image.BICUBIC)
STAMP = make_stamp('落伍者')
def stamp_ov(b, t, a):
    u = clamp(t / 0.16); sc = lerp(2.3, 1.0, u * u)
    g = STAMP if sc <= 1.001 else STAMP.resize((int(STAMP.width * sc), int(STAMP.height * sc)), Image.BILINEAR)
    paste_a(b, g, (W / 2 - g.width / 2, 560 - g.height / 2), a * clamp(t / 0.08) * 0.93)
ov(t_lw + 0.15, t_yc + 0.5, stamp_ov, 0.01, 0.5); SHAKES.append(t_lw + 0.31)
X(t_yc, t82, KB('a01', 1.25, 1.34, (.575, .6), (.56, .62), post=lamp((0.73, 0.12), 300, 0.2))); AITAG(t_yc, t82)
INFO(t_yc + 0.3, t82 - 0.1, '情景再现', '灯下译书', '1929—1930年 · 译卢那察尔斯基、蒲力汗诺夫的《艺术论》')
C(t82, t_ji, FILM('x_read', 1.0, 1.04)); TAG(t82, t_ji, T_LX)
X(t_ji, t83, CARDS('w3204', [('w3204', 1160, 540, 820, 1.2, 0.2)]))
INFO(t_ji + 0.3, t83 - 0.1, '史料 · 书影', '《艺术论》', '蒲力汗诺夫著 · 鲁迅译 · 1930年7月光华书局初版', SRC_WC)
X(t83, t_pp, KB('n05', 1.0, 1.1, (.5, .5), (.5, .5))); C(t_pp, e, KB('n05', 1.45, 1.62, (.5, .52), (.5, .5))); AITAG(t83, e)
DUST_A = (t83, e)

# S6-03 海婴百日 → 洗澡（电影）→“海婴与鲁迅，一岁与五十”
s, e = ST['S6-03'], EN['S6-03']; t_xt = at('有人笑他'); t41 = QT['Q41'][0]
X(s, t_xt, CARDS('hz161', [('hz161', 1140, 560, 700, 1.0, 0.2, 1300)]))
INFO(s + 0.4, t_xt - 0.1, '史料 · 照片', '海婴百日留影', '1929年9月27日，海婴在上海出生', SRC_HZ)
C(t_xt, t41, FILM('x_bath', 1.0, 1.05)); TAG(t_xt, t41, T_LX)
X(t41, e, CARDS('qj4119', [('qj4119', 1080, 540, 900, 0, 0.2)], grow=0.10, aim=(0.86, 720)))
INFO(t41 + 0.3, e - 0.1, '史料 · 照片', '“海婴与鲁迅，一岁与五十”', '1930年9月25日 · 鲁迅题字', SRC_QJ)

# S6-04 左联成立（电影）→ 讲话特写 → “横站”：弄堂两头同时飞来的箭
s, e = ST['S6-04'], EN['S6-04']; t_kh = at('他在成立大会'); t_ch = at('可此后'); t37 = QT['Q37'][0]; t_bn = at('不能正对')
X(s, t_kh, FILM('x_hall', 1.0, 1.05, off=0.2)); C(t_kh, t_ch, FILM('x_speak', 1.0, 1.06)); TAG(s, t_ch, T_LX)
INFO(s + 0.4, t_kh - 0.1, '史实', '中国左翼作家联盟成立', '1930年3月2日 · 上海中华艺术大学')
rA = random.Random(37); ARROWS = []; _tt = t_ch + 0.7
while _tt < e - 0.2:
    ARROWS.append((_tt, rA.choice((-1, 1)), rA.uniform(300, 760), rA.uniform(2600, 3400), rA.uniform(-0.05, 0.05), rA.uniform(0, 60))); _tt += rA.uniform(0.3, 0.62)
def arrows(c0, stop):
    def post(im, t, d, M, size):
        T = c0 + t; lay = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(lay)
        for ts, sd, y, v, sl, jt in ARROWS:
            u = T - ts
            if u < 0 or u > 1.3: continue
            dirn = -sd; xs = -60 if dirn > 0 else W + 60; dist = W / 2 - stop - jt + 60; trav = min(v * u, dist)
            xh = xs + dirn * trav; yh = y + sl * trav; ang = math.atan(sl)
            a = clamp(u / 0.05) * (1 - clamp((u - 0.75) / 0.5)); q = (1 - trav / dist) if trav < dist else 0
            def P(dx, dy): return (xh - dirn * (dx * math.cos(ang)) - dy * math.sin(ang) * dirn, yh - dirn * dx * math.sin(ang) + dy * math.cos(ang))
            wob = 0 if q > 0 else 4 * math.sin((u - dist / v) * 60) * math.exp(-(u - dist / v) * 6)   # 扎住后尾羽颤动
            if q > 0: dr.line((P(230, 0), P(230 + 420 * min(1, v * u / 600), 0)), fill=int(70 * a), width=3)   # 飞行拖影
            dr.line((P(0, 0), P(230, wob)), fill=int(235 * a), width=4)
            dr.line((P(0, 0), P(28, 11)), fill=int(235 * a), width=4); dr.line((P(0, 0), P(28, -11)), fill=int(235 * a), width=4)
            for k in (0, 13): dr.line((P(214 - k, wob), P(236 - k, 12 + wob)), fill=int(200 * a), width=2); dr.line((P(214 - k, wob), P(236 - k, -12 + wob)), fill=int(200 * a), width=2)
        im.paste((232, 224, 206), (0, 0), lay.filter(ImageFilter.GaussianBlur(0.7)))
    return post
X(t_ch, t_bn, KB('a03', 1.0, 1.12, (.5, .5), (.5, .47), post=arrows(t_ch - 0.5, 150)))
C(t_bn, e, KB('a03', 1.85, 1.95, (.5, .73), (.5, .745), post=arrows(t_bn, 230))); AITAG(t_ch, e)   # 推近时只取身形与两侧长影，不露脸

# S6-05 柔石 → 门口递合同 → 走进雾夜 → 东方旅社被捕 → 衣袋里的合同 → 夜街（电影）→ 五烈士依次亮起、熄灭 → 龙华
s, e = ST['S6-05'], EN['S6-05']
t_xr = at('他最信任'); t_nh = at('拿了合同'); t74 = QT['Q74'][0]; t_yd = at('衣袋里'); t_gt = at('听说官厅'); t_27 = at('2月7日')
X(s, t_xr, CARDS('hz174', [('hz174', 1160, 540, 820, -1.0, 0.2)], grow=0.06))
INFO(s + 0.4, t_xr - 0.1, '史料 · 照片', '柔石（1902—1931）', '左联作家 · 鲁迅最信任的青年朋友', SRC_HZ)
X(t_xr, t_nh, KB('a04', 1.05, 1.18, (.5, .45), (.5, .48), post=lamp((0.37, 0.2), 220, 0.18)))
INFO(t_xr + 0.3, t_nh - 0.1, '情景再现', '1931年1月16日夜', '柔石来问出书的事，带走合同抄件')
C(t_nh, t74, KB('a05', 1.0, 1.08, (.5, .5), (.5, .47), post=chain(fog(0.3, 40), lamp((0.615, 0.17), 200, 0.16))))
X(t74, t_yd, KB('a06', 1.02, 1.1, (.5, .5), (.55, .5)))
INFO(t74 + 0.3, t_yd - 0.1, '情景再现', '1931年1月17日', '上海东方旅社 · 柔石等被捕')
C(t_yd, t_gt, KB('a05', 1.6, 1.85, (.51, .5), (.51, .49), post=fog(0.22, 40))); AITAG(t_xr, t_gt); RECON(t_xr, t_gt)
C(t_gt, t_27, FILM('x_night', 1.0, 1.06)); TAG(t_gt, t_27, T_LX)
FIVE = [('hz174', '柔石'), ('hz176', '殷夫'), ('hz177', '胡也频'), ('hz179', '冯铿'), ('hz175', '李伟森')]
t_on = [at_char(nm, t_27) - 0.05 for _, nm in FIVE]; t_lh = at_char('龙华', t_27); t_bd = at('都还不到')
t_off = [t_bd + 0.45 + i * 0.22 for i in range(5)]
PW, PH, PY = 300, 410, 232
def five_prep():
    out = []
    for n, nm in FIVE:
        im = ImageOps.grayscale(IMG('card_' + n)).convert('RGB')
        r = max(PW / im.width, PH / im.height); im = im.resize((round(im.width * r) + 1, round(im.height * r) + 1), Image.LANCZOS)
        x = (im.width - PW) // 2; y = int((im.height - PH) * 0.3); im = im.crop((x, y, x + PW, y + PH))
        m = Image.new('L', (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((10, 10, PW - 10, PH - 10), 8, fill=255)
        out.append((im, m.filter(ImageFilter.GaussianBlur(7)), text_rgba(nm, SERIF(44, 'SemiBold'), CREAM + (255,), shadow=3)))
    return out
LH = text_rgba('龙华', SERIF(64, 'SemiBold'), (218, 124, 104, 255), shadow=4)
LH_D = text_rgba('1931年2月7日夜或8日晨', SERIF(40), (222, 216, 206, 255), shadow=3)
SRC5 = text_rgba('史料 · 照片　' + SRC_HZ, SANS(22), (150, 156, 156, 255))
DK = Image.new('RGB', (PW, PH), (8, 9, 11))
def portraits(im, T, lit_fn, xoff=0.0):
    for i, (pim, m, nim) in enumerate(DER('five', five_prep)):
        lit = clamp(lit_fn(i, T)); cx = W / 2 + (i - 2) * 340 + xoff
        im.paste(Image.blend(DK, pim, lit), (int(cx - PW / 2), PY), m)
        paste_a(im, nim, (cx - nim.width / 2, PY + PH + 16), clamp(lit * 1.15))
def lit5(i, T):
    v = 0.10 + 0.9 * ease((T - t_on[i]) / 0.5)
    if T > t_off[i]: v *= (1 - ease((T - t_off[i]) / 0.6)) * (0.8 + 0.2 * flick(T * 2.5, i))   # 像灯火一样熄灭
    return v
def five(c0):
    def fn(t, d):
        T = c0 + t; im = Image.new('RGB', (W, H), (8, 9, 11)); portraits(im, T, lit5)
        paste_a(im, SRC5, (72, 72), 0.8 * clamp((T - t_27) / 0.5) * (1 - clamp((T - t_off[0]) / 0.5)))
        a = clamp((T - t_lh) / 0.4)
        if a > 0:
            k = ease((T - (t_off[-1] + 0.35)) / 0.8); sc = lerp(1.0, 1.9, k)
            g = LH if sc < 1.001 else LH.resize((int(LH.width * sc), int(LH.height * sc)), Image.BILINEAR)
            paste_a(im, g, (W / 2 - g.width / 2, lerp(850, 480, k) - g.height / 2), a)
            paste_a(im, LH_D, (W / 2 - LH_D.width / 2, 620 - LH_D.height / 2), ease((T - t_off[-1] - 0.9) / 0.6))
        return im
    return fn
X(t_27, e, five(t_27 - 0.5))

# S6-06 手稿（电影）→ 珂勒惠支《牺牲》→ 母亲献出儿子 → 柔石的记念
s, e = ST['S6-06'], EN['S6-06']; t_bd6 = at_char('他在《北斗》'); t67 = QT['Q67'][0]; t_mq = at('是一个母亲'); t_ss = at('算是只有')
X(s, t_bd6, FILM('x_manu', 1.0, 1.05)); TAG(s, t_bd6, T_LX)
X(t_bd6, t67, CARDS('w16', [('w16', 1140, 560, 760, -1.0, 0.2, 1100)]))
INFO(t_bd6 + 0.3, t67 - 0.1, '史料 · 木刻', '珂勒惠支《牺牲》', '1922年 · 鲁迅选登于《北斗》创刊号（1931年9月）', '出处：Städel Museum, Frankfurt am Main')
C(t67, t_mq, KB('card_w16', 1.15, 1.25, (.5, .5), (.5, .45)))
X(t_mq, t_ss, KB('card_w16', 1.5, 1.9, (.5, .42), (.53, .3)))
X(t_ss, e, CARDS('hz174', [('hz174', 960, 520, 860, 0, 0.2)], grow=0.07))
DUST_B = (t_ss, e)

# S6-07 避居客栈 →《惯于长夜过春时》：竖排逐字显影，一联一景（客栈之夜 / 城头大王旗 / 朋辈幽影 → 刀丛 / 月光照缁衣）
s, e = ST['S6-07'], EN['S6-07']; t68, t68e = QT['Q68']
CPL = [t68 + k * (t68e - t68) / 4 for k in range(5)]; t_nx = CPL[2] + (CPL[3] - CPL[2]) / 2
A07 = lamp((0.145, 0.38), 240, 0.2)
X(s, t68, KB('a07', 1.0, 1.1, (.5, .5), (.45, .46), post=A07))
INFO(s + 0.4, t68 - 0.1, '情景再现', '避居花园庄旅馆', '1931年1月20日起 · 携许广平和海婴')
X(t68, CPL[1], KB('a07', 1.18, 1.3, (.6, .5), (.64, .5), post=A07))
def lightning(ts_list):
    def post(im, t, d, M, size):
        k = max([math.exp(-(t - x) * 9) * (1 if (t - x) < 0.06 or (t - x) > 0.12 else 0.3) for x in ts_list if t >= x] + [0])
        if k > 0.02: return Image.blend(im, Image.new('RGB', (W, H), (226, 232, 244)), 0.42 * k)
    return post
X(CPL[1], CPL[2], KB('a08', 1.0, 1.1, (.5, .5), (.56, .45), post=chain(rain(((0, 0, 1, 1),), 0.55, 0.25), lightning([0.9, 2.6]))))
def ghosts(c0):
    fg = fog(0.35, 50)
    def fn(t, d):
        T = c0 + t; im = Image.new('RGB', (W, H), (8, 9, 11)); portraits(im, T, lambda i, T: 0.32 + 0.08 * math.sin(T * 2.1 + i * 1.3), -330 - 20 * t)   # 让出右侧竖排诗句
        im = im.filter(ImageFilter.GaussianBlur(1.6)); fg(im, t, d, None, None); return im
    return fn
X(CPL[2], t_nx, ghosts(CPL[2] - 0.5))
X(t_nx, CPL[3], KB('a09', 1.15, 1.3, (.62, .45), (.64, .45)))
X(CPL[3], e, KB('a10', 1.6, 1.72, (.55, .72), (.57, .74), post=lamp((0.93, 0.83), 200, 0.15)))
AITAG(s, CPL[2]); AITAG(t_nx, e); RECON(s, t68)
HIDE.append((t68 - 0.3, t68e + 0.4))
F68 = SERIF(66, 'Medium'); P68 = [x for x in re.split('[，。]', Q['Q68']) if x]; PC68 = (t68e - t68) / 56; GL68 = {}
def g68(ch):
    if ch not in GL68: GL68[ch] = text_rgba(ch, F68, (248, 240, 222, 255), shadow=4, salpha=230, glow=10)
    return GL68[ch]
PX0, PDX, PY0, PDY = 1500, 118, 222, 86
A68 = text_rgba('——鲁迅' + QS['Q68'], SERIF(28), (214, 216, 214, 255), shadow=3, salpha=230, glow=6)
_bk = Image.new('L', (W, H), 0); ImageDraw.Draw(_bk).rounded_rectangle((PX0 - PDX - 130, PY0 - 120, PX0 + 130, PY0 + 6 * PDY + 120), 80, fill=150)
POEMBK = _bk.filter(ImageFilter.GaussianBlur(60))
def poem(b, t, a):
    T = t68 - 0.2 + t
    b.paste((6, 8, 10), (0, 0), POEMBK.point(lambda v, a=a: int(v * a)))
    for k in range(4):
        fo = 1 - clamp((T - CPL[k + 1] + 0.05) / 0.35) if k < 3 else 1.0
        if T < CPL[k] - 0.05 or fo <= 0: continue
        for m_ in range(2):
            x = PX0 - m_ * PDX
            for j, ch in enumerate(P68[2 * k + m_]):
                u = clamp((T - (CPL[k] + (m_ * 7 + j) * PC68)) / 0.4)
                if u <= 0: continue
                g = g68(ch); sc = lerp(1.18, 1.0, eout(u))
                if sc > 1.001: g = g.resize((int(g.width * sc), int(g.height * sc)), Image.BILINEAR)
                paste_a(b, g, (x - g.width / 2, PY0 + j * PDY - g.height / 2), a * clamp(u * 1.4) * fo)
    paste_a(b, A68, (W / 2 - A68.width / 2, H - 70 - A68.height / 2), a * clamp((T - t68 - 0.5) / 0.6))
ov(t68 - 0.2, e + 0.3, poem, 0.3, 0.6)

# S6-08 戴眼镜 / 落笔（电影）+ 大字《为了忘却的记念》→ 长夜的路，尽头一点光渐亮
s, e = ST['S6-08'], EN['S6-08']; t_zy = at('他终于写下'); t40 = QT['Q40'][0]; t_wz = at_char('但我知道'); t_pen = t_zy + 1.6
X(s, t_pen, FILM('x_glass', 1.0, 1.05)); C(t_pen, t40, FILM('x_pen', 1.0, 1.06)); TAG(s, t40, T_LX)
POP(t_zy, t40 + 0.2, Pop([('为了忘却的记念', SERIF(100, 'Bold'), CREAM, W / 2, 470, t_zy + 0.1, 0.1), ('1933年2月7—8日 · 柔石等遇害两周年', SERIF(40), (226, 220, 208), W / 2, 600, t_zy + 1.0, 0.04)], back=True))
def glow_grow(p, t_on, c0, R0=150, R1=460, a0=0.12, a1=0.6):
    def post(im, t, d, M, size):
        T = c0 + t; u = ease((T - t_on) / 5.5); R = int(lerp(R0, R1, u) / 10) * 10; a = lerp(a0, a1, u) * (0.9 + 0.1 * flick(T, 3))
        x, y = to_screen(M, p[0], p[1], size); m = DER(('radg', R), lambda: radial(R, 2.0))
        im.paste((255, 226, 176), (int(x - R), int(y - R)), m.point(lambda v, a=a: int(v * a)))
        if u > 0: return Image.blend(im, Image.new('RGB', (W, H), (40, 38, 34)), -0.10 * u)   # 整体随之微亮
    return post
X(t40, e, KB('a11', 1.0, 1.4, (.552, .5), (.552, .495), post=glow_grow((0.552, 0.495), t_wz, t40 - 0.5))); AITAG(t40, e)

# S6-09 1932年上海人群 → 劳工（纪录影像）→ 足踏在地上 → 与青年（电影）
s, e = ST['S6-09'], EN['S6-09']; t85 = QT['Q85'][0]; t86 = QT['Q86'][0]; t_wz9 = at('为着现在'); t_tz = at('我得引为同志')
X(s, t85, FILM('d_crowd', 1.0, 1.05)); TAG(s, t85, T_32)
INFO(s + 0.4, t85 - 0.1, '纪录影像', '上海街头', '1932年', '出处：美国国家档案馆（Internet Archive）')
X(t85, t86, FILM('d_labor', 1.0, 1.05)); TAG(t85, t86, T_30)
X(t86, t_wz9, KB('a13', 1.0, 1.08, (.5, .55), (.47, .58))); C(t_wz9, t_tz, KB('a13', 1.35, 1.48, (.3, .7), (.34, .7))); AITAG(t86, t_tz)
C(t_tz, e, FILM('x_youth', 1.0, 1.05, speed=0.92)); TAG(t_tz, e, T_LX)

# S6-10 与瞿秋白（电影）→ 瞿秋白像 + 联语手迹 → 雨中远去（电影）+ 就义日期 → 病中编校 →《海上述林》
s, e = ST['S6-10'], EN['S6-10']; t_sz = at('书赠'); t_ly = at('人生得一'); t_jy = at('瞿秋白就义后'); t_bz2 = at('病中的他'); t_hs = at_char('《海上述林》') - 0.2
X(s, t_sz, FILM('x_qiu', 1.0, 1.05)); TAG(s, t_sz, T_LX)
INFO(s + 0.4, t_sz - 0.1, '影视剧片段', '鲁迅与瞿秋白', LX_NOTE)
X(t_sz, t_jy, CARDS('qj1655', [('hz232', 640, 610, 660, -1.5, 0.2), ('qj1655', 1280, 540, 900, 1.0, R_(t_ly - 0.3, t_sz))]))
INFO(t_sz + 0.3, t_ly - 0.2, '史料 · 照片', '瞿秋白（1899—1935）', '左联领导人之一 · 鲁迅的知己', SRC_HZ)
INFO(t_ly + 0.1, t_jy - 0.1, '史料 · 手迹', '书赠瞿秋白联语', '清人何瓦琴句 · 上款“凝冰道兄属”', SRC_QJ)
X(t_jy, t_bz2, FILM('x_rain', 2.0, 2.06, (.56, .27), (.56, .26), off=4.4))   # 只取雨中远去的人力车，避开前景人头
POP(t_jy + 0.1, t_bz2 + 0.9, Pop([('1935年6月18日　瞿秋白在福建长汀就义', SERIF(46, 'SemiBold'), CREAM, W / 2, 210, t_jy + 0.15, 0.03)], back=True))
C(t_bz2, t_hs, FILM('x_ill', 1.0, 1.05)); C(t_hs, e, FILM('x_shulin', 1.0, 1.06)); TAG(t_jy, e, T_LX)
INFO(t_hs + 0.2, e - 0.1, '史实', '《海上述林》', '瞿秋白译文集 · 鲁迅编校 · 1936年以“诸夏怀霜社”名义出版')

# S6-11 书影墙（鲁迅题写的书名作底）→《中国小说史略》题字 → 刊物 → 木刻展（电影）→ 稿纸与“约三百万字” → 伏案（电影）→ 匕首、投枪 → 血路
s, e = ST['S6-11'], EN['S6-11']
t_xs = at('写出《中国小说史略》'); t_kw = at_char('还编刊物') - 0.3; t_mk = at('倡木刻'); t_fy = at('一生翻译'); t_300 = at_char('约有三百万字')
t_sh = at('上海十年'); t87 = QT['Q87'][0]; t_tq = at_char('是投枪'); t_dz = at('能和读者')
WALL = [('hz76', 330, 300, 330, -2.0), ('hz81', 760, 330, 360, 1.5), ('hz85', 1190, 300, 300, -1.0), ('hz112', 1610, 320, 320, 2.2),
        ('hz132', 330, 700, 350, 1.8), ('hz201', 760, 680, 360, -1.6), ('hz208', 1190, 700, 330, 1.0), ('hz136', 1610, 690, 350, -2.4)]
X(s, t_xs, ONB(DIMK(KB('card_inv7296', 1.25, 1.4, (.5, .35), (.5, .62)), 0.45), [(n, x, y, h, r, 0.3 + i * 0.55, 390) for i, (n, x, y, h, r) in enumerate(WALL)], fly=200))
C(t_xs, t_kw, KB('card_inv7292', 1.22, 1.34, (.49, .47), (.49, .45)))
INFO(t_xs + 0.2, t_kw - 0.1, '史料 · 题字', '鲁迅题写的书名', '《中国小说史略》等 · 全集彩插', SRC_QJ)
JOUR = [('hz97', 380, 540, 440, -2.0), ('hz154', 790, 520, 460, 1.5), ('hz151', 1200, 540, 420, -1.2), ('hz181', 1600, 520, 450, 2.0)]
C(t_kw, t_mk, ONB(DIMK(KB('card_inv7294', 1.2, 1.26, (.5, .5), (.52, .5)), 0.45), [(n, x, y, h, r, 0.02 + i * 0.13, 380) for i, (n, x, y, h, r) in enumerate(JOUR)], fly=160, fin=0.35))
C(t_mk, t_fy, FILM('x_mk', 1.0, 1.05)); TAG(t_mk, t_fy, T_LX)
TRANS = [('hz131', 330, 560, 380, -2.5, R_(t_fy + 0.3, t_fy)), ('hz207', 1590, 560, 400, 2.0, R_(t_fy + 0.7, t_fy))]
X(t_fy, t_sh, ONB(KB('a14', 1.02, 1.1, (.5, .5), (.47, .52), post=lamp((0.19, 0.19), 260, 0.18)), [c + (360,) for c in TRANS], fly=200)); AITAG(t_fy, t_sh)
F300, F_Y = SERIF(170, 'Bold'), SERIF(64, 'SemiBold')
YUE, WAN = text_rgba('约', F_Y, CREAM + (255,), shadow=5, glow=10), text_rgba('万字', F_Y, CREAM + (255,), shadow=5, glow=10)
def counter(b, t, a):   # 念到“约有三百万字”时数到 300
    T = t_fy + 0.4 + t; n = int(round(300 * eout((T - t_fy - 0.6) / (t_300 + 0.6 - t_fy - 0.6)))); g = DER(('n300', n), lambda: text_rgba(str(n), F300, CREAM + (255,), shadow=6, glow=12))
    tw = YUE.width + g.width + WAN.width - 140; x = W / 2 - tw / 2
    paste_a(b, YUE, (x, 520 - YUE.height / 2 + 30), a); paste_a(b, g, (x + YUE.width - 70, 520 - g.height / 2), a); paste_a(b, WAN, (x + YUE.width + g.width - 140, 520 - WAN.height / 2 + 30), a)
ov(t_fy + 0.4, t_sh + 0.3, counter, 0.3, 0.4)
C(t_sh, t87, FILM('x_desk', 1.0, 1.05)); TAG(t_sh, t87, T_LX)
X(t87, t_dz, KB('a15', 1.12, 1.3, (.42, .56), (.6, .45))); SHAKES.append(t_tq + 0.1)
X(t_dz, e, KB('a16', 1.0, 1.15, (.5, .5), (.5, .45))); AITAG(t87, e)

# S6-12 横眉冷对（冷调）→ 俯首（暖调）→ 左右分屏：前一句的冷，后一句的暖 → 第六次转身
s, e = ST['S6-12'], EN['S6-12']; t36 = QT['Q36'][0]; t_fs = at_char('俯首') - 0.15; t_rm = at('人们常记住'); t_wl = at('忘了后一句')
X(s, t_fs, FILM('x_cold', 1.0, 1.05, post=cold(0.8))); C(t_fs, t_rm, FILM('x_play', 1.0, 1.04, post=warm(1.0), off=0.12))
SPL_L = FILM('x_cold2', 1.0, 1.04, post=cold(0.9)); SPL_R = FILM('x_play', 1.0, 1.04, post=warm(1.0), off=4.0)
F_SP = SERIF(70, 'Bold')
SP1 = text_rgba('横眉冷对千夫指', F_SP, (214, 228, 242, 255), shadow=5, glow=10); SP2 = text_rgba('俯首甘为孺子牛', F_SP, (252, 228, 192, 255), shadow=5, glow=10)
DKH = Image.new('RGB', (960, H), (6, 8, 10))
def split(c0, xl=300, xr=480):
    def fn(t, d):
        T = c0 + t; im = Image.new('RGB', (W, H))
        kr = ease((T - t_wl + 0.1) / 0.6)
        lft = SPL_L(t, d).crop((xl, 0, xl + 960, H)); rgt = SPL_R(t, d).crop((xr, 0, xr + 960, H))
        im.paste(Image.blend(DKH, lft, lerp(1.0, 0.72, kr)), (0, 0)); im.paste(Image.blend(DKH, rgt, lerp(0.32, 1.0, kr)), (960, 0))
        ImageDraw.Draw(im).line((960, 0, 960, H), fill=(200, 196, 188), width=2)
        u1 = clamp((T - t_rm - 0.2) / 0.5); u2 = clamp((T - t_wl - 0.1) / 0.5)
        paste_a(im, SP1, (480 - SP1.width / 2, 210 - SP1.height / 2 + 20 * (1 - eout(u1))), u1 * lerp(1.0, 0.75, kr))
        paste_a(im, SP2, (1440 - SP2.width / 2, 210 - SP2.height / 2 + 20 * (1 - eout(u2))), u2)
        return im
    return fn
C(t_rm, TURN6, split(t_rm)); TAG(s, TURN6 + 0.3, T_LX)
X(TURN6, e, FILM('x_mk', 1.0, 1.06, post=dim(0.55, 0.68), off=5.0), 'flash'); SHAKES.append(TURN6 + 0.3)
POP(TURN6 + 0.15, e + 0.3, Pop([('第六次转身', SERIF(46), (226, 196, 186), W / 2, 330, TURN6 + 0.2, 0.08),
                               ('从进化论走到“新兴的无产者”', SERIF(64, 'SemiBold'), (232, 226, 214), W / 2, 460, TURN6 + 1.3, 0.06),
                               ('横站着，护着青年往前走', SERIF(96, 'Bold'), CREAM, W / 2, 600, TURN6 + 4.1, 0.1)], back=True))
build_tags()

# 片尾
def mmss(x): return f'{int(x // 60):02d}:{int(x % 60):02d}'
G_ = (70, 64, 58)
CR = [(f'样片 v3｜第六章 上海（B站母版 {mmss(OFF)}—{mmss(OFF + TOTAL_MAIN)}，无配音）', 40, 'SemiBold', INK),
      ('', 0, '', None),
      ('AI 情景再现：灯下译书、“横站”、柔石取合同、雾夜弄堂、东方旅社被捕、花园庄旅馆之夜、《惯于长夜过春时》诗意、', 26, 'Regular', G_),
      ('“夜正长，路也正长”、“足踏在地上”、稿纸与译本、“匕首”“投枪”“血路”（木刻风）；“进化的链子”沿用第五章（右上角已标注）', 26, 'Regular', G_),
      ('影视剧：电影《鲁迅》（2005，上海电影制片厂，丁荫楠导演，濮存昕饰鲁迅），非历史影像，已裁去转载台标', 26, 'Regular', G_),
      ('纪录影像：1920年代上海街景（Periscope Film）；“Shanghai, China, 1932”（美国国家档案馆）；1930年代中国劳工（AFP-27AV）', 26, 'Regular', G_),
      ('——均据 Internet Archive，已裁去时间码与黑边', 26, 'Regular', G_),
      ('历史照片、书影、手迹：林贤治《鲁迅画传》；《鲁迅全集》2005年版文前彩插；《创造月刊》《太阳月刊》《艺术论》：Wikimedia Commons', 26, 'Regular', G_),
      ('珂勒惠支《牺牲》（1922）：Städel Museum, Frankfurt am Main（公有领域）　鲁迅原文均据《鲁迅全集》2005年版', 26, 'Regular', G_)]
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
DUSTR = [DUST_A, DUST_B]   # “进化的链子”、柔石的记念两镜带浮尘
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
        print('TOTAL_MAIN', TOTAL_MAIN, 'TURN', round(TURN6, 2))
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

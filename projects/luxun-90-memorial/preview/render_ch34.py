# 样片 v3 r2：第三、四章 北京（1912—1926 从沉默到呐喊；彷徨与反抗绝望）。框架与 render_ch2.py 相同（相片卡、介绍卡、字幕、调色、颗粒）
# r2（2026-10-21）按反馈改：节奏收紧（旁白/原文说完 0.5 秒切走）；影像为主——1917年北京纪录影像（AI 上色版）、1920年代军阀战事纪录片、《觉醒年代》、电影《阿Q正传》（1981）；
# 文学作品用 AI 情景再现（狂人日记、孔乙己、故乡、祝福、在酒楼上、孤独者、秋夜、过客）；新增《在酒楼上》《孤独者》段落与《秋夜》；“吃人”从“仁义道德”字缝里放大成一组大字；修 0:35 卡顿（补树书屋片段换剪辑点）。1920x1080/25fps，无声
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
# ---------- 第三、四章时间线（r2：按紧凑时长直接排，不再沿用 storyboard 时长；本章从 0 秒起算） ----------
OFF = 332.75   # 第二章 r2 收紧后，本章在 B站母版中的起点（v2.6 分镜同步）
SEQ = [('S3-01', [{'vo': '1912年，他应教育总长蔡元培之邀进入教育部，5月随部到北京，住进宣武门外的绍兴县馆。'}]),
 ('S3-02', [{'vo': '辛亥之后，是复辟，是军阀混战。他白天上班，夜里抄古碑、读佛经。'}, {'q': 'Q15'}]),
 ('S3-03', [{'vo': '那时，老朋友钱玄同常来夜谈，劝他给《新青年》写文章。他说——'}, {'q': 'Q17'}, {'q': 'Q18'}]),
 ('S3-04', [{'vo': '1918年5月，《狂人日记》发表在《新青年》上，第一次署名“鲁迅”。'}, {'q': 'Q57'}, {'q': 'Q20'}]),
 ('S3-05', [{'q': 'Q21'}, {'sil': 1.5}]),
 ('S3-06', [{'vo': '此后几年，孔乙己、阿Q、闰土……一个个从他笔下走了出来。他一直在问自己——'}, {'q': 'Q89'}, {'vo': '这是他的第三次转身：沉默的抄碑人，发出了第一声呐喊。'}]),
 ('S4-01', [{'vo': '1923年，他和弟弟周作人失和，搬出八道湾，后来迁入西三条胡同的小院。'}]),
 ('S4-02', [{'vo': '《新青年》的同人也散了——'}, {'q': 'Q59'}]),
 ('S4-02a', [{'vo': '1924年的《在酒楼上》，当年拔神像胡子的吕纬甫，回乡教起了“子曰诗云”。他笑自己像只蝇子——'}, {'q': 'Q94'}]),
 ('S4-02b', [{'vo': '1925年的《孤独者》里，魏连殳做了杜师长的顾问，他在信里写——'}, {'q': 'Q95'}, {'vo': '后来，他为《彷徨》题诗——'}, {'q': 'Q24'}]),
 ('S4-03', [{'vo': '这一时期，他越来越多地拿起杂文。1925年的《灯下漫笔》，把几千年的历史归结为两种时代——'}, {'q': 'Q80'}, {'q': 'Q81'}]),
 ('S4-04', [{'vo': '他在屋后接出一间小书房，人称“老虎尾巴”。散文诗集《野草》，大多写在这里。'}, {'q': 'Q66'}]),
 ('S4-05', [{'vo': '《野草》里有一个过客，不知从哪里来，到哪里去。老翁说前面是坟，劝他回去。他说——'}, {'q': 'Q27'}, {'q': 'Q26'}]),
 ('S4-06', [{'q': 'Q25'}, {'vo': '看不见希望，也不向绝望下跪。这是他的第四次转身：反抗绝望。'}, {'sil': 1.0}]),
 ('S4-07', [{'vo': '他与朱安的旧式婚姻，已经过了将近二十年。1925年3月，女师大学生许广平给他写来第一封信。'}]),
 ('S4-08', [{'vo': '1926年3月18日，北京学生和市民到段祺瑞执政府门前请愿，卫队开枪。'}, {'sil': 0.8}, {'q': 'Q75'}, {'q': 'Q31'}])]
EXTRA = {'S3-04': 0.4, 'S4-08': 0.7}   # “吃人”大字落定、片尾“真的猛士”各多留一点
T = 0.0; TURN, ST, EN = {}, {}, {}
for sid, aud in SEQ:
    ST[sid] = T; t = T + LEAD
    for a in aud:
        if 'sil' in a: t += a['sil']; continue
        kind, txt = ('vo', a['vo']) if 'vo' in a else (a['q'], Q[a['q']])
        if kind == 'vo' and '转身' in txt and '这是' in txt:   # “这是他的第N次转身……”由转身字卡呈现
            a1, a2 = txt.split('这是', 1)
            if a1: t = SUB(t, 'vo', a1) + GAP
            TURN[sid] = t; t += nchar('这是' + a2) / VR + GAP; continue
        t = SUB(t, kind, txt) + GAP
    T = t - GAP + TAIL + EXTRA.get(sid, 0); EN[sid] = T
TURN3, TURN4 = TURN['S3-06'], TURN['S4-06']
TOTAL_MAIN = round(T, 2); CRED = 7.0; TOTAL = TOTAL_MAIN + CRED
assert 270 < TOTAL_MAIN < 278, TOTAL_MAIN
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
# 飘雪（《在酒楼上》窗外）：雪花坐标在原图空间，随推镜一起放大；只落在窗洞范围内
rs = random.Random(21)
SNOW = [(rs.uniform(0, 1), rs.uniform(0, 1), rs.uniform(0.035, 0.08), rs.uniform(0.004, 0.012), rs.uniform(0, 6.28), rs.choice([2, 2, 3, 3, 4])) for _ in range(170)]
WIN = (0.145, 0.02, 0.835, 0.625)   # g01 窗洞（相对坐标）
FLAKE = {}
for r in (2, 3, 4):
    m = Image.new('L', (r * 8, r * 8), 0); ImageDraw.Draw(m).ellipse((r * 3, r * 3, r * 5, r * 5), fill=255); m = m.filter(ImageFilter.GaussianBlur(r * 0.7))
    s_ = Image.new('RGBA', m.size, (240, 242, 246, 255)); s_.putalpha(m); FLAKE[r] = s_
def snow(im, TT, M, size, a=1.0):
    l, tp, r, b = WIN; sc = M[0] / 0.8
    for x0, y0, vy, sw, ph, rr in SNOW:
        v = (y0 + vy * TT) % 1.0; u = x0 + sw * math.sin(TT * 0.9 + ph)
        px, py = l + (r - l) * u, tp + (b - tp) * v
        x, y = to_screen(M, px, py, size); fl = FLAKE[rr]
        if -20 < x < W + 20 and -20 < y < H + 20:
            g = fl if sc < 1.15 else DER(('fl', rr, round(sc, 1)), lambda fl=fl, sc=sc: fl.resize((int(fl.width * min(sc, 2.2)), int(fl.height * min(sc, 2.2))), Image.BILINEAR))
            paste_a(im, g, (x - g.width / 2, y - g.height / 2), a * 0.75 * clamp(min(v, 1 - v) * 12))
# 星光（《秋夜》）：在原图天空范围内，忽明忽暗
rk = random.Random(9)
STARS = []
while len(STARS) < 46:
    x, y = rk.uniform(0.02, 0.98), rk.uniform(0.02, 0.5)
    if abs(x - 0.33) < 0.11 and y > 0.1 or abs(x - 0.66) < 0.08 and y > 0.1 or (abs(x - 0.56) < 0.05 and abs(y - 0.33) < 0.07): continue
    STARS.append((x, y, rk.uniform(0.6, 1.6), rk.uniform(0, 6.28), rk.choice([3, 4, 5])))
def star_img(r):
    s = r * 6; m = Image.new('L', (s, s), 0); d = ImageDraw.Draw(m)
    d.ellipse((s / 2 - r * .5, s / 2 - r * .5, s / 2 + r * .5, s / 2 + r * .5), fill=255)
    d.line((s / 2, s / 2 - r * 2.2, s / 2, s / 2 + r * 2.2), fill=150, width=1); d.line((s / 2 - r * 2.2, s / 2, s / 2 + r * 2.2, s / 2), fill=150, width=1)
    m = m.filter(ImageFilter.GaussianBlur(0.8)); im = Image.new('RGBA', (s, s), (226, 232, 246, 255)); im.putalpha(m); return im
def stars(im, TT, M, size):
    for x, y, sp, ph, r in STARS:
        sx, sy = to_screen(M, x, y, size); a = 0.25 + 0.75 * max(0, math.sin(TT * sp * 2.2 + ph)) ** 3
        g = DER(('star', r), lambda r=r: star_img(r)); paste_a(im, g, (sx - g.width / 2, sy - g.height / 2), a)
# 蝇子：飞一个小圈子，又回到原地（《在酒楼上》）
FLY_P = (0.45, 0.27)     # g01 窗外梅枝梢上一点（相对坐标）
def fly_img(k=1.7):
    im = Image.new('RGBA', (40, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((5, 5, 20, 16), fill=(214, 220, 228, 170)); d.ellipse((20, 5, 35, 16), fill=(214, 220, 228, 170))   # 翅
    d.ellipse((15, 9, 25, 22), fill=(16, 16, 18, 255)); im = im.resize((int(40 * k), int(30 * k)), Image.LANCZOS)
    return im.filter(ImageFilter.GaussianBlur(0.7))
FLY = fly_img()
def fly_pos(u):   # u∈[0,1]：从原点出发，逆时针绕一圈小圈子回到原点
    th = 2 * math.pi * ease(u); R = 0.05
    return FLY_P[0] + R * math.sin(th) * 0.9, FLY_P[1] - R * (1 - math.cos(th)) * 0.75 - 0.012 * math.sin(th * 2)

# ================= 第三章　北京（1912—1922）从沉默到呐喊 =================
# S3-01 1917年北京屋顶全景 + 章节卡 → 正阳门大街 → 绍兴县馆
s, e = ST['S3-01'], EN['S3-01']; t_5y = at_char('5月') - 0.2; t_xw = at_char('宣武门') - 0.3
X(0, t_5y, FILM('a_roof', 1.0, 1.05), 'flash'); TAG(0, t_xw, T_17)
POP(0.3, 3.6, Pop([('三｜北京', SERIF(120, 'Bold'), CREAM, W / 2, 450, 0.3, 0.09), ('1912—1922　从沉默到呐喊', SERIF(50), (232, 228, 218), W / 2, 600, 0.9, 0.05)], back=True))
C(t_5y, t_xw, FILM('a_st', 1.0, 1.04))
INFO(3.7, t_xw - 0.1, '纪录影像', '北京 · 1917年', A17_NOTE, SRC_IA)
X(t_xw, e, CARDS('hz56', [('hz56', 1140, 500, 820, 1.2, 0.2)]))
INFO(t_xw + 0.4, e - 0.1, '史料 · 照片', '绍兴县馆', '北京宣武门外南半截胡同 · 1912—1919年寓居', SRC_HZ)
# S3-02 军阀混战（纪录影像）→ 白天上班 → 夜里抄古碑（《觉醒年代》）→ “这寂寞……如大毒蛇”（电影《阿Q正传》片头：雪夜寓所）
s, e = ST['S3-02'], EN['S3-02']
t_bt = at_char('他白天上班') - 0.2; t_cb = at_char('夜里抄古碑') - 0.2; t_15 = at_char('这寂寞') - 0.3; t_ds = at_char('如大毒蛇') - 0.3
X(s, t_bt, FILM('r_gun', 1.02, 1.08)); TAG(s, t_bt, T_FR)
INFO(s + 0.4, t_bt - 0.1, '纪录影像', '军阀混战', '1920年代 · 纪录片《China At The Front》', SRC_IA)
C(t_bt, t_cb, FILM('a_off', 1.0, 1.04)); TAG(t_bt, t_cb, T_17)
C(t_cb, t_15, FILM('f_rub', 1.02, 1.08, speed=0.85)); TAG(t_cb, t_15, T_JX)
X(t_15, t_ds, FILM('q_yard', 1.0, 1.07)); TAG(t_15, e, T_AQ)
INFO(t_15 + 0.4, e - 0.1, '影视剧片段', '电影《阿Q正传》（1981）', AQ_NOTE)
X(t_ds, e, FILM('q_sil', 1.0, 1.06))
# S3-03 钱玄同夜谈（《觉醒年代》补树书屋）→ 铁屋子
s, e = ST['S3-03'], EN['S3-03']; t_17 = at_char('假如一间') - 0.3; t_18 = at_char('然而几个人') - 0.3
X(s, t_17, FILM('f_hall', 1.0, 1.04)); TAG(s, t_17, T_JX)
INFO(s + 0.4, t_17 - 0.1, '影视剧片段', '《觉醒年代》第13集', '补树书屋 · ' + JX_NOTE)
X(t_17, t_18, KB('d01', 1.12, 1.24, (.5, .57), (.5, .6))); AITAG(t_17, e)
INFO(t_17 + 0.5, t_18 - 0.2, '情景再现', '“铁屋子”', '《〈呐喊〉自序》中的比喻')
X(t_18, e, KB('d02', 1.04, 1.14, (.55, .5), (.6, .46)))
# S3-04 写作（《觉醒年代》）→ 《新青年》4卷5号 → 《狂人日记》首页 → 狂人夜翻历史（AI）→ “仁义道德”字缝里的“吃人”放大成一组大字
s, e = ST['S3-04'], EN['S3-04']
t_xq = at_char('发表在') - 0.2; t_dy = at_char('第一次署名') - 0.4; t_qm = at_char('署名') + 0.4; t_57 = at_char('我翻开') - 0.3; t_pai = at_char('歪歪斜斜') - 0.4
X(s, t_xq, FILM('f_write', 1.0, 1.05)); TAG(s, t_xq, T_JX)
INFO(s + 0.4, t_xq - 0.1, '影视剧片段', '《觉醒年代》第15集', '写作《狂人日记》 · 非历史影像')
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
X(t_xq, t_57, kr_fn)
INFO(t_xq + 0.3, t_dy - 0.1, '史料 · 刊物', '《新青年》第4卷第5号', '1918年5月', SRC_WC)
INFO(t_dy + 0.3, t_57 - 0.1, '史料 · 原刊', '《狂人日记》首页', '署名“鲁迅”——第一次用这个笔名', SRC_WC)
X(t_57, t_pai, KB('k01', 1.04, 1.16, (.62, .5), (.68, .55), post=lamp((0.745, 0.6), 280, 0.18))); AITAG(t_57, t_pai)
INFO(t_57 + 0.4, t_pai - 0.1, '情景再现', '《狂人日记》', '1918年4月作 · 收入《呐喊》')
t_20 = at_char('满本'); t_grow = at_char('吃人') - 0.5
rr = random.Random(5)
RY_COLS = [(x + rr.uniform(-14, 14), 400 + rr.uniform(-46, 46), rr.uniform(-7, 7)) for x in range(1560, 300, -180)]
CR_POS = [((RY_COLS[i][0] + RY_COLS[i + 1][0]) / 2, 360 + 120 * math.sin(i * 2.1)) for i in range(len(RY_COLS) - 1)]
CR_KEY = 3                                                    # 放大的那一组（居中）
def col_img(txt, f, fill, gap, shadow=4):
    h = int(len(txt) * gap + 40); w = int(f.size * 1.5); im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for i, ch in enumerate(txt): im.alpha_composite(text_rgba(ch, f, fill, shadow=shadow), (int(w / 2 - f.size / 2 - 8 - 2 * shadow), int(i * gap)))
    return im
BIGCR = col_img('吃人', SERIF(250, 'Black'), (190, 44, 34, 255), 270, shadow=10)
SMALL_K = 64 / 250
def ry_fn(t, d, e=e):
    TT = t_pai - 0.5 + t
    im, _ = kb(IMG('bg_k01'), lerp(1.06, 1.12, t / d), .5, .5); im = Image.blend(im, DARK, 0.8)
    g = ease((TT - t_grow) / 1.5)                              # 0→1：“吃人”放大到画面中央
    kdim = 1 - 0.55 * ease((TT - t_20) / 1.0) - 0.4 * g        # “仁义道德”逐渐隐去
    for i, (x, y, r) in enumerate(RY_COLS):
        a = clamp((TT - t_pai - 0.1 - i * 0.32) / 0.6) * kdim
        if a <= 0.01: continue
        c = DER(('ry', i), lambda r=r: col_img('仁义道德', SERIF(84, 'SemiBold'), (214, 204, 186, 255), 104).rotate(r, expand=True, resample=Image.BICUBIC))
        paste_a(im, c, (x - c.width / 2, y - c.height / 2 + 4 * math.sin(TT * 0.7 + i)), a)
    for i, (x, y) in enumerate(CR_POS):                         # 字缝里渐渐显出的红字
        a = clamp((TT - t_20 + 0.3 - i * 0.12) / 0.6)
        if i != CR_KEY: a *= 1 - ease((TT - t_grow) / 0.7)
        if a <= 0.01: continue
        if i == CR_KEY and g > 0:
            sc = lerp(SMALL_K, 1.0, g); cx, cy = lerp(x, W / 2, g), lerp(y, 430, g)
            c = BIGCR.resize((max(1, int(BIGCR.width * sc)), max(1, int(BIGCR.height * sc))), Image.BILINEAR)
            paste_a(im, c, (cx - c.width / 2, cy - c.height / 2), a)
        else:
            c = DER('crs', lambda: col_img('吃人', SERIF(64, 'Bold'), (196, 58, 44, 255), 78)); paste_a(im, c, (x - c.width / 2, y - c.height / 2), a)
    k = clamp((e - TT) / 0.45)                                 # 收尾压黑，下一镜头从黑场淡入
    return im if k >= 1 else Image.blend(DARK, im, k)
clip(t_pai - 0.5, e, ry_fn, 'fade', 1.0)
# S3-05 1917年北京的孩子（纪录影像）→ “救救孩子……”（画面中央大字 + 回声）
s, e = ST['S3-05'], EN['S3-05']; t_jj = at('救救孩子')
clip(s, e + 0.5, FILM('a_kid', 1.0, 1.05, post=dim(0, 0.5, t_jj - s, t_jj - s + 1.0)), 'fade', 0.6); TAG(s, e, T_17)
INFO(s + 0.4, t_jj - 0.2, '纪录影像', '北京的孩子 · 1917年', A17_NOTE, SRC_IA)
HIDE.append((t_jj - 0.05, e + 0.4))
JJ = text_rgba('救救孩子……', SERIF(100, 'Bold'), CREAM, shadow=8)
def echo(b, t, a):
    paste_a(b, JJ, (W / 2 - JJ.width / 2, 470 - JJ.height / 2), a * clamp(t / 0.6))
    for k in range(3):
        u = (t - 0.5 - k * 0.7) / 2.0
        if 0 < u < 1:
            s_ = 1 + 0.32 * u; g = JJ.resize((int(JJ.width * s_), int(JJ.height * s_)), Image.BILINEAR)
            paste_a(b, g, (W / 2 - g.width / 2, 470 - g.height / 2), a * 0.28 * (1 - u))
ov(t_jj, e + 0.4, echo, 0.01, 0.6)
# S3-06 毛笔写稿 → 人物快切（孔乙己 / 阿Q / 闰土 / 祥林嫂）→ “他一直在问自己” → 看客 → 第三次转身
s, e = ST['S3-06'], EN['S3-06']
t_ky = at_char('孔乙己') - 0.1; t_wen = at_char('他一直在问') - 0.2; t_xd = at_char('现代的') - 0.2
X(s, t_ky, FILM('q_brush', 1.0, 1.05)); TAG(s, t_ky, T_AQ)
MONT = [KB('e01', 1.02, 1.10, (.42, .55), (.44, .6)), FILM('q_circle', 1.0, 1.06), KB('e02', 1.0, 1.08, (.6, .55), (.64, .6)), KB('e03', 1.02, 1.12, (.56, .55), (.58, .52))]
step = (t_wen - t_ky) / len(MONT)
for i, fn in enumerate(MONT): C(t_ky + i * step, t_ky + (i + 1) * step, fn)
TAG(t_ky, t_wen, 'AI 情景再现 · 电影《阿Q正传》（1981）')
INFO(t_ky + 0.2, t_wen - 0.1, '情景再现 · 影视剧片段', '孔乙己 · 阿Q · 闰土 · 祥林嫂', '《孔乙己》1919　《阿Q正传》1921　《故乡》1921　《祝福》1924')
C(t_wen, t_xd, FILM('q_smoke', 1.0, 1.06)); TAG(t_wen, TURN3 + 0.7, T_AQ)
C(t_xd, TURN3 + 0.7, FILM('q_face', 1.0, 1.06))
X(TURN3 + 0.7, e, KB('bg_hz61', 1.0, 1.08, (.5, .5), (.5, .5)), 'flash'); SHAKES.append(TURN3 + 1.05)
POP(TURN3 + 0.9, e + 0.2, Pop([('第三次转身', SERIF(46), (226, 196, 186), W / 2, 380, TURN3 + 0.9, 0.08),
                               ('沉默的抄碑人，发出了第一声呐喊', SERIF(84, 'Bold'), CREAM, W / 2, 510, TURN3 + 1.3, 0.08)]))

# ================= 第四章　北京（1923—1926）彷徨与反抗绝望 =================
# S4-01 1917年北京城门 + 章节卡 → 八道湾 → 西三条
s, e = ST['S4-01'], EN['S4-01']; t_bc = s + 3.0; t_xs = at_char('后来迁入') - 0.2   # 章节卡收完再飞入八道湾照
X(s, t_bc, FILM('a_wall', 1.0, 1.05), 'flash'); TAG(s, t_bc, T_17)
POP(s + 0.3, s + 2.9, Pop([('四｜北京', SERIF(120, 'Bold'), CREAM, W / 2, 450, s + 0.4, 0.09), ('1923—1926　彷徨与反抗绝望', SERIF(50), (232, 228, 218), W / 2, 600, s + 1.0, 0.05)], back=True))
X(t_bc, t_xs, CARDS('qj103', [('qj103', 1140, 500, 640, -1.2, 0.6)]))
INFO(t_bc + 0.3, t_xs - 0.1, '史料 · 照片', '八道湾11号', '1919年11月迁入 · 1923年8月搬出', SRC_QJ)
X(t_xs, e, CARDS('hz80', [('hz80', 1140, 490, 780, 1.2, 0.2)]))
INFO(t_xs + 0.4, e - 0.1, '史料 · 照片', '西三条胡同21号', '1924年5月迁入 · 今北京鲁迅博物馆内', SRC_HZ)
# S4-02 同人星散（《觉醒年代》，渐灰）
s, e = ST['S4-02'], EN['S4-02']
X(s, e, FILM('f_group', 1.0, 1.05, speed=0.8, gray=lambda t, d: 0.9 * ease(t / d), post=dim(0, 0.35, 2.0, 7.5))); TAG(s, e, T_JX)
INFO(s + 0.4, e - 0.1, '影视剧片段', '《觉醒年代》第13集', '《新青年》同人 · 非历史影像')
# S4-02a 《在酒楼上》：雪中酒楼（飘雪）→ 推近窗外，一只蝇子飞了个小圈子，又停回原处
s, e = ST['S4-02a'], EN['S4-02a']; t_94 = at_char('飞了一个') - 0.2
def g01_fn(t, d, s=s):
    TT = s - 0.5 + t; u1 = clamp((TT - s) / (t_94 - s)); u2 = ease((TT - t_94 + 1.0) / 1.8)
    z = lerp(lerp(1.0, 1.08, u1), 1.75, u2); cx = lerp(.5, FLY_P[0], u2); cy = lerp(lerp(.5, .46, u1), FLY_P[1] - 0.03, u2)
    src = IMG('g01'); im, M = kb(src, z, cx, cy); snow(im, TT, M, src.size)
    uf = (TT - t_94 - 0.5) / 2.6                     # 起飞 → 绕圈 → 落回
    if TT > t_94 - 0.8:
        a = clamp((TT - t_94 + 0.8) / 0.6)
        if 0 < uf < 1:                                # 飞行轨迹（淡）
            for k in range(1, 9):
                uu = uf - k * 0.025
                if uu > 0: x, y = to_screen(M, *fly_pos(uu), src.size); paste_a(im, FLY, (x - FLY.width / 2, y - FLY.height / 2), a * 0.35 * (1 - k / 9))
        x, y = to_screen(M, *fly_pos(clamp(uf)), src.size); paste_a(im, FLY, (x - FLY.width / 2, y - FLY.height / 2), a)
    return im
X(s, e, g01_fn); AITAG(s, e)
INFO(s + 0.4, t_94 - 1.2, '情景再现', '《在酒楼上》', '1924年2月作 · 收入《彷徨》')
# S4-02b 《孤独者》：做了杜师长顾问的魏连殳（两种景别）→ 月光下潮湿的石路（《题〈彷徨〉》）
s, e = ST['S4-02b'], EN['S4-02b']; t_95 = at_char('我已经躬行') - 0.3; t_ti = at_char('他为《彷徨》') - 0.4; t_24 = at_char('寂寞新文苑') - 0.2
X(s, t_95, KB('g02', 1.0, 1.08, (.5, .5), (.5, .47))); AITAG(s, e)
INFO(s + 0.4, t_95 - 0.1, '情景再现', '《孤独者》', '1925年10月作 · 收入《彷徨》')
XQ(t_95, t_ti, KB('g02', 1.55, 1.75, (.5, .4), (.5, .37)))
X(t_ti, e, KB('g03', 1.0, 1.14, (.55, .5), (.555, .47)))
INFO(t_ti + 0.3, t_24 + 0.6, '情景再现', '《孤独者》结尾', '坦然地在潮湿的石路上走，月光底下')
# S4-03 伏案写杂文 → 灯下 → 1917年街头人群（压暗）上排字：两种时代的循环 → “第三样时代”
s, e = ST['S4-03'], EN['S4-03']; t_dx = at_char('1925年的《灯') - 0.2; t_ny = at_char('把几千年') - 0.3
t_l1, t_l2 = at_char('想做奴隶'), at_char('暂时做稳'); t_81 = at_char('而创造') - 0.1; t_3 = at_char('第三样时代'); t_qn = at_char('是现在的青年')
X(s, t_dx, FILM('q_write', 1.0, 1.05)); TAG(s, t_dx, T_AQ)
X(t_dx, t_ny, KB('h02', 1.04, 1.12, (.42, .5), (.46, .52), post=lamp((0.222, 0.36), 300, 0.2))); AITAG(t_dx, t_ny)
X(t_ny, e, FILM('a_crowd', 1.0, 1.06, post=dim(0.5, 0.6, 0, 20))); TAG(t_ny, e, T_17)
INFO(t_ny + 0.3, t_l1 - 0.3, '纪录影像', '北京街头 · 1917年', A17_NOTE, SRC_IA)
L1 = text_rgba('想做奴隶而不得的时代', SERIF(78, 'SemiBold'), CREAM, shadow=6)
L2 = text_rgba('暂时做稳了奴隶的时代', SERIF(78, 'SemiBold'), CREAM, shadow=6)
DOT = Image.new('RGBA', (60, 60), (0, 0, 0, 0)); _m = Image.new('L', (60, 60), 0); ImageDraw.Draw(_m).ellipse((22, 22, 38, 38), fill=255)
DOT.paste((236, 200, 170, 255), (0, 0), _m.filter(ImageFilter.GaussianBlur(3)))
def ring_img(a):
    im = Image.new('RGBA', (1300, 420), (0, 0, 0, 0)); ImageDraw.Draw(im).ellipse((20, 20, 1280, 400), outline=(214, 200, 182, int(150 * a)), width=3)
    return im
CY = 420
def loop_ov(b, t, a):
    TT = t_l1 - 0.2 + t; br = ease((TT - t_81) / 2.4); fo = 1 - ease((TT - t_3 + 0.3) / 0.8)   # 循环被打破：两行分开、变淡，“第三样时代”出现时隐去
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
ov(t_l1 - 0.2, e + 0.3, loop_ov, 0.3, 0.6)
POP(t_3, e + 0.3, Pop([('第三样时代', SERIF(136, 'Bold'), CREAM, W / 2, CY, t_3, 0.12)]))
POP(t_qn, e + 0.3, Pop([('是现在的青年的使命', SERIF(54, 'SemiBold'), (228, 200, 170), W / 2, CY + 170, t_qn, 0.07)]))
# S4-04 “老虎尾巴” → 《秋夜》：两株枣树（星光闪烁，镜头从这一株摇到那一株）
s, e = ST['S4-04'], EN['S4-04']; t_yc = at_char('散文诗集') - 0.3; t_y1 = at_char('一株是枣树'); t_y2 = at_char('还有一株')
X(s, t_yc, CARDS('qj497', [('qj497', 1140, 500, 640, -1.2, 0.2, 1500)]))
INFO(s + 0.4, t_yc - 0.1, '史料 · 照片', '“老虎尾巴”', '西三条21号 · 北屋后接出的小书房', SRC_QJ)
TL, TR = (0.335, 0.47), (0.665, 0.47)
def h01_fn(t, d):
    TT = t_yc - 0.5 + t; u1 = ease((TT - t_y1 + 1.2) / 1.6); u2 = ease((TT - t_y2 + 0.3) / 1.6)
    z = lerp(lerp(1.0, 1.06, clamp((TT - t_yc) / 4)), 1.7, u1); cx = lerp(lerp(.5, TL[0], u1), TR[0], u2); cy = lerp(.47, TL[1], u1)
    src = IMG('h01'); im, M = kb(src, z + 0.04 * u2, cx, cy); stars(im, TT, M, src.size); return im
X(t_yc, e, h01_fn); AITAG(t_yc, e)
INFO(t_yc + 0.4, t_y1 - 1.3, '情景再现', '《野草·秋夜》', '1924年9月15日作 · 《野草》首篇')
# S4-05 《过客》
s, e = ST['S4-05'], EN['S4-05']; t_27 = at_char('但是，那前面') - 0.3; t_26 = at_char('我以为绝望') - 0.3
X(s, t_27, KB('c01', 1.02, 1.12, (.45, .56), (.42, .56))); AITAG(s, e)
INFO(s + 0.6, t_27 - 0.2, '情景再现', '《野草·过客》', '1925年3月2日作')
X(t_27, t_26, KB('c02', 1.04, 1.13, (.5, .5), (.56, .55)))
X(t_26, e, KB('c01', 1.75, 1.95, (.56, .5), (.58, .46)))
# S4-06 1925 年像（“看不见希望，也不向绝望下跪”）→ 第四次转身
s, e = ST['S4-06'], EN['S4-06']
X(s, TURN4 + 0.7, CARDS('hz94', [('hz94', 1140, 480, 800, -1.0, 0.2)], grow=0.08))
INFO(s + 0.4, TURN4 - 0.2, '史料 · 照片', '鲁迅', '1925年7月 · 北京　为英译本《阿Q正传》所摄', SRC_HZ)
X(TURN4 + 0.7, e, KB('bg_hz94', 1.0, 1.08, (.5, .5), (.5, .5)), 'flash'); SHAKES.append(TURN4 + 1.05)
POP(TURN4 + 0.9, e + 0.2, Pop([('第四次转身', SERIF(46), (226, 196, 186), W / 2, 380, TURN4 + 0.9, 0.08),
                               ('反抗绝望', SERIF(124, 'Bold'), CREAM, W / 2, 520, TURN4 + 1.3, 0.16)]))
# S4-07 朱安 → 许广平 → 书信
s, e = ST['S4-07'], EN['S4-07']; t_xg = at_char('1925年3月') - 0.3; t_xin = at_char('给他写来') - 0.4
X(s, t_xg, CARDS('zhuan', [('zhuan', 1140, 490, 740, -1.2, 0.2)]))
INFO(s + 0.4, t_xg - 0.1, '史料 · 照片', '朱安', '1906年奉母命与鲁迅成婚', SRC_WC)
X(t_xg, t_xin, CARDS('hz95', [('hz95', 1140, 490, 800, 1.2, 0.2)]))
INFO(t_xg + 0.4, t_xin - 0.1, '史料 · 照片', '许广平', '北京女子师范大学学生', SRC_HZ)
X(t_xin, e, CARDS('qj3653', [('qj3653', 1140, 500, 840, -1.0, 0.2)], grow=0.05))
INFO(t_xin + 0.3, e - 0.1, '史料 · 手迹', '鲁迅致许广平信', '1925年 · 二人通信后编为《两地书》', SRC_QJ)
# S4-08 三一八 → 刘和珍 → “真的猛士”（中央大字）
s, e = ST['S4-08'], EN['S4-08']
t_103 = at_char('到段祺瑞') - 0.3; t_kq = at_char('卫队开枪'); t_lh = at_char('在四十余') - 0.5; t_31 = at_char('真的猛士') - 0.3; t_face = t_lh + 3.0
X(s, t_103, CARDS('hz102', [('hz102', 1140, 500, 640, -1.0, 0.2, 1560)]))
INFO(s + 0.4, t_103 - 0.1, '史料 · 照片', '三一八请愿', '1926年3月18日 · 北京', SRC_HZ)
def kq_post(im, t, d):
    k = 0.5 * eout((t - (t_kq - t_103 + 0.5)) / 0.35)
    if k > 0: im.paste(Image.blend(im, DARK, k))
X(t_103, t_lh, CARDS('hz103', [('hz103', 1140, 490, 800, 1.2, 0.2)], post=kq_post))
INFO(t_103 + 0.3, t_kq - 0.1, '史料 · 照片', '请愿群众与执政府卫队对峙', '1926年3月18日 · 北京', SRC_HZ)
X(t_lh, t_face, CARDS('hz104', [('hz104', 1140, 480, 800, -1.0, 0.2)]))
INFO(t_lh + 0.3, t_31 - 0.2, '史料 · 照片', '刘和珍（后排中）', '女师大学生自治会主席 · 1926年3月18日遇难', SRC_HZ)
X(t_face, t_31, KB('card_hz104', 1.22, 1.36, (.5, .2), (.5, .19)))
X(t_31, e, KB('bg_hz104', 1.0, 1.04, (.5, .5), (.5, .5), post=dim(0.9, 0.95, 0, 10)))
HIDE.append((t_31 + 0.1, e + 0.6))
t_zm, t_zs = at_char('敢于直面'), at_char('敢于正视')
POP(t_31 + 0.3, e + 0.3, Pop([('真的猛士，', SERIF(84, 'Bold'), CREAM, W / 2, 330, t_31 + 0.4, 0.1)]))
POP(t_zm, e + 0.3, Pop([('敢于直面惨淡的人生，', SERIF(72, 'SemiBold'), CREAM, W / 2, 470, t_zm, 0.08)]))
POP(t_zs, e + 0.3, Pop([('敢于正视淋漓的鲜血。', SERIF(72, 'SemiBold'), CREAM, W / 2, 590, t_zs, 0.08)]))
ATT31 = text_rgba('——鲁迅《记念刘和珍君》', SERIF(36), (214, 210, 200, 255), shadow=4)
ov(t_zs + 1.2, e + 0.3, lambda b, t, a: paste_a(b, ATT31, (W / 2 + 200 - ATT31.width / 2, 720), a), 0.6, 0.5)
build_tags()
# 片尾
def mmss(x): return f'{int(x // 60):02d}:{int(x % 60):02d}'
CR = [(f'样片 v3 r2｜第三、四章 北京（B站母版 {mmss(OFF)}—{mmss(OFF + TOTAL_MAIN)}，无配音）', 40, 'SemiBold', INK),
      ('', 0, '', None),
      ('AI 情景再现：铁屋子、《狂人日记》《孔乙己》《故乡》《祝福》《在酒楼上》《孤独者》《秋夜》《过客》、灯下写作（右上角已标注）', 26, 'Regular', (70, 64, 58)),
      ('影视剧：《觉醒年代》（2021）第8、13、15集，曹磊饰鲁迅；电影《阿Q正传》（1981，上海电影制片厂，岑范导演）', 26, 'Regular', (70, 64, 58)),
      ('以上均为非历史影像，已裁去原片字幕与台标', 26, 'Regular', (70, 64, 58)),
      ('纪录影像：Benjamin Brodsky 摄1917年北京（AI 修复上色版）、《China At The Front》（1920年代）——Internet Archive', 26, 'Regular', (70, 64, 58)),
      ('历史照片、手迹：林贤治《鲁迅画传》；《鲁迅全集》2005年版文前彩插　《新青年》原刊、朱安像：Wikimedia Commons（公有领域）', 26, 'Regular', (70, 64, 58)),
      ('鲁迅原文均据《鲁迅全集》2005年版', 26, 'Regular', (70, 64, 58))]
CRS = [text_rgba(c, SERIF(s, w), f + (255,)) if c else None for c, s, w, f in CR]
assert max(c.width for c in CRS if c) < W - 80, [c.width for c in CRS if c]
def cred(t, d):
    im = PAPER.copy(); y = 280
    for i, c in enumerate(CRS):
        if c: paste_a(im, c, (W / 2 - c.width / 2, y), clamp((t - 0.3 - i * 0.12) / 0.8))
        y += 80 if i == 0 else (30 if c is None else 58)
    return im
X(TOTAL_MAIN, TOTAL, cred)

WM = text_rgba('样片 v3 r2 · 无配音', SANS(22, 'Light'), (255, 255, 255, 255), shadow=2)

# ---------- 浮尘（淡） ----------
rnd = random.Random(11)
DUST = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(-12, 12), rnd.uniform(-18, -5), rnd.choice([2, 3, 4, 6]), rnd.uniform(0, 6.28)) for _ in range(40)]
SPR = {}
for r in (2, 3, 4, 6):
    m = Image.new('L', (r * 6, r * 6), 0); ImageDraw.Draw(m).ellipse((r * 2, r * 2, r * 4, r * 4), fill=255); m = m.filter(ImageFilter.GaussianBlur(r * 0.8))
    s = Image.new('RGBA', m.size, (236, 236, 230, 255)); s.putalpha(m); SPR[r] = s
DUSTR = [(t_17, ST['S3-04']), (ST['S4-05'], EN['S4-05'])]
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
        print('TOTAL_MAIN', TOTAL_MAIN, 'TURN', round(TURN3, 2), round(TURN4, 2))
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

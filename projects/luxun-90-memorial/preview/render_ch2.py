# 样片 v3：第二章 南京·东京·仙台（1898—1909 弃医从文）。框架与 render_preview_v3.py 相同（同一套相片卡、介绍卡、字幕、调色、颗粒）
# 真实素材为主；幻灯片放映、讲堂欢呼、雪地背影为 AI 情景再现（右上角标注）。1920x1080/25fps，无声，旁白与原文以字幕显示
# r2（2026-10-21）：节奏收紧——每个镜头在最后一句旁白/原文（含分镜设计的静默）结束后 0.5 秒切走；父亲照（与第一章重复）换成 AI“仙台寓所夜读”；幻灯片小字只写“画面为情景再现”。
# 先运行 prep_v3.py 与 prep_ch2.py 生成 preview/src3/。用法：python3 render_ch2.py [--plan] [--stills 1,2,3] [--part k/n out.mp4]（k 从 0 开始）
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
    for p in parts:
        if cur and (len(cur) + len(p) > n or (p.startswith('“') and cur.endswith('。'))): out.append(cur); cur = p
        else: cur += p
    if cur: out.append(cur)
    if len(out) >= 2 and nchar(out[-1]) <= 2 and len(out[-2]) + len(out[-1]) <= 24: _x = out.pop(); out[-1] += _x   # 句尾“提出——”之类并入上一行
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
# ---------- 第二章字幕（时序与 storyboard 一致；本章从 0 秒起算，B站母版对应 +179.5 秒） ----------
OFF = 179.5
T = 0.0; TURN2 = None; SHOTS = []
for sid in ['S2-01', 'S2-02', 'S2-03', 'S2-04', 'S2-05', 'S2-06', 'S2-07', 'S2-08', 'S2-09']:
    s = SHOT[sid]; t = T + 0.4
    for a in s.get('audio', []):
        if 'sil' in a: t += a['sil']; continue
        if 'vo' in a: kind, txt = 'vo', a['vo']
        elif 'q' in a: kind, txt = a['q'], Q[a['q']]
        else: continue
        if sid == 'S2-08':   # 后半句由“第二次转身”字卡呈现
            a1, a2 = txt.split('这是', 1); t = SUB(t, 'vo', a1) + GAP; TURN2 = t; t += nchar('这是' + a2) / VR + GAP; continue
        t = SUB(t, kind, txt) + GAP
    SHOTS.append((sid, T, s['dur'], max(0.0, t - GAP - T) if t > T + 0.4 + 1e-6 else 0.0)); T += s['dur']
TOTAL_MAIN = 167.0; CRED = 7.0; TOTAL = TOTAL_MAIN + CRED
# 节奏收紧：下面的画面仍按分镜原时长编排，最后用 M() 把每个镜头“声音结束 + TAIL”之后的留白压缩到 TAIL（声音段内只平移，不变速）
TAIL = 0.5; NEWD = {'S2-01': 4.0}   # 章节卡只有音乐，5 秒压到 4 秒
MAP, _ns = [], 0.0
for _sid, _os, _od, _A in SHOTS:
    _nd = NEWD.get(_sid, min(_od, _A + TAIL)); MAP.append((_os, _od, _A, _ns, _nd)); _ns += _nd
NEW_MAIN = _ns
def M(t):
    if t < 0: return t
    for os_, od, A, ns_, nd in MAP:
        if t < os_ + od:
            r = t - os_
            return ns_ + r if r <= A else ns_ + A + (r - A) * (nd - A) / (od - A)
    return t - TOTAL_MAIN + NEW_MAIN
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
SRC_HZ, SRC_QJ = '出处：林贤治《鲁迅画传》', '出处：《鲁迅全集》2005年版'

# ================= 第二章　南京·东京·仙台 =================
# S2-01 章节卡 → 矿路学堂课本
X(0, 6.6, CARDS('hz13', [('hz13', 1140, 490, 600, -1.4, 3.4)]), 'flash')
POP(0.3, 3.6, Pop([('二｜南京·东京·仙台', SERIF(120, 'Bold'), CREAM, W / 2, 450, 0.3, 0.09), ('1898—1909　弃医从文', SERIF(50), (232, 228, 218), W / 2, 600, 0.9, 0.05)], back=True))
INFO(3.8, 6.5, '史料 · 实物', '鲁迅在矿路学堂用过的课本', '南京 · 江南陆师学堂附设矿务铁路学堂', SRC_HZ)
# S2-02 《时务报》与严复 → 《天演论》 → 物竞天择
t_ty = 11.4
X(6.6, t_ty, CARDS('hz14a', [('hz14a', 930, 560, 520, -1.8, 0.2), ('hz14b', 1450, 540, 560, 2.0, 1.4)]))
INFO(7.0, t_ty - 0.1, '史料 · 报刊 / 照片', '《时务报》与严复', '维新派报刊 · 《天演论》译者', SRC_HZ)
X(t_ty, 16.2, CARDS('w0502', [('w0502', 1140, 500, 780, 1.2, 0.2)]))
INFO(t_ty + 0.4, 16.1, '史料 · 书影', '严复译《天演论》', '慎始基斋本 · 吴汝纶序', '出处：中国现代文学馆')
X(16.2, 21, KB('bg_w0502', 1.0, 1.08, (.5, .5), (.5, .5)))
POP(16.4, 21.2, Pop([('物竞天择', SERIF(150, 'Bold'), CREAM, W / 2, 440, 16.5, 0.16), ('——严复译《天演论》', SERIF(40), (214, 210, 200), W / 2 + 120, 610, 17.4, 0.04)]))
# S2-03 弘文学院 → “断发照” → 《自题小像》
t_ph = at_char('这张照片') - 0.6
X(21, t_ph, CARDS('hz18', [('hz18', 1140, 480, 760, -1.4, 0.2)]))
INFO(21.4, t_ph - 0.1, '史料 · 照片', '弘文学院毕业照', '1904年 · 东京', SRC_HZ)
X(t_ph, 30.4, CARDS('qj97', [('qj97', 1140, 475, 760, 1.4, 0.2)], grow=0.05))
INFO(t_ph + 0.4, 30.3, '史料 · 照片', '“断发照”', '1903年 · 东京　背面题《自题小像》赠许寿裳', SRC_QJ)
X(30.4, 37, CARDS('hz24b', [('hz24b', 1140, 500, 820, -1.0, 0.2)]))
INFO(30.8, 36.9, '史料 · 手迹', '《自题小像》', '1903年作 · 1931年重写', SRC_HZ)
# S2-04 仙台医专 → 住处 → 父亲（“救治像我父亲似的被误的病人”）
t_fa = at('我的梦很美满') - 0.3
X(37, 40.9, CARDS('hz30', [('hz30', 1110, 500, 520, -1.2, 0.2, 1240)]))
INFO(37.4, 40.8, '史料 · 照片', '仙台医学专门学校', '1904年秋入学 · 日本仙台', SRC_HZ)
X(40.9, t_fa, CARDS('hz31', [('hz31', 1140, 480, 640, 1.4, 0.2)]))
INFO(41.3, t_fa - 0.1, '史料 · 照片', '鲁迅在仙台的住处', '日本仙台', SRC_HZ)
X(t_fa, 54, KB('b05', 1.02, 1.15, (.56, .48), (.42, .6))); AITAG(t_fa, 54)   # 父亲照已在第一章用过，这里换成 AI 情景再现
INFO(t_fa + 0.4, 53.9, '情景再现', '仙台寓所的夜晚', '1904—1906年 · 医专学生周树人')
# S2-05 藤野严九郎 → 解剖学笔记
X(54, 60.6, CARDS('hz33', [('hz33', 1140, 480, 780, -1.4, 0.2)]))
INFO(54.4, 60.5, '史料 · 照片', '藤野严九郎', '仙台医专解剖学教授', SRC_HZ)
X(60.6, 69, CARDS('hz34', [('hz34', 1140, 480, 760, 1.0, 0.2)], grow=0.08))
INFO(61.0, 68.9, '史料 · 手稿', '鲁迅的解剖学笔记', '藤野先生用红笔批改', SRC_HZ)
# S2-06 幻灯片事件（情景再现；不用任何真实处决影像）
t_me = 85.2; t_wan = at('“万岁') - 0.2
X(69, 76.6, KB('b01', 1.0, 1.14, (.38, .5), (.5, .45)), 'black'); AITAG(69, 76.6)
INFO(69.8, 76.4, '情景再现', '日俄战争幻灯片', '仙台医专 · 细菌学课 · 1905—1906')
X(76.6, t_me, KB('b01', 2.05, 2.4, (.745, .35), (.745, .36))); AITAG(76.6, t_me)
X(t_me, t_wan, CARDS('hz35', [('hz35', 1140, 480, 800, -1.2, 0.2)], grow=0.06))
INFO(t_me + 0.3, t_wan - 0.1, '史料 · 照片', '与仙台医专同学合影', '1904年 · 后排右一为鲁迅', SRC_HZ)
X(t_wan, 93.2, KB('b02', 1.04, 1.12, (.5, .5), (.5, .46))); AITAG(t_wan, 93.2)
X(93.2, 98, KB('b03', 1.06, 1.2, (.7, .42), (.74, .38), post=dim(0.0, 0.8, 1.6, 4.6))); AITAG(93.2, 97.4)
NOTE = text_rgba('画面为情景再现', SANS(28), (214, 216, 214, 255), shadow=3)
ov(93.6, 97.8, lambda b, t, a: paste_a(b, NOTE, (W / 2 - NOTE.width / 2, H - 110 - NOTE.height / 2), a), 0.6, 0.6)
# S2-07 走出讲堂，走进雪地 → “改变他们的精神”
X(98, 104, KB('b04', 1.0, 1.06, (.5, .5), (.5, .5)), 'black'); AITAG(98, 104)
X(104, 109.8, KB('b04', 1.5, 1.66, (.49, .46), (.49, .44))); AITAG(104, 109.4)
X(109.8, 123, KB('bg_b04', 1.0, 1.08, (.5, .5), (.5, .5)))
t_gb, t_wy = at_char('改变他们的精神'), at_char('当然要推文艺')
POP(110.0, 123.2, Pop([('第一要著', SERIF(46), (226, 196, 186), W / 2, 330, max(110.1, t_gb - 1.2), 0.08),
                       ('改变他们的精神', SERIF(104, 'Bold'), CREAM, W / 2, 470, t_gb, 0.11)]))
POP(t_wy, 123.2, Pop([('当然要推文艺', SERIF(60, 'SemiBold'), (228, 200, 170), W / 2, 640, t_wy, 0.1)]))
# S2-08 藤野赠照 → 背面“惜别” → 第二次转身
t_xb = at('背面写着两个字') - 0.5
X(123, t_xb, CARDS('qj496', [('qj496', 1060, 500, 600, -1.0, 0.2, 1560)]))
INFO(123.4, t_xb - 0.1, '史料 · 照片', '藤野先生赠给鲁迅的照片', '1906年 · 正面与背面', SRC_QJ)
X(t_xb, TURN2 + 0.7, KB('card_qj496', 1.9, 2.2, (.85, .28), (.85, .25)))
X(TURN2 + 0.7, 139, KB('bg_qj496', 1.0, 1.08, (.5, .5), (.5, .5)), 'flash'); SHAKES.append(TURN2 + 1.05)
POP(TURN2 + 0.9, 139.2, Pop([('第二次转身', SERIF(46), (226, 196, 186), W / 2, 380, TURN2 + 0.9, 0.08),
                             ('放下手术刀，去医治人的精神', SERIF(86, 'Bold'), CREAM, W / 2, 510, TURN2 + 1.3, 0.09)]))
# S2-09 《河南》 → 《文化偏至论》“其首在立人” → 东京 → 《新生》 → 《域外小说集》“21本” → 回国
t_ls, t_xs, t_yw, t_21 = at_char('其首在立人'), at_char('可《新生》') - 0.3, at_char('《域外小说集》') - 0.3, at_char('二十一本'); t_hg = t_21 + 2.2
X(139, 145.4, CARDS('hz40', [('hz40', 1140, 500, 800, -1.2, 0.2)]))
INFO(139.4, 145.3, '史料 · 刊物', '《河南》月刊', '1908年 · 东京　连载《摩罗诗力说》的一页', SRC_HZ)
FEN_HL = (0.605, 0.2475, 0.650, 0.4684)   # “其首在立人，人立而後凡事舉”在《坟》1947年版第52页（PDF第53页）第4列的位置（相对坐标）
def fen_fn(t, d):
    im, _ = kb(IMG('bg_fen53'), lerp(1.03, 1.09, t / d), .5, .5)
    def mk(hl):
        c = make_card('fen53', 900, 0)
        if hl:
            w, h = c.width - 136, c.height - 136; l, tp, r, b = FEN_HL
            m = Image.new('RGB', c.size, (255, 255, 255)); ImageDraw.Draw(m).rectangle((68 + l * w, 68 + tp * h, 68 + r * w, 68 + b * h), fill=(236, 168, 146))
            a = c.getchannel('A'); c = ImageChops.multiply(c.convert('RGB'), m).convert('RGBA'); c.putalpha(a)
        return c
    pg = DER('fen0', lambda: mk(False)); a = clamp((t + 145.4 - t_ls) / 0.7)
    if a > 0: pg = Image.blend(pg, DER('fen1', lambda: mk(True)), eout(a))
    u = eout(t / 0.8); sc = lerp(1.10, 1.0, u) * (1 + 0.05 * t / d)
    g = pg.resize((int(pg.width * sc), int(pg.height * sc)), Image.BILINEAR)
    paste_a(im, g, (1150 - g.width / 2, 505 + 240 * (1 - u) - g.height / 2), clamp(t / 0.3))
    return im
X(145.4, 150.4, fen_fn)
INFO(145.8, 150.3, '史料 · 书影', '《文化偏至论》', '1907年作 · 1908年刊于《河南》', '出处：《坟》1947年版（国家图书馆藏）')
X(150.4, t_xs, CARDS('hz29', [('hz29', 1140, 480, 800, 1.2, 0.2)]))
INFO(150.8, t_xs - 0.1, '史料 · 照片', '鲁迅在东京', '1909年', SRC_HZ)
X(t_xs, t_21 - 0.2, CARDS('hz39', [('hz39', 830, 500, 600, -1.6, 0.2), ('hz43', 1430, 520, 640, 1.8, t_yw - t_xs)]))
INFO(t_xs + 0.3, t_yw - 0.1, '史料 · 图像', '《新生》原拟的封面画', '瓦茨《希望》　杂志没有办成', SRC_HZ)
INFO(t_yw + 0.2, t_21 - 0.3, '史料 · 书影', '《域外小说集》第一册', '1909年 · 东京　周树人、周作人译', SRC_HZ)
def num21(b, t, a):
    k = clamp(t / 0.9); n = max(1, round(21 * eout(k)))
    im = DER(('n21', n), lambda: text_rgba(str(n), SERIF(300, 'Bold'), CREAM, shadow=10)); paste_a(b, im, (W / 2 - im.width / 2 - 40, 470 - im.height / 2), a)
    u = DER('ben', lambda: text_rgba('本', SERIF(90, 'SemiBold'), CREAM, shadow=6)); paste_a(b, u, (W / 2 + im.width / 2 - 30, 520 - u.height / 2), a * clamp((t - 0.9) / 0.4))
    c = DER('n21c', lambda: text_rgba('《域外小说集》第一册　东京寄售处售出', SERIF(40), (214, 210, 200, 255), shadow=4)); paste_a(b, c, (W / 2 - c.width / 2, 700), a * clamp((t - 0.6) / 0.5))
X(t_21 - 0.2, t_hg, KB('bg_qj3344', 1.0, 1.06, (.5, .5), (.5, .5)))
ov(t_21, t_hg + 0.3, num21, 0.3, 0.5)
X(t_hg, 167, CARDS('qj492', [('qj492', 1140, 480, 780, -1.4, 0.2)]))
INFO(t_hg + 0.4, 166.9, '史料 · 照片', '鲁迅在杭州', '1909年 · 回国任教于浙江两级师范学堂', SRC_QJ)
# 片尾
CR = [(f'样片 v3 r2｜第二章 南京·东京·仙台（B站母版 02:59—{int((OFF + NEW_MAIN) // 60):02d}:{int((OFF + NEW_MAIN) % 60):02d}，无配音）', 40, 'SemiBold', INK),
      ('', 0, '', None),
      ('AI 情景再现：仙台寓所夜读、幻灯片放映、讲堂欢呼、走进雪地（画面右上角已标注）', 28, 'Regular', (70, 64, 58)),
      ('历史照片、手迹与《新生》封面画（瓦茨《希望》）：林贤治《鲁迅画传》；《鲁迅全集》2005年版文前彩插', 28, 'Regular', (70, 64, 58)),
      ('《天演论》书影：中国现代文学馆　《坟》1947年版：国家图书馆藏本扫描（Wikimedia Commons，公有领域）', 28, 'Regular', (70, 64, 58)),
      ('鲁迅原文均据《鲁迅全集》2005年版', 28, 'Regular', (70, 64, 58))]
CRS = [text_rgba(c, SERIF(s, w), f + (255,)) if c else None for c, s, w, f in CR]
def cred(t, d):
    im = PAPER.copy(); y = 330
    for i, c in enumerate(CRS):
        if c: paste_a(im, c, (W / 2 - c.width / 2, y), clamp((t - 0.3 - i * 0.12) / 0.8))
        y += 80 if i == 0 else (30 if c is None else 58)
    return im
X(TOTAL_MAIN, TOTAL, cred)

# ---------- 节奏收紧：把镜头、叠加层、字幕、震屏统一映射到新时间 ----------
def _nom(t0, t1, tr): return (t0 + 0.25, t1 - 0.5) if tr == 'flash' else ((t0, t1 - 0.5) if tr == 'black' else (t0 + 0.5, t1 - 0.5))
_new = []
for t0, t1, fn, tr, td in clips:
    a, b = _nom(t0, t1, tr); _new.append((M(a) - (a - t0), M(b) + (t1 - b), fn, tr, td))
clips[:] = _new
ovs[:] = [(M(t0), M(t1), dr, fin, fout) for t0, t1, dr, fin, fout in ovs]
subs[:] = [(M(t0), M(t1), ims, attr) for t0, t1, ims, attr in subs]
SUBLOG[:] = [(round(M(a), 2), round(M(b), 2), c) for a, b, c in SUBLOG]
SHAKES[:] = [M(x) for x in SHAKES]
TOTAL_MAIN = NEW_MAIN; TOTAL = TOTAL_MAIN + CRED

WM = text_rgba('样片 v3 · 无配音', SANS(22, 'Light'), (255, 255, 255, 255), shadow=2)

# ---------- 浮尘（淡） ----------
rnd = random.Random(11)
DUST = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(-12, 12), rnd.uniform(-18, -5), rnd.choice([2, 3, 4, 6]), rnd.uniform(0, 6.28)) for _ in range(40)]
SPR = {}
for r in (2, 3, 4, 6):
    m = Image.new('L', (r * 6, r * 6), 0); ImageDraw.Draw(m).ellipse((r * 2, r * 2, r * 4, r * 4), fill=255); m = m.filter(ImageFilter.GaussianBlur(r * 0.8))
    s = Image.new('RGBA', m.size, (236, 236, 230, 255)); s.putalpha(m); SPR[r] = s
DUSTR = [(M(a), M(b)) for a, b in [(69, 93.2), (109.8, 123)]]
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
PAPER_T = []   # 本章没有需要墨色字幕的纸面镜头（“惜别”特写仍用白字＋底部压暗）
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

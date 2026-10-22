
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

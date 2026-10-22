
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

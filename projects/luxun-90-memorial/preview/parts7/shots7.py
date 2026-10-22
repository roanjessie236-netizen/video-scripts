
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

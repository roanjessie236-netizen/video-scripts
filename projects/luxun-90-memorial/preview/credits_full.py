# 全片片尾字幕（两页，合并各章片尾的出处）：沿用尾声片尾的纸面与字体（取 render_ch7.py 前 118 行的函数）。输出 /tmp/full/credits.mp4
import subprocess, sys
src = open('/data/luxun90/preview/render_ch7.py', encoding='utf-8').read().split('\n')
g = {'__name__': 'cr'}; exec('\n'.join(src[:118]), g)   # 到 PAPER = make_paper() 为止，不读素材
W, H, PAPER, SERIF, text_rgba, paste_a, clamp, INK = g['W'], g['H'], g['PAPER'], g['SERIF'], g['text_rgba'], g['paste_a'], g['clamp'], g['INK']
G_ = (70, 64, 58); HD = (110, 52, 40)
P1 = [('《忘记我》——鲁迅逝世九十周年（1936—2026）', 44, 'SemiBold', INK), ('样片 v3｜全片（B站母版 19:00，无配音）', 28, 'Regular', G_), None,
      ('参考书目', 28, 'SemiBold', HD),
      ('《鲁迅全集》（人民文学出版社2005年版）　林贤治《鲁迅画传》　钱理群《鲁迅作品十五讲》　孔庆东《正说鲁迅》', 25, 'Regular', G_),
      ('片中鲁迅原文均据《鲁迅全集》2005年版逐字核对；毛泽东语据《毛泽东选集》第二卷（1991年第二版）第698页', 25, 'Regular', G_), None,
      ('影视剧（非历史影像，剧中鲁迅为演员扮演；已裁去原片字幕与台标）', 28, 'SemiBold', HD),
      ('电影《鲁迅》（2005，上海电影制片厂，丁荫楠导演，濮存昕饰鲁迅）', 25, 'Regular', G_),
      ('电视剧《觉醒年代》（2021）第8、13、15集，曹磊饰鲁迅　电影《阿Q正传》（1981，上海电影制片厂，岑范导演）', 25, 'Regular', G_), None,
      ('纪录影像（均据 Internet Archive，已裁去时间码、字幕与黑边）', 28, 'SemiBold', HD),
      ('Benjamin Brodsky 摄1917年北京（AI 修复上色版）　《China At The Front》（1920年代）', 25, 'Regular', G_),
      ('《The Northern Expedition & The Unification Of China》　《Chinese Coup d\'état of April 12 1927》', 25, 'Regular', G_),
      ('1920年代上海街景（Periscope Film）　“Shanghai, China, 1932”（美国国家档案馆）　1930年代中国劳工（AFP-27AV）', 25, 'Regular', G_)]
P2 = [('历史照片、手迹、书影', 28, 'SemiBold', HD),
      ('林贤治《鲁迅画传》　《鲁迅全集》2005年版文前彩插　沙飞摄《鲁迅葬仪》　《新中华》1936年第4卷第21期（据中国作家网蔡涛文转引）', 25, 'Regular', G_),
      ('《死》手稿：上观新闻2018年展览报道配图　《天演论》书影：中国现代文学馆　《坟》1947年版：国家图书馆藏本扫描', 25, 'Regular', G_),
      ('《新青年》原刊、朱安像、《创造月刊》《太阳月刊》《艺术论》：Wikimedia Commons　珂勒惠支《牺牲》（1922）：Städel Museum', 25, 'Regular', G_),
      ('美术作品：赵延年木刻《离家》　瓦茨《希望》（《新生》原拟封面画）', 25, 'Regular', G_), None,
      ('实拍照片', 28, 'SemiBold', HD),
      ('上海鲁迅墓 ScareCriterion12（CC BY-SA 4.0）　大陆新村9号 Zhou Guanhuai（CC BY-SA 4.0）　周家新台门 Gisling（CC BY-SA 3.0）', 25, 'Regular', G_),
      ('绍兴水巷 Taco Witte（CC BY 2.0）　上海鲁迅故居卧室：上海市文化和旅游局', 25, 'Regular', G_), None,
      ('AI 情景再现（画面右上角均已标注；不露鲁迅面部）', 28, 'SemiBold', HD),
      ('少年时期、仙台幻灯片与雪地、铁屋子与小说人物、《在酒楼上》《孤独者》《秋夜》《过客》、南下与“清党”、', 25, 'Regular', G_),
      ('横站、柔石与花园庄、《惯于长夜过春时》、木刻风“匕首”“投枪”、《“这也是生活”……》、今日四景（AI 生成，非实拍）', 25, 'Regular', G_), None,
      ('日文便条按全集所录排字，不仿笔迹；“没有忘”为印刷字体，不仿鲁迅笔迹；萤火为程序生成', 25, 'Regular', G_)]
def build(P):
    out = []
    for it in P:
        if it is None: out.append(None); continue
        txt, s, w, col = it
        while True:
            im = text_rgba(txt, SERIF(s, w), col + (255,))
            if im.width <= W - 160 or s <= 18: break
            s -= 1
        out.append((im, s))
    return out
def layout(L):
    h = sum(28 if x is None else (x[1] * 2.05 if x[1] >= 40 else x[1] * 1.9) for x in L); y = (H - h) / 2; pos = []
    for x in L:
        pos.append(y); y += 28 if x is None else (x[1] * 2.05 if x[1] >= 40 else x[1] * 1.9)
    return pos
PAGES = [(build(P), None) for P in (P1, P2)]; PAGES = [(L, layout(L)) for L, _ in PAGES]
D1, D2, XF, FO = 9.0, 9.0, 0.8, 1.0; TOTAL = D1 + D2
def page(k, t):
    L, pos = PAGES[k]; im = PAPER.copy(); n = 0
    for x, y in zip(L, pos):
        if x is None: continue
        paste_a(im, x[0], (W / 2 - x[0].width / 2, y), clamp((t - 0.2 - n * 0.08) / 0.7)); n += 1
    return im
def frame(T):
    if T < D1 - XF / 2: im = page(0, T)
    elif T < D1 + XF / 2:
        a = (T - (D1 - XF / 2)) / XF; im = g['Image'].blend(page(0, T), page(1, T - D1 + XF / 2 + 0.6), a)
    else: im = page(1, T - D1 + XF / 2 + 0.6)
    if T > TOTAL - FO: im = g['Image'].blend(im, g['Image'].new('RGB', (W, H), (0, 0, 0)), (T - (TOTAL - FO)) / FO)
    return im
if __name__ == '__main__':
    if '--stills' in sys.argv:
        for tt in (5.0, 14.0): frame(tt).save(f'/tmp/full/cr_{tt:.0f}.jpg', quality=88)
        sys.exit(0)
    N = int(round(TOTAL * 25))
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '25', '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '/tmp/full/credits.mp4'], stdin=subprocess.PIPE)
    for f in range(N): p.stdin.write(frame(f / 25).tobytes())
    p.stdin.close(); p.wait(); print('done', N)

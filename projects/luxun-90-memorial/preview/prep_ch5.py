# 第五章（厦门·广州 1926—1927）素材准备：画传/全集照片裁切；AI 情景再现图调色；纪录影像与电影片段抽帧（裁掉原片字幕、台标、黑边）并统一“冷调旧胶片·中档”。输出到 preview/src5/
# 原始页：pdftoppm -r 200 画传第120、123、125、132页 → v3/pdf/hzN-NNN.png；pdfimages -j 全集第855、3654页 → v3/pdf/qjN-000.jpg
# 电影《鲁迅》（2005）：GitHub assets/web/W40/clips/luxun-2005-full/ 下载到 v3/lx/（1280x720，上下黑边，左上角有转载台标，一律裁掉）
# 用法：python3 prep_ch5.py [--cards] [--film [名1,名2]]
import os, sys, subprocess, numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageDraw
import importlib.util
R = '/data/luxun90/'; P = R + 'preview/v3/pdf/'; O = R + 'preview/src5/'; FILES = '/data/.agent-service/files/'; LX = R + 'preview/v3/lx/'
spec = importlib.util.spec_from_file_location('pv', R + 'preview/prep_lib.py'); pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
os.makedirs(O, exist_ok=True)
AI = {'n01': 'be92a700-4203-49e9-bc82-22c164c63ce3',   # 1926年8月，北京车站站台：他和许广平走向列车（背影）
      'n02': '37b37c6a-5f65-4868-b9bb-9f474b303663',   # 南下的海船，甲板上的背影
      'n03': '4e34998f-106e-4b96-8dac-a99386f95fa4',   # 厦门大学宿舍，海边的夜，灯下写作（背影）
      'n04': 'b863aac0-27db-4946-b3ea-82cdea2740c4',   # “解剖我自己”：稿纸上的一把手术刀（学医出身），油灯
      'n05': 'a3c402cb-3b9c-4313-896a-9b2459220368',   # “进化的链子”：中间被照亮的一环
      'n06': '6a8c5b3c-be40-4623-ac24-d9e4e9192601',   # 雾中的石板桥，挑担的人走过
      'n07': '1cfe89bc-e9c9-4712-a509-6cca47ac36b4',   # 桥中间一块被踩平的石板，脚步走过
      'n08': 'a7cbb354-0710-40fe-89a2-1e42de1e44c9',   # 1927年4月15日夜，军警押走中大学生（情景再现）
      'n09': '64d3d0b7-7407-45cf-bf07-6f3994b39eec',   # “投书告密”：学生把折好的纸条递给军官
      'n10': 'd9350ee2-d7c6-4857-89e9-28078da6279b',   # “助官捕人”：学生领着士兵指认宿舍门
      'n11': '11ab1039-7087-4682-a672-69506d8c4f2c'}   # 白云楼雨夜，窗前的背影
CARD = {'qj855': ('qj855-000.jpg', None),                 # 1927年1月2日厦门南普陀坟间留影
        'qj3654': ('qj3654-000.jpg', None),               # 厦门大学全景明信片（1926年9月11日寄许广平，有鲁迅题字）
        'hz120': ('hz120-120.png', (0, 1030, 2400, 3300)),   # 国立中山大学
        'hz125': ('hz125-125.png', (800, 450, 2180, 2190)),  # 广州白云楼
        'hz123': ('hz123-123.png', (0, 0, 2400, 2990)),      # 1927年9月11日与许广平、蒋径三合影（裁去图注）
        'hz132': ('hz132-132.png', (290, 2040, 990, 3160))}  # 《而已集》封面（鲁迅设计）
FULL = {'qj3654', 'hz120'}   # 整屏推拉用，放大到 2400 宽
def trim(im, thr=14):
    g = np.asarray(ImageOps.grayscale(im)).astype(np.int16); bgv = np.median(np.concatenate([g[0], g[-1], g[:, 0], g[:, -1]]))
    m = np.abs(g - bgv) > thr; rows = np.where(m.mean(1) > 0.06)[0]; cols = np.where(m.mean(0) > 0.06)[0]
    if len(rows) < 10 or len(cols) < 10: return im
    return im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
SRC = {'c17': ('https://archive.org/download/china-amazing-china-in-1917-1080p-s-ai-p-3-audio-1917/China%20-%20Amazing%20China%20in%201917%20%5B1080p%23S%20AI%20P3%5D%20%5BAudio%5D%20%281917%29.mp4', 1920, 1080),
       # 《Amazing China in 1917》：Benjamin Brodsky 摄，AI 修复上色版（Internet Archive），4:3 画面位于 x 240—1680
       'ne': ('https://archive.org/download/the-northern-expedition-the-unification-of-china/The%20Northern%20Expedition%20%26%20The%20_Unification_%20Of%20China.mp4', 1280, 720),
       # 《The Northern Expedition & The Unification Of China》（The1920sChannel 汇编，Internet Archive）
       'coup': ('https://archive.org/download/chinese-coup-detat-of-april-12-1927/Chinese%20Coup%20d%27%C3%A9tat%20of%20April%2012%201927%20%5BxNoEth4m0iA%5D.mkv', 1920, 1080)}
       # 《Chinese Coup d'état of April 12 1927》（Internet Archive）：4:3 画面位于 x 249—1670，片中繁体字幕在 y 900 以下，一律裁掉
for f in os.listdir(LX):
    if f.endswith('.mp4'): SRC[f] = (LX + f, 1280, 720)   # 电影《鲁迅》（2005）：有效画面 y 55—665，左上角台标在 y 65 以上
LXC = (115, 64, 1050)
FILM = [('a_stn', [('c17', 102.0, 114.0, (240, 135, 1440))]),     # 1917年北京：正阳门东车站（京奉铁路）全景摇镜
        ('b_march', [('ne', 483.0, 493.0, (0, 0, 1280))]),         # 北伐时期军队行进（俯拍街道）
        ('p_arrest', [('coup', 108.05, 112.55, (250, 50, 1420))]), # 1927年“清党”：军警拖走被捕者
        ('p_desk', [('coup', 116.2, 124.1, (250, 50, 1420))]),     # 登记被捕的青年
        ('p_bars', [('coup', 124.25, 130.25, (250, 50, 1420))]),   # 铁栅后的被捕者
        ('x_desk', [('LX2005_P14_005755-010315.mp4', 98.6, 106.0, LXC)]),     # 电影《鲁迅》：书桌前
        ('x_doubt', [('LX2005_P02_000450-000755.mp4', 87.4, 92.6, LXC)]),     # 电影《鲁迅》：青年人群中，侧目而视
        ('x_youth', [('LX2005_P01_000000-000450.mp4', 271.0, 279.4, LXC)])]   # 电影《鲁迅》：在青年中间
def one(item):
    name, segs = item; d = O + name + '/'; os.makedirs(d, exist_ok=True); [os.remove(d + x) for x in os.listdir(d)]; k = 0
    tmp = f'/tmp/film5_{name}/'; os.makedirs(tmp, exist_ok=True)
    for f, a, b, (x0, y0, w) in segs:
        path, sw, sh = SRC[f]
        if w <= 1: x0, y0, w = sw * x0, sh * y0, sw * w
        cw = round(w / 2) * 2; ch = round(w * 9 / 32) * 2; cx, cy = round(x0), round(y0)
        [os.remove(tmp + x) for x in os.listdir(tmp)]
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-threads', '1', '-ss', str(a), '-t', str(b - a), '-i', path, '-an',
                        '-vf', f'crop={cw}:{ch}:{cx}:{cy},scale=1920:1080:flags=lanczos,fps=25', '-q:v', '2', tmp + '%04d.jpg'], check=True)
        for x in sorted(os.listdir(tmp)):
            pv.grade_base(Image.open(tmp + x)).save(d + f'{k:04d}.jpg', quality=90); k += 1
    pv.blur_bg(Image.open(d + f'{k // 2:04d}.jpg'), O + 'bg_' + name + '.jpg')
    return name, k
def film(only=None):
    from multiprocessing import Pool
    with Pool(2) as p:
        for name, k in p.imap_unordered(one, [x for x in FILM if not only or x[0] in only]): print(name, k, 'frames', flush=True)
if '--film' in sys.argv:
    _i = sys.argv.index('--film') + 1; film(sys.argv[_i].split(',') if _i < len(sys.argv) and not sys.argv[_i].startswith('--') else None)
if '--cards' in sys.argv or len(sys.argv) == 1:
    for n, fid in AI.items():
        im = pv.upto(Image.open(FILES + fid + '/tool-output-0.jpg').convert('RGB'))
        if n == 'n04':   # 稿纸上的“字”是 AI 生成的伪字：做成景深虚化，只留手术刀与油灯清晰
            w, h = im.size; m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rectangle((0, int(h * 0.36), int(w * 0.405), h), fill=255)
            m = m.filter(ImageFilter.GaussianBlur(w * 0.018)); im = Image.composite(im.filter(ImageFilter.GaussianBlur(w * 0.006)), im, m)
        pv.grade_base(im).save(O + n + '.jpg', quality=93); pv.blur_bg(im, O + 'bg_' + n + '.jpg')
    for n, (f, cr) in CARD.items():
        im = Image.open(f if f.startswith('/') else P + f).convert('RGB')
        if cr: im = trim(im.crop(cr))
        if n.startswith('hz'): im = im.filter(ImageFilter.MedianFilter(3))          # 减轻画传印刷网点
        if n in FULL: im = pv.upto(im, 2400)
        elif not n.startswith('hz') and max(im.size) < 1400:
            k = 1400 / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 30, 2))
        im.save(O + 'card_' + n + '.jpg', quality=93); pv.blur_bg(im, O + 'bg_' + n + '.jpg')
    print('cards ok')

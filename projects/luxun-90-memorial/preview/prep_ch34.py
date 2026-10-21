# 第三、四章（北京 1912—1926）素材准备：画传/全集/原刊扫描裁成相片卡；AI 图调色；《觉醒年代》片段抽帧（裁掉片中字幕与台标）并统一“冷调旧胶片·中档”。输出到 preview/src3/
# 原始页：pdftoppm -r 200 画传第54…134页 → v3/pdf/hzN-0NN.png；pdfimages -j 全集第101、103、497、498、3653、5514、6618页 → v3/pdf/qjN-000.jpg
# 《觉醒年代》片段：GitHub assets/web/W40/clips/juexing-niandai/ 下载到 v3/jx/（3840x2160/60fps，原片字幕与台标在画面下部，一律裁掉）
# r2（2026-10-21）：新增 1917年北京纪录影像（AI 上色版）、1920年代军阀战事纪录片、电影《阿Q正传》（1981）片段，及9张 AI 情景再现（文学作品复现）
# 用法：python3 prep_ch34.py [--cards] [--film [名1,名2]]
import os, sys, subprocess, numpy as np
from PIL import Image, ImageFilter, ImageOps
import importlib.util
R = '/data/luxun90/'; P = R + 'preview/v3/pdf/'; AW = R + 'assets/web/'; O = R + 'preview/src3/'; FILES = '/data/.agent-service/files/'; JX = R + 'preview/v3/jx/'
spec = importlib.util.spec_from_file_location('pv', R + 'preview/prep_lib.py'); pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
os.makedirs(O, exist_ok=True)
AI = {'d01': 'f73d6811-c71c-4dc4-993a-a9e983d496ec',   # 铁屋子：无窗铁屋里熟睡的人（脸不入画）
      'd02': 'bf1bd486-91dc-4a16-81a1-b7ff3e6e8c49',   # 铁屋子：一个人坐起，铁壁裂开一道光（背影）
      'c01': 'bbdf8166-9a4d-416b-af0d-fb6ea2d9e08a',   # 《过客》：荒野黄昏，过客拄杖走向坟地，老翁在土屋门口（脸在阴影里）
      'c02': '7f763204-5a89-42a1-9cd2-acebc510eb95',   # 《过客》：赤脚与木杖，向前走
      'k01': '14911f9d-ab4b-4407-8d47-f533660cc4e5',   # 《狂人日记》：油灯下夜翻历史书
      'e01': '1be9046d-3d65-41b0-a303-f93fea8e2aa2',   # 《孔乙己》：咸亨酒店柜台上排出九文大钱
      'e02': '6d2e8726-9b92-4066-84e0-b875df02a881',   # 《故乡》：月下瓜田，少年闰土刺猹
      'e03': 'aaa0d531-d208-4622-8b28-e4c4359ca92b',   # 《祝福》：祥林嫂雪巷
      'g01': 'db32e7a3-dac6-41c8-a80d-49ab99c1efa8',   # 《在酒楼上》：酒楼窗外雪中的梅与红山茶
      'g02': 'c8559de3-f5b7-44ea-a859-4ae817a8dc50',   # 《孤独者》：做了杜师长顾问的魏连殳，厅内军官打牌
      'g03': '20ffe2a3-1f71-4920-a2fd-460a31ffc095',   # 《孤独者》结尾：月光下湿石路上独行
      'h01': '8782406c-6d78-437a-a7c8-2511e35c9d00',   # 《秋夜》：后园墙外两株枣树
      'h02': 'b44032fd-8386-4aae-aad9-ea126c898b26'}   # 灯下写作
CARD = {  # 名: (文件, 裁切 l,t,r,b 像素)　r2 只保留仍在用的
 'hz56': ('hz56-056.png', (0, 0, 2400, 3250)),            # 绍兴县馆大门
 'w0701': (AW + 'W07/W07-01-xinqingnian-cover.png', None), 'w0702': (AW + 'W07/W07-02-kuangren-first-page.png', None),
 'hz61': ('hz61-061.png', (345, 1100, 2175, 2960)),         # 1925年为俄译本《阿Q正传》所摄
 'qj103': ('qj103-000.jpg', None), 'hz80': ('hz80-080.png', (0, 0, 2400, 2520)),
 'qj497': ('qj497-000.jpg', None), 'hz94': ('hz94-094.png', (264, 476, 1968, 2524)),
 'zhuan': ('/data/luxun90/preview/v3/web/zhuan_bj.jpg', None), 'hz95': ('hz95-095.png', (0, 0, 2400, 2900)), 'qj3653': ('qj3653-000.jpg', None),
 'hz102': ('hz102-102.png', (0, 1624, 2400, 3316)), 'hz103': ('hz103-103.png', (0, 1548, 1064, 3316)), 'hz104': ('hz104-104.png', (0, 0, 1548, 1896))}
def trim(im, thr=14):
    g = np.asarray(ImageOps.grayscale(im)).astype(np.int16); bgv = np.median(np.concatenate([g[0], g[-1], g[:, 0], g[:, -1]]))
    m = np.abs(g - bgv) > thr; rows = np.where(m.mean(1) > 0.06)[0]; cols = np.where(m.mean(0) > 0.06)[0]
    if len(rows) < 10 or len(cols) < 10: return im
    return im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
# 影像片段源：(路径或 URL, 宽, 高)。archive.org 远程文件用 ffmpeg -ss 直接截取，不整片下载
ARC = R + 'preview/v3/arc/'
SRC = {'c17': ('https://archive.org/download/china-amazing-china-in-1917-1080p-s-ai-p-3-audio-1917/China%20-%20Amazing%20China%20in%201917%20%5B1080p%23S%20AI%20P3%5D%20%5BAudio%5D%20%281917%29.mp4', 1920, 1080),
       # 《Amazing China in 1917》：Benjamin Brodsky 1917年拍摄的中国纪录片片段，AI 修复上色版（Internet Archive），4:3 画面位于 x 240—1680
       'aq': ('https://archive.org/download/the-true-story-of-ah-q-chn/The%20True%20Story%20Of%20Ah%20Q%20%281981%29%20CHN%20Disk%20Kino%20Bluray%20Original%20Version.mkv', 1920, 1080),
       # 电影《阿Q正传》（1981，上海电影制片厂，岑范导演，严顺开饰阿Q）蓝光原版，有效画面 y 131—947
       'fr': (ARC + 'front1927.mp4', 640, 480)}            # 纪录片《China At The Front》（1920年代军阀战事），Internet Archive
for f in os.listdir(JX): SRC[f] = (JX + f, 3840, 2160)    # 《觉醒年代》：GitHub assets/web/W40/clips/juexing-niandai/，原片字幕与台标在画面下部，一律裁掉
# (名, [(源, 起, 止, 裁切 (x0, y0, w))...])：同一名下多段顺接；裁切 ≤1 为原片比例，否则为像素；高 = w×9/16
FILM = [('f_rub', [('JXND_E08_S01_P05_001108-001118.mp4', 3.5, 5.45, (0.10, 0.04, 0.80)),
                   ('JXND_E08_S01_P09_001158-001208.mp4', 5.05, 7.25, (0.0, 0.05, 0.80))]),          # 第8集：街头书摊上翻看碑拓
        ('f_hall', [('JXND_E13_S01_P01_003621-003701.mp4', 1.1, 5.4, (0.26, 0.0, 0.72)),
                    ('JXND_E13_S01_P01_003621-003701.mp4', 12.3, 15.6, (0.2, 0.0, 0.80))]),        # 第13集：补树书屋，中景鲁迅（r2：避开原片卡顿与人名字幕）
        ('f_write', [('JXND_E15_S01_P01_001028-001108.mp4', 12.5, 14.7, (0.05, 0.0, 0.90)),
                     ('JXND_E15_S01_P03_001158-001258.mp4', 52.25, 55.0, (0.05, 0.0, 0.90))]),     # 第15集：写《狂人日记》
        ('f_group', [('JXND_E13_S01_P02_003701-003751.mp4', 14.4, 20.9, (0.12, 0.0, 0.82))]),     # 第13集：鲁迅近景 → 《新青年》同人全景
        ('a_roof', [('c17', 9.0, 16.0, (240, 120, 1440))]),       # 1917年北京：屋顶全景
        ('a_off', [('c17', 146.5, 149.5, (240, 135, 1440))]),     # 官员走下台阶
        ('a_st', [('c17', 177.5, 183.5, (240, 135, 1440))]),      # 正阳门大街人力车
        ('a_kid', [('c17', 525.5, 535.5, (240, 135, 1440))]),     # 孩子们直视镜头
        ('a_wall', [('c17', 755.5, 762.5, (240, 135, 1440))]),    # 城墙城门
        ('a_crowd', [('c17', 441.0, 459.0, (240, 135, 1440))]),   # 街头人群
        ('r_gun', [('fr', 256.5, 262.0, (0, 60, 640))]),          # 火炮开火
        ('q_yard', [('aq', 64.0, 70.0, (235, 131, 1450))]),       # 片头：雪夜院子，窗里亮灯
        ('q_sil', [('aq', 79.0, 85.0, (235, 131, 1450))]),        # 片头：桌前剪影
        ('q_smoke', [('aq', 98.0, 104.0, (235, 131, 1450))]),     # 片头：桌前抽烟（演员扮演鲁迅）
        ('q_write', [('aq', 490.0, 496.0, (235, 131, 1450))]),    # 伏案写作
        ('q_brush', [('aq', 506.0, 509.0, (235, 131, 1450))]),    # 毛笔写稿特写
        ('q_circle', [('aq', 6646.0, 6651.0, (235, 131, 1450))]), # 阿Q画圈
        ('q_face', [('aq', 7075.0, 7081.0, (235, 131, 1450))])]   # 看客面孔
def one(item):
    name, segs = item; d = O + name + '/'; os.makedirs(d, exist_ok=True); [os.remove(d + x) for x in os.listdir(d)]; k = 0
    tmp = f'/tmp/film_{name}/'; os.makedirs(tmp, exist_ok=True)
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
        im = pv.upto(Image.open(FILES + fid + '/tool-output-0.jpg').convert('RGB')); pv.grade_base(im).save(O + n + '.jpg', quality=93); pv.blur_bg(im, O + 'bg_' + n + '.jpg')
    for n, (f, cr) in CARD.items():
        im = Image.open(f if f.startswith('/') else P + f).convert('RGB')
        if cr: im = trim(im.crop(cr))
        if n == 'w2906':   # 国图黑白扫描：按原书暗红封面着色（白→暗红，黑→墨黑），片尾注明
            g = np.asarray(ImageOps.grayscale(im).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32)[..., None] / 255
            im = Image.fromarray((np.array([22, 18, 18]) * (1 - g) + np.array([118, 34, 36]) * g).astype(np.uint8))
            im = Image.blend(im, Image.effect_noise(im.size, 40).convert('RGB'), 0.06)
        if n.startswith('hz'): im = im.filter(ImageFilter.MedianFilter(3))          # 减轻画传印刷网点
        if not n.startswith('hz') and max(im.size) < 1400:
            k = 1400 / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 30, 2))
        im.save(O + 'card_' + n + '.jpg', quality=93); pv.blur_bg(im, O + 'bg_' + n + '.jpg')
    print('cards ok')

# 第三、四章（北京 1912—1926）素材准备：画传/全集/原刊扫描裁成相片卡；AI 图调色；《觉醒年代》片段抽帧（裁掉片中字幕与台标）并统一“冷调旧胶片·中档”。输出到 preview/src3/
# 原始页：pdftoppm -r 200 画传第54…134页 → v3/pdf/hzN-0NN.png；pdfimages -j 全集第101、103、497、498、3653、5514、6618页 → v3/pdf/qjN-000.jpg
# 《觉醒年代》片段：GitHub assets/web/W40/clips/juexing-niandai/ 下载到 v3/jx/（3840x2160/60fps，原片字幕与台标在画面下部，一律裁掉）
# 用法：python3 prep_ch34.py [--cards] [--film]
import os, sys, subprocess, numpy as np
from PIL import Image, ImageFilter, ImageOps
import importlib.util
R = '/data/luxun90/'; P = R + 'preview/v3/pdf/'; AW = R + 'assets/web/'; O = R + 'preview/src3/'; FILES = '/data/.agent-service/files/'; JX = R + 'preview/v3/jx/'
spec = importlib.util.spec_from_file_location('pv', R + 'preview/prep_lib.py'); pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
os.makedirs(O, exist_ok=True)
AI = {'d01': 'f73d6811-c71c-4dc4-993a-a9e983d496ec',   # 铁屋子：无窗铁屋里熟睡的人（脸不入画）
      'd02': 'bf1bd486-91dc-4a16-81a1-b7ff3e6e8c49',   # 铁屋子：一个人坐起，铁壁裂开一道光（背影）
      'c01': 'bbdf8166-9a4d-416b-af0d-fb6ea2d9e08a',   # 《过客》意象：荒野黄昏，过客拄杖走向坟地，老翁在土屋门口（脸在阴影里）
      'c02': '7f763204-5a89-42a1-9cd2-acebc510eb95'}   # 《过客》意象：赤脚与木杖，向前走
CARD = {  # 名: (文件, 裁切 l,t,r,b 像素)
 'hz54': ('hz54-054.png', (260, 488, 1232, 1660)),        # 蔡元培
 'qj5514': ('qj5514-000.jpg', None),                      # 1912年
 'hz56': ('hz56-056.png', (0, 0, 2400, 3250)),            # 绍兴县馆大门
 'hz55': ('hz55-055.png', (0, 0, 2308, 2680)),            # 袁世凯
 'hz57a': ('hz57-057.png', (0, 0, 2400, 1470)),           # 1917年1月京师图书馆开馆纪念照
 'hz57b': ('hz57-057.png', (0, 1980, 1608, 3316)),        # 补树书屋
 'w0806': (AW + 'W08/W08-06-wanglongsi-rubbing.jpg', None),
 'w0701': (AW + 'W07/W07-01-xinqingnian-cover.png', None), 'w0702': (AW + 'W07/W07-02-kuangren-first-page.png', None),
 'w2906': (AW + 'W29/W29-06-nahan-1923-cover.png', None), 'w2907': (AW + 'W29/W29-07-nahan-1923-colophon.png', None),
 'hz71a': ('hz71-071.png', (280, 170, 2180, 1500)), 'hz71b': ('hz71-071.png', (600, 1750, 1400, 3020)),
 'qj6618': ('qj6618-000.jpg', None), 'hz134': ('hz134-134.png', (260, 476, 952, 1472)),
 'hz61': ('hz61-061.png', (345, 1100, 2175, 2960)),         # 1925年为俄译本《阿Q正传》所摄
 'qj103': ('qj103-000.jpg', None), 'hz80': ('hz80-080.png', (0, 0, 2400, 2520)),
 'hz62': ('hz62-062.png', (280, 520, 1536, 2232)), 'hz79': ('hz79-079.png', (168, 465, 1272, 1991)), 'hz81': ('hz81-081.png', (900, 780, 2132, 2128)),
 'hz85y': ('hz85-085.png', (0, 0, 1010, 960)), 'hz85h': ('hz85-085.png', (900, 0, 1780, 980)), 'hz117': ('hz117-117.png', (272, 1736, 1412, 2848)),
 'qj497': ('qj497-000.jpg', None), 'hz94': ('hz94-094.png', (264, 476, 1968, 2524)),
 'zhuan': ('/data/luxun90/preview/v3/web/zhuan_bj.jpg', None), 'hz95': ('hz95-095.png', (0, 0, 2400, 2900)), 'qj3653': ('qj3653-000.jpg', None),
 'hz108': ('hz108-108.png', (248, 480, 2140, 1736)),
 'hz102': ('hz102-102.png', (0, 1624, 2400, 3316)), 'hz103': ('hz103-103.png', (0, 1548, 1064, 3316)), 'hz104': ('hz104-104.png', (0, 0, 1548, 1896))}
def trim(im, thr=14):
    g = np.asarray(ImageOps.grayscale(im)).astype(np.int16); bgv = np.median(np.concatenate([g[0], g[-1], g[:, 0], g[:, -1]]))
    m = np.abs(g - bgv) > thr; rows = np.where(m.mean(1) > 0.06)[0]; cols = np.where(m.mean(0) > 0.06)[0]
    if len(rows) < 10 or len(cols) < 10: return im
    return im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
# 《觉醒年代》片段：(名, 文件, [(起, 止), ...] 同一名下多段顺接, 裁切 (x0, y0, w) 为原片比例，高 = w×9/16)
FILM = [('f_rub', [('JXND_E08_S01_P05_001108-001118.mp4', 3.5, 5.45, (0.10, 0.04, 0.80)),
                   ('JXND_E08_S01_P09_001158-001208.mp4', 5.05, 7.25, (0.0, 0.05, 0.80))]),          # 第8集：街头书摊上翻看碑拓
        ('f_hall', [('JXND_E13_S01_P01_003621-003701.mp4', 1.1, 5.65, (0.26, 0.0, 0.72)),
                    ('JXND_E13_S01_P01_003621-003701.mp4', 8.05, 11.7, (0.0, 0.02, 0.80))]),       # 第13集：绍兴会馆补树书屋，同人来访
        ('f_write', [('JXND_E15_S01_P01_001028-001108.mp4', 12.5, 14.7, (0.05, 0.0, 0.90)),
                     ('JXND_E15_S01_P03_001158-001258.mp4', 52.25, 55.0, (0.05, 0.0, 0.90))]),     # 第15集：写《狂人日记》
        ('f_group', [('JXND_E13_S01_P02_003701-003751.mp4', 16.0, 20.6, (0.09, 0.0, 0.82))])]      # 第13集：《新青年》同人在会馆
def film():
    for name, segs in FILM:
        d = O + name + '/'; os.makedirs(d, exist_ok=True); k = 0
        for f, a, b, (x0, y0, w) in segs:
            cw, ch = round(3840 * w / 2) * 2, round(3840 * w * 9 / 16 / 2) * 2; cx, cy = round(3840 * x0), round(2160 * y0)
            tmp = '/tmp/film_tmp/'; os.makedirs(tmp, exist_ok=True); [os.remove(tmp + x) for x in os.listdir(tmp)]
            subprocess.run(['ffmpeg', '-loglevel', 'error', '-threads', '2', '-ss', str(a), '-t', str(b - a), '-i', JX + f, '-an',
                            '-vf', f'crop={cw}:{ch}:{cx}:{cy},scale=1920:1080:flags=lanczos,fps=25', '-q:v', '2', tmp + '%04d.jpg'], check=True)
            for x in sorted(os.listdir(tmp)):
                pv.grade_base(Image.open(tmp + x)).save(d + f'{k:04d}.jpg', quality=90); k += 1
        print(name, k, 'frames')
        pv.blur_bg(Image.open(d + f'{k // 2:04d}.jpg'), O + 'bg_' + name + '.jpg')
if '--film' in sys.argv: film()
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

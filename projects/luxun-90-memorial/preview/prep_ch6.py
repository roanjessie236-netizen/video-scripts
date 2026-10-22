# 第六章（上海 1927—1936）素材准备：AI 情景再现调色；画传/全集/原刊扫描裁成相片卡与书影；电影《鲁迅》（2005）与1920—30年代上海纪录影像抽帧，统一“冷调旧胶片·中档”。输出到 preview/src6/
# 原始页：pdftoppm -r 200 《鲁迅画传》（234页版）第141、146、161、174—181、232及书影各页 → v3/pdf/hzN-NNN.png；pdfimages -j 《鲁迅全集》第1244、1655、4119、7292—7298页 → v3/pdf/qjN-000.jpg
# 用法：python3 prep_ch6.py [--cards] [--film [名1,名2]]
import os, sys, glob, time, subprocess, numpy as np
from PIL import Image, ImageFilter, ImageOps
import importlib.util
R = '/data/luxun90/'; P = R + 'preview/v3/pdf/'; AW = R + 'assets/web/'; O = R + 'preview/src6/'; FILES = '/data/.agent-service/files/'; LX = R + 'preview/v3/lx/'
spec = importlib.util.spec_from_file_location('pv', R + 'preview/prep_lib.py'); pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
os.makedirs(O, exist_ok=True)
AI = {'a01': '9ee53ef4-21fd-492c-9260-a42382c94844',   # 灯下译书（绿灯罩台灯；人物脸不入画）
      'a03': '83654173-8673-4757-8556-96895e481eb2',   # “横站”：弄堂两端都有阴影，人物侧身居中
      'a04': 'c6108117-3496-43b5-8c59-93eb46e6efdd',   # 1931年1月16日夜：门口递合同（手部特写）
      'a05': '99794b8f-9489-46a0-a1e2-b9fcd3fa30ec',   # 青年揣着合同走进雾夜弄堂（背影）
      'a06': 'cf475f9a-a852-40c1-aaa6-6c4800b695c7',   # 1931年1月17日：东方旅社会场被捕
      'a07': 'b9f5b08f-a54a-4c57-bd76-5d88c54cb085',   # 避居花园庄旅馆：窗前坐者，妻儿在床
      'a08': 'cd56f0e9-15fe-44c4-94de-65cb613b5ad2',   # “城头变幻大王旗”
      'a09': '67e8b91c-26e1-4822-975d-fe6605b2bc86',   # “怒向刀丛觅小诗”
      'a10': 'f9d2c1ec-3a49-40aa-8682-eeeb83c46531',   # “月光如水照缁衣”（脸不入画）
      'a11': '6232418e-99e0-4ce2-af2d-bc2ecae37286',   # “夜正长，路也正长”
      'a13': '4b475062-9a1d-4ee3-a971-51f492059527',   # “足踏在地上”
      'a14': 'f1a0ff58-c523-426c-8fba-a1f40a600e6f',   # 稿纸与译本堆积
      'a15': '10617913-a2c7-45cf-99b3-a294b6b956f1',   # 木刻风：毛笔化作匕首、投枪
      'a16': '6c5ef7e3-8d40-4edd-94f4-464f7e98d4b3',   # 木刻风：劈开荆棘铁丝网的血路
      'n05': 'a3c402cb-3b9c-4313-896a-9b2459220368'}   # 第五章“进化的链子”（回扣）
CARD = {  # 名: (文件, 裁切 l,t,r,b 像素)
 'hz141': ('hz141-141.png', (0, 0, 2400, 2900)),           # 鲁迅与内山完造
 'w3201': (AW + 'W32/W32-01-chuangzao-v2n6-cover.png', None), 'w3202': (AW + 'W32/W32-02-taiyang-1928-june-inner-cover.png', None),
 'hz146': ('hz146-146.png', (1104, 2424, 1536, 3072)),     # 《文化批判》
 'w3204': (AW + 'W32/W32-04-art-theory-1930-cover.png', None),   # 《艺术论》1930
 'hz161': ('hz161-161.png', (0, 1512, 2400, 3312)),        # 海婴百日留影
 'qj4119': ('qj4119-000.jpg', None),                       # 海婴与鲁迅：一岁与五十
 'hz174': ('hz174-174.png', (1140, 504, 2136, 1920)), 'hz175': ('hz175-175.png', (312, 504, 1180, 1680)),
 'hz176': ('hz176-176.png', (1248, 792, 2160, 2040)), 'hz177': ('hz177-177.png', (312, 528, 1248, 1920)),
 'hz179': ('hz179-179.png', (1296, 1200, 2160, 2400)),     # 柔石、李伟森、殷夫、胡也频、冯铿
 'w16': (AW + 'W16/W16-01-kollwitz-das-opfer.jpg', (0, 0, 5000, 3687)),  # 珂勒惠支《牺牲》（Städel Museum）
 'hz232': ('hz232-232.png', (960, 0, 2400, 1800)),         # 瞿秋白
 'qj1655': ('qj1655-000.jpg', None),                       # 书赠瞿秋白联语
 'qj1244': ('qj1244-000.jpg', None),                       # 1931年8月木刻讲习会合影
 # 书影墙
 'hz76': ('hz76-076.png', (336, 1152, 1416, 1680)), 'hz81': ('hz81-081.png', (888, 552, 2184, 2208)), 'hz85': ('hz85-085.png', (0, 0, 2400, 1440)),
 'hz97': ('hz97-097.png', (1152, 1200, 2016, 2064)), 'hz112': ('hz112-112.png', (456, 672, 2136, 1728)), 'hz131': ('hz131-131.png', (1440, 820, 2200, 1560)),
 'hz132': ('hz132-132.png', (288, 1992, 1032, 3048)), 'hz136': ('hz136-136.png', (288, 504, 960, 1200)), 'hz151': ('hz151-151.png', (840, 1872, 2136, 3072)),
 'hz154': ('hz154-154.png', (1272, 1272, 2184, 2640)), 'hz170a': ('hz170-170.png', (1416, 504, 2184, 1584)), 'hz170b': ('hz170-170.png', (1176, 1896, 2208, 3048)),
 'hz171': ('hz171-171.png', (288, 504, 1416, 2088)), 'hz181': ('hz181-181.png', (1440, 504, 2184, 1536)), 'hz201': ('hz201-201.png', (300, 470, 1170, 1800)),
 'hz207': ('hz207-207.png', (1340, 770, 2100, 1720)), 'hz208': ('hz208-208.png', (240, 950, 1580, 2090)),
 # 鲁迅手书书名（全集彩插），反相为暗底浅字，作书影墙的底
 'inv7292': ('qj7292-000.jpg', None), 'inv7294': ('qj7294-000.jpg', None), 'inv7296': ('qj7296-000.jpg', None)}
def trim(im, thr=14):
    g = np.asarray(ImageOps.grayscale(im)).astype(np.int16); bgv = np.median(np.concatenate([g[0], g[-1], g[:, 0], g[:, -1]]))
    m = np.abs(g - bgv) > thr; rows = np.where(m.mean(1) > 0.06)[0]; cols = np.where(m.mean(0) > 0.06)[0]
    if len(rows) < 10 or len(cols) < 10: return im
    return im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
# 影像片段源：(路径或 URL, 宽, 高)。archive.org 远程文件用 ffmpeg -ss 直接截取，不整片下载
A = 'https://archive.org/download/'
SRC = {'cn': (A + 'ORR9sKeh6Yfrwt8xYAnO3lCVhmOTvZ/tmpnsz3u449.mov', 960, 540),   # 1920年代中国（Periscope Film）：4:3 画面在 x 120—840，底部烧录时间码，一律裁掉
       'na': (A + 'yt_RBF2zEn58Rw/RBF2zEn58Rw.mp4', 1920, 1080),                # 美国国家档案馆 “Shanghai, China, 1932”：4:3 画面在 x 240—1680
       'af': (A + 'AFP-27AV/AFP-27AV_720p.mp4', 1280, 720)}                     # 1930年代中国劳工与街市：4:3 画面在 x 160—1120
for f in sorted(glob.glob(LX + 'LX2005_P*.mp4')): SRC[os.path.basename(f)[7:10]] = (f, 1280, 720)   # 电影《鲁迅》（2005）分段，键 P01…P25
LXC = (115, 64, 1050)   # 电影《鲁迅》有效画面（去黑边与转载台标）
# (名, [(源, 起, 止, 裁切 (x0, y0, w))...])：同一名下多段顺接；高 = w×9/16
FILM = [('d_tram', [('cn', 556.5, 562.0, (120, 35, 720))]),     # 1920年代上海街景
        ('x_tram', [('P03', 33.0, 37.5, LXC)]),     # 电车上
        ('x_write', [('P18', 62.0, 66.5, LXC)]),    # 戴眼镜写作
        ('x_uchi', [('P04', 186.0, 192.0, LXC)]),   # 内山书店
        ('x_read', [('P15', 45.0, 50.5, LXC)]),     # 读报后抬头
        ('x_bath', [('P05', 3.0, 9.5, LXC)]),       # 给海婴洗澡
        ('x_hall', [('P05', 93.0, 101.5, LXC)]),    # 左联成立大会（红桌）
        ('x_speak', [('P05', 77.0, 86.5, LXC)]),    # 讲话特写
        ('x_night', [('P18', 130.0, 134.0, LXC)]),  # 夜街人影
        ('x_manu', [('P18', 74.0, 78.5, LXC)]),     # 手写稿
        ('x_glass', [('P19', 146.0, 151.5, LXC)]),  # 戴眼镜特写
        ('x_pen', [('P19', 152.0, 159.0, LXC)]),    # 手在稿纸上写字
        ('d_crowd', [('na', 8.0, 15.0, (240, 135, 1440))]),                        # 1932年上海街头人群
        ('d_labor', [('af', 9.0, 14.5, (160, 90, 960)), ('af', 100.0, 105.5, (160, 90, 960))]),   # 挑筐、拉绳的劳工
        ('x_youth', [('P09', 20.0, 27.0, LXC)]),    # 街头与青年
        ('x_qiu', [('P07', 88.0, 93.5, LXC)]),      # 与瞿秋白对坐
        ('x_rain', [('P08', 347.0, 352.5, LXC)]),   # 雨雾林荫道背影远去
        ('x_ill', [('P21', 285.0, 289.0, LXC)]),    # 戴眼镜拿蓝皮书
        ('x_shulin', [('P22', 15.0, 17.9, LXC)]),   # 《海上述林》上卷封面
        ('x_mk', [('P22', 18.0, 31.0, LXC)]),       # 木刻展与青年
        ('x_desk', [('P18', 81.0, 85.0, LXC)]),     # 绿台灯伏案
        ('x_cold', [('P15', 64.0, 67.5, LXC)]),     # 冷峻特写
        ('x_play', [('P16', 270.0, 281.0, LXC)]),   # 与海婴嬉戏
        ('x_cold2', [('P15', 50.5, 53.0, LXC), ('P15', 56.0, 58.4, LXC)])]   # 冷峻特写（分屏左半）
def one(item):
    name, segs = item; d = O + name + '/'; os.makedirs(d, exist_ok=True); [os.remove(d + x) for x in os.listdir(d)]; k = 0
    tmp = f'/tmp/film6_{name}/'; os.makedirs(tmp, exist_ok=True)
    for f, a, b, (x0, y0, w) in segs:
        path, sw, sh = SRC[f]
        cw = round(w / 2) * 2; ch = round(w * 9 / 32) * 2; cx, cy = round(x0), round(y0)
        for tr in range(6):   # archive.org 偶有 5XX，重试
            [os.remove(tmp + x) for x in os.listdir(tmp)]
            r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-threads', '1', '-ss', str(a), '-t', str(b - a), '-i', path, '-an',
                                '-vf', f'crop={cw}:{ch}:{cx}:{cy},scale=1920:1080:flags=lanczos,fps=25', '-q:v', '2', tmp + '%04d.jpg'])
            if r.returncode == 0 and len(os.listdir(tmp)) >= (b - a) * 25 - 3: break
            time.sleep(5 + 5 * tr)
        else: raise RuntimeError(name)
        for x in sorted(os.listdir(tmp)):
            pv.grade_base(Image.open(tmp + x)).save(d + f'{k:04d}.jpg', quality=90); k += 1
    pv.blur_bg(Image.open(d + f'{k // 2:04d}.jpg'), O + 'bg_' + name + '.jpg')
    return name, k
def film(only=None):
    from multiprocessing import Pool
    with Pool(3) as p:
        for name, k in p.imap_unordered(one, [x for x in FILM if not only or x[0] in only]): print(name, k, 'frames', flush=True)
if '--film' in sys.argv:
    _i = sys.argv.index('--film') + 1; film(sys.argv[_i].split(',') if _i < len(sys.argv) and not sys.argv[_i].startswith('--') else None)
if '--cards' in sys.argv or len(sys.argv) == 1:
    for n, fid in AI.items():
        im = pv.upto(Image.open(FILES + fid + '/tool-output-0.jpg').convert('RGB'))
        if n == 'a16': im = im.crop((0, 0, round(im.width * 0.97), round(im.height * 0.97))).resize(im.size, Image.LANCZOS)   # 裁掉右下角小记号
        pv.grade_base(im).save(O + n + '.jpg', quality=93); pv.blur_bg(im, O + 'bg_' + n + '.jpg')
    for n, (f, cr) in CARD.items():
        im = Image.open(f if f.startswith('/') else P + f).convert('RGB')
        if cr: im = trim(im.crop(cr))
        if n.startswith('inv'):   # 黑字白底 → 暗底浅米色字
            g = np.asarray(ImageOps.grayscale(im).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)[..., None] / 255
            im = Image.fromarray((np.array([206, 196, 176]) * (1 - g) + np.array([14, 16, 19]) * g).astype(np.uint8))
            im.save(O + 'card_' + n + '.jpg', quality=93); continue
        if n == 'w16': im = im.resize((2400, round(im.height * 2400 / im.width)), Image.LANCZOS)   # 原图 5000 宽，缩到 2400
        if n.startswith('hz'): im = im.filter(ImageFilter.MedianFilter(3))          # 减轻画传印刷网点
        if not n.startswith('hz') and max(im.size) < 1400:
            k = 1400 / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 30, 2))
        im.save(O + 'card_' + n + '.jpg', quality=93); pv.blur_bg(im, O + 'bg_' + n + '.jpg')
    print('cards ok')

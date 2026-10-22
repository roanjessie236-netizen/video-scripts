# 尾声（1936）素材准备：AI 情景再现（木刻风“这也是生活”四景、星夜窗前、写便条的手、今日四景）调色；全集彩插/画传照片裁切；电影《鲁迅》（2005）抽帧，统一“冷调旧胶片·中档”（今日画面只轻调）
# 大文件一律放 /tmp（/data 只放脚本）：输出 /tmp/src7/（preview/src7 为符号链接）；原始页 /tmp/src7pdf/；电影分段 /tmp/lx/LX2005_P*.mp4
# 原始页：pdfimages -j 《鲁迅全集》第2024、2026、6080、6083页 → qjN-000.jpg；pdftoppm -r 200 《鲁迅画传》（234页版）第234页 → hz234-234.png
# 用法：python3 prep_ch7.py [--cards] [--film [名1,名2]]
import os, sys, glob, time, subprocess, numpy as np
from PIL import Image, ImageFilter, ImageOps
import importlib.util
R = '/data/luxun90/'; P = '/tmp/src7pdf/'; O = '/tmp/src7/'; FILES = '/data/.agent-service/files/'; LX = '/tmp/lx/'
spec = importlib.util.spec_from_file_location('pv', R + 'preview/prep_lib.py'); pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
os.makedirs(O, exist_ok=True)
if not os.path.exists(R + 'preview/src7'): os.symlink(O, R + 'preview/src7')
# AI 图：(session file, 裁切 l,t,r,b 或 None, 调色强度)。木刻风四景按全集彩插大陆新村寓所内景（QJ-p2026）布置，不画时钟；人物一律不露脸
AI = {'b01': ('1c483e6a-fdb8-43ce-89f8-3a2e3ac5a98b', None, 0.75),                  # 1935年残秋：星夜窗前的背影（《亥年残秋偶作》）
      'w01': ('5d6137e3-9eda-46a8-abaf-b282c604c9fc', (58, 50, 1148, 832), 0.6),    # 木刻风：深夜卧室，街灯穿窗（床上人影不露脸）
      'w02': ('7c13d687-960c-49e1-bbfb-f8f276153b6a', (186, 18, 1192, 748), 0.6),   # 木刻风：书堆与未订的画集（书脊已去字）
      'w03': ('dbd66015-b909-43b6-99c8-7cb2db2af396', (232, 30, 1146, 738), 0.6),   # 木刻风：窗外里弄屋顶
      'w04': ('36949735-1e77-461d-9ab0-7a03db814a85', (124, 80, 1254, 690), 0.6),   # 木刻风：无穷的远方，无数灯火
      'c01': ('9eeadc0c-3b9f-49d8-a195-c16d4a45d9c6', None, 0.75),                  # 1936年10月18日凌晨：写便条的手（字迹模糊不可读）
      'd01': ('b57ae592-5883-4481-b16b-6be8e08dd2fd', None, 0.3),                   # 今日：墓前鲜花
      'd02': ('f5d29061-68fc-45b4-9947-cab8acb9e514', None, 0.3),                   # 今日：故居门前参观者背影
      'd03': ('21a8c013-7ce6-4e76-93b3-0853c9ad7556', None, 0.3),                   # 今日：地铁里读书的手
      'd05': ('d328e359-f613-44c9-9183-cdac51c8263c', None, 0.3)}                   # 夏夜河畔（萤火为程序生成）
CARD = {'qj2024': ('qj2024-000.jpg', None),                    # 1936年10月8日，全国第二回木刻流动展览会上（沙飞摄）
        'hz234': ('hz234-234.png', (320, 1220, 1600, 3020))}   # 1936年的鲁迅墓（万国公墓），墓碑下部是周海婴题字
PHOTO = {'p2026': ('qj2026-000.jpg', (0, 0, 1130, 740)),       # 大陆新村寓所卧室（内景）
         'p6080': ('qj6080-000.jpg', None),                    # 遗容
         'p6083': ('qj6083-000.jpg', None)}                    # 鲁迅墓（今鲁迅公园）
SRC = {os.path.basename(f)[7:10]: (f, 1280, 720) for f in sorted(glob.glob(LX + 'LX2005_P*.mp4'))}   # 电影《鲁迅》（2005）分段，键 P21…P25
LXC = (115, 64, 1050)   # 有效画面（去黑边与转载台标）
FILM = [('x_sick', [('P22', 229.0, 233.5, LXC)]),      # 病床（白天）
        ('x_night1', [('P23', 152.0, 157.0, LXC)]),    # 深夜病床
        ('x_wake', [('P23', 170.0, 172.9, LXC)]),      # 醒来
        ('x_xu', [('P23', 173.3, 179.0, LXC)]),        # 许广平被叫醒
        ('x_bottle', [('P24', 35.0, 41.0, (140, 100, 820))]),   # 病床边的药瓶（裁掉右侧闹钟）
        ('x_mkhall', [('P22', 114.0, 120.0, LXC)]),    # 木刻展上与青年
        ('x_asthma', [('P24', 6.0, 13.0, LXC)]),       # 深夜气喘
        ('x_ling', [('P24', 109.8, 116.0, LXC)]),      # 灵前烛光
        ('x_sangyi', [('P24', 276.5, 281.0, LXC)]),    # “鲁迅先生丧仪”
        ('x_songzang', [('P25', 11.5, 17.5, LXC)]),    # 送葬队伍经过街道
        ('x_mzh', [('P24', 285.0, 288.8, LXC)]),       # “民族魂”旗
        ('x_crowd25', [('P25', 48.0, 51.8, LXC)])]     # 送葬的人们
def one(item):
    name, segs = item; d = O + name + '/'; os.makedirs(d, exist_ok=True); [os.remove(d + x) for x in os.listdir(d)]; k = 0
    tmp = f'/tmp/film7_{name}/'; os.makedirs(tmp, exist_ok=True)
    for f, a, b, (x0, y0, w) in segs:
        path, sw, sh = SRC[f]
        cw = round(w / 2) * 2; ch = round(w * 9 / 32) * 2
        [os.remove(tmp + x) for x in os.listdir(tmp)]
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-threads', '1', '-ss', str(a), '-t', str(b - a), '-i', path, '-an',
                        '-vf', f'crop={cw}:{ch}:{x0}:{y0},scale=1920:1080:flags=lanczos,fps=25', '-q:v', '2', tmp + '%04d.jpg'], check=True)
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
    for n, (fid, cr, k) in AI.items():
        im = Image.open(FILES + fid + '/tool-output-0.jpg').convert('RGB')
        if cr: im = im.crop(cr)
        im = pv.upto(im); pv.grade_base(im, k).save(O + n + '.jpg', quality=93); pv.blur_bg(im, O + 'bg_' + n + '.jpg')
    for n, (f, cr) in CARD.items():
        im = Image.open(P + f).convert('RGB')
        if cr: im = im.crop(cr)
        if n.startswith('hz'): im = im.filter(ImageFilter.MedianFilter(3))          # 减轻画传印刷网点
        if max(im.size) < 1400:
            s = 1400 / max(im.size); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 30, 2))
        im.save(O + 'card_' + n + '.jpg', quality=93); pv.blur_bg(im, O + 'bg_' + n + '.jpg')
    for n, (f, cr) in PHOTO.items():   # 直接铺满画面慢推的史料照片
        im = Image.open(P + f).convert('RGB')
        if cr: im = im.crop(cr)
        im = pv.upto(im); pv.grade_base(im, 0.6).save(O + n + '.jpg', quality=93)
    print('cards ok')

# 第二章素材准备：画传/全集/《坟》1947年版裁切成相片卡；AI 情景再现图统一“冷调旧胶片·中档”。输出到 preview/src3/
# 原始页：pdftoppm -r 200 画传第13…43页 → v3/pdf/hzN-0NN.png；pdfimages -j 全集第97、492、496、3344页 → v3/pdf/qjN-000.jpg
#        《坟》1947年版（Commons NLC416-10jh006112-28811）pdfimages 第53页 → v3/pdf/fen1947_p53.png
import os, numpy as np
from PIL import Image, ImageFilter, ImageOps
import importlib.util
R = '/data/luxun90/'; P = R + 'preview/v3/pdf/'; AW = R + 'assets/web/'; O = R + 'preview/src3/'; FILES = '/data/.agent-service/files/'
spec = importlib.util.spec_from_file_location('pv', R + 'preview/prep_lib.py'); pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
os.makedirs(O, exist_ok=True)
AI = {'b01': 'e7bb0a87-52d0-439e-99ac-dbb3692ede4e',   # 幻灯机与银幕
      'b02': '716b9989-7dae-4f99-ab88-2fd92c18ff56',   # 讲堂里欢呼的学生（背面）
      'b03': '2bb75fbb-be65-4b54-afeb-ae5164ff85b3',   # 角落里不动的中国青年（背影）
      'b04': '747724ef-28fb-4e03-8d6d-bdd996d16df0',   # 走出讲堂进雪地（背影）
      'b05': '45adc504-b1e0-4a9b-9950-f44306067661'}   # 仙台寓所夜读解剖学（背影，r2 替换父亲照）
CARD = {  # 名: (文件, 裁切 l,t,r,b 像素)
 'hz13': ('hz13-013.png', (329, 2028, 1596, 2928)), 'hz14a': ('hz14-014.png', (271, 490, 2013, 1610)), 'hz14b': ('hz14-014.png', (827, 2040, 1335, 3148)),
 'hz18': ('hz18-018.png', (7, 476, 1837, 2900)), 'hz24b': ('hz24-024.png', (1340, 256, 2379, 2272)),
 'hz29': ('hz29-029.png', (22, 0, 1850, 2965)), 'hz30': ('hz30-030.png', (22, 0, 2400, 1098)), 'hz31': ('hz31-031.png', (0, 1880, 1580, 3230)),
 'hz33': ('hz33-033.png', (30, 640, 1165, 2253)), 'hz34': ('hz34-034.png', (475, 487, 1480, 1730)), 'hz40': ('hz40-040.png', (231, 499, 1279, 1991)),
 'hz43': ('hz43-043.png', (183, 481, 1066, 1596)), 'qj97': ('qj97-000.jpg', None), 'qj492': ('qj492-000.jpg', None), 'qj496': ('qj496-000.jpg', None),
 'qj3344': ('qj3344-000.jpg', None), 'w0502': (AW + 'W05/W05-02-tianyan-wu-preface.jpg', None), 
 'fen53': ('fen1947_p53.png', None),
 'hz35': ('hz35-035.png', (192, 0, 2160, 2880)), 'hz39': ('hz39-039.png', (272, 500, 1240, 1760))}
def trim(im, thr=14):
    """去掉四周与页面底色接近的白边/黑边"""
    g = np.asarray(ImageOps.grayscale(im)).astype(np.int16); bgv = np.median(np.concatenate([g[0], g[-1], g[:, 0], g[:, -1]]))
    m = np.abs(g - bgv) > thr; rows = np.where(m.mean(1) > 0.06)[0]; cols = np.where(m.mean(0) > 0.06)[0]
    if len(rows) < 10 or len(cols) < 10: return im
    return im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
for n, fid in AI.items():
    im = pv.upto(Image.open(FILES + fid + '/tool-output-0.jpg').convert('RGB')); pv.grade_base(im).save(O + n + '.jpg', quality=93); pv.blur_bg(im, O + 'bg_' + n + '.jpg')
for n, (f, cr) in CARD.items():
    im = Image.open(f if f.startswith('/') else P + f).convert('RGB')
    if cr: im = trim(im.crop(cr))
    if n.startswith('hz'): im = im.filter(ImageFilter.MedianFilter(3))          # 减轻画传印刷网点
    if n in ('w0502', 'w0602', 'qj496', 'qj97', 'qj492', 'qj3344') and max(im.size) < 1400:
        k = 1400 / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 30, 2))
    if n == 'fen53':   # 1-bit 扫描 → 旧纸色
        a = np.asarray(ImageOps.grayscale(im).filter(ImageFilter.GaussianBlur(0.7))).astype(np.float32)[..., None] / 255
        im = Image.fromarray((a * np.array([232, 224, 206]) + (1 - a) * np.array([36, 32, 30])).astype(np.uint8))
    im.save(O + 'card_' + n + '.jpg', quality=93); pv.blur_bg(im, O + 'bg_' + n + '.jpg')
print('ok')

# 样片 v3 素材准备：AI 情景再现图与当代实拍统一“冷调旧胶片·中档”（底色部分；暗角与颗粒在渲染时逐帧叠加）
# 老照片／手稿／版画保持原样，只另做模糊压暗的冷调背景。输出到 preview/src3/
import os, sys, numpy as np
from PIL import Image, ImageFilter, ImageOps
R = '/data/luxun90/'; S = R + 'preview/src/'; WEB = R + 'preview/v3/web/'; AW = R + 'assets/web/'; O = R + 'preview/src3/'
FILES = '/data/.agent-service/files/'
os.makedirs(O, exist_ok=True)
AI = {  # 编号: (会话文件ID, 裁切 l,t,r,b)  均为 1376x768 生成图
 'a01': ('13fad608-5fea-4d6e-9867-96619d05711c', None), 'a03': ('e6376029-6045-4a68-b33e-62c7d779f742', None),
 'a04': ('3b24b7dc-1a3f-485d-855e-410ffa5741ce', None), 'a05': ('41e84c14-e892-4404-bba8-bae1da211d33', (0, 0, 1334, 745)),
 'a06': ('1d2b8591-b28f-4751-aa65-2b1e42d74c36', None), 'a07': ('7a695a32-f145-494e-be70-648298568c63', None),
 'a08': ('7a3aa7a8-f663-4239-a41d-33d818f354fa', None), 'a09': ('5cd5f836-1e36-42be-bf68-2dfda72566bf', (0, 8, 1376, 768)),
 'a10': ('58f37269-e100-4e8e-b6bf-4afbddfc7da7', None), 'a11': ('14346210-e394-40f6-8fb7-d0511a40f5d8', None),
 'a12': ('78a07119-3153-4cf4-b5de-757701a378bc', None), 'a13': ('5b694439-8290-45d2-8eac-65f101e3bb2d', None)}
MOD = {'m_tomb': WEB + '上海鲁迅墓2020_1_.jpg', 'm_house': WEB + '上海市鲁迅故居.jpg', 'm_bed': AW + 'W11/W11-01-shanghai-bedroom-display.jpg',
       'm_water': AW + 'W04/W04-04-shaoxing-waterway.jpg', 'm_taimen': AW + 'W04/W04-01-zhou-new-taimen.jpg'}
CARD = {'w0201': AW + 'W02/W02-01-shafei-funeral-1936.jpg', 'w0202': AW + 'W02/W02-02-xinzhonghua-funeral-1936.jpg',
        'w01': AW + 'W01/W01-01-si-manuscript-web.jpg', 'qj2028': S + 'qj2028-000.jpg', 'hz231': S + 'c_hz231.png', 'hz4': S + 'c_hz4.png',
        'hz6': S + 'c_hz6.png', 'hz7': S + 'c_hz7.png', 'hz9': S + 'c_hz9.png', 'hz10f': S + 'c_hz10f.png', 'hz10m': S + 'c_hz10m.png',
        'hz11': S + 'c_hz11.png', 'art05': S + 'art05.jpg'}
CROP = {'art05': (0.0, 0.0, 1.0, 0.955), 'qj2028': (0.0, 0.0, 0.62, 0.70)}   # 版画去掉底部图注；手稿取《死》首页
def grade_base(im, k=0.75):
    a = np.asarray(im.convert('RGB')).astype(np.float32) / 255
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    a = lum + (a - lum) * (1 - 0.5 * k)                                                                   # 降饱和
    a = a + ((1 - lum) ** 2) * np.array([-0.05, 0.004, 0.07]) * k + (lum ** 2) * np.array([-0.035, 0.0, 0.03]) * k  # 阴影冷、高光微冷
    a = 0.05 * k + a * (1 - 0.09 * k)                                                                     # 抬黑、压白
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
def upto(im, w=2400):
    if im.width < w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 40, 2))
    elif im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    return im
def cover(im, w, h):
    r = max(w / im.width, h / im.height); im = im.resize((max(w, round(im.width * r)), max(h, round(im.height * r))), Image.LANCZOS)
    x = (im.width - w) // 2; y = (im.height - h) // 2; return im.crop((x, y, x + w, y + h))
def blur_bg(im, out):
    bg = cover(im.convert('RGB'), 2112, 1188).filter(ImageFilter.GaussianBlur(30))
    bg = Image.blend(bg, Image.new('RGB', bg.size, (22, 26, 30)), 0.6); grade_base(bg, 1.0).save(out, quality=92)
for n, (fid, cr) in AI.items():
    im = Image.open(FILES + fid + '/tool-output-0.jpg').convert('RGB')
    if cr: im = im.crop(cr)
    im = upto(im); grade_base(im).save(O + n + '.jpg', quality=93); blur_bg(im, O + 'bg_' + n + '.jpg')
for n, p in MOD.items():
    im = upto(Image.open(p).convert('RGB')); g = grade_base(im); g.save(O + n + '.jpg', quality=93); blur_bg(g, O + 'bg_' + n + '.jpg')
for n, p in CARD.items():
    im = Image.open(p).convert('RGB')
    if n in CROP:
        l, t, r, b = CROP[n]; im = im.crop((round(l * im.width), round(t * im.height), round(r * im.width), round(b * im.height)))
    if max(im.size) < 1400: im = im.resize((round(im.width * 1400 / max(im.size)), round(im.height * 1400 / max(im.size))), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 30, 2))
    if n == 'hz231': im = im.filter(ImageFilter.MedianFilter(3))   # 减轻印刷网点
    im.save(O + 'card_' + n + '.jpg', quality=93); blur_bg(im, O + 'bg_' + n + '.jpg')
# 片名墨字遮罩（取自 M02 书法片名的亮度）
t = ImageOps.grayscale(Image.open(S + 'm02_title.jpg')); m = t.point(lambda v: int(max(0, min(255, (v - 50) * 255 / 170))))
m.crop(m.getbbox()).save(O + 'title_mask.png')
# 全屏用：hz231 横幅裁切（脸部）、hz4 全屏
p = Image.open(S + 'c_hz231.png').convert('RGB'); p = p.crop((0, 0, p.width, round(p.width * 1188 / 2112)))
p = p.resize((p.width // 2, p.height // 2), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))   # 先缩小去网点
p.resize((2112, 1188), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 35, 2)).save(O + 'full_hz231.jpg', quality=93)
print('ok', len(os.listdir(O)))

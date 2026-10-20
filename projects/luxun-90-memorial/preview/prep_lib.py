# prep_v3.py / prep_ch2.py 共用：冷调旧胶片底色、放大、铺满、模糊压暗背景
import numpy as np
from PIL import Image, ImageFilter, ImageOps
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

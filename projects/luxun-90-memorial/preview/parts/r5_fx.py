T_NE, T_412, T_LX = '纪录影像 · 北伐（1926—1928）', '纪录影像 · 1927年“清党”', '影视剧《鲁迅》（2005）'
LX_NOTE = '上海电影制片厂 · 丁荫楠导演 · 濮存昕饰鲁迅　非历史影像'
NOTE = text_rgba('画面为情景再现', SANS(24), (214, 216, 214, 255), shadow=3)
def RECON(a, b): ov(a, b, lambda base, t, al: paste_a(base, NOTE, (W - 56 - NOTE.width + 14, 94), al), 0.4, 0.4)
def chain(*ps):
    def post(im, t, d, M, size):
        for p in ps: im = p(im, t, d, M, size) or im
        return im
    return post
# 雾气 / 蒸汽缓缓飘移（站台白雾、河上晨雾）
_fr = np.random.default_rng(5)
FOGT = Image.fromarray((np.clip(_fr.normal(0.5, 0.22, (40, 160)), 0, 1) * 255).astype(np.uint8)).resize((W * 2, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30))
def fog(a=0.3, speed=45, col=(214, 220, 228)):
    lut = [int(clamp((v - 120) / 100) * 255 * a) for v in range(256)]
    def post(im, t, d, M, size):
        x = int(t * speed) % W; im.paste(col, (0, 0), FOGT.crop((x, 0, x + W, H)).point(lut))
    return post
# 雨丝：坐标在原图空间（随推镜放大），可限定在窗洞等区域内
rr2 = random.Random(4)
RAIN = [(rr2.uniform(0, 1), rr2.uniform(0, 1), rr2.uniform(0.9, 1.5), rr2.uniform(28, 64), rr2.uniform(0.25, 0.6)) for _ in range(400)]
def rain(regions=((0, 0, 1, 1),), a=1.0, ang=0.1, n=220, col=(196, 206, 220)):
    def post(im, t, d, M, size):
        lay = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(lay); k = 0
        for l, tp, r, b in regions:
            m = int(n * (r - l) * (b - tp)) + 10
            for x0, y0, sp, ln, al in RAIN[k:k + m]:
                v = (y0 + sp * t) % 1.0; x, y = to_screen(M, l + (r - l) * x0, tp + (b - tp) * v, size)
                dr.line((x, y, x - ang * ln, y - ln), fill=int(255 * al * a), width=2)
            k += m
        im.paste(col, (0, 0), lay.filter(ImageFilter.GaussianBlur(0.7)))
    return post
# 海船的轻微摇晃（旋转 + 起伏）
def ROLL(n, z0, z1, c0, c1, amp=0.45, per=4.6, bob=5):
    base = KB(n, z0, z1, c0, c1)
    def fn(t, d):
        im = base(t, d); th = math.radians(amp * math.sin(2 * math.pi * t / per)); s_ = 1.035
        dy = bob * math.sin(2 * math.pi * t / per + 1.1); a_, b_ = math.cos(th) / s_, math.sin(th) / s_; cx, cy = W / 2, H * 0.6
        return im.transform((W, H), Image.AFFINE, (a_, b_, cx - a_ * cx - b_ * cy, -b_, a_, cy + b_ * cx - a_ * cy + dy), resample=Image.BILINEAR)
    return fn
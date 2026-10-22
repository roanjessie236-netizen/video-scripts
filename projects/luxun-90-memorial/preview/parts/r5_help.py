def at(sub):
    for a, b, c in SUBLOG:
        if sub in c: return a
    raise KeyError(sub)
def at_char(k, after=-1.0):
    for a, b, c in SUBLOG:
        if k in c and a >= after - 1e-6: return a + (b - a) * c.index(k) / len(c)
    raise KeyError(k)
def dim(k0, k1, t0=0.0, t1=1.0):
    def post(im, t, d, M, size):
        k = lerp(k0, k1, ease((t - t0) / max(0.01, t1 - t0))); return Image.blend(im, Image.new('RGB', (W, H), (6, 8, 10)), k) if k > 0 else im
    return post
SRC_HZ, SRC_QJ, SRC_WC, SRC_IA = '出处：林贤治《鲁迅画传》', '出处：《鲁迅全集》2005年版', '出处：Wikimedia Commons', '出处：Internet Archive'
DARK = Image.new('RGB', (W, H), (6, 8, 10))
HIDE = []   # 不显示底部字幕的区间（改为画面中央大字）
def C(a, b, fn): clip(a, b + 0.5, fn, 'cut', 0)          # 硬切（后一镜头盖住前一镜头）
def XQ(a, b, fn): clip(a - 0.2, b + 0.5, fn, 'fade', 0.4)  # 快叠化 0.4 秒

# ---------- 右上角来源标签（同一标签相邻时合并，切换时 0.25 秒淡变） ----------
TAGL = []
def TAG(a, b, txt): TAGL.append((a, b, txt))
def AITAG(a, b): TAG(a, b, 'AI 情景再现')
T_JX, T_AQ, T_17, T_FR = '影视剧《觉醒年代》', '电影《阿Q正传》（1981）', '纪录影像 · 1917年北京', '纪录影像 · 1920年代'
def build_tags():
    m = []
    for a, b, t in sorted(TAGL):
        if m and m[-1][2] == t and a - m[-1][1] < 0.6: m[-1][1] = max(m[-1][1], b)
        else: m.append([a, b, t])
    for a, b, t in m:
        im = DER(('tag', t), lambda t=t: tag_rgba(t))
        ov(a - 0.1, b + 0.1, lambda base, tt, al, im=im: paste_a(base, im, (W - 56 - im.width, 48), al), 0.25, 0.25)

# ---------- 影像片段（prep_ch34.py 已抽成 25fps 调色帧；片段不够长时自动放慢，不定格） ----------
import os
FILMN, SLOW = {}, []
def FILM(n, z0=1.0, z1=1.04, c0=(.5, .5), c1=(.5, .5), speed=1.0, gray=None, post=None, off=0.0):
    if n not in FILMN: FILMN[n] = len(os.listdir(S3 + n))
    def fn(t, d):
        N = FILMN[n]; sp = min(speed, (N - 1 - off * FPS) / max(1.0, d * FPS))
        if (n, round(d, 2)) not in [x[:2] for x in SLOW]: SLOW.append((n, round(d, 2), round(sp, 2)))
        k = max(0, min(N - 1, int(off * FPS + t * FPS * sp))); u = t / d
        src = Image.open(f'{S3}{n}/{k:04d}.jpg').convert('RGB')
        im, M = kb(src, lerp(z0, z1, u), lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u))
        if gray: g = gray(t, d); im = Image.blend(im, ImageOps.grayscale(im).convert('RGB'), g) if g > 0 else im
        if post: im = post(im, t, d, M, src.size) or im
        return im
    return fn
JX_NOTE = '2021年 · 曹磊饰鲁迅　非历史影像'
AQ_NOTE = '上海电影制片厂 · 岑范导演　片头鲁迅为演员扮演 · 非历史影像'
A17_NOTE = 'Benjamin Brodsky 摄 · 经 AI 修复上色'

# ---------- 动态效果 ----------
def radial(R, power=1.6):
    y, x = np.mgrid[-R:R, -R:R]; d = np.sqrt(x * x + y * y) / R
    return Image.fromarray((255 * np.clip(1 - d, 0, 1) ** power).astype(np.uint8))
def flick(t, seed=0):
    return 0.5 + 0.5 * (0.55 * math.sin(t * 11.3 + seed) + 0.3 * math.sin(t * 6.7 + 1.3 + seed) + 0.15 * math.sin(t * 23.1 + seed * 2))
def lamp(p, R=300, amp=0.16, col=(255, 196, 128)):
    """油灯火苗闪烁：灯焰周围暖光随时间起伏，整幅画面亮度随之微动"""
    def post(im, t, d, M, size):
        x, y = to_screen(M, p[0], p[1], size); f = flick(t, p[0] * 10)
        m = DER(('rad', R), lambda: radial(R)); a = amp * (0.35 + 0.65 * f)
        im.paste(col, (int(x - R), int(y - R)), m.point(lambda v, a=a: int(v * a)))
        k = 0.03 * (f - 0.5)
        return Image.blend(im, DARK, -k * 2) if k < 0 else im
    return post

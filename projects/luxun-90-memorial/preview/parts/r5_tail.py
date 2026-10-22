# ---------- 浮尘（淡） ----------
rnd = random.Random(11)
DUST = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(-12, 12), rnd.uniform(-18, -5), rnd.choice([2, 3, 4, 6]), rnd.uniform(0, 6.28)) for _ in range(40)]
SPR = {}
for r in (2, 3, 4, 6):
    m = Image.new('L', (r * 6, r * 6), 0); ImageDraw.Draw(m).ellipse((r * 2, r * 2, r * 4, r * 4), fill=255); m = m.filter(ImageFilter.GaussianBlur(r * 0.8))
    s = Image.new('RGBA', m.size, (236, 236, 230, 255)); s.putalpha(m); SPR[r] = s
DUSTR = [(t_17, ST['S3-04']), (ST['S4-05'], EN['S4-05'])]
def dust(base, T):
    a = max([clamp((T - a0) / 0.8) * clamp((a1 - T) / 0.8) for a0, a1 in DUSTR] + [0])
    if a <= 0: return
    for x0, y0, vx, vy, r, ph in DUST:
        paste_a(base, SPR[r], ((x0 + vx * T) % W, (y0 + vy * T) % H), a * (0.2 + 0.2 * math.sin(T * 1.7 + ph)))

# ---------- 胶片质感（逐帧：暗角 + 颗粒） ----------
_yy, _xx = np.mgrid[0:H, 0:W]; _d = np.sqrt(((_xx - W / 2) / (W / 2)) ** 2 + ((_yy - H / 2) / (H / 2)) ** 2)
VIG = Image.fromarray((255 * (1 - 0.35 * np.clip(_d - 0.55, 0, 1) ** 1.6)).astype(np.uint8)).convert('RGB')
_g = np.random.default_rng(7)
GRAIN = [Image.fromarray(np.clip(128 + _g.normal(0, 5.2, (H, W)), 0, 255).astype(np.uint8)).convert('RGB') for _ in range(6)]
del _yy, _xx, _d

# ---------- 合成 ----------
PAPER_T = []   # 本章��字镜头均为暗底白字
SUBGRAD = Image.new('RGBA', (W, 300), (0, 0, 0, 0)); SUBGRAD.putalpha(Image.linear_gradient('L').resize((W, 300)).point(lambda v: int((v / 255) ** 1.6 * 150)))
WHITE = Image.new('RGB', (W, H), (250, 250, 248)); BLACK = Image.new('RGB', (W, H), (0, 0, 0))
SHK = [(16, -10), (-12, 8), (8, -5), (-5, 3), (2, -1), (0, 0)]
def frame(T):
    base = BLACK; act = [c for c in clips if c[0] <= T < c[1]]; k0 = 0
    for i in range(len(act) - 1, -1, -1):   # 从最上面一个完全不透明的镜头开始画，下面被盖住的不再计算
        t0, t1, fn, tr, td = act[i]
        if tr == 'cut' or td <= 0 or T - t0 >= td: k0 = i; break
    for t0, t1, fn, tr, td in act[k0:]:
        img = fn(T - t0, t1 - t0)
        if tr == 'cut' or td <= 0 or T - t0 >= td: base = img; continue
        a = (T - t0) / td
        if tr in ('fade', 'black'): base = Image.blend(base, img, ease(a))
        elif tr == 'flash': base = Image.blend(Image.blend(base, img, ease(a)), WHITE, 0.9 * (1 - abs(2 * a - 1)))
    if base is BLACK: base = BLACK.copy()
    dust(base, T)
    for ts in SHAKES:
        if ts <= T < ts + len(SHK) / FPS:
            dx, dy = SHK[int((T - ts) * FPS)]; s = 1.025
            base = base.transform((W, H), Image.AFFINE, (1 / s, 0, W * (1 - 1 / s) / 2 - dx / s, 0, 1 / s, H * (1 - 1 / s) / 2 - dy / s), resample=Image.BILINEAR)
    base = ImageChops.multiply(base, VIG)
    base = ImageChops.add(base, GRAIN[int(T * FPS) % len(GRAIN)], 1.0, -128)
    for t0, t1, dr, fin, fout in ovs:
        if t0 <= T < t1: dr(base, T - t0, min(clamp((T - t0) / fin), clamp((t1 - T) / fout)))
    pm = any(a <= T < b for a, b in PAPER_T)
    hid = any(a <= T < b for a, b in HIDE)
    sa = 0 if hid else max([min(clamp((T - t0 + 0.4) / 0.4), clamp((t1 - T + 0.4) / 0.4)) for t0, t1, *_ in subs] + [0])
    if sa > 0 and not pm: paste_a(base, SUBGRAD, (0, H - SUBGRAD.height), sa)
    for t0, t1, ims, attr in subs:
        if t0 <= T < t1 and not hid:
            a = min(clamp((T - t0) / 0.15), clamp((t1 - T) / 0.15)); im = ims[pm]
            paste_a(base, im, (W / 2 - im.width / 2, H - 120 - im.height / 2), a)
            if attr: paste_a(base, attr[pm], (W / 2 - attr[pm].width / 2, H - 62 - attr[pm].height / 2), a)
    if T < TOTAL_MAIN: paste_a(base, WM, (W - 36 - WM.width, H - 40 - WM.height), 0.45)
    return base

if __name__ == '__main__':
    if '--plan' in sys.argv:
        for sid, _ in SEQ: print(sid, round(ST[sid], 2), round(EN[sid] - ST[sid], 2), '母版', round(OFF + ST[sid], 2))
        print('TOTAL_MAIN', TOTAL_MAIN, 'TURN', round(TURN3, 2), round(TURN4, 2))
        for s in SUBLOG: print(*s)
        for c in clips: print(round(c[0], 2), round(c[1], 2), c[3])
        for tt in np.arange(0, TOTAL, 0.5): frame_check = [c for c in clips if c[0] <= tt < c[1]]; assert frame_check, tt
        for c in clips:
            if c[3] != 'flash': c[2](min(c[1] - c[0] - 0.01, c[1] - c[0]) * 0.999, c[1] - c[0])
        print('片段放慢：', [x for x in SLOW if x[2] < 0.999])
        sys.exit(0)
    if '--stills' in sys.argv:
        for tt in [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]:
            frame(tt).save(f'/tmp/v3_{tt:06.1f}.jpg', quality=85)
        sys.exit(0)
    k, n = map(int, sys.argv[sys.argv.index('--part') + 1].split('/')); out = sys.argv[sys.argv.index('--part') + 2]
    N = int(round(TOTAL * FPS)); a, b = N * k // n, N * (k + 1) // n
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(frame(f / FPS).tobytes())
        if (f - a) % 250 == 0: print(k, f - a, '/', b - a, flush=True)
    p.stdin.close(); p.wait(); print('done', k)

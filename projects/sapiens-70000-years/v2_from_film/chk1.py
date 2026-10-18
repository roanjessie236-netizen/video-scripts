import sys, numpy as np, cv2
sys.path.insert(0, '/data/v2f/v1core')
import render as R
from grab import grab
W, H = R.W, R.H
def hp(x):
    x = x.astype(np.float32)
    return x - cv2.GaussianBlur(x, (0, 0), 6)
for j in [96, 2000, 4000]:
    k = -(-j * 5 // 4)
    f = grab(k)[0]
    g = hp(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))[200:1100, 300:2200]
    cs = []
    for i in range(8):
        G = hp(R.GRAIN[i][..., 0])[200:1100, 300:2200]
        cs.append(float((g * G).mean() / (g.std() * G.std())))
    print(j, k, 'grain corr', ' '.join('%.3f' % c for c in cs), 'expect', j % 8)
# subtitle alignment at t=4.0
j = 96; k = 120; f = grab(k)[0].astype(np.float32)
s, e, text, _ = R.TL['subtitles'][0]
L = R.subtitle_layer(text)
h, w = L.shape[:2]
x0 = int(round(W / 2 - w / 2)); y0 = int(round(H - 150 - h / 2))
P = L[..., :3]; A = L[..., 3]
a = R.window(4.0, s, e, 0.35, 0.35)
roi = f[y0 - 10:y0 + h + 10, x0 - 10:x0 + w + 10]
best = []
lum = roi.mean(2)
for dy in range(-4, 5):
    for dx in range(-4, 5):
        pa = np.zeros_like(lum); pa[10 + dy:10 + dy + h, 10 + dx:10 + dx + w] = P.mean(2)
        best.append((np.corrcoef(pa.ravel(), lum.ravel())[0, 1], dx, dy))
best.sort(reverse=True); print('align', best[:3], 'alpha', a, 'layer', w, h, x0, y0)

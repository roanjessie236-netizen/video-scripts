import sys, numpy as np, cv2
import core as C, fill
from grab import grab
t = float(sys.argv[1]); x = int(sys.argv[2]); wdt = int(sys.argv[3]) if len(sys.argv) > 3 else 900
gain = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
j = int(round(t * 24)); t = j / 24
F = grab(C.k_of_j(j))[0]
cg = C.fit_grain(F)
crop, out = fill.clean_band(F, t, cg)
x0, y0, x1, y1 = crop
G = F.copy(); G[y0:y1, x0:x1] = np.clip(out + 0.5, 0, 255).astype(np.uint8)
a = F[1200:1400, x:x + wdt]; b = G[1200:1400, x:x + wdt]
img = np.vstack([a, b]).astype(np.float32) * gain
cv2.imwrite(sys.argv[5] if len(sys.argv) > 5 else 'crop11.png', np.clip(img, 0, 255).astype(np.uint8))

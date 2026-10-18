import sys, numpy as np, cv2
sys.path.insert(0, '/data/v2f/v1core')
import render_core as R
from grab import grab
def hp(x):
    x = x.astype(np.float32)
    return x - cv2.GaussianBlur(x, (0, 0), 4)
Gs = [hp(R.GRAIN[i][..., 0]) for i in range(8)]
for j0 in [96, 2000, 4400]:
    k0 = -(-j0 * 5 // 4)
    fr = grab(k0, 12)
    for kk in range(12):
        k = k0 + kk; j = (4 * k) // 5
        g = hp(cv2.cvtColor(fr[kk], cv2.COLOR_BGR2GRAY))
        co = [float((g * G).sum() / (G * G).sum()) for G in Gs]
        print(k, j, j % 8, 'argmax', int(np.argmax(co)), ' '.join('%.3f' % c for c in co))

import sys, numpy as np, cv2
import core as C, fill
from grab import grab
ts = [float(x) for x in sys.argv[1].split(',')]
rows = []
for t in ts:
    j = int(round(t * 24)); t = j / 24
    F = grab(C.k_of_j(j))[0]
    cg = C.fit_grain(F)
    crop, out, dbg = fill.clean_band(F, t, cg, debug=True)
    x0, y0, x1, y1 = crop
    G = F.copy(); G[y0:y1, x0:x1] = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    a = F[1150:1440, 500:2060]; b = G[1150:1440, 500:2060]
    yv = np.clip(dbg['y'], 0, 255).astype(np.uint8)
    c = np.zeros_like(a); c[y0 - 1150:y1 - 1150, max(0, x0 - 500):min(1560, x1 - 500)] = yv[:, max(0, 500 - x0):max(0, 500 - x0) + min(1560, x1 - 500) - max(0, x0 - 500)]
    lab = np.vstack([a, b, c])
    cv2.putText(lab, '%.2fs' % t, (10, 40), 0, 1.2, (0, 255, 255), 2)
    rows.append(lab)
    print(t, 'grain', np.round(cg, 2), 'wt min %.2f' % dbg['wt'][dbg['aA'] > 0.5].min() if (dbg['aA'] > 0.5).any() else '',
          'ratio', np.percentile(dbg['ratio'], [5, 50, 95]).round(3))
img = np.vstack(rows)
cv2.imwrite('test_clean.jpg', cv2.resize(img, (img.shape[1] * 2 // 3, img.shape[0] * 2 // 3), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 90])

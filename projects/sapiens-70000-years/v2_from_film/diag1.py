import sys, numpy as np, cv2
import core as C, fill
from grab import grab
for t in [float(x) for x in sys.argv[1].split(',')]:
    j = int(round(t * 24)); t = j / 24
    F = grab(C.k_of_j(j))[0]
    cg = C.fit_grain(F)
    crop, out, d = fill.clean_band(F, t, cg, debug=True)
    x0, y0, x1, y1 = crop
    aA = d['aA']; xi = d['xinv'].mean(2); y = d['y'].mean(2)
    Fc = F[y0:y1, x0:x1].astype(np.float32).mean(2)
    # local mean-normalised ratio
    print('t=%.2f' % t)
    for lo, hi in [(0, 0.02), (0.02, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.8), (0.8, 0.95), (0.95, 1.01)]:
        m = (aA >= lo) & (aA < hi)
        if m.sum() < 50: continue
        print('  aA %.2f-%.2f n=%6d  F=%.1f  xinv=%.1f  y=%.1f  xinv/y=%.3f' % (lo, hi, m.sum(), Fc[m].mean(), xi[m].mean(), y[m].mean(), xi[m].mean() / y[m].mean()))

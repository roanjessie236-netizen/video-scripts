"""Measure the alpha of the two baked v1 closing captions in the user's re-timed ending (user frames 7992..8523)."""
import json, numpy as np, cv2
import core as C
from core import W, H
from render_core import caption_layer, text_layer, font
caps = C.TL1['captions']
lay = []
for s, e, text in caps:
    L = caption_layer(text)
    h, w = L.shape[:2]
    x0, y0 = int(round(W / 2 - w / 2)), int(round(H * 0.27 - h / 2))
    g = text_layer(text, font('Light', 92), (238, 242, 250), tracking=30)  # glyph only (same pad? check)
    lay.append((L, x0, y0, g))
    print(text, L.shape, g.shape, x0, y0)
X0, Y0, X1, Y1 = 600, 180, 1960, 600
res = []
for k, F in C.frames(7992, 8524):
    Fc = F[Y0:Y1, X0:X1].astype(np.float32)
    row = [k]
    for L, x0, y0, g in lay:
        h, w = L.shape[:2]
        A = L[..., 3]; P = L[..., :3]
        # glyph mask: the glyph-only layer has the same text origin when pads match; use core where A~1 and P bright
        core = (A > 0.97) & (P.mean(2) > 200)
        ring = (A > 0.25) & (A < 0.6)
        sub = Fc[y0 - Y0:y0 - Y0 + h, x0 - X0:x0 - X0 + w]
        Fcore = sub[core].mean(0); Fring = sub[ring].mean(0)
        Pc = P[core].mean(0); Pr = P[ring].mean(0); Ar = A[ring].mean()
        far = np.concatenate([Fc[:40].reshape(-1, 3), Fc[-40:].reshape(-1, 3)]).mean(0)
        bg = far.copy(); a = 0.0
        for it in range(8):
            a = float(np.clip(np.mean((Fcore - bg) / np.maximum(Pc - bg, 1)), 0, 1))
            # ring: Fr = bg(1-a Ar) + a Pr -> bg
            if a < 0.98:
                bg = np.clip((Fring - a * Pr) / max(1 - a * Ar, 0.05), 0, 255)
        row += [a, float(Fcore.mean())]
    res.append(row)
    if k % 50 == 0:
        print(k, ['%.3f' % v for v in row[1:]], flush=True)
json.dump(res, open('cap_alpha.json', 'w'))

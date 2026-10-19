# crop black letterbox/pillarbox bars from AI images, keep 16:9, overwrite in place (orig -> rej/)
import sys, shutil, numpy as np
from PIL import Image
for p in sys.argv[1:]:
    im = Image.open(p).convert('RGB'); a = np.asarray(im).astype(np.float32).mean(2)
    h, w = a.shape
    rows = a.mean(1); cols = a.mean(0)
    t = 0
    while t < h // 6 and rows[t] < 6 and a[t].max() < 40: t += 1
    b = h
    while b > h - h // 6 and rows[b - 1] < 6 and a[b - 1].max() < 40: b -= 1
    l = 0
    while l < w // 6 and cols[l] < 6 and a[:, l].max() < 40: l += 1
    r = w
    while r > w - w // 6 and cols[r - 1] < 6 and a[:, r - 1].max() < 40: r -= 1
    if (t, b, l, r) == (0, h, 0, w): print(p, 'no bars'); continue
    t += 2 if t else 0; b -= 2 if b < h else 0; l += 2 if l else 0; r -= 2 if r < w else 0
    ch, cw = b - t, r - l
    if cw / ch > 16 / 9: nw = int(ch * 16 / 9); l += (cw - nw) // 2; r = l + nw
    else: nh = int(cw * 9 / 16); t += (ch - nh) // 2; b = t + nh
    shutil.copy(p, 'rej/' + p.split('/')[-1].replace('.png', '_bars.png'))
    im.crop((l, t, r, b)).resize((w, h), Image.LANCZOS).save(p)
    print(p, 'cropped', (l, t, r, b))

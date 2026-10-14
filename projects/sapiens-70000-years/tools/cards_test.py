import sys, os
sys.path.insert(0, '/data/video')
import numpy as np, cv2
from render_core import *

bg = np.full((H, W, 3), 90, np.uint8)
f1 = bg.copy()
blit_center(f1, title_layer(), W / 2, H / 2)
f2 = bg.copy()
c = TL['chapters'][2]
blit_center(f2, chapter_layer(c[2], c[3], c[4]), W / 2, H / 2)
f3 = bg.copy()
blit_center(f3, endcard_layer(), W / 2, H / 2)
f4 = bg.copy()
L = lower_layer('公元前 3500 年', '美索不达米亚 · 城市诞生')
blit(f4, L, 116, H - 236 - L.shape[0])
blit_center(f4, caption_layer('我们从哪里来？'), W / 2, H * 0.27)
sheet = np.vstack([np.hstack([cv2.resize(f1, (960, 540)), cv2.resize(f2, (960, 540))]),
                   np.hstack([cv2.resize(f3, (960, 540)), cv2.resize(f4, (960, 540))])])
cv2.imwrite('/data/video/frames/cards.jpg', sheet)
# crop at full res of the chapter card for detail
ch = f2[H // 2 - 260:H // 2 + 260, W // 2 - 700:W // 2 + 700]
cv2.imwrite('/data/video/frames/card_detail.jpg', cv2.resize(ch, (1400 * 3 // 4, 520 * 3 // 4)))
print('ok', title_layer().shape, chapter_layer(c[2], c[3], c[4]).shape)

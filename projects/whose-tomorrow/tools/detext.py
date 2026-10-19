# inpaint AI gibberish-text regions: detext.py IMG x0,y0,x1,y1 [...]  (pixel coords of IMG); orig -> rej/
import sys, shutil, cv2, numpy as np
p = sys.argv[1]; im = cv2.imread(p)
shutil.copy(p, 'rej/' + p.split('/')[-1].replace('.png', '_text.png'))
m = np.zeros(im.shape[:2], np.uint8)
for r in sys.argv[2:]:
    x0, y0, x1, y1 = map(int, r.split(',')); m[y0:y1, x0:x1] = 255
out = cv2.inpaint(im, m, 5, cv2.INPAINT_TELEA)
soft = cv2.GaussianBlur(out, (0, 0), 3)
mf = cv2.GaussianBlur(cv2.dilate(m, np.ones((7, 7), np.uint8)).astype(np.float32) / 255, (0, 0), 3)[..., None]
cv2.imwrite(p, (out * (1 - mf) + soft * mf).astype(np.uint8)); print('detext', p)

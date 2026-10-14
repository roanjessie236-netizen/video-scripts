import cv2, numpy as np, glob, os, sys
A = '/data/video/assets'
os.makedirs('/data/video/frames', exist_ok=True)

def grid(img, step=0.1):
    h, w = img.shape[:2]
    out = img.copy()
    for i in range(1, 10):
        x = int(w * i * step); y = int(h * i * step)
        cv2.line(out, (x, 0), (x, h), (0, 255, 255), 1)
        cv2.line(out, (0, y), (w, y), (0, 255, 255), 1)
        cv2.putText(out, str(i), (x + 2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        cv2.putText(out, str(i), (2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
    return out

def sheet(names, out, tw=688, th=384):
    tiles = []
    for n in names:
        im = cv2.imread(f'{A}/{n}.jpg')
        im = cv2.resize(im, (tw, th), interpolation=cv2.INTER_AREA)
        im = grid(im)
        cv2.putText(im, n, (8, th - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        tiles.append(im)
    while len(tiles) % 2:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + 2]) for i in range(0, len(tiles), 2)]
    cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 80])

sheet(['02_earth', '03_wasteland', '04_firevisions', '06_campfire'], '/data/video/frames/sheetA.jpg')
sheet(['07_cave', '13_seed', '14_farm', '15_mesopotamia'], '/data/video/frames/sheetB.jpg')
sheet(['36_station', '37_child', '27_rocket', '26_electric'], '/data/video/frames/sheetC.jpg')
im = cv2.imread(f'{A}/11_map.jpg')
h, w = im.shape[:2]
for x in range(0, w, 50):
    cv2.line(im, (x, 0), (x, h), (0, 200, 255) if x % 100 == 0 else (0, 120, 160), 1)
    if x % 100 == 0:
        cv2.putText(im, str(x), (x + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
for y in range(0, h, 50):
    cv2.line(im, (0, y), (w, y), (0, 200, 255) if y % 100 == 0 else (0, 120, 160), 1)
    if y % 100 == 0:
        cv2.putText(im, str(y), (2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
cv2.imwrite('/data/video/frames/map_grid.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 85])
print('ok')

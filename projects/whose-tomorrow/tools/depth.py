#!/usr/bin/env python3
"""Depth maps for 2.5D parallax: Depth-Anything-V2-Small (CPU) on every engine/assets/*.jpg -> engine/depth/NAME.png
(16-bit, 736x414, 1 = near, edge-aware smoothed). Resumable. usage: depth.py [--only a,b] [--force]"""
import argparse, glob, os, time
import numpy as np, cv2, torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
torch.set_num_threads(2)
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(HERE, 'engine', 'assets'); D = os.path.join(HERE, 'engine', 'depth'); os.makedirs(D, exist_ok=True)
ap = argparse.ArgumentParser(); ap.add_argument('--only', default=''); ap.add_argument('--force', action='store_true'); a = ap.parse_args()
M = 'depth-anything/Depth-Anything-V2-Small-hf'
proc = AutoImageProcessor.from_pretrained(M); model = AutoModelForDepthEstimation.from_pretrained(M).eval()
for p in sorted(glob.glob(os.path.join(A, '*.jpg'))):
    n = os.path.splitext(os.path.basename(p))[0]
    if a.only and n not in a.only.split(','): continue
    dst = os.path.join(D, n + '.png')
    if os.path.exists(dst) and not a.force: continue
    t0 = time.time(); im = Image.open(p).convert('RGB').resize((1036, 588), Image.LANCZOS)
    with torch.no_grad():
        out = model(**proc(images=im, return_tensors='pt')).predicted_depth[0].numpy()
    d = cv2.resize(out.astype(np.float32), (736, 414), interpolation=cv2.INTER_CUBIC)
    lo, hi = np.percentile(d, 2), np.percentile(d, 98.5); d = np.clip((d - lo) / max(1e-6, hi - lo), 0, 1)
    g = cv2.resize(cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2GRAY), (736, 414)).astype(np.float32) / 255
    d = cv2.ximgproc.guidedFilter(g, d, 6, 1e-3) if hasattr(cv2, 'ximgproc') else cv2.bilateralFilter(d, 9, 0.1, 6)
    d = cv2.GaussianBlur(np.clip(d, 0, 1), (0, 0), 1.5)
    cv2.imwrite(dst, (d * 65535).astype(np.uint16)); print(n, '%.1fs' % (time.time() - t0), flush=True)
print('DEPTH DONE')

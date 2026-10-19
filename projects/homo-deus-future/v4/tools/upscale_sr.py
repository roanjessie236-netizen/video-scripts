#!/usr/bin/env python3
"""AI super-resolution for new v4 images: Real-ESRGAN realesr-general-x4v3 (+wdn blend, 'denoise strength')
on CPU, tiled, then Lanczos down to plate size 2944x1656 (2K render 2560x1440 + Ken Burns headroom).
usage: upscale_sr.py IN_DIR OUT_DIR [--dn 0.5] [--tile 384] [--mix 0.0]
"""
import argparse, glob, os, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from PIL import Image

class SRVGGNetCompact(nn.Module):
    def __init__(s, num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4):
        super().__init__()
        s.upscale = upscale
        s.body = nn.ModuleList([nn.Conv2d(num_in_ch, num_feat, 3, 1, 1), nn.PReLU(num_parameters=num_feat)])
        for _ in range(num_conv):
            s.body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1)); s.body.append(nn.PReLU(num_parameters=num_feat))
        s.body.append(nn.Conv2d(num_feat, num_out_ch * upscale * upscale, 3, 1, 1))
        s.upsampler = nn.PixelShuffle(upscale)
    def forward(s, x):
        out = x
        for l in s.body: out = l(out)
        return s.upsampler(out) + F.interpolate(x, scale_factor=s.upscale, mode='nearest')

def load(dn, sr_dir):
    a = torch.load(os.path.join(sr_dir, 'realesr-general-x4v3.pth'), map_location='cpu')
    b = torch.load(os.path.join(sr_dir, 'realesr-general-wdn-x4v3.pth'), map_location='cpu')
    a = a.get('params_ema', a.get('params', a)); b = b.get('params_ema', b.get('params', b))
    sd = {k: dn * a[k] + (1 - dn) * b[k] for k in a}
    m = SRVGGNetCompact(); m.load_state_dict(sd, strict=True); m.eval(); return m

@torch.no_grad()
def sr(m, img, tile=384, pad=12):
    x = torch.from_numpy(img.astype(np.float32) / 255.).permute(2, 0, 1)[None]
    _, _, h, w = x.shape; out = torch.zeros(1, 3, h * 4, w * 4)
    for y0 in range(0, h, tile):
        for x0 in range(0, w, tile):
            y1, x1 = min(y0 + tile, h), min(x0 + tile, w)
            py0, px0, py1, px1 = max(y0 - pad, 0), max(x0 - pad, 0), min(y1 + pad, h), min(x1 + pad, w)
            o = m(x[:, :, py0:py1, px0:px1])
            out[:, :, y0*4:y1*4, x0*4:x1*4] = o[:, :, (y0-py0)*4:(y0-py0)*4 + (y1-y0)*4, (x0-px0)*4:(x0-px0)*4 + (x1-x0)*4]
    return (out[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255. + .5).astype(np.uint8)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--dn', type=float, default=0.5); ap.add_argument('--tile', type=int, default=384)
    ap.add_argument('--mix', type=float, default=0.0, help='blend fraction of plain Lanczos upscale (texture keep)')
    ap.add_argument('--size', default='2944x1656'); ap.add_argument('--sr-dir', default='/data/sr')
    ap.add_argument('--only', default=''); a = ap.parse_args()
    torch.set_num_threads(os.cpu_count() or 2)
    W, H = map(int, a.size.split('x')); os.makedirs(a.out, exist_ok=True); m = load(a.dn, a.sr_dir)
    for f in sorted(glob.glob(os.path.join(a.inp, '*.png')) + glob.glob(os.path.join(a.inp, '*.jpg'))):
        name = os.path.splitext(os.path.basename(f))[0]
        if a.only and name not in a.only.split(','): continue
        dst = os.path.join(a.out, name + '.jpg')
        if os.path.exists(dst): continue
        t = time.time(); src = Image.open(f).convert('RGB')
        big = Image.fromarray(sr(m, np.asarray(src), a.tile)).resize((W, H), Image.LANCZOS)
        if a.mix > 0:
            big = Image.blend(big, src.resize((W, H), Image.LANCZOS), a.mix)
        big.save(dst, quality=95, subsampling=0)
        print(f'{name}: {src.size} -> {big.size} {time.time()-t:.1f}s', flush=True)

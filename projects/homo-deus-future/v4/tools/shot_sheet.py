#!/usr/bin/env python3
"""Contact sheet: one frame per shot (shot midpoint) from a rendered video. Usage: shot_sheet.py VIDEO SHOTLIST OUT.jpg"""
import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
video, shot, out = sys.argv[1:4]
S = json.load(open(shot, encoding='utf-8'))['marks']['shots']
items = sorted(S.items(), key=lambda kv: kv[1])
dur = json.load(open(shot, encoding='utf-8'))['duration']
W, H, C = 400, 225, 8
rows = (len(items) + C - 1) // C
sheet = Image.new('RGB', (W * C, (H + 26) * rows), (16, 16, 16))
font = ImageFont.truetype('/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc', 16) if False else ImageFont.load_default()
try:
    font = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf', 16)
except Exception:
    pass
for k, (name, t0) in enumerate(items):
    t1 = items[k + 1][1] if k + 1 < len(items) else dur
    tm = t0 + min(1.2, (t1 - t0) / 2)
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', '%.3f' % tm, '-i', video, '-frames:v', '1',
                                   '-vf', 'scale=%d:%d' % (W, H), '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:'])
    im = Image.frombytes('RGB', (W, H), raw)
    x, y = (k % C) * W, (k // C) * (H + 26)
    sheet.paste(im, (x, y))
    ImageDraw.Draw(sheet).text((x + 6, y + H + 4), '%02d %s  %d:%04.1f' % (k + 1, name, t0 // 60, t0 % 60), fill=(220, 220, 220), font=font)
sheet.save(out, quality=85)
print('wrote', out, sheet.size)

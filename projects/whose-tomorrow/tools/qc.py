import sys, os
from PIL import Image
out, ns = sys.argv[1], sys.argv[2:]
W = Image.new('RGB', (1536, 432 * ((len(ns) + 1) // 2)))
for i, p in enumerate(ns): W.paste(Image.open(p).convert('RGB').resize((768, 432)), ((i % 2) * 768, (i // 2) * 432))
W.save(out, quality=85)

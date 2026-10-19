"""Generate tools/prompts.py images with FLUX.1-schnell (HF Space via gradio_client). Resumable.
usage: gen_flux.py OUT_DIR [--only a,b] [--seed 7] [--w 1536 --h 864]"""
import argparse, os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompts import P, STYLE
from gradio_client import Client
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--only', default='')
ap.add_argument('--seed', type=int, default=7); ap.add_argument('--w', type=int, default=1536); ap.add_argument('--h', type=int, default=864)
ap.add_argument('--suffix', default=''); ap.add_argument('--space', default='black-forest-labs/FLUX.1-schnell')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
c = Client(a.space, verbose=False)
for name, p in P.items():
    if a.only and name not in a.only.split(','): continue
    dst = os.path.join(a.out, name + a.suffix + '.png')
    if os.path.exists(dst): continue
    for k in range(4):
        try:
            t = time.time()
            r = c.predict(prompt=p + STYLE, seed=a.seed, randomize_seed=False, width=a.w, height=a.h,
                          num_inference_steps=4, api_name='/infer')
            Image.open(r[0]).convert('RGB').save(dst)
            print(name, 'ok %.1fs' % (time.time() - t), flush=True); break
        except Exception as e:
            print(name, 'ERR', repr(e)[:300], flush=True); time.sleep(10 + 10 * k)

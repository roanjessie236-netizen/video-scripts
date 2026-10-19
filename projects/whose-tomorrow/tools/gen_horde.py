"""Generate tools/prompts.py images on AI Horde (Z-Image-Turbo, 1344x768, 8 steps). Resumable, 3 parallel jobs.
usage: gen_horde.py OUT_DIR [--only a,b] [--seed 7] [--jobs 3] [--model Z-Image-Turbo] [--suffix _b]"""
import argparse, os, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompts import P, P2, P3, STYLE
from horde import gen
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--only', default='')
ap.add_argument('--seed', type=int, default=7); ap.add_argument('--jobs', type=int, default=3)
ap.add_argument('--model', default='Z-Image-Turbo'); ap.add_argument('--suffix', default=''); ap.add_argument('--steps', type=int, default=9); ap.add_argument('--w', type=int, default=1344); ap.add_argument('--h', type=int, default=768); ap.add_argument('--v2', action='store_true'); ap.add_argument('--v3', action='store_true')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
if a.v2: P = {**P, **P2}
if a.v3: P = P3
def one(name):
    dst = os.path.join(a.out, name + a.suffix + '.png')
    if os.path.exists(dst): return
    k = 0
    while k < 4:
        try:
            tmp = dst + '.tmp'
            dt, wk, kd = gen(tmp, P[name] + STYLE, a.model, a.w, a.h, a.seed + k * 101, a.steps)
            Image.open(tmp).convert('RGB').save(dst); os.remove(tmp)
            print(name, 'ok %.0fs %s' % (dt, wk), flush=True); return
        except Exception as e:
            print(name, 'ERR', repr(e)[:200], flush=True)
            if '429' in repr(e): time.sleep(20); continue
            time.sleep(15 + 15 * k); k += 1
names = [n for n in a.only.split(',') if n in P] if a.only else list(P)   # --only order = priority order
with ThreadPoolExecutor(a.jobs) as ex: list(ex.map(one, names))
print('ALL DONE', flush=True)

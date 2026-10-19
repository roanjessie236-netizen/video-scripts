#!/usr/bin/env python3
"""v4: lengthen the pauses inside a few takes so the picture can cut on each word of an enumeration
(饥荒…瘟疫…和战争 / 长生不死…幸福快乐…化身为神 / 改写基因…与机器融合…创造…). No re-synthesis: silence is inserted
at the quietest point between the end of the word and the next onset. Writes clips_v4/ (all takes) + durs/bounds.
Usage: python3 stretch.py clips clips_v4"""
import json, os, shutil, subprocess, sys
import numpy as np
SR = 48000
SPEC = {3: [("饥荒", 0.30), ("瘟疫", 0.45)],
        9: [("长生不死", 0.15), ("快乐", 0.15)]}
src, dst = sys.argv[1:3]
os.makedirs(dst, exist_ok=True)
D = json.load(open(src + '/durs.json')); B = json.load(open(src + '/bounds.json', encoding='utf-8'))


def rd(p):
    return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', str(SR), 'pipe:']), np.float32).copy()


def wr(p, x):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'pipe:', p],
                   input=x.astype(np.float32).tobytes(), check=True)


rep = {}
for k in D:
    i = int(k)
    shutil.copy(os.path.join(src, '%02d.wav' % i), os.path.join(dst, '%02d.wav' % i))
    if i not in SPEC:
        continue
    a = rd(os.path.join(src, '%02d.wav' % i))
    win = int(0.01 * SR)
    env = np.sqrt(np.convolve(a * a, np.ones(win) / win, mode='same'))
    W = [list(w) for w in B[k]]
    ins = []
    for word, extra in SPEC[i]:
        j = next(n for n, w in enumerate(W) if w[2] == word)
        e1, o2 = W[j][0] + W[j][1], W[j + 1][0]
        lo, hi = int(min(e1, o2 - 0.02) * SR), int(o2 * SR)
        cut = lo + int(np.argmin(env[lo:hi])) if hi > lo else int(o2 * SR)
        ins.append((cut, extra, j))
    out, prev = [], 0
    for cut, extra, j in sorted(ins):
        out += [a[prev:cut], np.zeros(int(extra * SR), np.float32)]
        prev = cut
    out.append(a[prev:])
    y = np.concatenate(out)
    for cut, extra, j in ins:
        for w in W[j + 1:]:
            w[0] = round(w[0] + extra, 3)
    wr(os.path.join(dst, '%02d.wav' % i), y)
    B[k] = W
    D[k] = dict(D[k], dur=round(len(y) / SR, 3), stretched=round(sum(e for _, e, _ in ins), 3))
    rep[i] = D[k]['dur']
json.dump(D, open(dst + '/durs.json', 'w'), indent=0)
json.dump(B, open(dst + '/bounds.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('stretched', rep)

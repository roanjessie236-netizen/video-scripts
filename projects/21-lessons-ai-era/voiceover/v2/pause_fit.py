"""Merged sentences (one TTS take) — lengthen the comma pause inside the take so the 2nd half lands
0.15 s after its burned subtitle (same idea as Sapiens v3.2 tighten_l37.py, in reverse). No re-synthesis, no splicing of takes.
Usage: python3 pause_fit.py lines.json subs.json clips clips_fit"""
import json, os, re, shutil, subprocess, sys
import numpy as np
SR = 48000; P = r'[，。？！、—“”：；\s]'
lines, subs, src, dst = sys.argv[1:5]; os.makedirs(dst, exist_ok=True)
L = json.load(open(lines, encoding='utf-8')); S = {int(k): v for k, v in json.load(open(subs, encoding='utf-8')).items()}
D = json.load(open(src + '/durs.json')); B = json.load(open(src + '/bounds.json', encoding='utf-8'))
def rd(p): return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',p,'-f','f32le','-ac','1','-ar',str(SR),'pipe:']), np.float32).copy()
def wr(p, x): subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:',p], input=x.astype(np.float32).tobytes(), check=True)
rep = {}
for x in L:
    i = str(x['i']); shutil.copy(os.path.join(src, '%02d.wav' % x['i']), os.path.join(dst, '%02d.wav' % x['i']))
    if len(x['subs']) < 2: continue
    n1 = len(re.sub(P, '', x['parts'][0])); c = 0; k2 = None
    W = [w for w in B[i] if re.sub(P, '', w[2])]
    for k, w in enumerate(W):
        if c >= n1: k2 = k; break
        c += len(re.sub(P, '', w[2]))
    e1 = W[k2-1][0] + W[k2-1][1]; o2 = W[k2][0]
    target = S[x['subs'][1]]['s'] + 0.15 - x['s']; delta = round(target - o2, 3)
    if abs(delta) < 0.15: rep[i] = dict(pause=round(o2-e1, 3), delta=0); continue
    a = rd(os.path.join(src, '%02d.wav' % x['i']))
    win = int(0.01*SR); env = np.sqrt(np.convolve(a*a, np.ones(win)/win, mode='same'))
    lo, hi = int(e1*SR), int(o2*SR); cut = lo + int(np.argmin(env[lo:hi]))
    lvl = 20*np.log10(env[cut] + 1e-9)
    if delta > 0:
        y = np.concatenate([a[:cut], np.zeros(int(delta*SR), np.float32), a[cut:]])
    else:  # shorten: remove the quietest |delta| around cut (only if the pause is long enough)
        r = int(-delta*SR); y = np.concatenate([a[:cut - r//2], a[cut + r - r//2:]])
    wr(os.path.join(dst, '%02d.wav' % x['i']), y)
    D[i]['dur'] = round(len(y)/SR, 3)
    B[i] = [[w[0] + (delta if w[0] >= cut/SR else 0), w[1], w[2]] for w in B[i]]
    rep[i] = dict(pause_in=round(o2-e1, 3), delta=delta, pause_out=round(o2-e1+delta, 3), cut_s=round(cut/SR, 3), cut_level_db=round(lvl, 1))
json.dump(D, open(dst + '/durs.json', 'w'), indent=0); json.dump(B, open(dst + '/bounds.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(rep, open(dst + '/pause_fit.json', 'w'), indent=1); print(json.dumps(rep, indent=0))
F = json.load(open(src + '/fit.json', encoding='utf-8'))  # fit.json for mix_tl.py with the new durations
for x in F['lines']: x['dur'] = D[str(x['i'])]['dur']; x['fits'] = x['dur'] <= x['slot']
json.dump(F, open(dst + '/fit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

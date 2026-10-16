"""Place per-line clips on the subtitle timeline -> one voice-only preview track.

Usage: python3 align_track.py SUBS.srt CLIP_DIR TOTAL_SECONDS OUT.mp3
Same placement rule as mix_voice.py: a clip longer than its slot may start up
to LEAD s early; later clips are pushed back so lines never overlap.
"""
import os, sys, subprocess
import numpy as np

SR = 48000
LEAD = 0.8
GAP = 0.35

def ts(s):
    h, m, r = s.strip().split(':'); a, b = r.split(',')
    return int(h) * 3600 + int(m) * 60 + int(a) + int(b) / 1000

def subs(p):
    out = []
    for b in open(p, encoding='utf-8-sig').read().strip().split('\n\n'):
        l = b.strip().split('\n')
        if len(l) >= 3: out.append((int(l[0]), ts(l[1].split(' --> ')[0])))
    return out

def dec(p):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', 'pipe:'])
    return np.frombuffer(raw, np.float32)

def main(srt, clips, total, out):
    total = float(total); S = subs(srt)
    tr = np.zeros(int((total + 5) * SR), np.float32); prev = 0.0
    for k, (i, s) in enumerate(S):
        p = os.path.join(clips, '%02d.wav' % i)
        if not os.path.exists(p): print('#%02d missing' % i); continue
        x = dec(p); d = len(x) / SR
        nxt = S[k + 1][1] if k + 1 < len(S) else total
        t = s if d <= nxt - s - GAP else max(s - LEAD, 0)
        if prev: t = max(t, prev + GAP)
        a = int(t * SR); n = min(len(x), len(tr) - a); tr[a:a + n] += x[:n]; prev = t + d
        print('#%02d sub %6.2fs voice %6.2f-%6.2fs dur %4.1fs drift %+5.2fs%s' % (
            i, s, t, t + d, d, t - s, '  <-- check' if abs(t - s) > 1.2 else ''))
    tr = tr[:int(total * SR)]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'pipe:',
                    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9', '-b:a', '160k', out], input=tr.tobytes(), check=True)
    print('done ->', out)

if __name__ == '__main__':
    main(*sys.argv[1:5])

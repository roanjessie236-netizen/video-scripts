"""今日简史 v2.1 — replace only #5「思考」in the delivered v2 film, everything else stays sample-identical to v2.
Takes the v2 film's audio, swaps in [T0, T1] from a fresh mix (mix_tl.py run with the new clips_fit/05.wav;
same score / ducking / master gain), 50 ms equal-gain crossfades in score-only gaps; video stream copied.
Usage: python3 replace_l5.py V2.mp4 NEW_MIX_final.wav OUT.mp4 [--t0 15.4 --t1 18.5]"""
import argparse, subprocess
import numpy as np
SR = 48000
def rd(p): return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',p,'-ac','2','-ar',str(SR),'-f','f32le','pipe:']), np.float32).reshape(-1, 2)
ap = argparse.ArgumentParser(); ap.add_argument('v2'); ap.add_argument('new'); ap.add_argument('out')
ap.add_argument('--t0', type=float, default=15.4); ap.add_argument('--t1', type=float, default=18.5); ap.add_argument('--xf', type=float, default=0.05)
a = ap.parse_args()
old = rd(a.v2); new = rd(a.new); n = len(old)  # keep the full v2 length; only [t0-xf, t1+xf] comes from the new mix
new = np.concatenate([new[:n], np.zeros((max(0, n - len(new)), 2), np.float32)])
m = np.zeros(n, np.float32); i0, i1, x = int(a.t0*SR), int(a.t1*SR), int(a.xf*SR)
m[i0:i1] = 1; m[i0-x:i0] = np.linspace(0, 1, x); m[i1:i1+x] = np.linspace(1, 0, x)
for t, k in [(a.t0, i0), (a.t1, i1)]:
    r = old[k-x:k+x] - new[k-x:k+x]
    print('junction %.2f s: old/new residual %.1f dB (signal %.1f dB)' % (t, 10*np.log10(np.mean(r**2)+1e-15), 10*np.log10(np.mean(old[k-x:k+x]**2)+1e-15)))
y = old*(1-m[:, None]) + new*m[:, None]
subprocess.run(['ffmpeg','-v','error','-y','-i',a.v2,'-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:','-map','0:v','-map','1:a',
                '-c:v','copy','-c:a','aac','-b:a','256k','-ar',str(SR),'-movflags','+faststart',a.out], input=y.astype(np.float32).tobytes(), check=True)
print('done ->', a.out)

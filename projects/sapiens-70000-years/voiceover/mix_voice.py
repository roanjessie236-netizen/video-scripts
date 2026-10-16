"""Mix a narration voice-over into a finished film.

Usage:
  python3 mix_voice.py VIDEO.mp4 SUBS.srt IN_DIR OUT.mp4

IN_DIR contains EITHER
  * per-line clips named by subtitle number: 01.wav, 02.mp3, 3.m4a ... (preferred), OR
  * one full-length track named full.* that is already aligned to the video.

Per-line mode: each clip is trimmed of leading/trailing silence and placed at its
subtitle start. If a clip is longer than its slot it may start up to LEAD seconds
early, and later clips are pushed back so lines never overlap. A drift report and
a re-timed SRT (for platform CC subtitles) are written next to OUT.
The film's existing score is ducked under the voice with a sidechain compressor.
"""
import os, re, sys, glob, subprocess, wave
import numpy as np

SR = 48000
LEAD = 0.8   # max seconds a long clip may start before its subtitle
GAP = 0.35   # min silence between consecutive lines
EXT = ('wav', 'mp3', 'm4a', 'aac', 'flac', 'ogg', 'opus')

def ts(s):
    h, m, rest = s.strip().split(':'); sec, ms = rest.split(',')
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000

def fts(t):
    t = max(0, t); ms = int(round(t * 1000))
    return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)

def read_srt(p):
    out = []
    for b in open(p, encoding='utf-8-sig').read().strip().split('\n\n'):
        ls = b.strip().split('\n')
        if len(ls) < 3: continue
        a, z = ls[1].split(' --> ')
        out.append(dict(i=int(ls[0]), s=ts(a), e=ts(z), text='\n'.join(ls[2:])))
    return out

def duration(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode().strip())

def decode(p):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', 'pipe:'])
    return np.frombuffer(raw, np.float32).copy()

def trim(x, thr_db=-45, pad=0.05):
    if len(x) == 0: return x
    win = int(0.02 * SR)
    env = np.sqrt(np.convolve(x * x, np.ones(win) / win, mode='same'))
    idx = np.where(env > 10 ** (thr_db / 20))[0]
    if len(idx) == 0: return x[:0]
    a = max(0, idx[0] - int(pad * SR)); z = min(len(x), idx[-1] + int(pad * SR))
    return x[a:z]

def write_wav(p, x):
    x = np.clip(x, -1, 1)
    with wave.open(p, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

def main(video, srt, ind, out):
    total = duration(video)
    subs = read_srt(srt)
    work = os.path.splitext(out)[0] + '_work'; os.makedirs(work, exist_ok=True)
    files = [f for f in glob.glob(os.path.join(ind, '*')) if f.lower().rsplit('.', 1)[-1] in EXT]
    full = [f for f in files if os.path.basename(f).lower().startswith('full.')]
    track = np.zeros(int(total * SR) + SR, np.float32)
    report, new_srt = [], []
    if full:
        x = decode(full[0]); n = min(len(x), len(track)); track[:n] = x[:n]
        report.append('full track mode: %s (%.1fs)' % (os.path.basename(full[0]), len(x) / SR))
        new_srt = subs
    else:
        clips = {}
        for f in files:
            m = re.match(r'^(\d{1,3})(?:\D.*)?\.\w+$', os.path.basename(f))
            if m: clips[int(m.group(1))] = f
        missing = [s['i'] for s in subs if s['i'] not in clips]
        if missing: report.append('MISSING clips for lines: %s' % missing)
        prev_end = 0.0
        for k, s in enumerate(subs):
            nxt = subs[k + 1]['s'] if k + 1 < len(subs) else total
            if s['i'] not in clips:
                new_srt.append(s); continue
            x = trim(decode(clips[s['i']])); d = len(x) / SR
            slot = nxt - s['s'] - GAP
            t = s['s'] if d <= slot else max(s['s'] - LEAD, 0)
            t = max(t, prev_end + GAP if prev_end else 0)
            a = int(t * SR); z = min(len(track), a + len(x))
            track[a:z] += x[:z - a]
            prev_end = t + d
            report.append('#%02d sub %6.2fs  voice %6.2f-%6.2fs  dur %4.1fs  drift %+5.2fs%s' % (
                s['i'], s['s'], t, t + d, d, t - s['s'], '  <-- check' if abs(t - s['s']) > 1.2 else ''))
            new_srt.append(dict(i=s['i'], s=t, e=min(t + d + 0.3, nxt + max(0, prev_end - nxt) + 0.3), text=s['text']))
        if prev_end > total: report.append('WARNING: voice runs past the end of the video (%.1fs > %.1fs)' % (prev_end, total))
    raw = os.path.join(work, 'voice_raw.wav'); write_wav(raw, track[:int(total * SR)])
    voice = os.path.join(work, 'voice.wav')
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af',
        'highpass=f=70,lowpass=f=14000,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,'
        'aecho=0.8:0.5:40|80:0.10|0.05,loudnorm=I=-16:TP=-1.5:LRA=9', '-ar', str(SR), voice])
    fc = ('[1:a]aformat=channel_layouts=stereo,asplit=2[v][sc];'
          '[0:a]volume=0.75[m];'
          '[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=25:release=500[md];'
          '[md][v]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]')
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', voice, '-filter_complex', fc,
        '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out])
    with open(os.path.splitext(out)[0] + '.srt', 'w', encoding='utf-8') as f:
        for n, s in enumerate(new_srt, 1):
            f.write('%d\n%s --> %s\n%s\n\n' % (n, fts(s['s']), fts(s['e']), s['text']))
    open(os.path.splitext(out)[0] + '_report.txt', 'w', encoding='utf-8').write('\n'.join(report) + '\n')
    print('\n'.join(report)); print('done ->', out)

if __name__ == '__main__':
    main(*sys.argv[1:5])

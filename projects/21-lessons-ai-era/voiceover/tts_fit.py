"""Synthesize per-line narration with edge-tts and auto-fit each line to its subtitle slot.

Usage: python3 tts_fit.py lines.json SUBS.srt OUT_DIR [--voice V] [--rate-offset N] [--total T] [--jobs 4]
lines.json: [{i, t, rate, pitch, vol, cue}]; '‖' in t = dramatic pause (split + silence).
slot = next subtitle start - start - GAP (last line: total - start - TAIL).
Too long -> shrink pauses to PAUSE_MIN, then re-synthesize faster (rate <= MAX_RATE).
Writes OUT_DIR/NN.wav (48 kHz mono, trimmed) and OUT_DIR/fit.json (final params per line).
"""
import argparse, asyncio, hashlib, json, math, os, subprocess
import numpy as np
import edge_tts

SR = 48000
PAUSE = 0.45
PAUSE_MIN = 0.25
GAP = 0.35
TAIL = 1.0
MAX_RATE = 12


def ts(s):
    h, m, r = s.strip().split(':'); a, b = r.split(',')
    return int(h) * 3600 + int(m) * 60 + int(a) + int(b) / 1000


def read_srt(p):
    out = []
    for b in open(p, encoding='utf-8-sig').read().strip().split('\n\n'):
        l = b.strip().split('\n')
        if len(l) >= 3: out.append((int(l[0]), ts(l[1].split(' --> ')[0])))
    return out


def decode(p):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', 'pipe:'])
    return np.frombuffer(raw, np.float32).copy()


def trim(x, thr_db=-45, pad=0.04):
    win = int(0.02 * SR)
    env = np.sqrt(np.convolve(x * x, np.ones(win) / win, mode='same'))
    idx = np.where(env > 10 ** (thr_db / 20))[0]
    if len(idx) == 0: return x[:0]
    return x[max(0, idx[0] - int(pad * SR)):min(len(x), idx[-1] + int(pad * SR))]


async def synth(text, voice, rate, pitch, vol, path, tries=5):
    if os.path.exists(path) and os.path.getsize(path) > 1000: return
    for k in range(tries):
        try:
            await edge_tts.Communicate(text, voice, rate='%+d%%' % rate, pitch=pitch, volume=vol).save(path)
            if os.path.getsize(path) > 1000: return
        except Exception as e:
            print('  retry', k + 1, e, flush=True)
        await asyncio.sleep(2 + 2 * k)
    raise RuntimeError('tts failed: ' + text)


async def render(L, voice, rate, pause, tmp):
    parts = [p for p in L['t'].split('‖') if p.strip()]
    segs = []
    for j, p in enumerate(parts):
        pitch, vol = L.get('pitch', '+0Hz'), L.get('vol', '+0%')
        key = hashlib.md5(('%s|%s|%d|%s|%s' % (p, voice, rate, pitch, vol)).encode()).hexdigest()[:10]
        mp = os.path.join(tmp, '%02d_%d_%s.mp3' % (L['i'], j, key))  # cache keyed on text + all voice params
        await synth(p, voice, rate, pitch, vol, mp)
        segs.append(trim(decode(mp)))
        if j < len(parts) - 1: segs.append(np.zeros(int(pause * SR), np.float32))
    return np.concatenate(segs), len(parts) - 1


async def fit_line(L, slot, a, tmp, sem):
    async with sem:
        r0 = int(str(L.get('rate', '-8%')).rstrip('%')) + a.rate_offset
        rate, pause, hist = r0, PAUSE, []
        x, npause = await render(L, a.voice, rate, pause, tmp)
        for k in range(5):
            d = len(x) / SR; hist.append([rate, pause, round(d, 2)])
            if d <= slot or k == 4: break
            if npause and pause > PAUSE_MIN:
                pause = PAUSE_MIN
            elif rate < MAX_RATE:
                speech = d - npause * pause
                need = math.ceil((100 + rate) * speech / max(slot - npause * pause, 0.5) * 1.03 - 100)
                rate = min(MAX_RATE, max(rate + 2, need))
            else:
                break
            x, npause = await render(L, a.voice, rate, pause, tmp)
        d = len(x) / SR
        wp = os.path.join(a.out, '%02d.wav' % L['i'])
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'pipe:', wp],
                       input=x.tobytes(), check=True)
        adj = rate != r0 or pause != PAUSE
        print('#%02d %4.2fs / slot %5.2fs  rate %+d%%%s  %s' % (L['i'], d, slot, rate, '  (auto-fit)' if adj else '', L['t']), flush=True)
        return dict(i=L['i'], t=L['t'], cue=L.get('cue', ''), pitch=L.get('pitch', '+0Hz'), vol=L.get('vol', '+0%'),
                    rate_in=r0, rate=rate, pause=pause, slot=round(slot, 2), dur=round(d, 2), fits=d <= slot,
                    adjusted=adj, tries=hist)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lines'); ap.add_argument('srt'); ap.add_argument('out')
    ap.add_argument('--voice', default='zh-CN-YunjianNeural')
    ap.add_argument('--rate-offset', type=int, default=0, help='added to every line rate, in percent')
    ap.add_argument('--total', type=float, default=224.0)
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); tmp = os.path.join(a.out, '_tmp'); os.makedirs(tmp, exist_ok=True)
    S = read_srt(a.srt)
    slots = {}
    for k, (i, s) in enumerate(S):
        slots[i] = (S[k + 1][1] - GAP if k + 1 < len(S) else a.total - TAIL) - s
    lines = json.load(open(a.lines, encoding='utf-8'))
    sem = asyncio.Semaphore(a.jobs)
    res = await asyncio.gather(*[fit_line(L, slots[L['i']], a, tmp, sem) for L in lines])
    res.sort(key=lambda r: r['i'])
    json.dump(dict(voice=a.voice, rate_offset=a.rate_offset, pause=PAUSE, pause_min=PAUSE_MIN, gap=GAP,
                   max_rate=MAX_RATE, lines=res), open(os.path.join(a.out, 'fit.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('fit: %d/%d lines inside slot, %d auto-adjusted' % (sum(r['fits'] for r in res), len(res), sum(r['adjusted'] for r in res)))


if __name__ == '__main__':
    asyncio.run(main())
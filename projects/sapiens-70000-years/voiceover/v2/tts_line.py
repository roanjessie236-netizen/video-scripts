"""Synthesize each narration line as ONE edge-tts call (continuous prosody, no splicing).
Usage: python3 tts_line.py lines.json OUT_DIR [--voice V] [--rate-offset N] [--total 287]
lines.json: [{i, s (voice start), t (spoken text), sub (subtitle text if different), en, rate, pitch, vol, cue}].
Writes OUT_DIR/NN.wav (48k mono, trimmed), OUT_DIR/durs.json {i: seconds} and OUT_DIR/fit.json. Cache keyed on text+params."""
import argparse, asyncio, hashlib, json, os, subprocess
import numpy as np, edge_tts
SR = 48000
def decode(p):
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(SR),'-f','f32le','pipe:'])
    return np.frombuffer(raw, np.float32).copy()
def trim(x, thr_db=-45, pad=0.03):
    win = int(0.02*SR); env = np.sqrt(np.convolve(x*x, np.ones(win)/win, mode='same'))
    idx = np.where(env > 10**(thr_db/20))[0]
    return x[max(0, idx[0]-int(pad*SR)):min(len(x), idx[-1]+int(pad*SR))]
async def one(L, a, sem):
    async with sem:
        rate = L['rate'] + a.rate_offset + L.get('radj', 0)
        key = hashlib.md5(('%s|%s|%d|%s|%s' % (L['t'], a.voice, rate, L['pitch'], L['vol'])).encode()).hexdigest()[:10]
        mp = os.path.join(a.out, '_tmp', '%02d_%s.mp3' % (L['i'], key))
        for k in range(6):
            if os.path.exists(mp) and os.path.getsize(mp) > 1000: break
            try:
                await edge_tts.Communicate(L['t'], a.voice, rate='%+d%%' % rate, pitch=L['pitch'], volume=L['vol']).save(mp)
            except Exception as e:
                print('retry', L['i'], e, flush=True); await asyncio.sleep(2 + 2*k)
        x = trim(decode(mp))
        subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:', os.path.join(a.out, '%02d.wav' % L['i'])], input=x.tobytes(), check=True)
        return L['i'], round(len(x)/SR, 3), rate
async def main():
    ap = argparse.ArgumentParser(); ap.add_argument('lines'); ap.add_argument('out')
    ap.add_argument('--voice', default='zh-CN-YunjianNeural'); ap.add_argument('--rate-offset', type=int, default=0)
    ap.add_argument('--jobs', type=int, default=5); ap.add_argument('--total', type=float, default=287.0); a = ap.parse_args()
    os.makedirs(os.path.join(a.out, '_tmp'), exist_ok=True)
    lines = json.load(open(a.lines, encoding='utf-8')); sem = asyncio.Semaphore(a.jobs)
    res = await asyncio.gather(*[one(L, a, sem) for L in lines])
    json.dump({str(i): dict(dur=d, rate=r) for i, d, r in res}, open(os.path.join(a.out, 'durs.json'), 'w'), indent=0)
    R = {i: (d, r) for i, d, r in res}  # fit.json in the format mix_tl.py reports from
    fit = dict(voice=a.voice, rate_offset=a.rate_offset, lines=[dict(
        i=L['i'], t=L['t'], cue=L.get('cue', ''), pitch=L['pitch'], vol=L['vol'], rate_in=L['rate'], rate=R[L['i']][1], pause=0,
        slot=round((lines[k + 1]['s'] if k + 1 < len(lines) else a.total) - L['s'] - 0.35, 2), dur=R[L['i']][0],
        fits=R[L['i']][0] <= (lines[k + 1]['s'] if k + 1 < len(lines) else a.total) - L['s'] - 0.35, adjusted=False)
        for k, L in enumerate(lines)])
    json.dump(fit, open(os.path.join(a.out, 'fit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    bad = [x['i'] for x in fit['lines'] if not x['fits']]
    print('lines that overrun their slot:', bad or 'none')
    print('done', len(res))
asyncio.run(main())

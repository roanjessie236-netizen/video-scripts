"""未来简史 v4 TTS — same engine/rules as Sapiens v2 tts_line.py (one edge-tts call per sentence, no splicing),
plus WordBoundary capture so merged sentences can be checked against the burned subtitle of their 2nd half.
A line may carry "ctx" (text spoken before it in the same take): the take is synthesized as ctx+t and cut at the
quietest point of the pause before t — used for #5「思考。」, which as a 2-character standalone input came out
creaky / mispronounced (Whisper heard it as「复刻」); after「更深层的东西——」it is read as the natural answer to the dash.
Usage: python3 tts_line.py lines.json OUT_DIR [--voice zh-CN-YunjianNeural] [--total 224]
Writes OUT/NN.wav (48k mono, trimmed), OUT/durs.json, OUT/bounds.json (word onsets in trimmed clip), OUT/fit.json."""
import argparse, asyncio, hashlib, json, os, re, subprocess
import numpy as np, edge_tts
SR = 48000
PUNCT = r'[，。？！、—“”：；…\s]'
def decode(p):
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(SR),'-f','f32le','pipe:'])
    return np.frombuffer(raw, np.float32).copy()
def trim(x, thr_db=-45, pad=0.03):
    win = int(0.02*SR); env = np.sqrt(np.convolve(x*x, np.ones(win)/win, mode='same'))
    idx = np.where(env > 10**(thr_db/20))[0]
    a = max(0, idx[0]-int(pad*SR)); return x[a:min(len(x), idx[-1]+int(pad*SR))], a/SR
async def one(L, a, sem):
    async with sem:
        rate = L['rate'] + a.rate_offset + L.get('radj', 0)
        text = L.get('ctx', '') + L['t']
        key = hashlib.md5(('%s|%s|%d|%s|%s' % (text, a.voice, rate, L['pitch'], L['vol'])).encode()).hexdigest()[:10]
        mp = os.path.join(a.out, '_tmp', '%02d_%s.mp3' % (L['i'], key)); bj = mp[:-4] + '.json'
        for k in range(6):
            if os.path.exists(mp) and os.path.getsize(mp) > 1000 and os.path.exists(bj): break
            try:
                c = edge_tts.Communicate(text, a.voice, rate='%+d%%' % rate, pitch=L['pitch'], volume=L['vol'], boundary='WordBoundary')
                audio = bytearray(); B = []
                async for ch in c.stream():
                    if ch['type'] == 'audio': audio += ch['data']
                    elif ch['type'] == 'WordBoundary': B.append([ch['offset']/1e7, ch['duration']/1e7, ch['text']])
                open(mp, 'wb').write(audio); json.dump(B, open(bj, 'w'), ensure_ascii=False)
            except Exception as e:
                print('retry', L['i'], e, flush=True); await asyncio.sleep(2 + 2*k)
        x = decode(mp); B0 = json.load(open(bj)); c0 = 0.0
        if L.get('ctx'):  # cut off the context: quietest 10 ms point between the last ctx word and the first word of t
            n = len(re.sub(PUNCT, '', L['ctx'])); k = 0
            while n > 0: n -= len(re.sub(PUNCT, '', B0[k][2])); k += 1
            e1, o = B0[k-1][0] + B0[k-1][1], B0[k][0]; w10 = int(0.01*SR)
            env = np.sqrt(np.convolve(x*x, np.ones(w10)/w10, mode='same')); lo = int(e1*SR)
            c = lo + int(np.argmin(env[lo:int(o*SR)])); x = x[c:]; c0 = c/SR; B0 = B0[k:]
        x, off = trim(x); B = [[round(o-c0-off, 3), round(d, 3), w] for o, d, w in B0]
        subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:', os.path.join(a.out, '%02d.wav' % L['i'])], input=x.tobytes(), check=True)
        return L['i'], round(len(x)/SR, 3), rate, B
async def main():
    ap = argparse.ArgumentParser(); ap.add_argument('lines'); ap.add_argument('out')
    ap.add_argument('--voice', default='zh-CN-YunjianNeural'); ap.add_argument('--rate-offset', type=int, default=0)
    ap.add_argument('--jobs', type=int, default=5); ap.add_argument('--total', type=float, default=224.0); a = ap.parse_args()
    os.makedirs(os.path.join(a.out, '_tmp'), exist_ok=True)
    lines = json.load(open(a.lines, encoding='utf-8')); sem = asyncio.Semaphore(a.jobs)
    res = await asyncio.gather(*[one(L, a, sem) for L in lines])
    json.dump({str(i): dict(dur=d, rate=r) for i, d, r, _ in res}, open(os.path.join(a.out, 'durs.json'), 'w'), indent=0)
    json.dump({str(i): B for i, _, _, B in res}, open(os.path.join(a.out, 'bounds.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    R = {i: (d, r) for i, d, r, _ in res}
    fit = dict(voice=a.voice, rate_offset=a.rate_offset, lines=[dict(
        i=L['i'], t=L['t'], cue=L.get('cue', ''), pitch=L['pitch'], vol=L['vol'], rate_in=L['rate'], rate=R[L['i']][1], pause=0,
        slot=round((lines[k + 1]['s'] if k + 1 < len(lines) else a.total) - L['s'] - 0.35, 2), dur=R[L['i']][0],
        fits=R[L['i']][0] <= (lines[k + 1]['s'] if k + 1 < len(lines) else a.total) - L['s'] - 0.35, adjusted=False)
        for k, L in enumerate(lines)])
    json.dump(fit, open(os.path.join(a.out, 'fit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('lines that overrun their slot:', [x['i'] for x in fit['lines'] if not x['fits']] or 'none')
    print('done', len(res))
asyncio.run(main())

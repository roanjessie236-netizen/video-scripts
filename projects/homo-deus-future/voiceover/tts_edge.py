"""Synthesize per-line narration clips with edge-tts (needs internet).

Usage: python3 tts_edge.py lines.json OUT_DIR [VOICE]
lines.json items: {i, t, rate, pitch, vol}. '‖' in t = dramatic pause (split + silence).
Each line -> OUT_DIR/NN.wav (48 kHz mono), ready for mix_voice.py.
"""
import asyncio, json, os, sys, subprocess
import numpy as np
import edge_tts

SR = 48000
PAUSE = 0.45

def decode(p):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', 'pipe:'])
    return np.frombuffer(raw, np.float32).copy()

def trim(x, thr_db=-45, pad=0.04):
    win = int(0.02 * SR)
    env = np.sqrt(np.convolve(x * x, np.ones(win) / win, mode='same'))
    idx = np.where(env > 10 ** (thr_db / 20))[0]
    if len(idx) == 0: return x[:0]
    return x[max(0, idx[0] - int(pad * SR)):min(len(x), idx[-1] + int(pad * SR))]

async def synth(text, voice, rate, pitch, vol, path, tries=4):
    for k in range(tries):
        try:
            await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=vol).save(path)
            if os.path.getsize(path) > 1000: return
        except Exception as e:
            print('  retry', k + 1, e)
        await asyncio.sleep(2 + 2 * k)
    raise RuntimeError('tts failed: ' + text)

async def main(lines_p, out, voice):
    os.makedirs(out, exist_ok=True); tmp = os.path.join(out, '_tmp'); os.makedirs(tmp, exist_ok=True)
    for L in json.load(open(lines_p, encoding='utf-8')):
        parts = [p for p in L['t'].split('‖') if p.strip()]
        segs = []
        for j, p in enumerate(parts):
            mp = os.path.join(tmp, '%02d_%d.mp3' % (L['i'], j))
            await synth(p, voice, L.get('rate', '-8%'), L.get('pitch', '+0Hz'), L.get('vol', '+0%'), mp)
            segs.append(trim(decode(mp)))
            if j < len(parts) - 1: segs.append(np.zeros(int(PAUSE * SR), np.float32))
        x = np.concatenate(segs)
        wp = os.path.join(out, '%02d.wav' % L['i'])
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'pipe:', wp], input=x.tobytes(), check=True)
        print('#%02d %.2fs %s' % (L['i'], len(x) / SR, L['t']))

if __name__ == '__main__':
    a = sys.argv
    asyncio.run(main(a[1], a[2], a[3] if len(a) > 3 else 'zh-CN-YunjianNeural'))

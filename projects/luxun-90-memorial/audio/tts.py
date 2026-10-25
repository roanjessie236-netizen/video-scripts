# 配音合成：按字幕时间逐句生成（edge-tts），自动调语速贴合字幕显示时长；旁白/原文两种声音；返回放好位置的人声轨
import asyncio, json, re, subprocess, sys, os, numpy as np
sys.path.insert(0, '/tmp/pylib'); import edge_tts
SR = 48000; CACHE = '/tmp/vo/cache/'; os.makedirs(CACHE, exist_ok=True)
VR, QR = 4.2, 3.3
def nchar(t): return len(re.sub(r'[，。；：！？、—“”（）\s]', '', t))
PRON = {'许寿裳': '许寿常', '阒寂': '去寂', '竦听': '耸听'}                 # 只改配音稿，字幕不变（多音字/生僻字）
EMO = {'九十年过去了，我们没有听他的话': (-6, -2), '这一次，就当是写给先生的一封回信': (-8, -2), '他停止了呼吸': (-3, -1),
       '可是先生': (-5, -1), '先生，九十年过去了': (-10, -3), '您让我们忘记您': (-8, -2), '我们会好好生活': (-8, -2),
       '只是在黑夜里': (-6, -2), '有一分热': (-4, -1), '不要做任何关于纪念的事情': (-3, -1)}
def speak_text(t):
    for a, b in PRON.items(): t = t.replace(a, b)
    return t.replace('——', '，')
async def _gen(text, voice, rate, pitch, path):
    await edge_tts.Communicate(text, voice, rate=f'{rate:+d}%', pitch=f'{pitch:+d}Hz').save(path)
def gen(text, voice, rate, pitch):
    key = re.sub(r'\W', '', voice)[-10:] + f'_{rate:+d}_{pitch:+d}_' + str(abs(hash(text)) % 10**10)
    mp3 = CACHE + key + '.mp3'
    if not os.path.exists(mp3):
        for k in range(4):
            try: asyncio.run(_gen(text, voice, rate, pitch, mp3)); break
            except Exception as e:
                if k == 3: raise
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
    # 去掉首尾静音
    e = np.convolve(np.abs(x), np.ones(480) / 480, 'same'); idx = np.where(e > 10 ** (-42 / 20))[0]
    return x[max(0, idx[0] - 240): idx[-1] + 2400] if len(idx) else x
def fx(x, kind):
    flt = 'highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2' if kind == 'vo' else \
          'highpass=f=110,lowpass=f=9500,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,aecho=0.85:0.7:28|52:0.14|0.08'
    y = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', flt, '-f', 'f32le', '-'],
                                     input=x.astype(np.float32).tobytes(), capture_output=True).stdout, np.float32)
    act = y[np.abs(y) > 0.01]; rms = np.sqrt((act ** 2).mean()) if len(act) else 1
    return y * (10 ** (-17 / 20) / rms)          # 每句人声统一到约 -17 dBFS（有声部分）
def fit_line(text, kind, window, room, voice):
    """window：字幕显示时长；room：到下一句开始前可多用的时间"""
    base_r, base_p = (0, 0) if kind == 'vo' else (-16, -3)
    er, ep = next((v for k, v in EMO.items() if k in text), (0, 0))
    r, p = base_r + er, base_p + ep; st = speak_text(text); log = []
    for it in range(4):
        x = gen(st, voice, r, p); d = len(x) / SR; log.append((r, round(d, 2)))
        hi = window + min(0.35, max(0.0, room - 0.15)); lo = window * (0.9 if kind == 'vo' else 0.8)
        if d > hi: r = min(r + int(np.ceil((d / (window * 0.98) - 1) * 100)) + 1, 35)
        elif d < lo: r = max(r - int(np.ceil((1 - d / (window * 0.97)) * 100)), -15 if kind == 'vo' else -28)
        else: break
        if (r, p) == (log[-1][0], p) : break
    return x, log
def build(lines, total, narr, quo):
    """lines: [dict(t, kind, txt)]，t 为时间线上的秒；返回 (人声轨, 每句记录)"""
    out = np.zeros(int(total * SR) + SR, np.float32); rec = []
    for i, L in enumerate(lines):
        kind = 'vo' if L['kind'] == 'vo' else 'q'
        window = nchar(L['txt']) / (VR if kind == 'vo' else QR)
        nxt = lines[i + 1]['t'] if i + 1 < len(lines) else total
        room = nxt - (L['t'] + window)
        x, log = fit_line(L['txt'], kind, window, room, narr if kind == 'vo' else quo)
        y = fx(x, kind); a = int(L['t'] * SR); out[a:a + len(y)] += y[:len(out) - a]
        rec.append(dict(t=L['t'], kind=L['kind'], win=round(window, 2), dur=round(len(x) / SR, 2), end=round(L['t'] + len(x) / SR, 2), next=round(nxt, 2), log=log, txt=L['txt']))
    return out, rec

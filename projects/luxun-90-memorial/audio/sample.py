# 试听：序（0—68 秒）＋尾声 S7-05—S7-07；两版旁白音色
import json, sys, subprocess, numpy as np
sys.path.insert(0, '/tmp/vo'); import tts
SR = tts.SR; d = json.load(open('/tmp/vo/tl_sample.json'))
A0, B0, BOFF = 68.6, 88.75, 68.6        # 尾声段在试听里的起点
lines = [dict(e) for e in d['S0']] + [dict(e, t=round(BOFF + e['t'] - B0, 3)) for e in d['S7'] if e['t'] >= B0]
TOTAL = 68.6 + (143.96 - 88.75) + 1.5
def music():
    x1 = np.fromfile('/tmp/vo/mus/jx2.raw', np.int16)   # 8 kHz 仅分析用；配乐取 48k 立体声
    def seg(k, start, dur):
        return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', f'/tmp/vo/mus/jx{k}.m4s', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                            capture_output=True).stdout, np.float32).reshape(-1, 2)
    m = np.zeros((int(TOTAL * SR) + SR, 2), np.float32)
    def put(y, t0, fin, fout, gain_db):
        y = y.copy(); n = len(y); r = np.ones(n, np.float32)
        a = int(fin * SR); b = int(fout * SR); r[:a] = np.linspace(0, 1, a); r[n - b:] = np.minimum(r[n - b:], np.linspace(1, 0, b))
        rms = np.sqrt((y ** 2).mean()); y = y * r[:, None] * (10 ** (gain_db / 20) / rms); s = int(t0 * SR); m[s:s + n] += y[:len(m) - s]
    put(seg(2, 334.1, 68.6), 0.0, 2.5, 1.6, -21)                      # 序：《觉醒年代》原声中较静的一段（钢琴/弦乐）
    put(seg(2, 1223.7 + 136.5, TOTAL - A0), A0, 1.2, 2.5, -21)        # 尾声：《觉醒年代》原声《期盼》，“先生，九十年过去了”起渐强，片尾前到高潮
    return m
def duck(voice, n):
    e = np.abs(voice[:n]); k = int(0.05 * SR); e = np.convolve(e, np.ones(k) / k, 'same') > 0.004
    # 说话前 0.25 秒开始压低，说完 0.6 秒后恢复
    act = np.zeros(n, bool); idx = np.flatnonzero(e)
    if len(idx):
        on = np.zeros(n + 1, np.int32); s = np.clip(idx - int(0.25 * SR), 0, n); t = np.clip(idx + int(0.6 * SR), 0, n)
        np.add.at(on, s, 1); np.add.at(on, t, -1); act = np.cumsum(on)[:n] > 0
    g = np.where(act, 10 ** (-11 / 20), 1.0).astype(np.float32)
    k = int(0.35 * SR); g = np.convolve(g, np.ones(k) / k, 'same')
    return g
for tag, narr, quo in [('J', 'zh-CN-YunjianNeural', 'zh-CN-YunyangNeural'), ('Y', 'zh-CN-YunyangNeural', 'zh-CN-YunjianNeural')]:
    v, rec = tts.build(lines, TOTAL, narr, quo)
    json.dump(rec, open(f'/tmp/vo/rec_{tag}.json', 'w'), ensure_ascii=False, indent=0)
    m = music(); n = min(len(m), len(v)); g = duck(v, n)
    mix = m[:n] * g[:, None] + v[:n, None] * 0.98
    mix.astype(np.float32).tofile(f'/tmp/vo/mix_{tag}.f32'); v[:n].astype(np.float32).tofile(f'/tmp/vo/vo_{tag}.f32')
    for r in rec: print(tag, f"{r['t']:6.2f} win {r['win']:5.2f} dur {r['dur']:5.2f} end {r['end']:6.2f} next {r['next']:6.2f}", r['log'], r['txt'][:14])

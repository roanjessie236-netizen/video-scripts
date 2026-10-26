# 全片配乐＋混音：按章铺《觉醒年代》原声与阿炳老录音；人声时压低 11 dB；输出全片混音与分轨（人声、配乐），并按上下两段切开
import json, subprocess, numpy as np
SR = 48000; END = 1146.92; SPLIT = 15181 / 25          # 上段止于第五章起点 607.24 秒
M = '/tmp/vo/mus/'
P1, P2 = M + 'jx1.m4s', M + 'jx2.m4s'
# (全片起点, 全片终点, 文件, 素材起点, 淡入, 淡出, 目标 RMS dB, 说明)
PLAN = [
 (0.0,    68.6,  P2, 334.1,          2.5, 1.6, -21, '序｜《陈独秀和家人2》（觉醒年代原声，较静的钢琴/弦乐，与试听一致）'),
 (68.0,  179.6,  M + 'erquan.mp3', 0.6, 1.5, 2.0, -22, '一｜阿炳《二泉映月》（老录音）'),
 (179.5, 332.9,  P1, 1961.1 + 92,    1.5, 2.0, -21, '二｜《李大钊》后半（渐强，落在“一生事业的起点”）'),
 (332.7, 435.7,  P2, 831.7 + 62,     1.5, 2.0, -21, '三｜《黑暗》后半（钞古碑—铁屋子—呐喊）'),
 (435.5, 573.5,  M + 'hanchun.mp3', 0.4, 1.5, 2.0, -22, '四上｜阿炳《寒春风曲》（老录音，彷徨、反抗绝望）'),
 (571.5, 607.3,  P1, 450.0 + 112,    2.0, 1.5, -21, '四下｜《存亡时刻》尾段（三一八）'),
 (607.2, 650.3,  P2, 1595.5,         1.5, 1.5, -21, '五上｜《思绪》（厦门）'),
 (649.0, 724.8,  P1, 1456.9,         1.0, 1.5, -22, '五下｜《局势》（广州清党—思路轰毁）'),
 (724.7, 804.2,  P2, 0.0,            1.5, 1.5, -21, '六①｜《奉献》（上海定居、左联）'),
 (803.0, 912.0,  P2, 1734.4 + 80,    1.5, 2.0, -21, '六②｜《我们的同胞》中段（柔石等遇害、《惯于长夜》、为了忘却的记念）'),
 (910.5, 986.0,  P2, 1520.4,         1.5, 1.5, -21, '六③｜《光明》（瞿秋白、横眉冷对、第六次转身）'),
 (985.9, 1075.6, P2, 2899.3,         1.5, 1.2, -21, '尾声上｜《依然》开头（病重—逝世）'),
 (1074.71, END,  P2, 1223.7 + 136.5, 1.2, 2.5, -21, '尾声下＋片尾｜《期盼》（与试听一致，“先生，九十年过去了”起渐强）'),
]
def seg(f, start, dur):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', f, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                        capture_output=True).stdout, np.float32).reshape(-1, 2)
N = int(END * SR)
mus = np.zeros((N, 2), np.float32)
for t0, t1, f, s0, fin, fout, gdb, _ in PLAN:
    y = seg(f, s0, t1 - t0).copy(); n = len(y); r = np.ones(n, np.float32)
    a, b = int(fin * SR), int(fout * SR); r[:a] = np.linspace(0, 1, a); r[n - b:] = np.minimum(r[n - b:], np.linspace(1, 0, b))
    rms = np.sqrt((y ** 2).mean()); y = y * r[:, None] * (10 ** (gdb / 20) / rms)
    s = int(t0 * SR); mus[s:s + n] += y[:N - s]
vo = np.fromfile('/tmp/vo/vo_full.f32', np.float32)[:N]
vo = np.concatenate([vo, np.zeros(N - len(vo), np.float32)])
# 压低：有人声（含前 0.25 秒、后 0.6 秒）时 -11 dB，0.35 秒平滑
e = np.convolve(np.abs(vo), np.ones(2400) / 2400, 'same') > 0.004
on = np.zeros(N + 1, np.int32); idx = np.flatnonzero(e)
np.add.at(on, np.clip(idx - int(0.25 * SR), 0, N), 1); np.add.at(on, np.clip(idx + int(0.6 * SR), 0, N), -1)
act = np.cumsum(on)[:N] > 0
g = np.where(act, 10 ** (-11 / 20), 1.0).astype(np.float32)
k = int(0.35 * SR); c = np.cumsum(np.concatenate([[0], g])); g = ((c[k:] - c[:-k]) / k).astype(np.float32); g = np.concatenate([g, np.full(N - len(g), g[-1], np.float32)])
mus_d = mus * g[:, None]; vo2 = np.repeat(vo[:, None] * 0.98, 2, 1)
mix = mus_d + vo2
for name, arr in [('mix', mix), ('stem_vo', vo2), ('stem_mus', mus_d)]: arr.astype(np.float32).tofile(f'/tmp/vo/{name}_full.f32')
json.dump([dict(t0=p[0], t1=p[1], src=p[7]) for p in PLAN], open('/tmp/vo/music_plan.json', 'w'), ensure_ascii=False, indent=0)
print('ok', N / SR, 'peak', float(np.abs(mix).max()))

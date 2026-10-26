# 全片配音：旁白云健；原文云健·旧录音质感（第二轮 C3）。按全片时间线逐句合成，画面不动，声音贴字幕起点。
# 语速分三档（用户：信息量少的地方可以适当加快）：
#   key  情感重点句（EMO 表）：放慢、降调，可放慢去填满字幕时长
#   info 含年份/数字、人名地名、书名、引号术语的“信息句”：正常语速，只轻微放慢补时（最多 -6%）
#   low  其余过渡/引出句（如“他说——”“后来，他为《彷徨》题诗——”）：加快 10%，不为凑字幕放慢，句后留白交给配乐
# 原文：放慢（基础 -16%/-4Hz），最多放慢到 -28% 去贴字幕；为不压到下一句，必要时可加快（最多 +10%）。
import json, re, sys, os, numpy as np
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/tmp/vo'); import tts
SR = tts.SR; END = 1146.92
tts.PRON.update({'於菟': '乌途', '荷戟': '贺戟', '憎恶': '憎雾', '编校': '编较', '正长': '正常', '魏连殳': '魏连书', '冯铿': '冯坑'})
tts.QPROF.update(base=(-16, -4), rev=(0.45, -17),
                 flt='highpass=f=200,lowpass=f=5200,equalizer=f=1800:t=q:w=1:g=3,acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=2,asoftclip=type=tanh:threshold=0.7')
NARR = QUO = 'zh-CN-YunjianNeural'
NAMES = '鲁迅 周樟寿 蔡元培 钱玄同 周作人 许广平 朱安 段祺瑞 藤野 严复 吕纬甫 魏连殳 杜师长 内山完造 柔石 殷夫 胡也频 冯铿 李伟森 珂勒惠支 瞿秋白 毛泽东 许寿裳 海婴 刘和珍 ' \
        '绍兴 南京 东京 仙台 北京 厦门 广州 上海 龙华 八道湾 西三条 大陆新村 中山大学 教育部 左联 创造社 太阳社 孔乙己 阿Q 闰土'.split()
tts.EMO.update({'他不让人纪念': (-2, -1), '次转身': (-4, -1)})          # 开篇第一句、各章“第N次转身”字卡句按重点句处理
THEME = ['看不见希望，也不向绝望下跪', '人们常记住前一句的冷', '五十五岁那年秋天', '病得最重的一个夜里']   # 点题句：正常语速
def info_tokens(t):
    return 2 * len(re.findall(r'\d+|[一二三四五六七八九十]{2,}岁', t)) + t.count('《') + t.count('“') + sum(t.count(n) for n in NAMES)
def tier(e):
    if e['kind'] != 'vo': return 'q'
    if any(k in e['txt'] for k in tts.EMO): return 'key'
    if any(k in e['txt'] for k in THEME): return 'info'
    n = tts.nchar(e['txt']); k = info_tokens(e['txt'])
    return 'info' if k >= 2 or (k == 1 and n <= 14 and not e['txt'].endswith(('——', '：'))) else 'low'
POL = {  # 基础语速, 填时下限（占字幕时长比例）, 最慢, 最快
    'key': (0, 0.9, -15, 25), 'info': (0, 0.85, -6, 30), 'low': (10, 0.0, 10, 35), 'q': (None, 0.8, -28, 10)}
def fit(e, hard_end):
    k = tier(e); r0, lo_r, rmin, rmax = POL[k]
    if k == 'q': r0, p0 = tts.QPROF['base']
    else: p0 = 0
    er, ep = next((v for kk, v in tts.EMO.items() if kk in e['txt']), (0, 0))
    r, p = r0 + er, p0 + ep; rmin = min(rmin, r)
    win = e['win']; st = tts.speak_text(e['txt']); log = []
    # 允许的最长时长：字幕时长＋到下一句前留 0.5 秒的余量（旁白最多多占 0.35 秒，原文最多 0.8 秒）
    room = hard_end - (e['t'] + win)
    hi = win + (min(0.35, max(0.0, room - 0.15)) if k != 'q' else min(0.8, max(0.0, room - 0.5)))
    hi = max(hi, 0.5)
    for it in range(5):
        x = tts.gen(st, QUO if k == 'q' else NARR, r, p); d = len(x) / SR; log.append((r, round(d, 2)))
        if d > hi and r < rmax: r = min(r + int(np.ceil((d / (hi * 0.98) - 1) * 100)) + 1, rmax)
        elif d < win * lo_r and r > rmin: r = max(r - int(np.ceil((1 - d / (win * lo_r * 1.03)) * 100)), rmin)
        else: break
    return x, dict(t=e['t'], kind=e['kind'], tier=k, win=win, dur=round(d, 2), end=round(e['t'] + d, 2), next=e['next'], log=log, txt=e['txt'])
if __name__ == '__main__':
    L = json.load(open('/tmp/vo/tl_full.json'))
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda e: fit(e, e['next']), L))
    out = np.zeros(int(END * SR) + SR, np.float32); rec = []
    for (x, r), e in zip(res, L):
        y = tts.fx(x, 'vo' if e['kind'] == 'vo' else 'q'); a = int(e['t'] * SR); out[a:a + len(y)] += y[:len(out) - a]; rec.append(r)
    out[:int(END * SR)].tofile('/tmp/vo/vo_full.f32'); json.dump(rec, open('/tmp/vo/rec_full.json', 'w'), ensure_ascii=False, indent=0)
    for r in rec:
        print(f"{r['t']:7.2f} {r['tier']:4s} win {r['win']:5.2f} dur {r['dur']:5.2f} slack {r['next'] - r['end']:5.2f} {r['log']} {r['txt'][:16]}")

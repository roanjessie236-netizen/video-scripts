# 全片配音：旁白云健；原文云健·旧录音质感（第二轮 C3）。按全片时间线逐句合成，画面不动，声音贴字幕起点。
# 语速分三档（用户：信息量少的地方可以适当加快）：
#   key  情感重点句（EMO 表）：放慢、降调，可放慢去填满字幕时长
#   info 含年份/数字、人名地名、书名、引号术语的“信息句”：正常语速，只轻微放慢补时（最多 -6%）
#   low  其余过渡/引出句（如“他说——”“后来，他为《彷徨》题诗——”）：加快 10%，不为凑字幕放慢，句后留白交给配乐
# 原文：放慢（基础 -16%/-4Hz），最多放慢到 -28% 去贴字幕；为不压到下一句，必要时可加快（最多 +10%）。
# v5（2026-10-27）按反馈：
#   诗词（Q09 等）按句拆开分别合成、句间停顿（逗号 0.35 秒、句号 0.7 秒），基础 -20%；
#   画面不动的章节里，长原文若整句读完仍明显早于字幕（如第一章 Q05），改为按字幕行分段合成、每段从该行出现时起读；
#   引出原文的“……提出——”类句子，若与下一句之间空得多，略放慢并稍后起读（最多 0.6 秒），读完紧接原文；
#   第三、四章重新排时：每句按自然语速合成（fixed），字幕时长＝实际配音时长（dur34.py）。
#   时间线改由 timeline_full.py 写入 /tmp/vo/tl_full.json、tl_meta.json（含 END）。
import json, re, sys, os, csv, numpy as np
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/tmp/vo'); import tts
SR = tts.SR; END = 1146.92
tts.PRON.update({'於菟': '乌途', '荷戟': '贺戟', '憎恶': '憎雾', '编校': '编较', '正长': '正常', '魏连殳': '魏连书', '冯铿': '冯坑'})
tts.QPROF.update(base=(-16, -4), rev=(0.45, -17),
                 flt='highpass=f=200,lowpass=f=5200,equalizer=f=1800:t=q:w=1:g=3,acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=2,asoftclip=type=tanh:threshold=0.7')
NARR = QUO = 'zh-CN-YunjianNeural'
NAMES = '鲁迅 周樟寿 蔡元培 钱玄同 周作人 许广平 朱安 段祺瑞 藤野 严复 吕纬甫 魏连殳 杜师长 内山完造 柔石 殷夫 胡也频 冯铿 李伟森 珂勒惠支 瞿秋白 毛泽东 许寿裳 海婴 刘和珍 ' \
        '章士钊 杨荫榆 绍兴 南京 东京 仙台 北京 厦门 广州 上海 龙华 八道湾 西三条 大陆新村 中山大学 教育部 左联 创造社 太阳社 孔乙己 阿Q 闰土'.split()
tts.EMO.update({'他不让人纪念': (-2, -1), '次转身': (-4, -1), '这是他对新文化运动的反思': (-3, -1), '更痛惜青年的血': (-3, -1)})          # 开篇第一句、各章“第N次转身”字卡句按重点句处理
THEME = ['看不见希望，也不向绝望下跪', '人们常记住前一句的冷', '五十五岁那年秋天', '病得最重的一个夜里',
         '那几年，他自己的生活', '女师大学潮愈演愈烈', '从此他更认定']   # 点题句：正常语速
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

QT = {r[0]: r[1] for r in csv.reader(open('/tmp/root/quotes_src.tsv', encoding='utf-8'), delimiter='\t')}
QT.update({'Q98': '改革自然常不免于流血，但流血非即等于改革。'})
POEMS = {QT[i] for i in ['Q09', 'Q24', 'Q36', 'Q39', 'Q41', 'Q68', 'Q72', 'Q88']}
POEM_RATE = -20
RATE = {QT['Q57']: -6, QT['Q20']: -6}          # 第三章“仁义道德……吃人”：用户嫌慢，原文这两句读快些
def natural(e):
    """自然语速（不为贴字幕调整）：返回 (档, 语速, 音高)"""
    k = tier(e); r0 = POL[k][0]; p0 = 0
    if k == 'q': r0, p0 = tts.QPROF['base']
    er, ep = next((v for kk, v in tts.EMO.items() if kk in e['txt']), (0, 0))
    r, p = r0 + er, p0 + ep
    if e['txt'] in POEMS: r = POEM_RATE + er
    return k, RATE.get(e['txt'], r), p
def synth(txt, kind, r, p, poem=False):
    """返回 (音频, 时间信息)：诗词为分句起点 [('p', 秒, 分句)]，其余为逐词时间 [('w', 秒, 时长, 词)]"""
    v = QUO if kind != 'vo' else NARR
    if poem:
        x, st = tts.gen_poem(txt, v, r, p); return x, [('p', t, w) for t, w in st]
    x, mk = tts.gen(tts.speak_text(txt), v, r, p, marks=True); return x, [('w', o, d, w) for o, d, w in mk]
def _al(s): return len(re.findall(r'\w', s))
def chunk_starts(txt, dur, info, lead=0.08):
    """字幕各行相对起点（秒）：按逐词时间/诗句起点定位每行第一个字"""
    cs = CHUNKS(txt); idx, n = [], 0
    for c in cs: idx.append(n); n += _al(c)
    N = max(1, n)
    if info and info[0][0] == 'p':
        bd, m = [], 0
        for _, t, w in info: bd.append((m, t)); m += _al(w)
        sc = m / N
        T = lambda i: max([t for m0, t in bd if m0 <= i * sc + 1e-6] + [0.0])
    elif info:
        ws, m = [], 0
        for _, o, d, w in info:
            k = _al(w)
            if k: ws.append((m, k, o, d)); m += k
        sc = m / N if m else 1.0
        def T(i):
            j = i * sc
            for m0, k, o, d in ws:
                if m0 <= j < m0 + k: return o + d * (j - m0) / k
            return dur * i / N
    else:
        T = lambda i: dur * i / N
    st = [0.0] + [max(0.0, T(i) - lead) for i in idx[1:]]
    return [round(x, 3) for x in st]
_src = open('/tmp/gh/preview/render_ch34.py', encoding='utf-8').read()
_g = {'re': re}; exec(_src[_src.index('def nchar(txt)'):_src.index('FS, FA = SERIF')], _g); CHUNKS = _g['chunks']
def fit_generic(txt, kind, tierk, r, p, win, hi, lo_r, rmin, rmax, poem=False):
    log = []
    for it in range(6):
        x, info = synth(txt, kind, r, p, poem); d = len(x) / SR; log.append((r, round(d, 2)))
        if d > hi and r < rmax: r = min(r + int(np.ceil((d / (hi * 0.98) - 1) * 100)) + 1, rmax)
        elif d < win * lo_r and r > rmin: r = max(r - int(np.ceil((1 - d / (win * lo_r * 1.03)) * 100)), rmin)
        else: break
    if d > hi:                                 # 来回摆动仍超长：改用试过的、不超长的最长一档
        ok = [(dd, rr) for rr, dd in log if dd <= hi]
        if ok:
            r = max(ok)[1]; x, info = synth(txt, kind, r, p, poem); d = len(x) / SR; log.append((r, round(d, 2)))
    return x, info, d, log
def fit(e, hard_end):
    """画面不动的章节：整句贴字幕（同 v4），诗词用分句模式"""
    k = tier(e); _, lo_r, rmin, rmax = POL[k]; _, r, p = natural(e); rmin = min(rmin, r)
    poem = e['txt'] in POEMS
    if poem: rmin, rmax = min(rmin, r), 6
    win = e['win']; room = hard_end - (e['t'] + win)
    hi = win + (min(0.35, max(0.0, room - 0.15)) if k != 'q' else min(0.8, max(0.0, room - 0.5))); hi = max(hi, 0.5)
    if e.get('leadin'):                       # 引出句：允许略放慢去贴近下一句（过渡句最慢到正常语速）
        lo_r, rmin = 1.0, min(rmin, 0 if k == 'low' else -8); hi = max(hi, min(win + 0.3, hard_end - e['t'] - 0.3))
    x, info, d, log = fit_generic(e['txt'], e['kind'], k, r, p, win, hi, lo_r, rmin, rmax, poem)
    return x, info, d, log, k
def place_chunks(e, hard_end):
    """按字幕行分段合成：每段从该行出现时起读（行时间取自画面里的字幕）"""
    k = tier(e); _, r0, p = natural(e); segs = []; log = []
    rows = e['rows']
    for i, (a, b, c) in enumerate(rows):
        nxt = rows[i + 1][0] if i + 1 < len(rows) else hard_end
        w = b - a; hi = max(0.4, min(w + 0.5, nxt - a - 0.12))
        x, info, d, lg = fit_generic(c, e['kind'], k, r0, p, w, hi, 0.8, -28, 10, c in POEMS or e['txt'] in POEMS)
        segs.append((a, x, d, c)); log.append(lg[-1])
    return segs, log, k
if __name__ == '__main__':
    L = json.load(open('/tmp/vo/tl_full.json')); END = json.load(open('/tmp/vo/tl_meta.json'))['END']
    def run(e):
        if e.get('fixed'):                     # 第三、四章：自然语速，字幕已按配音排
            k, r, p = natural(e); x, info = synth(e['txt'], e['kind'], r, p, e['txt'] in POEMS)
            d = len(x) / SR
            return [(e['t'], x)], dict(t=e['t'], kind=e['kind'], tier=k, mode='fixed', win=e['win'], dur=round(d, 2), end=round(e['t'] + d, 2), next=e['next'], log=[(r, round(d, 2))], txt=e['txt'],
                                       cs=[(round(e['t'] + a, 2), c) for a, c in zip(e['cs'], CHUNKS(e['txt']))])
        x, info, d, log, k = fit(e, e['next']); t0 = e['t']; mode = 'poem' if e['txt'] in POEMS else 'fit'
        rows = e.get('rows') or []
        ahead = e['kind'] != 'vo' and len(rows) >= 2 and d < 0.85 * e['win'] and e['win'] - d > 1.5
        if (ahead or (e['txt'] in POEMS and len(rows) >= 2)):
            segs, lg, k = place_chunks(e, e['next']); mode = 'rows'
            end = max(a + dd for a, _, dd, _ in segs)
            return [(a, x) for a, x, _, _ in segs], dict(t=t0, kind=e['kind'], tier=k, mode=mode, win=e['win'], dur=round(end - t0, 2), end=round(end, 2), next=e['next'], log=lg, txt=e['txt'],
                                                       cs=[(round(a, 2), c) for a, _, _, c in segs], segs=[(round(a, 2), round(dd, 2)) for a, _, dd, _ in segs])
        if e.get('leadin'):                    # 读完紧接下一句：最多推迟 0.6 秒起读
            sh = min(0.6, max(0.0, e['next'] - 0.3 - (t0 + d))); t0 += sh; mode = 'leadin+%.2f' % sh
        cs = CHUNKS(e['txt']); st = chunk_starts(e['txt'], d, info)
        return [(t0, x)], dict(t=round(t0, 3), kind=e['kind'], tier=k, mode=mode, win=e['win'], dur=round(d, 2), end=round(t0 + d, 2), next=e['next'], log=log, txt=e['txt'],
                               cs=[(round(t0 + a, 2), c) for a, c in zip(st, cs)])
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(run, L))
    out = np.zeros(int(END * SR) + SR, np.float32); rec = []
    for (pieces, r), e in zip(res, L):
        for t, x in pieces:
            y = tts.fx(x, 'vo' if e['kind'] == 'vo' else 'q'); a = int(t * SR); out[a:a + len(y)] += y[:len(out) - a]
        rec.append(r)
    out[:int(END * SR)].tofile('/tmp/vo/vo_full.f32'); json.dump(rec, open('/tmp/vo/rec_full.json', 'w'), ensure_ascii=False, indent=0)
    for r in rec:
        print(f"{r['t']:7.2f} {r['tier']:4s} {r['mode']:10s} win {r['win']:5.2f} dur {r['dur']:5.2f} slack {r['next'] - r['end']:5.2f} {r['log']} {r['txt'][:16]}")

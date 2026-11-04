# 全片时间线：从六个分章渲染脚本中只执行“字幕排时”部分（打桩，不读素材），导出每句旁白/原文（含转身字卡句）的起点，换算到全片时间
# v5（2026-10-27）：第三、四章重排后时长变了，第五章起的全片起点按 full_film.py 规则重算；每句另记画面字幕各行起止（rows，供配音按行对位）；
#   第三、四章各句标 fixed（自然语速，字幕按配音排，win＝实际配音时长，cs＝各行起点）；“……——/：”引出原文的旁白标 leadin。
import re, csv, json, yaml, numpy as np
G = '/tmp/gh/preview/'; FPS = 25
CH = [  # 脚本, 结束行正则, 转身字卡补丁 (原文, 替换)
 ('render_preview_v3.py', r'^TOTAL_MAIN = 179\.5', [("if (sid, kind) == ('S1-06', 'vo'): t +=", "if (sid, kind) == ('S1-06', 'vo'): __turns.append((t, txt)); t +=")]),
 ('render_ch2.py', r'^    return t - TOTAL_MAIN \+ NEW_MAIN', [("TURN2 = t; t +=", "TURN2 = t; __turns.append((t, '这是' + a2)); t +=")]),
 ('render_ch34.py', r'^TOTAL_MAIN = ', [("TURN[sid] = t; t +=", "TURN[sid] = t; __turns.append((t, '这是' + a2)); t +=")]),
 ('render_ch5.py', r'^TOTAL_MAIN = ', [("TURN[sid] = t; t +=", "TURN[sid] = t; __turns.append((t, '这是' + a2)); t +=")]),
 ('render_ch6.py', r'^TOTAL_MAIN = ', [("TURN[sid] = t; t +=", "TURN[sid] = t; __turns.append((t, a2)); t +=")]),
 ('render_ch7.py', r'^TOTAL_MAIN = ', [])]
LENS = [179.5, 153.25, None, 117.48, 261.25]      # 各章在全片中的时长（第三四章取 render_ch34 的 TOTAL_MAIN）；规则同 full_film.py
LAST_END, XF, CR_N = 3599, 25, 450
def nchar(t): return len(re.sub(r'[，。；：！？、—“”（）\s]', '', t))
DUR = json.load(open('/tmp/vo/dur34.json', encoding='utf-8'))
F = [0]; out = []; meta = {}
for ci, (fn, endp, patches) in enumerate(CH):
    src = open(G + fn, encoding='utf-8').read().split('\n')
    a = next(i for i, l in enumerate(src) if l.startswith('# ---------- 字幕')); b = next(i for i, l in enumerate(src) if i > a and re.search(endp, l))
    code = '\n'.join(src[a:b + 1])
    code = code.replace('def SUB(t0, kind, txt=None):', 'def SUB(t0, kind, txt=None):\n    __n0 = len(SUBLOG); __r = _SUB0(t0, kind, txt); __calls.append((t0, kind, txt or Q[kind], list(SUBLOG[__n0:]))); return __r\ndef _SUB0(t0, kind, txt=None):', 1)
    for o, n in patches:
        assert code.count(o) == 1, (fn, o); code = code.replace(o, n)
    g = {'re': re, 'csv': csv, 'yaml': yaml, 'np': np, 'ROOT': '/tmp/root/', 'text_rgba': lambda *x, **k: None, 'SERIF': lambda *x, **k: None,
         'SANS': lambda *x, **k: None, 'FPS': FPS, 'subs': [], '__calls': [], '__turns': []}
    exec(code, g)
    if ci == 2:
        LENS[2] = g['TOTAL_MAIN']; meta['T34'] = g['TOTAL_MAIN']; meta['ST34'] = g['ST']
        cum = 0.0; F = [0]
        for x in LENS: cum += x; F.append(int(cum * FPS + 0.5))
    off = [0, 4488, 8319][ci] / FPS if ci < 3 else F[ci] / FPS
    M = g.get('M') if fn == 'render_ch2.py' else None
    mp = (lambda x: M(x)) if M else (lambda x: x)
    items = [(t, k, x, 'sub', rows) for t, k, x, rows in g['__calls']] + [(t, 'vo', x, 'card', []) for t, x in g['__turns']]
    items.sort(key=lambda e: e[0])
    for t, k, x, how, rows in items:
        tc = mp(t)
        e = dict(ch=ci, t=round(off + tc, 3), tch=round(tc, 3), kind=k, txt=x, how=how, win=round(nchar(x) / (4.2 if k == 'vo' else 3.3), 3),
                 rows=[(round(off + mp(ra), 3), round(off + mp(rb), 3), c) for ra, rb, c in rows])
        if ci == 2:
            D = DUR[x]; e.update(fixed=True, win=D['dur'], cs=D['cs'])
        out.append(e)
    print(fn, 'off', round(off, 2), len(items), 'turn cards', len(g['__turns']), 'TOTAL_MAIN', g.get('TOTAL_MAIN'))
out.sort(key=lambda e: e['t'])
CRED_START = (F[5] + LAST_END - XF) / FPS; END = (F[5] + LAST_END - XF + CR_N) / FPS
for i, e in enumerate(out):
    e['next'] = out[i + 1]['t'] if i + 1 < len(out) else CRED_START
    if e['kind'] == 'vo' and not e.get('fixed') and e['txt'].rstrip().endswith(('——', '：')) and i + 1 < len(out) and out[i + 1]['kind'] != 'vo':
        e['leadin'] = True
meta.update(END=END, F=F, CRED_START=CRED_START)
json.dump(out, open('/tmp/vo/tl_full.json', 'w'), ensure_ascii=False, indent=0)
json.dump(meta, open('/tmp/vo/tl_meta.json', 'w'), ensure_ascii=False, indent=0)
print('F', F, 'END', END, 'CRED_START', CRED_START)
print('lines', len(out), 'vo', sum(e['kind'] == 'vo' for e in out), 'q', sum(e['kind'] != 'vo' for e in out), 'leadin', sum(bool(e.get('leadin')) for e in out))
r = [(e['rows'][-1][1] - e['rows'][0][0]) / e['win'] for e in out if e['rows'] and not e.get('fixed')]
print('rows窗/估算窗 比值：min %.2f median %.2f max %.2f' % (min(r), float(np.median(r)), max(r)))
bad = [(round(e['t'], 2), round(e['next'] - e['t'] - e['win'], 2), e['txt'][:12]) for e in out if e['next'] - e['t'] - e['win'] < 0.3]
print('tight/overlap', bad[:20])

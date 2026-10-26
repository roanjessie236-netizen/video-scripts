# 全片时间线：从六个分章渲染脚本中只执行“字幕排时”部分（打桩，不读素材），导出每句旁白/原文（含转身字卡句）的起点，换算到全片时间
import re, csv, json, yaml, numpy as np
G = '/tmp/gh/preview/'
CH = [  # 脚本, 全片起点（full_film.py 的帧对齐起点）, 结束行正则, 转身字卡补丁 (原文, 替换)
 ('render_preview_v3.py', 0.0, r'^TOTAL_MAIN = 179\.5', [("if (sid, kind) == ('S1-06', 'vo'): t +=", "if (sid, kind) == ('S1-06', 'vo'): __turns.append((t, txt)); t +=")]),
 ('render_ch2.py', 4488 / 25, r'^    return t - TOTAL_MAIN \+ NEW_MAIN', [("TURN2 = t; t +=", "TURN2 = t; __turns.append((t, '这是' + a2)); t +=")]),
 ('render_ch34.py', 8319 / 25, r'^TOTAL_MAIN = ', [("TURN[sid] = t; t +=", "TURN[sid] = t; __turns.append((t, '这是' + a2)); t +=")]),
 ('render_ch5.py', 15181 / 25, r'^TOTAL_MAIN = ', [("TURN[sid] = t; t +=", "TURN[sid] = t; __turns.append((t, '这是' + a2)); t +=")]),
 ('render_ch6.py', 18118 / 25, r'^TOTAL_MAIN = ', [("TURN[sid] = t; t +=", "TURN[sid] = t; __turns.append((t, a2)); t +=")]),
 ('render_ch7.py', 24649 / 25, r'^TOTAL_MAIN = ', [])]
def nchar(t): return len(re.sub(r'[，。；：！？、—“”（）\s]', '', t))
out = []
for ci, (fn, off, endp, patches) in enumerate(CH):
    src = open(G + fn, encoding='utf-8').read().split('\n')
    a = next(i for i, l in enumerate(src) if l.startswith('# ---------- 字幕')); b = next(i for i, l in enumerate(src) if i > a and re.search(endp, l))
    code = '\n'.join(src[a:b + 1])
    code = code.replace('def SUB(t0, kind, txt=None):', 'def SUB(t0, kind, txt=None):\n    __calls.append((t0, kind, txt or Q[kind]))', 1)
    for o, n in patches:
        assert code.count(o) == 1, (fn, o); code = code.replace(o, n)
    g = {'re': re, 'csv': csv, 'yaml': yaml, 'np': np, 'ROOT': '/tmp/root/', 'text_rgba': lambda *x, **k: None, 'SERIF': lambda *x, **k: None,
         'SANS': lambda *x, **k: None, 'subs': [], '__calls': [], '__turns': []}
    exec(code, g)
    M = g.get('M') if fn == 'render_ch2.py' else None
    items = [(t, k, x, 'sub') for t, k, x in g['__calls']] + [(t, 'vo', x, 'card') for t, x in g['__turns']]
    items.sort(key=lambda e: e[0])
    for t, k, x, how in items:
        tc = M(t) if M else t
        out.append(dict(ch=ci, t=round(off + tc, 3), tch=round(tc, 3), kind=k, txt=x, how=how,
                        win=round(nchar(x) / (4.2 if k == 'vo' else 3.3), 3)))
    print(fn, len(items), 'turn cards', len(g['__turns']), 'TOTAL_MAIN', g.get('TOTAL_MAIN'))
out.sort(key=lambda e: e['t'])
for i, e in enumerate(out):
    e['next'] = out[i + 1]['t'] if i + 1 < len(out) else 1128.92
json.dump(out, open('/tmp/vo/tl_full.json', 'w'), ensure_ascii=False, indent=0)
print('lines', len(out), 'vo', sum(e['kind'] == 'vo' for e in out), 'q', sum(e['kind'] != 'vo' for e in out))
bad = [(round(e['t'], 2), round(e['next'] - e['t'] - e['win'], 2), e['txt'][:12]) for e in out if e['next'] - e['t'] - e['win'] < 0.3]
print('tight/overlap', bad[:20])

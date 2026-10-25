# 从各章渲染脚本中只执行“字幕排时”部分（打桩，不读素材），导出每句旁白/原文的起止时间（章内秒）
import re, csv, json, sys, yaml
def run(path, start_pat, end_pat, extra=''):
    src = open(path, encoding='utf-8').read().split('\n')
    a = next(i for i, l in enumerate(src) if start_pat in l); b = next(i for i, l in enumerate(src) if i > a and re.search(end_pat, l))
    g = {'re': re, 'csv': csv, 'yaml': yaml, 'ROOT': '/data/luxun90/', 'text_rgba': lambda *x, **k: None, 'SERIF': lambda *x, **k: None, 'subs': []}
    code = '\n'.join(src[a:b + 1]) + '\n' + extra
    # 记录每次 SUB 调用：(起点, 类型, 全文)
    g['__calls'] = []
    exec(code.replace('def SUB(t0, kind, txt=None):', 'def SUB(t0, kind, txt=None):\n    __calls.append((t0, kind, txt or Q[kind]))', 1), g)
    return g
out = {}
g = run('/tmp/vo/render_preview_v3.py', '# ---------- 字幕', r'^SUB\(42\.6')
out['S0'] = [dict(t=round(t, 3), kind=k, txt=x) for t, k, x in g['__calls']]
g = run('/data/luxun90/preview/render_ch7.py', '# ---------- 字幕', r'^TOTAL_MAIN')
out['S7'] = [dict(t=round(t, 3), kind=k, txt=x) for t, k, x in g['__calls']]
out['S7_ST'] = {k: round(v, 3) for k, v in g['ST'].items()}; out['S7_TOTAL_MAIN'] = g['TOTAL_MAIN']
out['rates'] = dict(VR=g['VR'], QR=g['QR'])
json.dump(out, open('/tmp/vo/tl_sample.json', 'w'), ensure_ascii=False, indent=1)
nch = g['nchar']
for k in ('S0', 'S7'):
    for e in out[k]:
        d = nch(e['txt']) / (g['QR'] if e['kind'] != 'vo' else g['VR'])
        print(k, f"{e['t']:7.2f} {e['t']+d:7.2f}", e['kind'], e['txt'][:40])
print(out['S7_ST'], out['S7_TOTAL_MAIN'])

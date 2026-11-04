# 第三、四章：每句按自然语速先合成，记下实际时长与各行字幕起点（逐词时间对齐）→ /tmp/vo/dur34.json，供 render_ch34.py 排时
import json, sys, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/tmp/vo'); import tts_full as F
src = open('/tmp/gh/preview/render_ch34.py', encoding='utf-8').read()
g = {'__name__': 'dur34', 'sys': sys}; sys.argv = ['render_ch34.py', '--plan']
exec(src[:src.index('T = 0.0; TURN, ST, EN')].replace("DURF = '/tmp/vo/dur34.json'", "DURF = '/nonexistent'"), g)
items = []
for sid, aud in g['SEQ']:
    for a in aud:
        if 'sil' in a: continue
        kind, txt = ('vo', a['vo']) if 'vo' in a else (a['q'], g['Q'][a['q']])
        if kind == 'vo' and '转身' in txt and '这是' in txt:
            a1, a2 = txt.split('这是', 1)
            if a1: items.append((sid, 'vo', a1))
            items.append((sid, 'vo', '这是' + a2)); continue
        items.append((sid, kind, txt))
def run(it):
    sid, kind, txt = it; e = {'kind': kind, 'txt': txt}
    k, r, p = F.natural(e); poem = txt in F.POEMS
    x, info = F.synth(txt, kind, r, p, poem); d = len(x) / F.SR
    return txt, dict(sid=sid, kind=kind, tier=k, rate=r, pitch=p, poem=poem, dur=round(d, 3), cs=F.chunk_starts(txt, d, info), chunks=F.CHUNKS(txt))
with ThreadPoolExecutor(6) as ex: res = dict(ex.map(run, items))
json.dump(res, open('/tmp/vo/dur34.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for t, r in res.items(): print(r['sid'], r['tier'], r['rate'], r['dur'], len(r['cs']), t[:20])
print('total', round(sum(r['dur'] for r in res.values()), 1), len(res))

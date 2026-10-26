# 配音版字幕（SRT）：按配音实际起止，长句按成片字幕的分行规则（chunks）切开，时长按字数分配
import json, re
src = open('/tmp/gh/preview/render_ch34.py', encoding='utf-8').read()
a = src.index('def nchar(txt)'); b = src.index('FS, FA = SERIF')
g = {'re': re}; exec(src[a:b], g); chunks, nchar = g['chunks'], g['nchar']
R = json.load(open('/tmp/vo/rec_full.json'))
def ts(x): h, r = divmod(x, 3600); m, s = divmod(r, 60); return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}'
out, n = [], 0
for r in R:
    cs = chunks(r['txt']); tot = sum(len(c) for c in cs); u = r['t']; d = r['dur'] + 0.25
    for c in cs:
        dd = d * len(c) / tot; n += 1
        out.append(f'{n}\n{ts(u)} --> {ts(u + dd - 0.04)}\n{c}\n'); u += dd
open('/tmp/vo/忘记我_配音版字幕.srt', 'w', encoding='utf-8').write('\n'.join(out))
print(n, 'entries')

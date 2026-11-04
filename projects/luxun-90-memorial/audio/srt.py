# 配音版字幕（SRT）：按配音实际的每行起点（rec_full.json 的 cs，TTS 合成时按字幕分行逐段对齐）出字幕；
# 行止＝下一行起点；句末行止＝配音结束+0.25 s（不超过下一句起点）；统一提前 0.04 s 收尾
import json
R = json.load(open('/tmp/vo/rec_full.json'))
def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
out, n = [], 0
for i, r in enumerate(R):
    cs = r['cs']; nxt = R[i + 1]['t'] if i + 1 < len(R) else 1e9
    for j, (u, c) in enumerate(cs):
        v = cs[j + 1][0] if j + 1 < len(cs) else min(r['end'] + 0.25, nxt)
        n += 1; out.append(f'{n}\n{ts(u)} --> {ts(v - 0.04)}\n{c}\n')
open('/tmp/vo/忘记我_配音版字幕.srt', 'w', encoding='utf-8').write('\n'.join(out))
print(n, 'entries')

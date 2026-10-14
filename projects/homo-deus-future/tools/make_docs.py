#!/usr/bin/env python3
"""Generate narration.srt from shotlist.json (narration subtitles + closing captions).

Usage: python3 tools/make_docs.py      (run after python3 timeline.py)
script.md and README.md are maintained by hand.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sl = json.load(open(os.path.join(ROOT, 'shotlist.json'), encoding='utf-8'))
CAPS = ['下一章人类历史。', '正在等待我们书写。']


def ts(x):
    ms = int(round(x * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)


cues = [(float(s[0]), float(s[1]), s[2]) for s in sl['subtitles']]
for i, c in enumerate(sl.get('captions', [])):
    if isinstance(c, dict):
        cues.append((float(c['s']), float(c['e']), c['text']))
    elif len(c) >= 3:
        cues.append((float(c[0]), float(c[1]), c[2]))
    else:
        cues.append((float(c[0]), float(c[1]), CAPS[i]))
cues.sort()
assert all('\ufffd' not in t for _, _, t in cues), 'corrupted character in subtitles'
out = ''.join('%d\n%s --> %s\n%s\n\n' % (i + 1, ts(s), ts(e), t) for i, (s, e, t) in enumerate(cues))
open(os.path.join(ROOT, 'narration.srt'), 'w', encoding='utf-8').write(out)
print('wrote', os.path.join(ROOT, 'narration.srt'), len(cues), 'cues')

#!/usr/bin/env python3
"""write SRTs from engine/shotlist.json.
  out/voice.srt          narration placement for mix_tl.py (index = line no. = clip NN.wav, start = VO start)
  out/<name>.zh-en.srt      bilingual subtitles (subtitles + on-screen captions), out/<name>.zh.srt, out/<name>.en.srt
usage: python3 tools/export_srt.py [NAME]"""
import json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(HERE, 'engine', 'shotlist.json'), encoding='utf-8'))
LINES = {x['i']: x for x in json.load(open(os.path.join(HERE, 'voiceover', 'lines.json'), encoding='utf-8'))}
name = sys.argv[1] if len(sys.argv) > 1 else 'whose_tomorrow'
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)


def ts(t):
    ms = int(round(max(t, 0) * 1000))
    return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def write(path, items):
    with open(path, 'w', encoding='utf-8') as f:
        for k, (a, b, txt) in enumerate(items, 1):
            f.write('%d\n%s --> %s\n%s\n\n' % (k, ts(a), ts(b), txt))


with open(os.path.join(out, 'voice.srt'), 'w', encoding='utf-8') as f:
    for v in TL['voice']:
        f.write('%d\n%s --> %s\n%s\n\n' % (v['i'], ts(v['start']), ts(v['start'] + v['dur']),
                                          LINES[v['i']]['sub'].replace('/', '')))
ev = [(s, e, zh, en) for s, e, zh, _src, en in TL['subtitles']] + [(s, e, zh.replace('/', ''), en) for s, e, zh, en in TL['captions']]
ev.sort()
# captions overlap the neighbouring subtitle fades a little: clip each cue to the next start
items = []
for k, (s, e, zh, en) in enumerate(ev):
    if k + 1 < len(ev):
        e = min(e, ev[k + 1][0] - 0.04)
    items.append((s, e, zh, en))
write(os.path.join(out, name + '.zh-en.srt'), [(s, e, zh + '\n' + en) for s, e, zh, en in items])
write(os.path.join(out, name + '.zh.srt'), [(s, e, zh) for s, e, zh, en in items])
write(os.path.join(out, name + '.en.srt'), [(s, e, en) for s, e, zh, en in items])
print('voice lines', len(TL['voice']), 'cues', len(items))

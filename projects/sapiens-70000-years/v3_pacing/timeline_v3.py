"""v3 timeline: narration starts = W(v2f start) + small shifts; v2 subtitle rule [VO start - 0.15, VO end + 0.5] (clipped to
next start - 0.1); line 37 rewritten. Writes vo/vo_starts_v3.srt, shotlist_v3.json (render), audio/*.srt, vo/fit.json."""
import json, wave, copy
from warp import W, OFF_END
SHIFT = {1: -0.2, 2: 0.55, 3: 0.3, 33: -0.4, 37: 0.2}
L37 = '真正的问题，不是我们想成为什么，而是——我们究竟应该想要什么？'
E37 = 'The real question is not what we want to become, but what we should want.'


def ts(x):
    h, m, s = x.split(':'); s, ms = s.split(','); return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def fts(t):
    ms = int(round(max(0, t) * 1000))
    return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


rows = []
for b in open('/data/v2f/audio/vo_starts_v2f.srt', encoding='utf-8').read().strip().split('\n\n'):
    l = b.split('\n'); rows.append([int(l[0]), ts(l[1].split(' --> ')[0]), l[2]])
dur = {i: wave.open('/data/v3/vo/clips/%02d.wav' % i).getnframes() / 48000 for i, _, _ in rows}
for r in rows:
    r[1] = round(W(r[1]) + SHIFT.get(r[0], 0), 3)
    if r[0] == 37:
        r[2] = L37
# narration timing srt (mix placement)
out = []
for n, (i, s, txt) in enumerate(rows):
    e = s + dur[i] + 0.5
    if n + 1 < len(rows):
        e = min(e, rows[n + 1][1] - 0.1)
    out.append('%d\n%s --> %s\n%s\n' % (i, fts(s), fts(e), txt))
open('vo/vo_starts_v3.srt', 'w', encoding='utf-8').write('\n'.join(out))
# render timeline: v2 shotlist with retimed subtitles 1-38
TL2 = json.load(open('/data/v2f/v2core/shotlist.json', encoding='utf-8'))
TL3 = copy.deepcopy(TL2)
subs = []
for n, (i, s, txt) in enumerate(rows[:38]):
    old = TL2['subtitles'][n]
    zh, en = (L37, E37) if i == 37 else (old[2], old[4])
    subs.append([round(s - 0.15, 3), round(s + dur[i] + 0.5, 3), zh, old[3], en])
for n in range(len(subs) - 1):
    subs[n][1] = round(min(subs[n][1], subs[n + 1][0] - 0.1), 3)
TL3['subtitles'] = subs
json.dump(TL3, open('shotlist_v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# viewer srt files (zh + bilingual); 39/40 = the baked closing questions of the user's ending (measured visibility)
caps = [(271.208 + OFF_END, 274.575 + OFF_END, '我们从哪里来？', 'Where do we come from?'),
        (275.608 + OFF_END, 278.242 + OFF_END, '我们将走向哪里？', 'Where are we going?')]
allsubs = [(s, e, zh, en) for s, e, zh, _, en in subs] + caps
open('audio/sapiens_v3_2K_subtitles_bilingual.srt', 'w', encoding='utf-8').write(
    '\n'.join('%d\n%s --> %s\n%s\n%s\n' % (k + 1, fts(s), fts(e), zh, en) for k, (s, e, zh, en) in enumerate(allsubs)))
open('audio/sapiens_v3_2K_subtitles_zh.srt', 'w', encoding='utf-8').write(
    '\n'.join('%d\n%s --> %s\n%s\n' % (k + 1, fts(s), fts(e), zh) for k, (s, e, zh, en) in enumerate(allsubs)))
# fit.json for the mix report
fit = json.load(open('/data/sp/vo2/fit.json', encoding='utf-8'))
for x in fit['lines']:
    if x['i'] == 37:
        x['t'] = L37; x['dur'] = round(dur[37], 3)
json.dump(fit, open('vo/fit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
d = json.load(open('/data/sp/vo2/durs.json')); d['37']['dur'] = round(dur[37], 3)
json.dump(d, open('vo/clips/durs.json', 'w'), indent=0)
print('subs', len(subs), 'last', subs[-1][:2], 'caps', [c[:2] for c in caps])

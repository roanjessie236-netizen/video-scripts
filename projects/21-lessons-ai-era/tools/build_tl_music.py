#!/usr/bin/env python3
"""Build /data/tl/eng/music.py for 《今日简史：AI时代，人类如何重新定义自己》 (224 s).

music.py = film-2 music.py (instrument library + helper functions, everything before the first
log('opening') of its score) + tools/score_tl.py (the new 224 s cue) + the REVERB + MASTER stage.
Usage: python3 tools/build_tl_music.py [film2_music.py] [out_music.py]
"""
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else '/data/hd/music.py'
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, '..', 'music.py')
txt = open(src, encoding='utf-8').read()
F = '# ================================================================== FUTURE SCORE'
M = '# ================================================================== REVERB + MASTER'
i0 = txt.index(F)
i1 = txt.index("log('opening')", i0)
i2 = txt.index(M)
head, master = txt[:i1], txt[i2:]
assert 'DUR = 234.0' in head
head = head.replace('DUR = 234.0', 'DUR = 224.0')
head = head.replace("'/data/hd/out/score.wav'", "'/data/tl/eng/out/score.wav'")
head = head.replace('《未来简史：人类之后，会是谁？》', '《今日简史：AI时代，人类如何重新定义自己》')
for name in ('HEART =', 'BOOM =', 'CRASH =', 'def metal', 'def flute_phrase', 'def lead', 'def str_line'):
    assert name in head, name
if '234' in master:
    print('WARNING: literal 234 in master stage')
score = open(os.path.join(HERE, 'score_tl.py'), encoding='utf-8').read()
open(dst, 'w', encoding='utf-8').write(head + score + '\n' + master)
print('wrote', os.path.abspath(dst), len(head + score + master), 'chars')

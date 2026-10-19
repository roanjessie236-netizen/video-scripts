#!/usr/bin/env python3
"""Build music_wt.py for 《明天属于谁》.

music_wt.py = Film-1 instrument library (sapiens music.py before the 'harmony' marker, constants patched)
+ homo-deus-future tools/score.py helpers (lines before the v2 edit map) + tools/score_wt.py (the cue, read from
shotlist marks) + the Film-1 reverb/master stage (patched: film length, GAINENV).
Usage: python3 tools/build_music_wt.py [SAPIENS_MUSIC.py SCORE_HELPERS.py SHOTLIST.json OUT_music_wt.py]
"""
import sys, os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
src, helpers, shot, dst = (sys.argv[1:5] + [None] * 4)[:4]
src = src or '/data/hd/sapv2/music.py'
helpers = helpers or '/data/hd/tools/score.py'
shot = shot or os.path.join(HERE, '..', 'engine', 'shotlist.json')
dst = dst or os.path.join(HERE, '..', 'music_wt.py')
txt = open(src, encoding='utf-8').read()
H = '# ------------------------------------------------------------------ harmony'
M = '# ================================================================== REVERB + MASTER'
head, master = txt[:txt.index(H)], txt[txt.index(M):]
dur = json.load(open(shot, encoding='utf-8'))['duration']
d0 = head.index('"""'); d1 = head.index('"""', d0 + 3) + 3
head = head[:d0] + '"""Procedural score for 《明天属于谁》 (%.2f s). Built by tools/build_music_wt.py; cue in tools/score_wt.py."""' % dur + head[d1:]
head, n = re.subn(r'^DUR = .*$', 'DUR = %.3f' % dur, head, flags=re.M); assert n == 1
head = head.replace('default_rng(70000)', 'default_rng(1848)')
head = head.replace("'/data/video/out/score.wav'", "'/data/wt/out/score.wav'")
assert '(33, 36, 38, 41, 43, 45, 46)' in head
head = head.replace('(33, 36, 38, 41, 43, 45, 46)', '(33, 36, 38, 40, 41, 43, 45)')
hel = open(helpers, encoding='utf-8').read()
hel = hel[:hel.index('# ------------------------------------------------------------------ v2 edit map')]
cue = open(os.path.join(HERE, 'score_wt.py'), encoding='utf-8').read()
a = 'mix = DRY + 0.9 * hall_wet + 0.85 * cath_wet\n'
assert a in master
master = master.replace(a, a + 'mix *= GAINENV[None, :]\n')
master = master.replace('for s in range(0, 300, 10):', 'for s in range(0, int(DUR), 10):')
out = head + hel + '\n\n' + cue + '\n\n' + master
open(dst, 'w', encoding='utf-8').write(out)
print('wrote', dst, len(out), 'chars, DUR', dur)

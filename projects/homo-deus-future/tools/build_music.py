#!/usr/bin/env python3
"""Build /data/hd/music.py for 《未来简史：人类之后，会是谁？》.

music.py = Film-1 instrument library (projects/sapiens-70000-years/music.py, everything before the
'harmony' marker, with a few constants patched) + tools/score.py (the new 234 s cue) + the Film-1
reverb/master stage (patched for the new length).
Usage: python3 tools/build_music.py [film1_music.py] [out_music.py]
"""
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else '/data/video/music.py'
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, '..', 'music.py')
txt = open(src, encoding='utf-8').read()

H = '# ------------------------------------------------------------------ harmony'
M = '# ================================================================== REVERB + MASTER'
assert H in txt and M in txt
head = txt[:txt.index(H)]
master = txt[txt.index(M):]

# new docstring
d0 = head.index('"""')
d1 = head.index('"""', d0 + 3) + 3
head = head[:d0] + '''"""Procedural score for 《未来简史：人类之后，会是谁？》.

234 s, 44.1 kHz, stereo. Pure numpy (no samples, no internet). Built by tools/build_music.py.
Sections (seconds) follow the picture edit in shotlist.json:
  0-30.4      opening : low electronic drone + cosmic shimmer, impact 13.0 (into the city), title 22.6
  30.4-72     ch 1    : intelligence - synth arps 96 BPM, sub pulse, electronic kit, strings
  72-121      ch 2    : redesigning life - strings/spiccato + celesta DNA motif, braam 106, brass 111+
  121-166.4   ch 3    : humans & machines - felt piano, pulse, low ostinato, 'u' choir, heartbeat
  166.4-205   ch 4    : new era - Eastern orchestral epic: taiko, guzheng, erhu, dizi, brass, choir; climax 197.8
  204.8-234   ending  : warm piano + choir, solo voice, resolve to Cadd9 at 228.2
Usage: python3 music.py [out.wav]
"""''' + head[d1:]


def rep(s, a, b, must=True):
    if a not in s:
        assert not must, 'missing: ' + a
        return s
    return s.replace(a, b)


head = rep(head, 'DUR = 300.0', 'DUR = 234.0')
head = rep(head, 'default_rng(70000)', 'default_rng(2047)', must=False)
head = rep(head, "'/data/video/out/score.wav'", "'/data/hd/out/score.wav'")
head = rep(head, '(33, 36, 38, 41, 43, 45, 46)', '(33, 36, 38, 40, 41, 43, 45)')
master = rep(master, 'fo = int(5 * SR)', 'fo = int(4.5 * SR)', must=False)
master = rep(master, 'for s in range(0, 300, 10):', 'for s in range(0, int(DUR), 10):')

score = open(os.path.join(HERE, 'score.py'), encoding='utf-8').read()
open(dst, 'w', encoding='utf-8').write(head + score + '\n\n' + master)
print('wrote', os.path.abspath(dst), len(head + score + master), 'chars')

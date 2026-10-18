"""music_v3.py = music_v2f.py with the v3 time warp applied at the note level (onsets + sustained durations)."""
import re
src = open('/data/v2f/music_v2f.py', encoding='utf-8').read()
def rep(a, b, n=1):
    global src
    c = src.count(a)
    assert c == n, (a, c)
    src = src.replace(a, b)
rep('import numpy as np, wave, sys, time\n',
    'import numpy as np, wave, sys, time\nsys.path.insert(0, "/data/v3")\nfrom warp import W, f_at, N_NEW\n')
rep('N_VIDEO = int(SR * DUR)\n',
    '# v3: the score is written in v1/user time (DUR = 284.125) and every onset / sustained duration goes through W(t)\n'
    'DUR_NEW = N_NEW / 24\nN_VIDEO = int(SR * DUR_NEW)\n')
rep(re.search(r'N = 12544000[^\n]*\n', src).group(0),
    'def _smooth7(n):\n    while True:\n        m = n\n        for p in (2, 3, 5, 7):\n            while m % p == 0:\n                m //= p\n'
    '        if m == 1:\n            return n\n        n += 1\n\n\nN = _smooth7(N_VIDEO)  # 7-smooth: keeps the long FFTs fast and small\n')
rep('    i0 = int(round(t0 * SR))\n', '    i0 = int(round(W(t0) * SR))\n')
rep('# ------------------------------------------------------------------ dsp helpers\n',
    'def S(t0, d):\n    """warped length of an event that lasts d seconds (v1 time) from t0"""\n    return W(t0 + d) - W(t0)\n\n\n'
    '# ------------------------------------------------------------------ dsp helpers\n')
rep("        bassgain=0.8, voices=4):\n", "        bassgain=0.8, voices=4):\n    dur = S(t0, dur)\n")
rep("def choir(t0, notes, dur, gain, att=1.6, rel=2.5, vowels=('a', 'o'), hall=0.25, cath=0.65, voices=3):\n",
    "def choir(t0, notes, dur, gain, att=1.6, rel=2.5, vowels=('a', 'o'), hall=0.25, cath=0.65, voices=3):\n    dur = S(t0, dur)\n")
rep("def ambience(t0, dur, gain, fin=3.0, fout=3.0, wind=1.0, shimmer=1.0):\n",
    "def ambience(t0, dur, gain, fin=3.0, fout=3.0, wind=1.0, shimmer=1.0):\n    dur = S(t0, dur)\n")
rep("def flute_phrase(t0, notes, beat, gain, pan=-0.25, rel=1.4):\n",
    "def flute_phrase(t0, notes, beat, gain, pan=-0.25, rel=1.4):\n    beat = beat * f_at(t0)\n")
rep("ensemble('saw', 38, 47,", "ensemble('saw', 38, S(20.5, 47),")
rep("ensemble('saw', 45, 47,", "ensemble('saw', 45, S(20.5, 47),")
rep("ensemble('saw', 26, 26,", "ensemble('saw', 26, S(200, 26),")
rep("place(swell(2.0), 68.0", "place(swell(S(68.0, 2.0)), 68.0")
rep("place(riser(6.0, 120, 3.0), 114.0", "place(riser(S(114.0, 6.0), 120, 3.0), 114.0")
rep("place(swell(2.0), 118.0", "place(swell(S(118.0, 2.0)), 118.0")
rep("place(noise_fx(2.0, 2000, 11000, 0.06, 0.9), 152.4", "place(noise_fx(S(152.4, 2.0), 2000, 11000, 0.06, 0.9), 152.4")
rep("place(riser(2.4, 160, 2.5), 165.6", "place(riser(S(165.6, 2.4), 160, 2.5), 165.6")
rep("place(riser(2.8, 160, 3.0), 174.8", "place(riser(S(174.8, 2.8), 160, 3.0), 174.8")
rep("place(noise_fx(10.5, 25, 220, 1.6, 4.0), 175.8", "place(noise_fx(S(175.8, 10.5), 25, 220, 1.6, 4.0), 175.8")
rep("place(riser(4.0, 150, 3.0), 248.0", "place(riser(S(248.0, 4.0), 150, 3.0), 248.0")
rep("place(brass_note(m, 5.8, att=0.5", "place(brass_note(m, S(t0, 5.8), att=0.5")
rep("place(brass_note(m, d, att=0.3, rel=0.8, swell=0.7), t0", "place(brass_note(m, S(t0, d), att=0.3, rel=0.8, swell=0.7), t0")
rep("brass_note(m, d * 0.95,", "brass_note(m, S(t, d) * 0.95,")
rep("brass_note(m - 12, d * 0.95,", "brass_note(m - 12, S(t, d) * 0.95,")
rep("place(brass_note(m, d, att=0.2, rel=1.2, swell=0.8), t0", "place(brass_note(m, S(t0, d), att=0.2, rel=1.2, swell=0.8), t0")
rep("place(brass_note(m, 6, att=1.5, rel=0.4, swell=1.0), t0", "place(brass_note(m, S(t0, 6), att=1.5, rel=0.4, swell=1.0), t0")
rep("brass_note(m, d * 0.96,", "brass_note(m, S(t, d) * 0.96,")
rep("brass_note(m - 12, d * 0.96,", "brass_note(m - 12, S(t, d) * 0.96,")
rep("for s in range(0, int(DUR), 10):", "for s in range(0, int(DUR_NEW), 10):")
open('/data/v3/music_v3.py', 'w', encoding='utf-8').write(src)
print('ok')

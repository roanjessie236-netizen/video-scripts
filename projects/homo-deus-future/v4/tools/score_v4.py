# ================================================================== FUTURE SCORE v4  (Homo Deus v4, shotlist DUR)
# Inserted by tools/build_music_v4.py between the Film-1 instrument library (+ tools/score.py helpers) and the
# reverb/master stage. Written directly in v4 picture time: every cue is read from engine/shotlist.json marks
# (line starts LL, word onsets W, shot starts SH, title, silence, chapter cards), so a re-timed edit re-scores itself.
import json as _json, os as _os
_SL = _json.load(open(_os.environ.get('SHOTLIST', '/data/hd/v4/engine/shotlist.json'), encoding='utf-8'))
MK = _SL['marks']
LL = {int(k): v for k, v in MK['L'].items()}
W = {int(k): v for k, v in MK['W'].items()}
SH = MK['shots']
TITLE, SIL, LIGHTS, GOD = MK['title'], MK['sil'], MK['lights'], MK['god']
CHC = MK['ch']
GAINENV = np.ones(N, np.float32)


def w(i, word):
    return next(t for x, t in W[i] if x == word)


def prog_at(t0, items):
    """[(dur_or_None, chord)] chained from t0; returns [(start, dur, chord)]."""
    out, t = [], t0
    for d, c in items:
        out.append((t, d, c))
        t += d
    return out


def chain(points, end):
    """[(start, chord)] + end -> [(start, dur, chord)]"""
    out = []
    for k, (s, c) in enumerate(points):
        e = points[k + 1][0] if k + 1 < len(points) else end
        out.append((s, e - s, c))
    return out


def mute(t0, t1, down=0.06, up=0.12):
    i0, i1 = int(t0 * SR), int(t1 * SR)
    a, b = int(down * SR), int(up * SR)
    GAINENV[i0:i0 + a] *= np.linspace(1, 0, a, dtype=np.float32)
    GAINENV[i0 + a:i1] = 0.0
    GAINENV[i1:i1 + b] *= np.linspace(0, 1, b, dtype=np.float32)


PP = [0, 1, 2, 3, 2, 1, 2, 3]

# ------------------------------------------------------------------ OPENING  cosmos -> earth -> city lights -> title
log('opening')
place(ensemble('saw', 33, TITLE + 1.0, p=1.6, voices=4, cents=8, vib=0.0, att=3.0, rel=2.5, width=0.9), 0.0, 0.2,
      hall=0.15, cath=0.5)
place(ensemble('saw', 45, TITLE, p=1.4, voices=3, cents=14, vib=0.0, att=4.0, rel=1.5, width=1.0), 0.0, 0.07,
      hall=0.1, cath=0.6)
ambience(0.0, TITLE + 3.5, 0.15, fin=2.5, fout=2.5, wind=0.45, shimmer=1.3)
for t in np.arange(1.25, TITLE - 0.3, 1.25):
    place(HEART, t, ramp(t, [(1.25, 0.07), (TITLE, 0.2)]), hall=0.1, cath=0.2)
for i, m in enumerate([69, 72, 76, 79, 81, 84, 88]):          # the city lights switch on
    celesta(LIGHTS + i * 0.34, m, 0.065, pan=-0.6 + 0.2 * i)
arp([(LIGHTS, TITLE - LIGHTS, 'Am9')], BEAT / 2, [(LIGHTS, 0.012), (TITLE, 0.045)], [0, 1, 2, 3, 2, 1, 2, 3],
    bright_pts=[(0, 0.5), (TITLE, 1.0)])
place(riser(2.8, 120.0, 3.2), TITLE - 2.8, 0.16, hall=0.2, cath=0.2)
impact(TITLE, 0.85, with_braam=True, notes=(29, 41, 48))     # title
OP = chain([(TITLE, 'Fmaj7'), (TITLE + 1.5, 'Gsus')], SH['famine'])
pad_prog(OP, [(TITLE, 0.13), (TITLE + 1.5, 0.12)], p=3.0, att=0.4, rel=1.4)
choir(TITLE, [64, 69, 72], SH['famine'] - TITLE, 0.06, att=0.8, rel=2.0, vowels=('o',))
arp(OP, BEAT / 2, [(TITLE, 0.04), (SH['famine'], 0.045)], [0, 2, 1, 3])

# ------------------------------------------------------------------ CH1a  the three old enemies (grim)
log('ch1')
T_F, T_P, T_W = w(3, '饥荒'), SH['plague'], SH['war']
T4 = SH['abundance']
G1 = chain([(SH['famine'], 'Am'), (T_F, 'F'), (T_P, 'Dm'), (T_W, 'E')], T4)
place(BOOM, SH['famine'], 0.3, hall=0.1, cath=0.3)
timp(SH['famine'], 33, 0.25)
pad_prog(G1, [(SH['famine'], 0.08), (T_W, 0.11)], p=2.0, att=0.9, rel=1.4, hall=0.35, cath=0.3)
str_line(SH['famine'], [(45, T_F - SH['famine']), (41, T_P - T_F), (38, T_W - T_P), (40, T4 - T_W)], 0.07)
ambience(SH['famine'], T4 - SH['famine'] + 1.0, 0.08, fin=1.0, fout=1.5, wind=0.8, shimmer=0.3)
for t, ch, g in [(T_F, 'F', 0.4), (T_P, 'Dm', 0.45), (T_W, 'E', 0.55)]:   # 饥荒 / 瘟疫 / 战争
    taiko(t, g, big=True)
    timp(t, TR[ch], 0.3)
    place(BOOM, t, 0.18 + 0.1 * (ch == 'E'), hall=0.1, cath=0.3)
for m in CH['E'][1:4]:                                         # brass stab on 战争
    place(brass_note(m, 1.0, att=0.05, rel=0.9, swell=0.2), T_W, 0.12, hall=0.4, cath=0.2)
for t in np.arange(T_W + 4 * BEAT / 2, T4 - 0.2, BEAT):          # war drums under 「三个敌人」
    taiko(t, ramp(t, [(T_W, 0.12), (T4, 0.2)]), pan=0.2 * np.sin(t))
place(swell(1.2), T4 - 1.2, 0.1, hall=0.3)

# ------------------------------------------------------------------ CH1b  today: abundance / old age / suicide (96 BPM)
T_LONE, T_SUG = SH['lonely'], SH['sugar']
P1 = [(T4 + 2.5 * k, 2.5, c) for k, c in enumerate(['Am', 'F', 'C', 'G', 'Am', 'F'])]
P1[-1] = (P1[-1][0], T_SUG - P1[-1][0], P1[-1][2])
impact(T4, 0.35)
arp(P1, BEAT / 2, [(T4, 0.03), (T_LONE, 0.045), (T_SUG, 0.04)], [0, 1, 2, 3, 1, 2, 3, 2],
    bright_pts=[(T4, 0.6), (T_LONE, 1.1), (T_SUG, 0.8)])
subpulse(P1, BEAT / 2, [(T4, 0.03), (T_LONE, 0.05)], T4, T_LONE)
beat_kit(T4 + 8 * BEAT, T_LONE - 0.05, [(T4 + 8 * BEAT, 0.09), (T_LONE, 0.13)])          # kick from L5
beat_kit(T_LONE, T_SUG - 0.1, [(T_LONE, 0.06), (T_SUG, 0.06)], kick=False)               # L6: the floor drops away
pad_prog(P1, [(T4, 0.06), (T_LONE, 0.08), (T_SUG, 0.09)], p=3.5, att=1.0, rel=0.5, hall=0.35, cath=0.15)
for t in np.arange(T_LONE, T_SUG - 0.2, 2 * BEAT):
    place(HEART, t, 0.06, hall=0.1, cath=0.2)
glitch(SH['oldage'] - 0.1, 0.5, 0.06, 2)

# ------------------------------------------------------------------ L7 cap  「如今，糖比火药更危险。」 cold drop
place(BOOM, T_SUG, 0.45, hall=0.1, cath=0.35)
place(subtone(28, 3.0), T_SUG, 0.18, hall=0.05)
place(METAL, T_SUG, 0.06, pan=0.2, hall=0.3, cath=0.4)
place(ensemble('saw', 76, SH['sunrise'] - T_SUG, p=1.2, voices=3, cents=16, vib=0.0, att=0.4, rel=1.5, width=1.0),
      T_SUG, 0.025, hall=0.2, cath=0.6)
place(ensemble('saw', 28, SH['sunrise'] - T_SUG, p=1.2, voices=3, cents=6, vib=0.0, att=0.1, rel=1.0, width=0.3),
      T_SUG, 0.07, hall=0.05)

# ------------------------------------------------------------------ L8-L9  new goals -> 神 (rising strings/choir)
T_S, T_I, T_B, T_D = SH['sunrise'], SH['immortality'], SH['bliss'], SH['divinity']
P8 = chain([(T_S, 'F'), ((T_S + T_I) / 2, 'G')], T_I)
pad_prog(P8, [(T_S, 0.08), (T_I, 0.12)], p=3.2, att=1.6, rel=1.2, hall=0.4, cath=0.3)
choir_prog(P8, [(T_S, 0.04), (T_I, 0.07)], att=1.8, rel=1.2)
str_line(T_S, [(69, 1.3), (72, 1.35), (74, 1.3), (76, T_I - T_S - 3.95)], 0.06)
arp(P8, BEAT / 2, [(T_S, 0.015), (T_I, 0.04)], [0, 2, 1, 3], bright_pts=[(T_S, 0.6), (T_I, 1.2)])
timp_roll(T_I - 1.8, 1.8, 43, 0.08, 0.4)
place(riser(1.8, 160.0, 2.6), T_I - 1.8, 0.12, hall=0.2)
P9 = chain([(T_I, 'Am'), (T_B, 'F'), (T_D, 'G'), (GOD, 'C')], SH['dna'])
for s, d, ch in P9[:3]:                                         # 长生不死 / 幸福快乐 / 化身为神
    taiko(s, 0.45, big=True)
    timp(s, TR[ch], 0.32)
pad_prog(P9, [(T_I, 0.12), (GOD, 0.15)], p=4.2, att=0.15, rel=1.6, hall=0.4, cath=0.25)
brass_prog(P9, 0.1)
choir_prog(P9, [(T_I, 0.07), (GOD, 0.12)], att=0.3, rel=2.0)
spic(P9, BEAT / 2, [(T_I, 0.05), (GOD, 0.07)], [0, 1, 2, 3], T_I, GOD)
impact(GOD, 1.0, with_braam=True, notes=(36, 48, 55))          # 神
choir(GOD, [m + 12 for m in CH['C'][3:]], SH['dna'] - GOD + 0.5, 0.06, att=0.2, rel=2.5, vowels=('a',))

# ------------------------------------------------------------------ CH2  redesigning life (strings + celesta DNA)
log('ch2')
C2 = CHC[1]
P2 = chain([(C2, 'Fmaj7'), (C2 + 5, 'C/E'), (C2 + 10, 'Dm'), (C2 + 15, 'Am'), (C2 + 20, 'F')], SH['upload'])
timp(C2, 41, 0.3)
place(BOOM, C2, 0.22, hall=0.1, cath=0.3)
for i, m in enumerate([72, 76, 79, 81, 84, 88]):
    celesta(C2 + 0.2 + i * 0.12, m, 0.05, pan=-0.5 + 0.2 * i)
pad_prog(P2, [(C2, 0.09), (C2 + 15, 0.12), (SH['upload'], 0.13)], p=3.8, att=1.2, rel=1.2, hall=0.4, cath=0.2)
for k, t in enumerate(np.arange(LL[10][0], LL[14][0], 1.25)):  # DNA helix motif
    for j, m in enumerate([81, 76, 72, 76] if k % 2 == 0 else [84, 79, 76, 79]):
        celesta(t + j * 0.156, m, 0.045, pan=(-0.5 if k % 2 == 0 else 0.5) * (1 - j / 3))
spic(P2, BEAT / 2, [(SH['lab'], 0.04), (LL[14][0], 0.065), (SH['upload'], 0.07)], [0, 2, 1, 3, 0, 2, 1, 2],
     SH['lab'], SH['upload'])
subpulse(P2, BEAT, [(SH['nanobots'], 0.03), (SH['upload'], 0.05)], SH['nanobots'], SH['upload'])
for t, m in [(SH['editing'], 38), (SH['hands'], 41), (SH['artlife'], 45)]:  # 改写基因 / 与机器融合 / 非有机生命
    timp(t, m, 0.26)
    taiko(t, 0.18, pan=0.2)
for t in (SH['nanobots'], SH['cellplanets']):                   # radial transitions
    place(noise_fx(2.0, 300, 4000, 1.5, 0.3), t - 1.5, 0.12, hall=0.2, cath=0.3)
choir_prog(P2, [(C2 + 15, 0.05), (C2 + 20, 0.08)], att=1.5, rel=1.5, t_lo=C2 + 14.9)
brass_prog(P2, 0.07, t_lo=C2 + 19.9)

# ------------------------------------------------------------------ 如果 x3 -> 「我们还是原来的自己吗？」
T_U, T_M = SH['upload'], SH['mirror']
PQ = chain([(T_U, 'Am'), (SH['ar'], 'F'), (SH['stationin'], 'Dm')], T_M)
pad_prog(PQ, [(T_U, 0.05), (T_M, 0.06)], p=2.2, att=0.8, rel=1.5, hall=0.4, cath=0.35)
for (s, d, ch), li in zip(PQ, (15, 16, 17)):
    t0 = LL[li][0]
    notes = [m + 12 for m in CH[ch][2:]]
    piano(t0, CH[ch][1], 0.09, pan=-0.1)
    for k in range(int((s + d - t0 - 0.2) / (BEAT / 2))):
        piano(t0 + (k + 1) * BEAT / 2, notes[PP[k % 8] % len(notes)], 0.06 * (1.0 if k % 2 == 0 else 0.8))
t = T_U + 0.3
while t < T_M - 0.2:                                            # accelerating heartbeat
    place(HEART, t, ramp(t, [(T_U, 0.08), (T_M, 0.18)]), hall=0.1, cath=0.2)
    t += ramp(t, [(T_U, 1.1), (T_M, 0.55)])
place(ensemble('saw', 88, CHC[2] - T_M, p=1.0, voices=2, cents=10, vib=0.0, att=0.8, rel=1.0, width=1.0), T_M,
      0.012, hall=0.2, cath=0.7)                                # near silence under L18
place(swell(1.0), CHC[2] - 1.0, 0.1, hall=0.3)

# ------------------------------------------------------------------ CH3  the intelligence revolution
log('ch3')
C3 = CHC[2]
T_H, T_BCI, T_ALG, T_AUT = SH['humanism'], SH['bci'], SH['algochoice'], SH['assistant']
P3 = chain([(C3, 'Am'), (C3 + 5, 'F'), (C3 + 10, 'C'), (C3 + 15, 'G')], T_H)
impact(C3, 0.6, with_braam=True, notes=(33, 45, 52))
arp(P3, BEAT / 2, [(C3, 0.035), (C3 + 11, 0.05), (T_H, 0.055)], [0, 1, 2, 3, 1, 2, 3, 2],
    bright_pts=[(C3, 0.6), (T_H, 1.2)])
subpulse(P3, BEAT / 2, [(SH['ainetwork'], 0.035), (T_H, 0.055)], SH['ainetwork'], T_H)
beat_kit(C3 + 10 * BEAT, T_H - 0.05, [(C3 + 10 * BEAT, 0.09), (T_H, 0.14)])
beat_kit(C3 + 18 * BEAT, T_H - 0.05, [(C3 + 18 * BEAT, 0.12), (T_H, 0.14)], kick=False, ticks=False, clap=True)
pad_prog(P3, [(C3, 0.06), (T_H, 0.09)], p=3.5, att=1.2, rel=0.8, hall=0.35, cath=0.15)
for k, t in enumerate([SH['ainetwork'], SH['datacenter'], SH['neurons'], SH['neurons2']]):
    glitch(t - 0.05, 0.6, 0.06, 30 + k)
for i, m in enumerate([88, 84, 81, 79, 76, 74, 72, 69]):     # 生命就是数据处理
    celesta(SH['neurons'] + 0.3 + i * 0.16, m, 0.04, pan=0.7 - 0.2 * i)
# humanism: warm strings, no beat
pad(T_H, T_BCI - T_H, 'Fmaj7', gain=0.11, p=2.6, att=0.6, rel=1.2, hall=0.4, cath=0.35)
str_line(T_H, [(69, 1.45), (72, 1.45), (76, T_BCI - T_H - 2.9)], 0.06)
choir(T_H, [64, 69, 72], T_BCI - T_H, 0.035, att=1.2, rel=1.2, vowels=('o',))
piano(T_H + 0.05, 53, 0.07, pan=-0.1)
# bci -> algorithm choices -> 权威
PB = chain([(T_BCI, 'Dm'), (T_ALG, 'Esus')], T_AUT)
glitch(T_BCI - 0.05, 0.5, 0.07, 40)
pad_prog(PB, [(T_BCI, 0.08), (T_AUT, 0.12)], p=3.6, att=0.4, rel=0.6)
arp(PB, BEAT / 2, [(T_BCI, 0.04), (T_ALG, 0.045)], [0, 1, 2, 3], t_hi=T_ALG)
arp(PB, BEAT / 4, [(T_ALG, 0.03), (T_AUT, 0.06)], [0, 1, 2, 3, 1, 2, 3, 2], bright_pts=[(T_ALG, 0.8), (T_AUT, 1.4)],
    t_lo=T_ALG)
subpulse(PB, BEAT / 2, [(T_BCI, 0.04), (T_AUT, 0.06)], T_BCI, T_AUT)
beat_kit(T_BCI, T_AUT - 0.1, [(T_BCI, 0.1), (T_AUT, 0.15)])
spic(PB, BEAT / 2, [(T_ALG, 0.04), (T_AUT, 0.07)], [0, 1, 2, 3], T_ALG, T_AUT)
timp_roll(T_AUT - 1.5, 1.5, 40, 0.1, 0.45)
place(riser(3.2, 160.0, 2.8), T_AUT - 3.2, 0.14, hall=0.2)
impact(T_AUT, 0.9, with_braam=True, notes=(33, 45, 52))      # 权威
T_EL, T_CL = SH['elevator'], SH['clinic']
PA = chain([(T_AUT, 'Am'), (T_EL, 'Esus'), (LL[27][0] + 2.1, 'E')], T_CL)
pad_prog(PA, [(T_AUT, 0.11), (T_EL, 0.09), (T_CL, 0.08)], p=3.2, att=0.3, rel=1.8, hall=0.4, cath=0.3)
arp(PA, BEAT / 2, [(T_AUT, 0.05), (T_EL, 0.035)], [0, 1, 2, 3, 1, 2, 3, 2], t_hi=T_EL)
subpulse(PA, BEAT / 2, [(T_AUT, 0.05), (T_EL, 0.04)], T_AUT, T_EL)
beat_kit(T_AUT + 2 * BEAT, T_EL - 0.1, [(T_AUT, 0.12), (T_EL, 0.1)])
spic(PA, BEAT / 2, [(T_EL, 0.04), (T_CL, 0.03)], [0, 1, 2, 1], T_EL, T_CL - 0.3, octave=-12)
choir_prog(PA, [(T_EL, 0.04), (T_CL, 0.05)], att=1.5, rel=2.0, vowels=('u',), t_lo=T_EL)
glitch(T_EL - 0.05, 0.7, 0.07, 41)

# ------------------------------------------------------------------ the 'useless class'  (sparse, human)
log('useless class')
T_DS = SH['dataism']
PI = chain([(T_CL, 'Am'), (SH['automation'], 'Fmaj7'), (SH['worker2'], 'C/E'), (SH['faces'], 'Dm'),
            (SH['divide'], 'Am'), (SH['castes'], 'F'), (SH['crowdwalk'], 'G'), (SH['toport'], 'Esus'),
            (SH['toport'] + 2.0, 'E')], T_DS)
impact(T_CL, 0.22, notes=(33, 45))
place(ensemble('saw', 33, T_DS - T_CL, p=1.4, voices=4, cents=8, vib=0.0, att=3.0, rel=3.0, width=0.9), T_CL, 0.09,
      hall=0.1, cath=0.5)
place(ensemble('saw', 45, 22.0, p=1.3, voices=3, cents=14, vib=0.0, att=5.0, rel=4.0, width=1.0), T_CL, 0.03,
      hall=0.1, cath=0.6)
ambience(T_CL, T_DS - T_CL, 0.065, fin=2.5, fout=2.0, wind=0.3, shimmer=0.9)
pad_prog(PI, [(T_CL, 0.04), (SH['crowdwalk'], 0.05), (T_DS, 0.07)], p=2.0, att=2.2, rel=2.2, hall=0.4, cath=0.35)
KEEP = [1, 0, 1, 1, 0, 1, 0, 1]
for s, d, ch in PI:
    e = s + d
    notes = [m + 12 for m in CH[ch][2:]]
    piano(s + 0.05, CH[ch][1], 0.085, pan=-0.1)
    dense = s >= SH['crowdwalk'] - 0.01                        # the crowd sets off: the piano walks on every beat
    step = BEAT if dense else 2 * BEAT
    k, t = 0, s + step
    while t < e - 0.3:
        if dense or KEEP[k % 8]:
            piano(t, notes[PP[k % 8] % len(notes)], 0.065 * (1.0 if k % 2 == 0 else 0.8))
        t += step
        k += 1
glitch(SH['automation'] - 0.05, 0.6, 0.05, 21)                 # machine pulse under automation
subpulse(PI, BEAT / 2, [(SH['automation'], 0.016), (SH['worker'], 0.028), (SH['worker2'], 0.01)],
         SH['automation'], SH['worker2'])
for t in np.arange(SH['automation'], SH['worker2'], BEAT):
    place(SHAKER, t, 0.05, pan=0.3, hall=0.1)
choir_prog(PI, [(SH['faces'], 0.035), (SH['castes'], 0.05), (T_DS, 0.065)], att=2.4, rel=2.4, vowels=('u',),
           t_lo=SH['faces'] - 0.1)
T_NOT = w(31, '绝不')
piano(T_NOT, 76, 0.06, pan=0.2)                                # 「绝不意味着人失去了价值」
piano(T_NOT + 1.25, 79, 0.05, pan=0.25)
for t in np.arange(SH['divide'], SH['crowdwalk'], 2 * BEAT):   # the divided species: slow, uneasy heartbeat
    place(HEART, t, ramp(t, [(SH['divide'], 0.06), (SH['crowdwalk'], 0.11)]), hall=0.1, cath=0.2)
timp(SH['toport'] + 2.0, TR['E'], 0.1)
place(riser(1.6, 140.0, 2.2), T_DS - 1.6, 0.06, hall=0.3)

# ------------------------------------------------------------------ CH4a  dataism: eerie data pads + celesta
log('ch4')
T_DG, T_MT, T_UG, T_FE = SH['datagalaxy'], SH['metro'], SH['underground'], SH['futureearth']
PD = chain([(T_DS, 'Am9'), (T_DG, 'Fmaj7'), (T_UG, 'Esus')], T_FE)
impact(T_DS, 0.3)
glitch(T_DS - 0.05, 0.8, 0.07, 50)
for i, m in enumerate([88, 84, 81, 79, 76, 74, 72, 69, 64]):
    celesta(T_DS + 0.1 + i * 0.13, m, 0.045, pan=0.7 - 0.17 * i)
pad_prog(PD, [(T_DS, 0.06), (T_UG, 0.09)], p=2.8, att=2.0, rel=1.2, hall=0.4, cath=0.4)
arp(PD, BEAT / 2, [(T_DS, 0.02), (T_DG, 0.03), (T_FE, 0.045)], [0, 1, 2, 3, 1, 2, 3, 2],
    bright_pts=[(T_DS, 0.5), (T_FE, 1.0)])
subpulse(PD, BEAT / 2, [(T_DG, 0.02), (T_FE, 0.04)], T_DG, T_FE)
for rep in (T_DG, T_DG + 2.0):                                 # the universe as data flow
    for i, m in enumerate([88, 84, 81, 79, 76, 74, 72, 69]):
        celesta(rep + i * 0.16, m, 0.04, pan=0.7 - 0.2 * i)
glitch(T_MT - 0.05, 0.6, 0.05, 51)
for m in (40, 47, 52):                                         # 正在过时的算法: low brass
    place(brass_note(m, T_FE - T_UG, att=0.6, rel=1.2, swell=0.9), T_UG, 0.08, hall=0.4, cath=0.3)
timp_roll(T_FE - 1.3, 1.3, 40, 0.1, 0.5)
place(riser(2.2, 160.0, 2.6), T_FE - 2.2, 0.13, hall=0.2)

# ------------------------------------------------------------------ CH4b  epic montage -> hard cut to silence
T_ST = SH['starship']
PE = chain([(T_FE, 'F'), (SH['moonbase'], 'G'), (SH['marscity'], 'Am'), (T_ST, 'E')], SIL)
impact(T_FE, 0.75, with_braam=True, notes=(29, 41, 48))
zheng_gliss(T_FE, 57, 86, 0.07)
pad_prog(PE, [(T_FE, 0.16), (T_ST, 0.22)], p=4.5, att=0.3, rel=1.0, hall=0.4, cath=0.2)
choir_prog(PE, [(T_FE, 0.08), (T_ST, 0.15)], att=0.4, rel=1.2)
choir_prog(PE, [(SH['marscity'], 0.08), (T_ST, 0.1)], att=0.3, rel=1.2, up=12, t_lo=SH['marscity'] - 0.01)
brass_prog(PE, 0.11, t_hi=T_ST)
brass_prog(PE, 0.15, t_lo=T_ST - 0.01)
timp_prog(PE, 0.3)
E3 = [(72, 2), (74, 2), (76, 2), (79, 2), (81, 3), (83, 2)]
lead(T_FE, E3, BEAT, 0.17)
flute_phrase(T_FE, [(m + 12, b) for m, b in E3], BEAT, 0.055, pan=-0.3)
zheng_arp(PE, BEAT / 2, [(T_FE, 0.05), (SIL, 0.07)], T_FE, SIL)
spic(PE, BEAT / 2, [(T_FE, 0.06), (SIL, 0.09)], [0, 1, 2, 3], T_FE, SIL)
for t in (T_FE, SH['moonbase'], SH['marscity']):
    taiko_bar(t, ramp(t, [(T_FE, 0.35), (SH['marscity'], 0.45)]))
k = 0
for t in np.arange(T_ST, SIL - 0.05, 0.125):                     # taiko roll into the cut
    taiko(t, ramp(t, [(T_ST, 0.22), (SIL, 0.6)]), pan=0.25 * (-1) ** k)
    k += 1
timp_roll(T_ST, SIL - T_ST, 40, 0.2, 0.7)
place(riser(SIL - T_ST + 0.2, 160.0, 3.0), T_ST - 0.2, 0.17, hall=0.2)
place(CRASH, T_ST, 0.12, hall=0.3, cath=0.3)
mute(SIL, SH['spaceport'] - 0.1)                               # 「是否仍然知道，如何成为人？」 in silence

# ------------------------------------------------------------------ after the silence -> ending
log('ending')
T_SP, T_CH = SH['spaceport'], SH['child']
choir(T_SP, [57, 60, 64], T_CH - T_SP, 0.05, att=2.5, rel=1.8, vowels=('o',))
pad(T_SP, T_CH - T_SP, 'Am', gain=0.04, p=2.0, att=2.5, rel=1.5, hall=0.4, cath=0.4, bassgain=0.5)
celesta(w(41, '神人'), 84, 0.035, pan=0.3)
piano(w(41, '神人'), 72, 0.05)
P5 = chain([(T_CH, 'Fmaj7'), (207.7, 'C/E'), (212.1, 'Dm'), (216.1, 'Gsus'), (219.1, 'G'), (222.1, 'Fmaj7'),
            (LL[48][0], 'Cadd9')], DUR)
pad_prog(P5, [(T_CH, 0.07), (LL[48][0], 0.06)], p=2.2, att=1.6, rel=2.2, hall=0.35, cath=0.35, bassgain=0.5)
ambience(T_CH, DUR - T_CH, 0.07, fin=3.0, fout=5.0, wind=0.2, shimmer=1.2)
for s, d, ch in P5[:-1]:
    e = s + d
    notes = [m + 12 for m in CH[ch][2:]]
    piano(s, CH[ch][1], 0.1, pan=-0.1)
    step = BEAT if s < 216.0 else BEAT / 2
    g = 0.10 if s < 216.0 else 0.085
    k = 0
    while s + step * (k + 1) < e - 0.05:
        piano(s + step * (k + 1), notes[PP[k % 8]], g * (1.0 if k % 2 == 0 else 0.8))
        k += 1
choir_prog(P5, [(212, 0.07), (222, 0.11)], att=2.0, rel=2.0, t_lo=212.0, t_hi=LL[48][0] - 0.1)
T_E = LL[48][0]
choir(T_E, CH['Cadd9'][2:], 6.0, 0.13, att=1.5, rel=4.0)
for i, m in enumerate([48, 55, 62, 64, 67, 72]):
    piano(T_E + 0.09 * i, m, 0.1, pan=-0.3 + 0.12 * i)
piano(T_E + 0.6, 76, 0.08)
piano(T_E + 1.7, 79, 0.07)
for li in (44, 45, 46):                                          # the three questions
    celesta(LL[li][0] - 0.1, 88, 0.035, pan=0.4)
    celesta(LL[li][0] + 0.2, 84, 0.028, pan=0.2)
for t, m, d in [(216.2, 76, 4.0), (220.2, 74, 2.3), (222.5, 74, 2.5), (225.0, 72, 3.0), (228.0, 76, 6.0)]:
    lead(t, [(m, d)], 1.0, 0.05, kind='u', p=4.0, vibd=0.006, glide=0.05, pan=0.0, rel=2.0, cath=0.9)
T_EC = MK['endcard']
celesta(T_EC, 84, 0.06, pan=-0.2)                               # end card chime
celesta(T_EC + 0.09, 91, 0.04, pan=0.2)
piano(T_EC, 72, 0.06)

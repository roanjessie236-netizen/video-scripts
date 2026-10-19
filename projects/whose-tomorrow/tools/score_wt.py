# ================================================================== SCORE 《明天属于谁》 (shotlist DUR)
# Inserted by tools/build_music_wt.py between the Film-1 instrument library (+ homo-deus tools/score.py helpers) and
# the reverb/master stage. Every cue is read from engine/shotlist.json marks (line starts LL, word onsets W, shot
# starts SH), so a re-timed edit re-scores itself.
# Arc: rain + piano (1930) -> machine pulse -> title -> frame drums & flute (deep past) -> industrial hammers ->
# electronic pulse (AI) -> sparse piano (paradox) -> tension & flood -> water resolves (Dujiangyan) -> cold digital
# (cloud lords) -> warm I-V-vi-IV turn (shared future) -> near-silence -> march -> choir & brass resolution.
import json as _json, os as _os
_SL = _json.load(open(_os.environ.get('SHOTLIST', '/data/wt/engine/shotlist.json'), encoding='utf-8'))
MK = _SL['marks']
LL = {int(k): v for k, v in MK['L'].items()}
W = {int(k): v for k, v in MK['W'].items()}
SH = MK['shots']
TITLE, SIL = MK['title'], MK['sil']
CHC = MK['ch']
GAINENV = np.ones(N, np.float32)
np.random.seed(2026)


def w(i, word):
    return next(t for x, t in W[i] if x == word)


def chain(points, end):
    keep, nxt = [], end          # v2: drop chord points squeezed out by a tighter edit (keep the later harmony)
    for s_, c_ in reversed(points):
        if s_ < nxt - 0.3:
            keep.append((s_, c_))
            nxt = s_
    points = keep[::-1]
    out = []
    for k, (s, c) in enumerate(points):
        e = points[k + 1][0] if k + 1 < len(points) else end
        assert e - s > 0.05, ('bad chord span', points, end)
        out.append((s, e - s, c))
    return out


def dip(t0, t1, g, fade=0.8):
    """multiply the music by g between t0 and t1 (with fades)"""
    i0, i1, f = int(t0 * SR), int(t1 * SR), int(fade * SR)
    GAINENV[i0:i0 + f] *= np.linspace(1, g, f, dtype=np.float32)
    GAINENV[i0 + f:i1 - f] *= g
    GAINENV[i1 - f:i1] *= np.linspace(g, 1, f, dtype=np.float32)


def frame(t, g, hi=False, pan=0.0):
    place((FD_HI if hi else FD_LO)[int(t * 7) % 2], t, g, pan=pan, hall=0.3, cath=0.1)


def piano_walk(prog, step, g, keep=None, pat=None):
    pat = pat or [0, 1, 2, 3, 2, 1, 2, 3]
    for s, d, ch in prog:
        notes = [m + 12 for m in CH[ch][2:]]
        piano(s + 0.03, CH[ch][1], g * 1.25, pan=-0.1)
        k, t = 0, s + step
        while t < s + d - 0.25:
            if keep is None or keep[k % len(keep)]:
                piano(t, notes[pat[k % len(pat)] % len(notes)], g * (1.0 if k % 2 == 0 else 0.8))
            t += step
            k += 1


# ------------------------------------------------------------------ PROLOGUE  1930 study (rain, piano) -> machines
log('prologue')
T_RB, T_DC, T_OT, T_MC = SH['robotarms'], SH['datacenter'], SH['overtime'], SH['machinecity']
ambience(0.0, T_RB + 1.0, 0.09, fin=1.5, fout=1.5, wind=0.15, shimmer=0.4)
for t in np.arange(0.2, T_RB, 0.031):                            # rain on the window
    if np.random.rand() < 0.55:
        place(SHAKER, t, 0.008 + 0.01 * np.random.rand(), pan=np.random.uniform(-0.8, 0.8), hall=0.2)
P0 = chain([(0.6, 'Am'), (LL[1][0] + 2.1, 'F'), (LL[2][0] - 0.3, 'C')], T_RB)
piano_walk(P0, 2 * BEAT, 0.07, keep=[1, 1, 0, 1])
pad_prog(P0, [(0.6, 0.03), (T_RB, 0.05)], p=2.0, att=2.0, rel=1.5, hall=0.4, cath=0.3)
for i, t in enumerate(np.arange(LL[1][0] + 0.1, LL[1][1], 0.21)):   # typewriter keys under Keynes
    if i % 5 != 4:
        place(METAL, t, 0.004, pan=0.3, hall=0.05)
# machines: pulse enters on 机器
P0b = chain([(T_RB, 'Am'), (T_DC, 'F'), (T_OT, 'Dm'), (T_MC, 'Esus'), (T_MC + 2.6, 'E')], TITLE)
impact(T_RB, 0.25)
arp(P0b, BEAT / 2, [(T_RB, 0.025), (T_DC, 0.04), (T_MC, 0.05)], [0, 1, 2, 3, 1, 2, 3, 2],
    bright_pts=[(T_RB, 0.5), (T_MC, 1.1)])
subpulse(P0b, BEAT / 2, [(T_RB, 0.025), (T_MC, 0.05)], T_RB, TITLE - 0.3)
beat_kit(T_DC, T_OT - 0.1, [(T_DC, 0.06), (T_OT, 0.08)], kick=False)
for t in np.arange(T_OT, T_MC, 2 * BEAT):                        # 我们却并没有因此变得轻松
    place(HEART, t, 0.07, hall=0.1, cath=0.2)
pad_prog(P0b, [(T_RB, 0.05), (T_MC, 0.1)], p=3.0, att=1.0, rel=1.0, hall=0.35, cath=0.25)
choir_prog(P0b, [(T_MC, 0.04), (TITLE, 0.08)], att=1.5, rel=1.5, vowels=('u',), t_lo=T_MC - 0.1)
glitch(T_DC - 0.05, 0.5, 0.05, 3)
place(BOOM, T_MC, 0.25, hall=0.1, cath=0.3)
timp_roll(TITLE - 2.4, 2.4, 40, 0.06, 0.4)
place(riser(3.0, 120.0, 3.2), TITLE - 3.0, 0.15, hall=0.2, cath=0.2)
impact(TITLE, 0.9, with_braam=True, notes=(29, 41, 48))         # title
OP = chain([(TITLE, 'Fmaj7'), (TITLE + 1.6, 'Gsus')], SH['cave'] + 1.0)
pad_prog(OP, [(TITLE, 0.13), (SH['cave'], 0.08)], p=3.0, att=0.4, rel=1.6)
choir(TITLE, [64, 69, 72], SH['cave'] + 1.0 - TITLE, 0.06, att=0.8, rel=2.2, vowels=('o',))

# ------------------------------------------------------------------ CH1  the deep past: frame drums, flute, zheng
log('ch1')
C1 = SH['cave']
T_CF, T_WH, T_ZG, T_STM, T_TX = SH['campfire'], SH['wheat'], SH['ziggurat'], SH['steam'], SH['textile']
ambience(C1, T_STM - C1, 0.08, fin=2.0, fout=0.5, wind=0.7, shimmer=0.2)
place(ensemble('saw', 33, T_STM - C1, p=1.4, voices=4, cents=7, vib=0.0, att=3.0, rel=1.0, width=0.9), C1, 0.1,
      hall=0.1, cath=0.5)                                           # A drone under the ancient world
timp(CHC[0] + 0.1, 33, 0.25)
place(BOOM, CHC[0] + 0.1, 0.18, hall=0.1, cath=0.3)
for k, t in enumerate(np.arange(T_CF - 4 * BEAT, T_ZG, BEAT / 2)):   # frame drums (campfire -> wheat)
    pos = k % 8
    if pos in (0, 3, 6):
        frame(t, ramp(t, [(T_CF - 4 * BEAT, 0.05), (T_CF, 0.12), (T_ZG, 0.15)]), pan=-0.2)
    elif pos in (2, 5, 7):
        frame(t, ramp(t, [(T_CF, 0.04), (T_ZG, 0.07)]), hi=True, pan=0.25)
F1 = [(69, 3), (72, 1), (74, 2), (76, 2), (74, 1), (72, 1), (69, 4), (67, 2), (69, 4)]
flute_phrase(LL[7][0] - 0.3, F1, BEAT / 2 * 1.0 + 0.0, 0.06, pan=-0.25)      # the storyteller's tune
P1 = chain([(T_WH, 'Am'), (T_WH + 1.6, 'G'), (T_ZG, 'F'), (T_ZG + 2.2, 'E')], T_STM)
zheng_arp(P1, BEAT / 2, [(T_WH, 0.05), (T_ZG, 0.06)], T_WH, T_STM - 0.3)
pad_prog(P1, [(T_WH, 0.05), (T_ZG, 0.08)], p=2.4, att=1.0, rel=0.8, hall=0.35, cath=0.3)
for t in (T_ZG, T_ZG + 4 * BEAT):                               # 粮仓、私有财产、阶级和国家: the state arrives
    taiko(t, 0.3, big=True)
for m in (40, 47, 52):
    place(brass_note(m, T_STM - T_ZG, att=0.5, rel=0.6, swell=0.8), T_ZG, 0.06, hall=0.4, cath=0.3)
timp(w(9, '阶级'), 40, 0.2)
timp(w(9, '国家'), 40, 0.26)
# industrial revolution: hammers on the beat
PI = chain([(T_STM, 'Am'), (T_TX, 'F'), (T_TX + 2.4, 'Dm')], SH['quern'])
impact(T_STM, 0.55, with_braam=True, notes=(33, 45, 52))
place(noise_fx(2.4, 200, 3000, 0.05, 1.1), T_STM, 0.05, hall=0.3)   # steam hiss
for k, t in enumerate(np.arange(T_STM + BEAT, SH['quern'] - 0.2, BEAT / 2)):
    if k % 2 == 0:
        place(METAL, t, ramp(t, [(T_STM, 0.03), (T_TX, 0.045)]), pan=0.3 * (-1) ** (k // 2), hall=0.2, cath=0.2)
    if k % 4 == 0:
        taiko(t, 0.14, pan=-0.15)
spic(PI, BEAT / 2, [(T_STM, 0.05), (SH['quern'], 0.06)], [0, 1, 2, 1], T_STM, SH['quern'] - 0.1, octave=-12)
pad_prog(PI, [(T_STM, 0.08), (SH['quern'], 0.07)], p=3.0, att=0.3, rel=1.2, hall=0.35, cath=0.2)
timp_prog(PI, 0.2)
# Marx: 手推磨 / 蒸汽磨  (quiet piano, then the steam mill hits)
T_Q, T_SM = SH['quern'], MK['steammill']
pad(T_Q, T_SM - T_Q, 'Am', gain=0.05, p=2.0, att=0.8, rel=0.6, hall=0.4, cath=0.4)
for k, (dt, m) in enumerate([(0.0, 57), (0.9, 60), (1.8, 64), (2.7, 62)]):
    piano(LL[12][0] + 0.9 + dt, m, 0.07)
impact(T_SM, 0.5)
timp(T_SM, 41, 0.28)
place(METAL, T_SM, 0.05, hall=0.3, cath=0.3)
PM = chain([(T_SM, 'F'), (T_SM + 2.0, 'G')], SH['hm_a'])
pad_prog(PM, [(T_SM, 0.09), (SH['hm_a'], 0.1)], p=3.2, att=0.2, rel=1.0, hall=0.35, cath=0.25)
for t in np.arange(T_SM + BEAT, SH['hm_a'] - 0.2, BEAT):
    place(METAL, t, 0.02, pan=0.25, hall=0.2)
# the diagram lights up tier by tier
T_HA, T_HB = SH['hm_a'], SH['hm_b']
PH = chain([(T_HA, 'C'), (T_HB, 'G'), (T_HB + 1.6, 'Am')], SH['campfire2'])
pad_prog(PH, [(T_HA, 0.08), (SH['campfire2'], 0.09)], p=2.8, att=0.6, rel=1.4, hall=0.4, cath=0.3)
for i, m in enumerate([60, 64, 67]):
    celesta(T_HA + 0.2 + i * 0.25, m + 12, 0.045, pan=-0.3 + 0.3 * i)
for i, m in enumerate([67, 71, 74, 79]):
    celesta(T_HB + 0.1 + i * 0.22, m + 12, 0.045, pan=-0.3 + 0.2 * i)
choir_prog(PH, [(T_HB, 0.04), (SH['campfire2'], 0.06)], att=1.0, rel=1.5, vowels=('o',), t_lo=T_HB - 0.1)
# Harari's stories (flute callback) -> who labours, who owns (low brass, tension)
T_C2, T_OW, T_OW2 = SH['campfire2'], SH['owner'], SH['owner2']
ambience(T_C2, T_OW - T_C2 + 0.5, 0.06, fin=0.8, fout=0.8, wind=0.6, shimmer=0.3)
flute_phrase(T_C2 + 0.4, [(69, 3), (72, 1), (74, 2), (76, 4), (74, 2), (72, 4)], BEAT / 2, 0.05, pan=-0.2)
for k, t in enumerate(np.arange(T_C2, T_OW, BEAT)):
    frame(t, 0.06 if k % 2 == 0 else 0.035, hi=k % 2 == 1)
PO = chain([(T_C2, 'Am'), (T_C2 + 2.5, 'F'), (T_OW, 'Dm'), (T_OW + 2.4, 'Esus'), (T_OW2, 'E')], SH['aiengine'])
pad_prog(PO, [(T_C2, 0.06), (T_OW, 0.08), (SH['aiengine'], 0.1)], p=3.0, att=1.0, rel=0.6, hall=0.4, cath=0.3)
for m in (38, 45, 50):
    place(brass_note(m, T_OW2 - T_OW, att=0.6, rel=0.4, swell=0.9), T_OW, 0.07, hall=0.4, cath=0.3)
str_line(T_OW, [(62, 1.2), (64, 1.2), (65, T_OW2 - T_OW - 2.4)], 0.05)
for t in np.arange(T_OW, T_OW2, BEAT):
    place(HEART, t, ramp(t, [(T_OW, 0.06), (T_OW2, 0.12)]), hall=0.1, cath=0.2)
timp(w(15, '谁'), 40, 0.18)
timp(T_OW2, 40, 0.3)
taiko(T_OW2, 0.3, big=True)

# ------------------------------------------------------------------ CH2  the new steam engine: electronic pulse
log('ch2')
C2 = SH['aiengine']
T_AG, T_AN, T_AU, T_EO = SH['aigrid'], SH['ainetwork'], SH['automation'], SH['emptyoffice']
T_SW, T_SN, T_MT, T_SC, T_HU = SH['switchboard'], SH['station'], SH['metro'], SH['scaffold'], SH['humanoids']
T_E3 = SH['worker']
place(riser(1.6, 150.0, 2.6), C2 - 1.6, 0.12, hall=0.2)
impact(C2, 0.7, with_braam=True, notes=(33, 45, 52))
glitch(C2 - 0.05, 0.8, 0.07, 11)
P2 = chain([(C2, 'Am'), (C2 + 4 * BEAT, 'F'), (MK['engine'], 'C'), (T_AG, 'G'), (T_AG + 4 * BEAT, 'Am'),
            (T_AN, 'F'), (T_AU, 'Dm'), (T_EO, 'Esus')], T_SW)
arp(P2, BEAT / 2, [(C2, 0.03), (T_AG, 0.05), (T_SW, 0.055)], [0, 1, 2, 3, 1, 2, 3, 2],
    bright_pts=[(C2, 0.6), (T_AU, 1.2)])
subpulse(P2, BEAT / 2, [(C2, 0.03), (T_AG, 0.05)], C2, T_SW - 0.2)
beat_kit(T_AG, T_SW - 0.15, [(T_AG, 0.09), (T_EO, 0.13)])
pad_prog(P2, [(C2, 0.07), (T_SW, 0.09)], p=3.4, att=0.8, rel=0.8, hall=0.35, cath=0.15)
impact(MK['engine'], 0.45)                                      # 「蒸汽机」
for i, m in enumerate([76, 79, 81, 84, 88]):
    celesta(T_AG + 0.1 + i * 0.12, m, 0.04, pan=-0.5 + 0.25 * i)
for k, t in enumerate([T_AN, T_AU, T_EO]):
    glitch(t - 0.05, 0.5, 0.06, 12 + k)
# old jobs vanish (switchboard: the beat drops out, a lonely retro piano) -> new jobs (station / metro)
place(METAL, T_SW, 0.03, hall=0.4, cath=0.4)
pad(T_SW, T_SN - T_SW, 'Dm', gain=0.05, p=2.0, att=0.4, rel=0.8, hall=0.4, cath=0.3)
for k, m in enumerate([62, 65, 69, 65, 62, 60]):
    piano(T_SW + 0.2 + k * BEAT, m, 0.06)
P2b = chain([(T_SN, 'F'), (T_MT, 'C'), (T_MT + 4 * BEAT, 'G'), (T_MT + 8 * BEAT, 'Am'), (LL[21][0], 'F'),
             (T_SC + 4 * BEAT, 'Dm'), (T_HU, 'Am'), (T_HU + 4 * BEAT, 'Esus'), (T_E3 - 2.2, 'E')], T_E3)
impact(T_SN, 0.3)
arp(P2b, BEAT / 2, [(T_SN, 0.04), (T_MT, 0.055), (T_HU, 0.06)], [0, 1, 2, 3, 1, 2, 3, 2],
    bright_pts=[(T_SN, 0.8), (T_HU, 1.3)], t_hi=T_E3 - 0.3)
subpulse(P2b, BEAT / 2, [(T_SN, 0.04), (T_HU, 0.06)], T_SN, T_E3 - 0.3)
beat_kit(T_MT, T_E3 - 0.3, [(T_MT, 0.12), (T_HU, 0.15)])
beat_kit(T_MT + 8 * BEAT, T_E3 - 0.3, [(T_MT, 0.1), (T_HU, 0.13)], kick=False, ticks=False, clap=True)
pad_prog(P2b, [(T_SN, 0.07), (T_SC, 0.1), (T_E3, 0.11)], p=3.4, att=0.6, rel=1.0, hall=0.35, cath=0.2)
brass_prog(P2b, 0.07, t_lo=T_SC - 0.1)
spic(P2b, BEAT / 2, [(T_HU, 0.05), (T_E3, 0.07)], [0, 1, 2, 3], T_HU, T_E3 - 0.3)
glitch(T_HU - 0.05, 0.7, 0.07, 16)
for t in np.arange(T_HU, T_E3 - 0.3, BEAT):                      # robots: metallic steps
    place(METAL, t, 0.012, pan=0.35 * np.sin(t * 3), hall=0.2)
timp_roll(T_E3 - 1.8, 1.8, 40, 0.08, 0.45)
place(riser(2.4, 160.0, 2.8), T_E3 - 2.4, 0.13, hall=0.2)

# ------------------------------------------------------------------ CH3  the paradox: sparse piano, heartbeat
log('ch3')
C3 = T_E3
T_W2, T_LO, T_PX, T_DV, T_CO = SH['worker2'], SH['lonely'], SH['paradox'], SH['divide'], SH['conflict']
impact(C3, 0.35, notes=(33, 45))
place(ensemble('saw', 33, T_CO - C3, p=1.4, voices=4, cents=8, vib=0.0, att=2.5, rel=1.5, width=0.9), C3, 0.08,
      hall=0.1, cath=0.5)
ambience(C3, T_CO - C3, 0.06, fin=2.0, fout=1.5, wind=0.3, shimmer=0.8)
P3 = chain([(C3, 'Am'), (T_W2, 'Fmaj7'), (T_LO, 'C/E'), (SH['v2_scaffold'], 'Am'), (SH['v2_lockedgate'], 'F'),
            (SH['v2_lockedgate'] + 2.6, 'G'), (T_PX, 'Dm'), (T_PX + 2.4, 'Am'), (T_DV, 'F'),
            (T_DV + 2.5, 'Esus')], T_CO)
pad_prog(P3, [(C3, 0.04), (T_CO, 0.06)], p=2.0, att=2.0, rel=2.0, hall=0.4, cath=0.35)
piano_walk(P3, 2 * BEAT, 0.065, keep=[1, 0, 1, 1, 0, 1, 0, 1])
choir_prog(P3, [(T_PX, 0.03), (T_CO, 0.05)], att=2.0, rel=2.0, vowels=('u',), t_lo=T_PX - 0.1)
piano(w(26, '堆积如山'), 81, 0.045, pan=0.3)
piano(w(26, '收入'), 76, 0.05, pan=0.2)
for t in np.arange(T_DV, T_CO, 2 * BEAT):
    place(HEART, t, ramp(t, [(T_DV, 0.06), (T_CO, 0.1)]), hall=0.1, cath=0.2)
# 矛盾: forces race ahead (rising arp), relations stand still (one stuck low note)
T_F, T_R = w(28, '生产力'), w(28, '生产关系')
T_LU = SH['luddites']
PC = chain([(T_CO, 'Am'), (T_F, 'F'), (T_F + 1.0, 'G'), (T_R, 'Esus'), (T_R + 1.4, 'E')], T_LU)
impact(T_CO + 0.3, 0.3)
pad_prog(PC, [(T_CO, 0.06), (T_LU, 0.09)], p=3.0, att=0.6, rel=0.6, hall=0.4, cath=0.3)
arp(PC, BEAT / 4, [(T_F, 0.02), (T_R, 0.06)], [0, 1, 2, 3, 1, 2, 3, 2], bright_pts=[(T_F, 0.6), (T_R, 1.5)],
    t_lo=T_F, t_hi=T_LU - 0.1)
for t in np.arange(T_R, T_LU - 0.1, BEAT / 2):                  # 原地踏步: the stuck note
    place(spic_note(40), t, 0.07, pan=-0.2, hall=0.2)
timp_roll(T_LU - 1.4, 1.4, 40, 0.06, 0.35)
# Luddites / sea ban / flood -> Dujiangyan
T_HJ, T_FL, T_DJ = SH['haijin'], SH['flood'], SH['dujiangyan']
T_SMASH = MK['smash']
PL = chain([(T_LU, 'Am'), (T_SMASH, 'Dm'), (T_HJ, 'Am'), (T_HJ + 1.9, 'F'), (T_FL, 'Dm'), (T_FL + 1.3, 'E')], T_DJ)
pad_prog(PL, [(T_LU, 0.08), (T_FL, 0.12)], p=3.4, att=0.3, rel=0.8, hall=0.35, cath=0.25)
for t in np.arange(T_LU, T_HJ, BEAT):
    taiko(t, ramp(t, [(T_LU, 0.12), (T_HJ, 0.2)]), pan=0.2 * np.sin(t))
for k in range(3):                                             # 砸毁
    place(METAL, T_SMASH + k * BEAT / 2, 0.08, pan=0.3 * (-1) ** k, hall=0.3, cath=0.2)
    taiko(T_SMASH + k * BEAT / 2, 0.35, big=k == 0)
place(CRASH, T_SMASH, 0.08, hall=0.3, cath=0.3)
zheng_gliss(T_HJ, 57, 81, 0.06)                                # 海禁 (Ming harbour)
for t in np.arange(T_HJ, T_FL, BEAT):
    frame(t, 0.08)
timp(T_HJ, 33, 0.25)
for m in (33, 45, 52):
    place(brass_note(m, T_FL - T_HJ, att=0.3, rel=0.5, swell=0.6), T_HJ, 0.06, hall=0.4, cath=0.3)
place(riser(T_DJ - T_FL + 0.2, 100.0, 3.0), T_FL - 0.2, 0.16, hall=0.2)    # the flood
timp_roll(T_FL, T_DJ - T_FL, 40, 0.15, 0.55)
place(noise_fx(T_DJ - T_FL + 1.5, 80, 1500, 0.6, 1.6), T_FL, 0.12, hall=0.3, cath=0.2)
for t in np.arange(T_FL, T_DJ - 0.1, BEAT / 4):
    taiko(t, ramp(t, [(T_FL, 0.12), (T_DJ, 0.3)]), pan=0.25 * np.sin(9 * t))
impact(T_DJ, 0.6, with_braam=True, notes=(29, 41, 48))           # the river is guided, not dammed
PDJ = chain([(T_DJ, 'F'), (T_DJ + 2.0, 'C'), (T_DJ + 4.0, 'G')], SH['threeroads'])
pad_prog(PDJ, [(T_DJ, 0.12), (SH['threeroads'], 0.08)], p=3.2, att=0.3, rel=1.6, hall=0.4, cath=0.3)
choir_prog(PDJ, [(T_DJ, 0.08), (SH['threeroads'], 0.05)], att=0.5, rel=2.0, vowels=('o',))
zheng_arp(PDJ, BEAT / 2, [(T_DJ, 0.06), (SH['threeroads'], 0.04)], T_DJ, SH['threeroads'] - 0.4)
str_line(T_DJ, [(72, 2.0), (76, 2.0), (74, SH['threeroads'] - T_DJ - 4.0)], 0.05)

# ------------------------------------------------------------------ CH4  three tomorrows
log('ch4')
C4 = SH['threeroads']
T_CC, T_DS, T_CS, T_QU = SH['cloudcastle'], SH['dataism'], SH['cloudserfs'], SH['queue']
T_AS, T_HV, T_WS, T_GC = SH['assembly'], SH['harvest'], SH['workshop'], SH['gardencity']
impact(C4, 0.4, notes=(33, 45))
pad(C4, T_CC - C4, 'Am9', gain=0.07, p=2.6, att=1.2, rel=0.8, hall=0.4, cath=0.4)
for k, m in enumerate([76, 81, 84]):                           # three roads: three chimes
    celesta(w(33, '三') + k * 0.42, m, 0.04, pan=-0.5 + 0.5 * k)
ambience(C4, T_CC - C4 + 1.0, 0.07, fin=1.5, fout=1.0, wind=0.4, shimmer=1.2)
# first tomorrow: cloud lords (cold, digital)
P4a = chain([(T_CC, 'Am9'), (T_CC + 4 * BEAT, 'Fmaj7'), (T_DS, 'Dm'), (T_DS + 4 * BEAT, 'Am9'), (T_CS, 'F'),
             (T_CS + 3.0, 'Esus')], T_QU)
glitch(T_CC - 0.05, 0.7, 0.07, 41)
place(ensemble('saw', 81, T_QU - T_CC, p=1.0, voices=3, cents=18, vib=0.0, att=1.0, rel=1.0, width=1.0), T_CC,
      0.018, hall=0.2, cath=0.7)
place(ensemble('saw', 28, T_QU - T_CC, p=1.2, voices=3, cents=6, vib=0.0, att=0.6, rel=0.8, width=0.3), T_CC,
      0.06, hall=0.05)
arp(P4a, BEAT / 2, [(T_CC, 0.025), (T_CS, 0.045)], [0, 2, 1, 3, 0, 2, 1, 3], bright_pts=[(T_CC, 0.5), (T_CS, 0.9)])
subpulse(P4a, BEAT / 2, [(T_CC, 0.03), (T_CS, 0.05)], T_CC, T_QU - 0.2)
beat_kit(T_DS, T_QU - 0.2, [(T_DS, 0.06), (T_CS, 0.09)], kick=False)
pad_prog(P4a, [(T_CC, 0.05), (T_CS, 0.07)], p=2.6, att=1.0, rel=0.8, hall=0.4, cath=0.4)
for i, m in enumerate([88, 84, 81, 79, 76, 74, 72, 69]):
    celesta(T_DS + 0.1 + i * 0.14, m, 0.035, pan=0.7 - 0.2 * i)
for t in np.arange(T_CS, T_QU - 0.2, BEAT):                      # identical screens: mechanical ticks
    place(METAL, t, 0.01, pan=0.4, hall=0.1)
place(BOOM, w(36, '施舍'), 0.15, hall=0.1, cath=0.3)
# second tomorrow: patching the old order (thin, grey)
PQ = chain([(T_QU, 'Dm'), (T_QU + 3.0, 'Am')], T_AS)
pad_prog(PQ, [(T_QU, 0.04), (T_AS, 0.035)], p=2.0, att=0.8, rel=1.0, hall=0.4, cath=0.35)
for k, m in enumerate([62, 60, 57, 60, 62, 60, 57, 55]):
    piano(T_QU + 0.3 + k * 2 * BEAT * 0.5, m, 0.05 if k % 2 == 0 else 0.04)
ambience(T_QU, T_AS - T_QU, 0.05, fin=0.5, fout=0.8, wind=0.2, shimmer=0.2)
for t in np.arange(T_QU, T_AS, 0.04):                            # rain
    if np.random.rand() < 0.5:
        place(SHAKER, t, 0.006 + 0.006 * np.random.rand(), pan=np.random.uniform(-0.8, 0.8), hall=0.2)
# third tomorrow: common owners (warm I-V-vi-IV turn)
T_TURN = MK['turn']
place(swell(1.4), T_AS - 1.0, 0.1, hall=0.3)
impact(T_TURN, 0.45, notes=(36, 48, 55))
P4c = chain([(T_TURN, 'C'), (T_TURN + 4 * BEAT, 'G'), (T_HV, 'Am'), (T_HV + 4 * BEAT, 'F'), (T_HV + 8 * BEAT, 'C'),
             (T_WS, 'G'), (T_WS + 4 * BEAT, 'Am'), (T_WS + 8 * BEAT, 'Fmaj7')], T_GC)
pad_prog(P4c, [(T_TURN, 0.08), (T_GC, 0.12)], p=3.2, att=0.8, rel=1.2, hall=0.4, cath=0.3, bassgain=0.6)
choir_prog(P4c, [(T_TURN, 0.04), (T_WS, 0.07)], att=1.2, rel=1.5, vowels=('o',))
piano_walk(P4c, BEAT, 0.07)
str_line(T_TURN, [(67, 2.5), (72, 2.5), (71, T_HV - T_TURN - 5.0)], 0.05)
zheng_arp(P4c, BEAT / 2, [(T_HV, 0.04), (T_GC, 0.055)], T_HV, T_GC - 0.2)
spic(P4c, BEAT / 2, [(T_WS, 0.03), (T_GC, 0.05)], [0, 1, 2, 3], T_WS, T_GC - 0.2)
for t in np.arange(T_HV, T_GC - 0.1, 2 * BEAT):
    frame(t, 0.07)
    frame(t + BEAT, 0.04, hi=True)
lead(T_WS + 0.2, [(76, 2), (79, 2), (81, 3), (79, 1), (76, 2), (74, 2), (72, 4)], BEAT, 0.09, kind='saw', pan=0.2)
# the Manifesto line: full choir + brass, cadence to C
T_MF = MK['manifesto']
PMF = chain([(T_GC, 'Fmaj7'), (T_MF + 1.9, 'G'), (T_MF + 3.9, 'Am'), (T_MF + 5.4, 'F'), (LL[42][1], 'C')], SIL + 0.6)
place(riser(1.2, 160.0, 2.4), T_GC - 1.0, 0.1, hall=0.2)
impact(T_MF - 0.2, 0.7, with_braam=True, notes=(29, 41, 48))
pad_prog(PMF, [(T_GC, 0.14), (LL[42][1], 0.15), (SIL, 0.1)], p=3.8, att=0.4, rel=2.0, hall=0.4, cath=0.3)
choir_prog(PMF, [(T_GC, 0.09), (LL[42][1], 0.13)], att=0.8, rel=2.2)
choir_prog(PMF, [(T_MF + 3.9, 0.05), (LL[42][1], 0.07)], att=0.8, rel=2.2, up=12, t_lo=T_MF + 3.8)
brass_prog(PMF, 0.1)
timp_prog(PMF, 0.25)
zheng_arp(PMF, BEAT / 2, [(T_GC, 0.05), (LL[42][1], 0.04)], T_GC, LL[42][1])
lead(T_MF + 0.1, [(79, 3), (81, 3), (84, 4), (83, 2), (81, 2), (79, 6)], BEAT, 0.09, kind='saw', pan=0.15)
dip(SIL, MK['march'] - 0.3, 0.35, fade=1.2)                    # near-silence: 「但这样的明天，不会自动到来」

# ------------------------------------------------------------------ EPILOGUE  silence -> march -> resolution
log('epilogue')
T_CR, T_MA, T_HA2, T_BR = SH['crossroads'], SH['march'], SH['hands'], SH['bridge']
T_CW, T_TP, T_CH, T_SU, T_EN = SH['crowdwalk'], SH['toport'], SH['child'], SH['sunrise'], SH['end']
place(ensemble('saw', 33, T_MA - SIL + 1.0, p=1.2, voices=4, cents=8, vib=0.0, att=1.5, rel=1.0, width=0.9), SIL, 0.12,
      hall=0.1, cath=0.5)
for t in np.arange(SIL + 0.5, T_MA, 2 * BEAT):
    place(HEART, t, 0.09, hall=0.1, cath=0.2)
celesta(w(43, '自动'), 76, 0.03, pan=0.2)
# 1886: march (frame-drum 'snare' + taiko on the downbeat), rising
PE1 = chain([(T_MA, 'Am'), (T_MA + 4 * BEAT, 'F'), (T_HA2, 'C'), (T_HA2 + 4 * BEAT, 'G'), (T_BR, 'Am'),
             (T_BR + 4 * BEAT, 'F'), (T_CW, 'C'), (T_TP, 'Gsus'), (T_TP + 0.5, 'G')], T_CH)
impact(T_MA, 0.35)
for k, t in enumerate(np.arange(T_MA, T_CH - 0.2, BEAT / 2)):
    g = ramp(t, [(T_MA, 0.05), (T_HA2, 0.07), (T_CW, 0.1), (T_CH, 0.12)])
    pos = k % 8
    if pos == 0:
        taiko(t, g * 2.0, big=k % 16 == 0)
    if pos in (2, 6):
        frame(t, g * 1.3, hi=True, pan=0.2)
    if pos in (5, 7):
        frame(t, g * 0.7, hi=True, pan=-0.2)
pad_prog(PE1, [(T_MA, 0.07), (T_CW, 0.13), (T_CH, 0.14)], p=3.6, att=0.6, rel=1.0, hall=0.4, cath=0.25, bassgain=0.6)
brass_prog(PE1, 0.08, t_lo=T_HA2 - 0.1)
choir_prog(PE1, [(T_BR, 0.05), (T_CH, 0.1)], att=1.0, rel=1.5, t_lo=T_BR - 0.1)
timp_prog(PE1, 0.22)
spic(PE1, BEAT / 2, [(T_HA2, 0.04), (T_CH, 0.07)], [0, 1, 2, 3], T_HA2, T_CH - 0.2)
str_line(T_MA, [(69, 2.5), (72, 2.5), (76, T_HA2 - T_MA - 5.0 + 0.0)], 0.05)
impact(T_HA2 + 0.3, 0.4)                                        # 技术决定可能性 / 制度决定结果
timp(w(45, '结果'), 36, 0.3)
lead(T_BR + 0.1, [(76, 2), (79, 2), (81, 2), (84, 2), (83, 2), (81, 2), (79, 4)], BEAT, 0.08, kind='saw', pan=0.2)
timp_roll(T_TP, T_CH - T_TP, 43, 0.1, 0.5)
place(riser(T_CH - T_TP + 0.3, 160.0, 2.6), T_TP - 0.3, 0.14, hall=0.2)
# 「那么，明天属于谁？」 the question in near-silence (piano + celesta)
pad(T_CH, T_SU - T_CH + 0.4, 'Fmaj7', gain=0.05, p=2.0, att=0.6, rel=1.4, hall=0.4, cath=0.4)
choir(T_CH, [57, 64, 69], T_SU - T_CH, 0.035, att=1.0, rel=1.2, vowels=('o',))
for k, m in enumerate([72, 76, 79]):
    piano(LL[48][0] + 0.6 + k * 0.45, m, 0.07, pan=-0.1 + 0.1 * k)
celesta(w(48, '谁'), 88, 0.04, pan=0.3)
# 「属于每一个为它共同奋斗的人。」 final resolution -> end card
PF = chain([(T_SU, 'C'), (w(49, '共同'), 'G'), (LL[49][1] + 0.2, 'Am'), (LL[49][1] + 1.6, 'F'), (T_EN + 1.4, 'Cadd9')],
           MK['end'])
impact(T_SU + 0.3, 0.8, with_braam=True, notes=(36, 48, 55))
pad_prog(PF, [(T_SU, 0.15), (T_EN + 1.4, 0.12), (MK['end'], 0.06)], p=4.0, att=0.3, rel=3.0, hall=0.4, cath=0.35)
choir_prog(PF, [(T_SU, 0.12), (T_EN + 1.4, 0.13)], att=0.4, rel=3.0)
choir_prog(PF, [(T_SU, 0.05), (T_EN + 1.4, 0.07)], att=0.6, rel=3.0, up=12)
brass_prog(PF, 0.11, t_hi=T_EN + 1.3)
timp_prog(PF, 0.28, t_hi=T_EN + 1.3)
zheng_arp(PF, BEAT / 2, [(T_SU, 0.05), (T_EN + 1.4, 0.03)], T_SU, T_EN + 1.4)
lead(T_SU + 0.3, [(79, 3), (76, 1), (79, 2), (84, 4), (83, 2), (79, 4)], BEAT, 0.1, kind='saw', pan=0.15)
ambience(T_EN, MK['end'] - T_EN, 0.06, fin=2.0, fout=4.0, wind=0.2, shimmer=1.2)
T_EC = MK['endcard']
for i, m in enumerate([48, 55, 62, 64, 67, 72]):
    piano(T_EC + 0.09 * i, m, 0.08, pan=-0.3 + 0.12 * i)
celesta(T_EC + 0.6, 84, 0.05, pan=-0.2)
celesta(T_EC + 0.7, 91, 0.035, pan=0.2)

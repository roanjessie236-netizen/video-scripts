# ================================================================== TODAY SCORE  (21 Lessons, 224 s)
# Inserted by tools/build_tl_music.py after the film-1/film-2 instrument + helper library.
# 0-23 low electronics, cut at 15.8 ('thinking'), title hit 18.4 | ch1 23-61 pulse + strings
# ch2 61-105 rhythm + orchestral layers, drop 76.4-86 (useless-class risk), warmth returns 86.2
# ch3 105-156 machine sound -> cello 120, silence 125-128.6, piano/cello, build
# ch4 156-224 build, drop 176.6-178.8, restrained choir climax 195, tail from 211, Cadd9 at 216.4
log('opening')
PP = [0, 1, 2, 3, 2, 1, 2, 3]
place(ensemble('saw', 33, 16.0, p=1.5, voices=4, cents=8, vib=0.0, att=4.0, rel=0.5, width=0.9), 0.0, 0.2,
      hall=0.15, cath=0.5)
place(ensemble('saw', 45, 15.6, p=1.3, voices=3, cents=14, vib=0.0, att=6.0, rel=0.4, width=1.0), 0.0, 0.07,
      hall=0.1, cath=0.6)
ambience(0.0, 16.0, 0.14, fin=3.0, fout=0.5, wind=0.6, shimmer=0.8)
for t, g in [(3.6, 0.10), (7.2, 0.14), (10.8, 0.18), (13.4, 0.16)]:      # fire -> writing -> machine -> chip
    place(BOOM, t, g, hall=0.15, cath=0.4)
place(metal(1.2, 420.0), 7.3, 0.07, hall=0.4, cath=0.2)
for t in np.arange(7.2, 15.6, 1.25):
    place(HEART, t, ramp(t, [(7.2, 0.07), (15.0, 0.18)]), hall=0.1, cath=0.2)
arp([(10.8, 5.0, 'Am9')], BEAT / 2, [(10.8, 0.012), (15.6, 0.045)], [0, 1, 2, 3, 2, 1, 2, 3],
    bright_pts=[(0, 0.5), (15.6, 1.0)], t_hi=15.7)
place(riser(4.0, 120.0, 3.0), 11.8, 0.15, hall=0.2, cath=0.2)
# 15.8 'thinking': everything stops, thin air
celesta(15.85, 88, 0.06, pan=0.0)
celesta(16.7, 81, 0.035, pan=-0.3)
pad(15.8, 2.6, 'Am9', gain=0.03, p=1.6, att=0.6, rel=1.0, hall=0.5, cath=0.5, octave=12)
place(riser(1.8, 300.0, 2.0), 16.6, 0.10, hall=0.3)
impact(18.4, 0.85, with_braam=True, notes=(29, 41, 48))                  # data centre + title
pad_prog([(18.4, 4.6, 'Fmaj7')], [(18.4, 0.12), (23.0, 0.10)], p=3.0, att=0.5, rel=1.4)
choir(18.6, [64, 69, 72], 4.6, 0.05, att=1.0, rel=2.0, vowels=('o',))
glitch(22.4, 0.6, 0.07, 1)

# ------------------------------------------------------------------ CH1 23-61  pulse + strings
log('ch1')
P1 = [(23.0, 4.6, 'Am'), (27.6, 3.8, 'F'), (31.4, 4.0, 'C'), (35.4, 5.0, 'G'), (40.4, 4.0, 'Am'), (44.4, 3.2, 'F'),
      (47.6, 3.2, 'C'), (50.8, 3.0, 'G'), (53.8, 3.6, 'Dm'), (57.4, 2.0, 'Esus'), (59.4, 1.6, 'E')]
place(BOOM, 23.0, 0.25, hall=0.1, cath=0.3)
taiko(23.0, 0.22)
arp(P1, BEAT / 2, [(23, 0.03), (40, 0.05), (53, 0.06), (61, 0.04)], [0, 1, 2, 3, 1, 2, 3, 2],
    bright_pts=[(23, 0.5), (45, 1.2), (58, 0.8)])
subpulse(P1, BEAT / 2, [(31.4, 0.03), (50, 0.055), (59, 0.06)], 31.4, 60.0)
beat_kit(40.4, 58.0, [(40.4, 0.09), (50, 0.14), (58, 0.15)])
pad_prog(P1, [(23, 0.06), (40, 0.09), (55, 0.12), (61, 0.12)], p=3.5, att=1.4, rel=1.6, hall=0.35, cath=0.15)
str_line(35.4, [(71, 2.5), (74, 2.5), (76, 4.0), (77, 3.2), (76, 3.2), (74, 3.0), (74, 3.6), (76, 3.6)], 0.06)
for t, sd in [(31.4, 2), (40.4, 3), (50.8, 4)]:
    glitch(t, 0.6, 0.07, sd)
for i, m in enumerate([88, 84, 81, 79, 76, 74, 72, 69]):                # neural galaxy
    celesta(35.6 + i * 0.16, m, 0.045, pan=0.7 - 0.2 * i)
timp_roll(58.0, 3.0, 40, 0.1, 0.45)
place(riser(3.4, 160.0, 2.6), 57.6, 0.14, hall=0.2)

# ------------------------------------------------------------------ CH2 61-105  work: rhythm + orchestra, drop, warmth
log('ch2')
P2 = [(61.0, 5.0, 'Am'), (66.0, 3.6, 'F'), (69.6, 2.8, 'Dm'), (72.4, 2.6, 'Esus'), (75.0, 2.6, 'E'), (77.6, 4.4, 'Am'),
      (82.0, 4.2, 'F'), (86.2, 5.4, 'C'), (91.6, 3.6, 'G'), (95.2, 3.8, 'Am'), (99.0, 3.0, 'F'), (102.0, 3.0, 'Gsus')]
impact(61.0, 0.6, with_braam=True, notes=(33, 45, 52))
pad_prog(P2, [(61, 0.10), (75, 0.13), (77, 0.06), (86, 0.07), (99, 0.12), (105, 0.12)], p=3.6, att=1.2, rel=1.6,
         hall=0.4, cath=0.2)
spic(P2, BEAT / 2, [(63, 0.04), (70, 0.065), (76.2, 0.075)], [0, 2, 1, 3, 0, 2, 1, 2], 63.0, 76.4)
subpulse(P2, BEAT / 2, [(66, 0.035), (76, 0.055)], 66.0, 76.4)
beat_kit(66.0, 76.4, [(66, 0.10), (76, 0.15)])
timp_prog(P2, 0.2, 69.6, 76.6)
brass_prog(P2, 0.07, t_lo=72.4, t_hi=77.6)
for t in np.arange(72.4, 76.4, BEAT / 2):
    taiko(t, ramp(t, [(72.4, 0.08), (76.4, 0.25)]), pan=0.1)
# 76.4-86: the risk -- low drone, heartbeat, distant glitches only
place(BOOM, 76.6, 0.3, hall=0.15, cath=0.4)
place(ensemble('saw', 33, 9.6, p=1.4, voices=3, cents=10, vib=0.0, att=1.0, rel=2.0, width=0.8), 76.6, 0.09,
      hall=0.2, cath=0.5)
for t in np.arange(77.6, 86.0, 1.25):
    place(HEART, t, ramp(t, [(77.6, 0.16), (85.5, 0.10)]), hall=0.1, cath=0.2)
for t, sd in [(79.2, 5), (82.4, 6)]:
    glitch(t, 0.5, 0.05, sd)
ambience(76.6, 10.0, 0.06, fin=1.5, fout=2.0, wind=0.5, shimmer=0.3)
# 86.2: lifelong learning -- warmth returns
for s, e, ch in segs(P2[7:]):
    notes = [m + 12 for m in CH[ch][2:]]
    piano(s, CH[ch][1], 0.09, pan=-0.1)
    k, t = 0, s + BEAT
    while t < e - 0.05:
        piano(t, notes[PP[k % 8]], 0.075 * (1.0 if k % 2 == 0 else 0.8))
        t += BEAT
        k += 1
str_line(91.6, [(74, 3.6), (76, 3.8), (77, 3.0), (79, 3.0)], 0.06)
subpulse(P2, BEAT / 2, [(95.2, 0.025), (104, 0.045)], 95.2, 104.6)
choir_prog(P2, [(99, 0.04), (104, 0.07)], att=1.5, rel=1.5, t_lo=99.0, t_hi=105.0)
place(riser(3.0, 160.0, 2.6), 102.0, 0.12, hall=0.2)

# ------------------------------------------------------------------ CH3 105-156  creativity: machine -> cello/piano
log('ch3')
P3 = [(105.0, 4.6, 'Am'), (109.6, 3.4, 'F'), (113.0, 3.0, 'C'), (116.0, 4.0, 'G'), (120.0, 5.0, 'Am'),
      (125.0, 3.6, 'Am'), (128.6, 3.8, 'Fmaj7'), (132.4, 5.0, 'C'), (137.4, 5.0, 'G'), (142.4, 5.2, 'Am'),
      (147.6, 4.2, 'Fmaj7'), (151.8, 4.2, 'Gsus')]
impact(105.0, 0.45)
arp(P3[:4], BEAT / 4, [(105, 0.02), (116, 0.035), (119.8, 0.0)], [0, 1, 2, 3], bright_pts=[(105, 1.4), (120, 1.4)],
    t_lo=105.4, t_hi=119.6)
for t, sd in [(109.6, 10), (113.0, 11), (116.0, 12)]:
    glitch(t, 0.5, 0.06, sd)
for t in np.arange(105.0, 119.6, 2 * BEAT):
    place(metal(0.6, 900.0), t, 0.02, hall=0.4, cath=0.2)
pad_prog(P3, [(105, 0.05), (120, 0.07), (124.6, 0.05), (125.0, 0.0), (128.4, 0.0), (128.6, 0.06), (142, 0.09),
              (156, 0.12)], p=2.6, att=1.5, rel=1.8, hall=0.35, cath=0.35)
CELLO = dict(kind='saw', p=2.0, vibd=0.012, glide=0.08, pan=-0.15, rel=1.8, cath=0.3)
lead(120.0, [(57, 3), (59, 1), (60, 2), (64, 2)], BEAT, 0.10, **CELLO)
for t, m, g in [(120.0, 45, 0.08), (121.25, 64, 0.06), (122.5, 69, 0.06), (123.75, 72, 0.05)]:
    piano(t, m, g)
ambience(124.6, 4.4, 0.05, fin=0.6, fout=1.0, wind=0.3, shimmer=0.8)    # the pause
for t0, notes in [(128.6, [(53, 3), (57, 3)]), (132.4, [(55, 4), (52, 2), (55, 2)]), (137.4, [(59, 4), (62, 4)]),
                  (142.4, [(64, 4), (60, 4)]), (147.6, [(57, 4), (60, 2.7)]), (151.8, [(62, 6.7)])]:
    lead(t0, notes, BEAT, 0.10, **CELLO)
for s, e, ch in segs(P3[6:]):
    notes = [m + 12 for m in CH[ch][2:]]
    piano(s, CH[ch][1], 0.09, pan=-0.1)
    step = 2 * BEAT if s < 137.0 else BEAT
    k, t = 0, s + step
    while t < e - 0.05:
        piano(t, notes[PP[k % 8]], 0.075 * (1.0 if k % 2 == 0 else 0.8))
        t += step
        k += 1
str_line(137.4, [(74, 5.0), (76, 5.2), (76, 4.2), (74, 4.2)], 0.06)
choir_prog(P3, [(142.4, 0.04), (151.8, 0.08)], att=2.0, rel=2.0, vowels=('u',), t_lo=142.4, t_hi=156.0)
spic(P3, BEAT / 2, [(142.4, 0.03), (155, 0.06)], [0, 1, 2, 1], 142.4, 155.6, octave=-12)
timp_roll(153.6, 2.4, 43, 0.08, 0.4)
place(riser(3.2, 160.0, 2.8), 152.8, 0.14, hall=0.2)

# ------------------------------------------------------------------ CH4 156-224  the human answer
log('ch4')
P4 = [(156.0, 4.6, 'Fmaj7'), (160.6, 4.4, 'C'), (165.0, 4.2, 'G'), (169.2, 4.0, 'Am'), (173.2, 3.4, 'F'),
      (176.6, 2.2, 'Gsus'), (178.8, 3.4, 'Fmaj7'), (182.2, 4.0, 'C'), (186.2, 4.0, 'G'), (190.2, 3.4, 'Am'),
      (193.6, 1.4, 'E'), (195.0, 4.2, 'F'), (199.2, 3.0, 'G'), (202.2, 2.8, 'Am'), (205.0, 3.0, 'F'), (208.0, 3.0, 'G')]
impact(156.0, 0.85, with_braam=True, notes=(29, 41, 48))
place(CRASH, 156.0, 0.16, hall=0.3, cath=0.3)
pad_prog(P4[:6], [(156, 0.11), (173, 0.15)], p=4.0, att=0.8, rel=1.4, hall=0.4, cath=0.2)
choir_prog(P4[:5], [(156, 0.05), (173, 0.08)], att=1.0, rel=1.6, t_hi=176.6)
arp(P4, BEAT / 2, [(160.6, 0.025), (173, 0.045), (176.4, 0.0)], [0, 1, 2, 3, 1, 2, 3, 2], t_lo=160.6, t_hi=176.4)
spic(P4, BEAT / 2, [(165, 0.04), (176.4, 0.07)], [0, 2, 1, 3, 0, 2, 1, 2], 165.0, 176.4)
timp_prog(P4, 0.2, 165.0, 176.6)
str_line(160.6, [(72, 4.4), (74, 4.2), (76, 4.0), (77, 3.4)], 0.07)
place(riser(2.6, 160.0, 2.4), 174.0, 0.12, hall=0.2)
# 176.6-178.8: the questions -- drop
place(BOOM, 176.6, 0.22, hall=0.2, cath=0.4)
ambience(176.4, 2.8, 0.05, fin=0.3, fout=0.8, wind=0.3, shimmer=1.0)
celesta(177.0, 81, 0.04)
celesta(177.8, 76, 0.03)
# 178.8: know yourself -- rebuild
Q = P4[6:]
pad_prog(Q, [(178.8, 0.10), (193, 0.15), (195, 0.18), (208, 0.14)], p=4.2, att=0.8, rel=1.6, hall=0.4, cath=0.25)
arp(Q, BEAT / 2, [(178.8, 0.03), (194, 0.05), (211, 0.03)], [0, 1, 2, 3, 1, 2, 3, 2],
    bright_pts=[(178.8, 0.8), (195, 1.2), (211, 0.8)])
subpulse(Q, BEAT / 2, [(182.2, 0.03), (194.6, 0.055), (205, 0.05), (210.6, 0.0)], 182.2, 210.8)
beat_kit(186.2, 194.6, [(186.2, 0.08), (194.6, 0.13)], ticks=False)
spic(Q, BEAT / 2, [(186.2, 0.04), (194.8, 0.07), (211, 0.05)], [0, 1, 2, 3], 186.2, 210.6)
timp_prog(Q, 0.24, 186.2, 211.0)
THEME = [(178.8, [(69, 2), (72, 3.4)]), (182.2, [(72, 2), (76, 4.4)]), (186.2, [(74, 2), (79, 4.4)]),
         (190.2, [(76, 2), (72, 3.4)]), (193.6, [(71, 2.2)]), (195.0, [(77, 3), (76, 1), (72, 2.7)]),
         (199.2, [(74, 2), (79, 2.8)]), (202.2, [(76, 4.4)]), (205.0, [(72, 2), (69, 2.8)]), (208.0, [(74, 4.8)])]
for t0, notes in THEME:
    lead(t0, notes, BEAT, 0.13 if t0 < 195 else 0.15, rel=1.6)
    if 195.0 <= t0 < 206.0:
        flute_phrase(t0, [(m + 12, b) for m, b in notes], BEAT, 0.05, pan=-0.3)
place(riser(2.8, 160.0, 2.8), 192.4, 0.14, hall=0.2)
timp_roll(193.6, 1.4, 40, 0.15, 0.5)
impact(195.0, 0.75, with_braam=False)                                   # restrained climax
place(CRASH, 195.0, 0.14, hall=0.3, cath=0.3)
choir_prog(Q, [(195, 0.11), (205, 0.12)], att=0.8, rel=2.0, up=12, t_lo=195.0, t_hi=211.0)
brass_prog(Q, 0.08, t_lo=195.0, t_hi=211.0)
for t in (199.2, 202.2, 205.0):
    timp(t, 43, 0.3)
# 211-224 tail
P5 = [(211.0, 5.4, 'Fmaj7'), (216.4, 7.6, 'Cadd9')]
pad_prog(P5, [(211, 0.08), (216.4, 0.07)], p=2.2, att=1.6, rel=3.0, hall=0.35, cath=0.35, bassgain=0.5)
ambience(211.0, 13.0, 0.07, fin=2.0, fout=4.0, wind=0.2, shimmer=1.2)
notes = [m + 12 for m in CH['Fmaj7'][2:]]
piano(211.0, CH['Fmaj7'][1], 0.1, pan=-0.1)
for k, t in enumerate(np.arange(211.0 + BEAT, 216.3, BEAT)):
    piano(t, notes[PP[k % 8]], 0.085 * (1.0 if k % 2 == 0 else 0.8))
for i, m in enumerate([48, 55, 62, 64, 67, 72]):
    piano(216.4 + 0.09 * i, m, 0.09, pan=-0.3 + 0.12 * i)
piano(217.2, 76, 0.07)
piano(218.6, 79, 0.06)
choir(216.4, CH['Cadd9'][2:], 6.0, 0.10, att=1.5, rel=3.5)
for t, m, d in [(212.6, 76, 3.6), (216.4, 79, 3.0), (219.6, 76, 3.6)]:
    lead(t, [(m, d)], 1.0, 0.045, kind='u', p=4.0, vibd=0.006, glide=0.05, pan=0.0, rel=2.0, cath=0.9)
celesta(220.2, 88, 0.03, pan=0.4)
celesta(221.6, 84, 0.025, pan=-0.3)


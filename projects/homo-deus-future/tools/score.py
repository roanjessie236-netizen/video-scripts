# ================================================================== FUTURE SCORE  (Homo Deus, 234 s)
# Inserted by tools/build_music.py between the Film-1 instrument library and the reverb/master stage.
CH = {
    'Am': [33, 45, 52, 57, 60, 64], 'Am9': [33, 45, 52, 59, 60, 64], 'F': [29, 41, 48, 57, 60, 65],
    'Fmaj7': [29, 41, 48, 57, 60, 64], 'C': [36, 48, 55, 60, 64, 67], 'C/E': [28, 40, 48, 55, 60, 64],
    'Cadd9': [36, 48, 55, 62, 64, 67], 'G': [31, 43, 50, 55, 59, 62], 'Gsus': [31, 43, 50, 55, 60, 62],
    'Dm': [26, 38, 45, 53, 57, 62], 'E': [28, 40, 47, 56, 59, 64], 'Esus': [28, 40, 47, 57, 59, 64],
}
TR = {'Am': 33, 'Am9': 33, 'F': 41, 'Fmaj7': 41, 'C': 36, 'C/E': 40, 'Cadd9': 36, 'G': 43, 'Gsus': 43,
      'Dm': 38, 'E': 40, 'Esus': 40}
BEAT = 0.625          # 96 BPM
PENT = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86, 88]


def ramp(t, pts):
    return float(np.interp(t, [p[0] for p in pts], [p[1] for p in pts]))


def segs(prog):
    for s, d, ch in prog:
        yield s, s + d, ch


def smooth1(x, k):
    k = max(2, int(k))
    xp = np.pad(x, (k // 2, k - k // 2), mode='edge')
    c = np.concatenate([[0.0], np.cumsum(xp, dtype=np.float64)])
    return ((c[k:] - c[:-k]) / k)[:len(x)]


_sy = {}


def synth(m, dur, bright=1.0):
    k = (m, round(dur, 3), bright)
    if k not in _sy:
        n = int((dur + 0.3) * SR)
        t = np.arange(n) / SR
        ph = 2 * np.pi * mtof(m) * t
        s = np.zeros(n)
        for h in range(1, 10):
            s += np.sin(h * ph + 0.3 * h) / h * np.exp(-t * (1.5 + 2.6 * h / bright))
        s *= np.minimum(1.0, t / 0.004) * np.exp(-t * 2.2 / max(dur, 0.05))
        _sy[k] = (s * 0.5).astype(np.float32)
    return _sy[k]


def arp(prog, step, gain_pts, pattern, octave=12, bright_pts=((0, 1.0), (300, 1.0)), t_lo=0.0, t_hi=1e9):
    k = 0
    for s, e, ch in segs(prog):
        notes = [m + octave for m in CH[ch][2:]]
        t = s
        while t < e - 1e-6:
            if t_lo <= t < t_hi:
                m = notes[pattern[k % len(pattern)] % len(notes)]
                g = ramp(t, gain_pts) * (1.0 if k % 4 == 0 else 0.78)
                b = max(0.25, round(ramp(t, bright_pts) * 4) / 4)
                place(synth(m, step * 1.6, b), t, g, pan=0.35 * np.sin(k * 0.7), hall=0.3, cath=0.15)
            t += step
            k += 1


_sub = {}


def subtone(m, dur):
    k = (m, round(dur, 3))
    if k not in _sub:
        n = int((dur + 0.1) * SR)
        t = np.arange(n) / SR
        f = mtof(m)
        s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
        s *= np.minimum(1.0, t / 0.01) * np.exp(-t * 3.0 / dur)
        _sub[k] = s.astype(np.float32)
    return _sub[k]


def subpulse(prog, step, gain_pts, t_lo, t_hi):
    for s, e, ch in segs(prog):
        t = s
        while t < e - 1e-6:
            if t_lo <= t < t_hi:
                place(subtone(CH[ch][0] + 12, step * 0.95), t, ramp(t, gain_pts), hall=0.05)
            t += step


KICK = drum(170, 46, 0.025, 0.32, 0.9, 0.08, 40, 500, 0.01, sub=0.6)
CLAP = noise_fx(0.25, 900, 5000, 0.002, 0.07)


def beat_kit(t0, t1, gain_pts, kick=True, ticks=True, clap=False, step=BEAT):
    k = 0
    t = t0
    while t < t1 - 1e-6:
        g = ramp(t, gain_pts)
        if kick and k % 2 == 0:
            place(KICK, t, g, hall=0.08, cath=0.05)
        if clap and k % 2 == 1:
            place(CLAP, t, g * 0.45, hall=0.3)
        if ticks:
            for j in range(4):
                place(SHAKER, t + j * step / 4, g * (0.22 if j == 2 else 0.1), pan=0.3, hall=0.1)
        t += step
        k += 1


def glitch(t0, dur, gain, seed):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    s = np.zeros(n)
    i = 0
    while i < n:
        L = int(r.uniform(0.008, 0.04) * SR)
        f = r.choice([220, 440, 880, 1320, 1760, 2640, 3520]) * r.uniform(0.98, 1.02)
        tt = np.arange(min(L, n - i)) / SR
        if r.random() < 0.6:
            s[i:i + len(tt)] = np.sign(np.sin(2 * np.pi * f * tt)) * r.uniform(0.2, 1.0)
        i += L + int(r.uniform(0, 0.03) * SR)
    s = bandf(s, lo=300, hi=9000, order=2) * env_ar(n, 0.005, dur * 0.5)
    place(s.astype(np.float32), t0, gain, pan=r.uniform(-0.5, 0.5), hall=0.2)


_sp = {}


def spic_note(m):
    if m not in _sp:
        _sp[m] = ensemble('saw', m, 0.11, p=3.0, voices=3, cents=9, vib=0.0, att=0.008, rel=0.14, width=0.6)
    return _sp[m]


def spic(prog, step, gain_pts, pattern, t_lo, t_hi, octave=0):
    k = 0
    for s, e, ch in segs(prog):
        notes = CH[ch][2:]
        t = s
        while t < e - 1e-6:
            if t_lo <= t < t_hi:
                m = notes[pattern[k % len(pattern)] % len(notes)] + octave
                place(spic_note(m), t, ramp(t, gain_pts) * (1.0 if k % 4 == 0 else 0.75), hall=0.35, cath=0.1)
            t += step
            k += 1


def pad_prog(prog, gain_pts, **kw):
    for s, e, ch in segs(prog):
        pad(s, e - s, ch, gain=ramp(s, gain_pts), **kw)


def brass_prog(prog, gain, t_lo=0.0, t_hi=1e9, frm=1):
    for s, e, ch in segs(prog):
        if t_lo <= s < t_hi:
            for m in CH[ch][frm:frm + 3]:
                place(brass_note(m, e - s, att=0.2, rel=1.0, swell=0.7), s, gain, hall=0.4, cath=0.15)


def choir_prog(prog, gain_pts, att=1.0, rel=1.5, vowels=('a', 'o'), up=0, t_lo=0.0, t_hi=1e9):
    for s, e, ch in segs(prog):
        if t_lo <= s < t_hi:
            choir(s, [m + up for m in CH[ch][3:]], e - s, ramp(s, gain_pts), att=att, rel=rel, vowels=vowels)


def timp_prog(prog, g, t_lo=0.0, t_hi=1e9):
    for s, e, ch in segs(prog):
        if t_lo <= s < t_hi:
            timp(s, TR[ch], g)


def str_line(t0, notes, gain):
    t = t0
    for m, d in notes:
        place(ensemble('saw', m, d, p=3.0, voices=5, cents=11, vib=0.005, vibrate=5.2, att=0.35, rel=0.9,
                       width=0.8), t, gain, hall=0.4, cath=0.25)
        t += d


def piano(t, m, g, pan=0.1):
    place(pluck(m, 2.6, bright=0.55, tau=1.4, pos=0.12), t, g, pan=pan, hall=0.45, cath=0.25)


_ce = {}


def celesta(t, m, g, pan=0.0):
    if m not in _ce:
        n = int(2.6 * SR)
        tt = np.arange(n) / SR
        f = mtof(m)
        s = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 1.6) + 0.35 * np.sin(2 * np.pi * f * 4.0 * tt) * np.exp(-tt * 6)
             + 0.15 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 4)) * np.minimum(1.0, tt / 0.002)
        _ce[m] = (s * 0.6).astype(np.float32)
    place(_ce[m], t, g, pan=pan, hall=0.4, cath=0.5)


def zheng_gliss(t0, lo, hi, g, dt=0.045):
    ns = [m for m in PENT if lo <= m <= hi]
    for i, m in enumerate(ns):
        place(pluck(m, 2.5, bright=1.0, tau=1.4), t0 + i * dt, g * (0.7 + 0.3 * i / len(ns)),
              pan=-0.3 + 0.6 * i / len(ns), hall=0.35, cath=0.2)


def zheng_arp(prog, step, gain_pts, t_lo, t_hi):
    k = 0
    for s, e, ch in segs(prog):
        notes = [m + 12 for m in CH[ch][2:]]
        t = s
        while t < e - 1e-6:
            if t_lo <= t < t_hi:
                place(pluck(notes[[0, 1, 2, 3, 2, 1][k % 6] % len(notes)], 2.2, bright=1.0, tau=1.2), t,
                      ramp(t, gain_pts) * (1.0 if k % 2 == 0 else 0.7), pan=-0.35, hall=0.35, cath=0.15)
            t += step
            k += 1


def lead(t0, notes, beat, gain, kind='saw', p=3.2, vibd=0.011, glide=0.07, pan=0.18, rel=1.3, cath=0.3):
    """Erhu-like bowed lead (kind='saw') or a solo voice (kind = a vowel)."""
    total = sum(b for _, b in notes) * beat
    n = int((total + rel) * SR)
    t = np.arange(n) / SR
    f = np.zeros(n)
    since = np.zeros(n)
    pos = 0.0
    for m, b in notes:
        i0, i1 = int(pos * SR), int((pos + b * beat) * SR)
        f[i0:i1] = mtof(m)
        since[i0:i1] = np.arange(i1 - i0) / SR
        pos += b * beat
    iend = int(total * SR)
    f[iend:] = mtof(notes[-1][0])
    since[iend:] = since[iend - 1] + np.arange(n - iend) / SR
    lf = smooth1(np.log(f), glide * SR)
    vd = vibd * np.clip((since - 0.15) / 0.4, 0, 1)
    f = np.exp(lf) * (1 + vd * np.sin(2 * np.pi * 6.0 * t))
    i, fr = phase_idx(f)
    tone = look(table(kind, notes[0][0], p), i, fr)
    dyn = 0.8 + 0.2 * np.sin(np.pi * np.clip(t / max(total, 0.1), 0, 1))
    bow = 0.85 + 0.15 * np.minimum(1.0, since / 0.12)
    s = bandf(tone * dyn * bow * env_ar(n, 0.09, rel), lo=220, hi=6500, order=2)
    place(s.astype(np.float32), t0, gain, pan=pan, hall=0.35, cath=cath)


def taiko_bar(t, g):
    taiko(t, g, big=True)
    taiko(t + 1.5 * BEAT, g * 0.5, pan=-0.2)
    taiko(t + 2 * BEAT, g * 0.7, pan=0.15)
    place(FD_LO[0], t + 2 * BEAT, g * 0.18, pan=0.3, hall=0.2)
    taiko(t + 3 * BEAT, g * 0.6, pan=-0.1)
    taiko(t + 3.5 * BEAT, g * 0.4, pan=0.2)


# ------------------------------------------------------------------ OPENING 0-30.4  low electronics + cosmos
log('opening')
place(ensemble('saw', 33, 30.0, p=1.6, voices=4, cents=8, vib=0.0, att=5.0, rel=3.0, width=0.9), 0.0, 0.2,
      hall=0.15, cath=0.5)
place(ensemble('saw', 45, 13.0, p=1.4, voices=3, cents=14, vib=0.0, att=6.0, rel=2.0, width=1.0), 0.0, 0.08,
      hall=0.1, cath=0.6)
ambience(0.0, 32.0, 0.16, fin=4.0, fout=3.0, wind=0.45, shimmer=1.3)
for t in np.arange(3.75, 12.6, 1.25):
    place(HEART, t, ramp(t, [(3.75, 0.08), (12.5, 0.24)]), hall=0.1, cath=0.2)
place(riser(4.2, 120.0, 3.2), 8.8, 0.16, hall=0.2, cath=0.2)
impact(13.0, 0.9, with_braam=True, notes=(33, 45, 52))
pad(13.0, 9.8, 'Am9', gain=0.10, p=2.4, att=2.2, rel=2.0, hall=0.3, cath=0.3)
for i, m in enumerate([69, 72, 76, 79, 81, 84, 88]):          # the city lights switch on
    celesta(13.6 + i * 0.42, m, 0.07, pan=-0.6 + 0.2 * i)
arp([(18.0, 4.6, 'Am9')], BEAT / 2, [(18.0, 0.015), (22.6, 0.05)], [0, 1, 2, 3, 2, 1, 2, 3],
    bright_pts=[(0, 0.5), (22.6, 1.0)])
impact(22.6, 0.7, with_braam=True, notes=(29, 41, 48))           # title
OP = [(22.6, 3.8, 'Fmaj7'), (26.4, 4.0, 'Gsus')]
pad_prog(OP, [(22.6, 0.13), (26.4, 0.12)], p=3.0, att=0.6, rel=1.4)
choir(22.6, [64, 69, 72], 5.0, 0.06, att=1.0, rel=2.0, vowels=('o',))
arp(OP, BEAT / 2, [(22.6, 0.04), (30.4, 0.05)], [0, 2, 1, 3])
place(riser(3.4, 160.0, 2.6), 27.0, 0.13, hall=0.2)
glitch(29.5, 0.8, 0.08, 1)

# ------------------------------------------------------------------ CH1 30.4-72  intelligence: synth + strings
log('ch1')
P1 = [(30.4, 5, 'Am'), (35.4, 5, 'F'), (40.4, 5, 'C'), (45.4, 5, 'G'), (50.4, 5, 'Am'), (55.4, 5, 'F'),
      (60.4, 5, 'Dm'), (65.4, 3.4, 'Esus'), (68.8, 3.2, 'E')]
taiko(30.4, 0.3)
place(BOOM, 30.4, 0.3, hall=0.1, cath=0.3)
arp(P1, BEAT / 2, [(30.4, 0.035), (50, 0.05), (62, 0.06), (65.4, 0.035), (72, 0.02)], [0, 1, 2, 3, 1, 2, 3, 2],
    bright_pts=[(30.4, 0.5), (55, 1.25), (65, 0.75)])
subpulse(P1, BEAT / 2, [(36.6, 0.035), (55, 0.06), (64, 0.06), (66, 0.0)], 36.6, 66.0)
beat_kit(43.75, 64.0, [(43.75, 0.10), (55, 0.16), (63.5, 0.16)])
beat_kit(55.4, 62.9, [(55.4, 0.16), (62.9, 0.16)], kick=False, ticks=False, clap=True)
pad_prog(P1, [(30.4, 0.06), (50, 0.09), (62, 0.12), (72, 0.13)], p=3.5, att=1.4, rel=1.6, hall=0.35, cath=0.15)
str_line(50.4, [(72, 2.5), (76, 2.5), (77, 3.75), (76, 1.25), (74, 5.0), (76, 6.6)], 0.07)
for t, sd in [(36.6, 2), (43.0, 3), (49.0, 4), (62.6, 5)]:
    glitch(t, 0.6, 0.07, sd)
for rep in (55.0, 58.75):                                     # data like the Milky Way
    for i, m in enumerate([88, 84, 81, 79, 76, 74, 72, 69]):
        celesta(rep + i * 0.16, m, 0.045, pan=0.7 - 0.2 * i)
timp_roll(68.8, 3.2, 40, 0.1, 0.45)
place(riser(3.6, 160.0, 2.6), 68.4, 0.14, hall=0.2)

# ------------------------------------------------------------------ CH2 72-121  redesigning life: orchestra + electronics
log('ch2')
P2 = [(72.0, 5, 'Fmaj7'), (77.0, 5, 'C/E'), (82.0, 5, 'Dm'), (87.0, 5, 'Am'), (92.0, 5, 'F'), (97.0, 5, 'C'),
      (102.0, 4, 'G'), (106.0, 5, 'Am'), (111.0, 3.2, 'F'), (114.2, 3.8, 'Dm'), (118.0, 3.0, 'Esus')]
impact(72.0, 0.55, with_braam=True, notes=(29, 41, 48))
pad_prog(P2, [(72, 0.10), (92, 0.13), (106, 0.16), (118, 0.17)], p=3.8, att=1.2, rel=1.6, hall=0.4, cath=0.2)
spic(P2, BEAT / 2, [(79, 0.04), (92, 0.065), (104.6, 0.075)], [0, 2, 1, 3, 0, 2, 1, 2], 79.0, 104.6)
subpulse(P2, BEAT, [(86, 0.03), (104, 0.05)], 86.0, 104.6)
for k, t in enumerate(np.arange(79.4, 93.0, 1.25)):           # DNA helix motif
    for j, m in enumerate([81, 76, 72, 76] if k % 2 == 0 else [84, 79, 76, 79]):
        celesta(t + j * 0.156, m, 0.05, pan=(-0.5 if k % 2 == 0 else 0.5) * (1 - j / 3))
timp_prog(P2, 0.22, 92.0, 121.0)
for t in (97.2, 103.8):                                       # into the body / cells like planets
    place(noise_fx(2.0, 300, 4000, 1.6, 0.3), t, 0.12, hall=0.2, cath=0.3)
impact(106.0, 0.6, with_braam=True, notes=(33, 45, 52))
choir_prog(P2, [(106, 0.07), (118, 0.12)], att=1.5, rel=1.5, t_lo=106.0, t_hi=121.0)
r2 = np.random.default_rng(7)
for t in np.arange(106.6, 113.0, 0.625):
    celesta(t, int(r2.choice(PENT[5:])), 0.035, pan=r2.uniform(-0.7, 0.7))
brass_prog(P2, 0.09, t_lo=111.0, t_hi=121.0)
for t in np.arange(117.5, 121.0, BEAT / 2):
    taiko(t, ramp(t, [(117.5, 0.1), (121, 0.32)]), pan=0.1)
place(riser(3.2, 160.0, 2.8), 117.8, 0.14, hall=0.2)

# ------------------------------------------------------------------ CH3 121-166.4  humans & machines: piano + pulse + voices
log('ch3')
P3 = [(121.0, 5.8, 'Am'), (126.8, 5.2, 'Fmaj7'), (132.0, 4.8, 'C'), (136.8, 6.0, 'G'), (142.8, 5.8, 'Am'),
      (148.6, 5.2, 'Fmaj7'), (153.8, 5.2, 'Dm'), (159.0, 4.0, 'Esus'), (163.0, 2.8, 'E')]
impact(121.0, 0.5)
pad_prog(P3, [(121, 0.08), (142.8, 0.07), (160, 0.09)], p=2.6, att=2.0, rel=2.0, hall=0.35, cath=0.35)
PP = [0, 1, 2, 3, 2, 1, 2, 3]
for s, e, ch in segs(P3):
    if s >= 163:
        break
    notes = [m + 12 for m in CH[ch][2:]]
    piano(s, CH[ch][1], 0.09, pan=-0.1)
    step = 2 * BEAT if 144.0 <= s < 159.0 else BEAT
    k, t = 0, s + step
    while t < e - 0.05:
        piano(t, notes[PP[k % 8]], 0.08 * (1.0 if k % 2 == 0 else 0.8))
        t += step
        k += 1
subpulse(P3, BEAT / 2, [(126.8, 0.03), (142, 0.045)], 126.8, 142.8)
spic(P3, BEAT / 2, [(132, 0.04), (142.8, 0.07)], [0, 1, 2, 1], 132.0, 142.8, octave=-12)
beat_kit(132.0, 142.8, [(132, 0.08), (142.8, 0.13)], ticks=False)
for m in (43, 50, 55):                                        # the underground city: scale
    place(brass_note(m, 6.0, att=0.6, rel=1.5, swell=0.9), 136.8, 0.09, hall=0.4, cath=0.3)
for t, sd in [(120.8, 6), (126.8, 7), (142.8, 8), (148.6, 9)]:
    glitch(t, 0.7, 0.07, sd)
ambience(142.8, 24.0, 0.08, fin=2.0, fout=3.0, wind=0.2, shimmer=1.5)
for t in np.arange(144.8, 160.0, 1.25):
    place(HEART, t, ramp(t, [(144.8, 0.1), (159.0, 0.2)]), hall=0.1, cath=0.2)
choir_prog(P3, [(142.8, 0.05), (159, 0.09)], att=2.0, rel=2.0, vowels=('u',), t_lo=142.8, t_hi=163.5)
place(riser(1.6, 400.0, 1.5), 164.8, 0.08, hall=0.3)

# ------------------------------------------------------------------ CH4 166.4-205  a new era: Eastern orchestral epic
log('ch4')
P4 = [(166.4, 2.5, 'F'), (168.9, 2.5, 'G'), (171.4, 5.0, 'Am'), (176.4, 2.5, 'F'), (178.9, 2.5, 'G'),
      (181.4, 2.5, 'C'), (183.9, 2.5, 'Esus'), (186.4, 2.5, 'F'), (188.9, 2.5, 'G'), (191.4, 2.5, 'Am'),
      (193.9, 2.5, 'C'), (196.4, 1.4, 'E'), (197.8, 2.5, 'F'), (200.3, 2.5, 'G'), (202.8, 2.2, 'Am')]
place(CRASH, 166.4, 0.2, hall=0.3, cath=0.3)
zheng_gliss(166.4, 57, 86, 0.12)
pad_prog(P4, [(166.4, 0.12), (186.4, 0.17), (197.8, 0.22)], p=4.5, att=0.6, rel=1.4, hall=0.4, cath=0.2)
choir_prog(P4, [(166.4, 0.07), (186.4, 0.12), (197.8, 0.17)], att=0.6, rel=1.6)
choir_prog(P4, [(197.8, 0.09), (202.8, 0.1)], att=0.4, rel=2.0, up=12, t_lo=197.8)
timp_prog(P4, 0.3)
lead(168.9, [(67, 2), (69, 2), (72, 4), (74, 2), (76, 4), (74, 2), (72, 1), (69, 1)], BEAT, 0.16)
lead(181.4, [(76, 2), (79, 2), (81, 3), (79, 1), (76, 4)], BEAT, 0.16)
E3 = [(72, 2), (74, 2), (76, 2), (79, 2), (81, 4)]
lead(188.9, E3, BEAT, 0.18)
flute_phrase(188.9, [(m + 12, b) for m, b in E3], BEAT, 0.06, pan=-0.3)
EC = [(81, 2), (84, 1), (81, 1), (79, 2), (76, 2), (79, 1), (76, 1), (76, 2)]
lead(197.8, EC, BEAT, 0.18, rel=2.0)
flute_phrase(197.8, [(m + 12, b) for m, b in EC], BEAT, 0.06, pan=-0.3)
zheng_arp(P4, BEAT / 2, [(173, 0.05), (196, 0.07)], 173.9, 196.4)
for t in np.arange(173.9, 196.0, 4 * BEAT):
    taiko_bar(t, ramp(t, [(173.9, 0.25), (193.9, 0.45)]))
brass_prog(P4, 0.09, t_lo=181.4, t_hi=197.8)
brass_prog(P4, 0.14, t_lo=197.8)
spic(P4, BEAT / 2, [(186.4, 0.06), (196.4, 0.09)], [0, 1, 2, 3], 186.4, 196.4)
place(riser(3.0, 160.0, 2.8), 194.8, 0.15, hall=0.2)
for i in range(10):
    taiko(196.4 + 0.14 * i, 0.25 + 0.035 * i, pan=0.25 * (-1) ** i)
timp_roll(196.4, 1.4, 40, 0.2, 0.6)
impact(197.8, 1.0, with_braam=True, notes=(29, 41, 48))
for t in (200.3,):
    taiko_bar(t, 0.5)
taiko(202.8, 0.7, big=True)
place(CRASH, 202.8, 0.2, hall=0.3, cath=0.3)

# ------------------------------------------------------------------ ENDING 204.8-234  warm piano + choir
log('ending')
P5 = [(204.8, 5.0, 'Fmaj7'), (209.8, 4.4, 'C/E'), (214.2, 4.0, 'Dm'), (218.2, 3.0, 'Gsus'), (221.2, 3.0, 'G'),
      (224.2, 4.0, 'Fmaj7'), (228.2, 5.8, 'Cadd9')]
pad_prog(P5, [(204.8, 0.07), (228.2, 0.06)], p=2.2, att=1.6, rel=2.2, hall=0.35, cath=0.35, bassgain=0.5)
ambience(204.8, 29.2, 0.08, fin=3.0, fout=5.0, wind=0.2, shimmer=1.2)
for s, e, ch in segs(P5[:-1]):
    notes = [m + 12 for m in CH[ch][2:]]
    piano(s, CH[ch][1], 0.1, pan=-0.1)
    step = BEAT if s < 218.0 else BEAT / 2
    g = 0.10 if s < 218.0 else 0.085
    k = 0
    while s + step * (k + 1) < e - 0.05:
        piano(s + step * (k + 1), notes[PP[k % 8]], g * (1.0 if k % 2 == 0 else 0.8))
        k += 1
choir_prog(P5, [(214, 0.08), (228, 0.12)], att=2.0, rel=2.0, t_lo=214.0, t_hi=228.0)
choir(228.2, CH['Cadd9'][2:], 6.0, 0.14, att=1.5, rel=4.0)
for i, m in enumerate([48, 55, 62, 64, 67, 72]):
    piano(228.2 + 0.09 * i, m, 0.1, pan=-0.3 + 0.12 * i)
piano(228.8, 76, 0.08)
piano(229.9, 79, 0.07)
for t, m, d in [(216.2, 76, 4.0), (220.2, 74, 2.3), (222.5, 74, 2.5), (225.0, 72, 3.0), (228.0, 76, 6.0)]:
    lead(t, [(m, d)], 1.0, 0.05, kind='u', p=4.0, vibd=0.006, glide=0.05, pan=0.0, rel=2.0, cath=0.9)
for t, m in [(221.6, 88), (223.4, 84), (225.2, 91), (227.0, 86)]:
    celesta(t, m, 0.03, pan=0.4)

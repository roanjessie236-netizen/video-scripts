#!/usr/bin/env python3
"""Procedural score for 《人类简史：七万年的文明觉醒》.

300 s, 44.1 kHz, stereo. Pure numpy (no samples, no internet).
Sections (seconds) follow the picture edit in shotlist.json:
  0-21    opening   : cosmic ambience + low taiko, impact at 11.0, title hit at 17.6
  21-70   act 1     : frame drums 72 BPM + dizi-like flute + drone, building
  70-120  act 2     : strings Dm-Bb-F-C + guzheng-like plucks + timpani, braam at 106
  120-200 act 3     : 100 BPM spiccato ostinato, brass from 148.8, climax 168-187
  200-300 act 4     : felt-piano pulse, build w/ choir, grand climax 252-266, choir alone 266-287 (v2)
Usage: python3 music.py [out.wav]
"""
import numpy as np, wave, sys, time

SR = 44100
DUR = 284.125  # v2 from the user's film: their own ending cut (4:44.125)
N_VIDEO = int(SR * DUR)
N = 12544000  # 7-smooth length >= N_VIDEO: keeps the long FFTs (filters / reverbs) fast and small (no Bluestein)
rng = np.random.default_rng(70000)
OUT = sys.argv[1] if len(sys.argv) > 1 else '/data/video/out/score.wav'
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:6.1f}s]', *a, flush=True)


def mtof(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


# ------------------------------------------------------------------ buses
DRY = np.zeros((2, N), np.float32)
HALL = np.zeros((2, N), np.float32)
CATH = np.zeros((2, N), np.float32)


def place(sig, t0, gain=1.0, pan=0.0, hall=0.25, cath=0.0):
    sig = np.asarray(sig, np.float32)
    if sig.ndim == 1:
        a = (float(np.clip(pan, -1, 1)) + 1) * np.pi / 4
        st = np.stack([sig * np.cos(a) * 1.41421356, sig * np.sin(a) * 1.41421356])
    else:
        st = sig
    i0 = int(round(t0 * SR))
    if i0 < 0:
        st = st[:, -i0:]
        i0 = 0
    n = min(st.shape[1], N - i0)
    if n <= 0:
        return
    seg = st[:, :n] * gain
    DRY[:, i0:i0 + n] += seg
    if hall:
        HALL[:, i0:i0 + n] += seg * hall
    if cath:
        CATH[:, i0:i0 + n] += seg * cath


# ------------------------------------------------------------------ dsp helpers
def bandf(x, lo=None, hi=None, order=4):
    x = np.asarray(x, np.float64)
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    H = np.ones_like(f)
    if hi is not None:
        H /= np.sqrt(1 + (f / hi) ** (2 * order))
    if lo is not None:
        H /= np.sqrt(1 + (lo / np.maximum(f, 1e-6)) ** (2 * order))
    return np.fft.irfft(X * H, n).astype(np.float32)


def env_ar(n, a, r):
    e = np.ones(n, np.float32)
    na = min(int(a * SR), n)
    if na > 0:
        e[:na] = np.sin(np.linspace(0, np.pi / 2, na)) ** 2
    nr = min(int(r * SR), n - na)
    if nr > 0:
        e[n - nr:] *= np.cos(np.linspace(0, np.pi / 2, nr)) ** 2
    return e


def norm(x, peak=1.0):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


# ------------------------------------------------------------------ wavetables
TBL = 4096
_tc = {}
VOW = {
    'a': [(800, 1.0, 120), (1150, 0.55, 130), (2900, 0.22, 170), (3300, 0.14, 190)],
    'o': [(450, 1.0, 95), (800, 0.45, 105), (2830, 0.08, 160)],
    'u': [(325, 1.0, 75), (700, 0.2, 95), (2530, 0.05, 160)],
}


def table(kind, midi, p=6.0):
    key = (kind, int(round(midi)), round(p, 1))
    if key in _tc:
        return _tc[key]
    f0 = mtof(midi)
    K = max(1, min(96, int(14000 / f0)))
    k = np.arange(1, K + 1, dtype=np.float64)
    if kind == 'saw':
        w = (1 / k) * np.exp(-(k - 1) / p)
    elif kind == 'flute':
        base = np.array([1, .42, .2, .11, .07, .045, .03, .02, .012, .008])
        w = base[:K]
        k = k[:len(w)]
    elif kind in VOW:
        fk = k * f0
        w = 0.03 + sum(a * np.exp(-0.5 * ((fk - fc) / bw) ** 2) for fc, a, bw in VOW[kind])
        w = w * k ** -0.5
    else:
        raise ValueError(kind)
    ph = 2 * np.pi * np.arange(TBL) / TBL
    sig = np.zeros(TBL)
    for kk, a in zip(k, w):
        sig += a * np.sin(kk * ph)
    sig = (sig / np.max(np.abs(sig))).astype(np.float32)
    _tc[key] = sig
    return sig


def phase_idx(freq):
    ph = np.cumsum(freq / SR) + rng.random()
    idx = (ph % 1.0) * TBL
    i = idx.astype(np.int32)
    fr = (idx - i).astype(np.float32)
    return i, fr


def look(tb, i, fr):
    return tb[i] * (1 - fr) + tb[(i + 1) & (TBL - 1)] * fr


def ensemble(kind, midi, dur, p=6.0, voices=4, cents=10, vib=0.003, vibrate=5.0,
             att=0.8, rel=1.5, width=0.7, drift=0.0012, bright_tb=None, bright_env=None):
    """Detuned ensemble of wavetable voices, returns stereo (2, n) of length dur+rel."""
    n = int((dur + rel) * SR)
    t = np.arange(n, dtype=np.float64) / SR
    f0 = mtof(midi)
    tb = table(kind, midi, p)
    out = np.zeros((2, n), np.float32)
    vibenv = np.clip(t / 0.7, 0, 1)
    for v in range(voices):
        x = (v / (voices - 1) - 0.5) * 2 if voices > 1 else 0.0
        c = x * cents + rng.normal(0, cents * 0.15)
        rate = vibrate * (0.88 + 0.24 * rng.random())
        fr_ = f0 * 2 ** (c / 1200) * (1 + vib * vibenv * np.sin(2 * np.pi * rate * t + rng.random() * 6.28)
                                      + drift * np.sin(2 * np.pi * 0.21 * (1 + rng.random()) * t + rng.random() * 6.28))
        i, fr = phase_idx(fr_)
        s = look(tb, i, fr)
        if bright_tb is not None:
            s = s * (1 - bright_env) + look(bright_tb, i, fr) * bright_env
        a = (x * width + 1) * np.pi / 4
        out[0] += s * np.cos(a)
        out[1] += s * np.sin(a)
    out *= env_ar(n, att, rel) * (1.0 / np.sqrt(voices))
    return out


# ------------------------------------------------------------------ instruments
def pad(t0, dur, ch, gain=0.2, p=5.0, att=1.2, rel=1.8, hall=0.35, cath=0.1, octave=0,
        bassgain=0.8, voices=4):
    for m in CH[ch][1:]:
        s = ensemble('saw', m + octave, dur, p=p, voices=voices, cents=9, vib=0.0035, att=att, rel=rel, width=0.8)
        place(s, t0, gain * 0.55, hall=hall, cath=cath)
    if bassgain > 0:
        s = ensemble('saw', CH[ch][0], dur, p=p * 0.6, voices=3, cents=6, vib=0.0012, att=att, rel=rel, width=0.25)
        place(s, t0, gain * bassgain, hall=hall * 0.6)


def brass_note(midi, dur, att=0.18, rel=0.7, voices=3, swell=0.5):
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    b = np.clip(t / max(att * 2.5, 0.05), 0, 1) * (0.55 + swell * 0.45 * np.clip(t / max(dur, 0.1), 0, 1))
    b = np.clip(b, 0, 1).astype(np.float32)
    s = ensemble('saw', midi, dur, p=2.2, voices=voices, cents=7, vib=0.002, vibrate=4.8, att=att, rel=rel,
                 width=0.5, bright_tb=table('saw', midi, 11.0), bright_env=b)
    return np.tanh(s * 1.6) / 1.2


def choir(t0, notes, dur, gain, att=1.6, rel=2.5, vowels=('a', 'o'), hall=0.25, cath=0.65, voices=3):
    for m in notes:
        for vw in vowels:
            s = ensemble(vw, m, dur, voices=voices, cents=13, vib=0.006, vibrate=5.3, att=att, rel=rel, width=0.95,
                         drift=0.002)
            place(s, t0, gain / len(vowels), hall=hall, cath=cath)


_pl = {}


def pluck(midi, dur=3.0, bright=1.0, tau=1.6, pos=0.17, inharm=0.00025, key=None):
    key = key or (midi, dur, bright, tau, pos)
    if key in _pl:
        return _pl[key]
    f0 = mtof(midi)
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 18):
        fk = f0 * k * np.sqrt(1 + inharm * k * k)
        if fk > 15000:
            break
        a = abs(np.sin(np.pi * k * pos)) / k ** (1.3 - 0.3 * bright)
        tk = tau / (1 + 0.5 * (k - 1) / bright)
        out += a * np.sin(2 * np.pi * fk * t + rng.random() * 6.28) * np.exp(-t / tk)
    na = int(0.002 * SR)
    out[:na] *= np.linspace(0, 1, na)
    m = int(0.03 * SR)
    nz = bandf(rng.standard_normal(m), lo=1500, hi=7000) * np.exp(-np.arange(m) / SR / 0.006)
    out[:m] += 0.25 * bright * nz / (np.max(np.abs(nz)) + 1e-9) * np.max(np.abs(out))
    out = norm(out).astype(np.float32)
    _pl[key] = out
    return out


def drum(f_hi, f_lo, tau_f, tau_a, dur, noise_amt, n_lo, n_hi, n_tau, sub=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f_lo + (f_hi - f_lo) * np.exp(-t / tau_f)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau_a)
    nz = bandf(rng.standard_normal(n), lo=n_lo, hi=n_hi) * np.exp(-t / n_tau)
    s = body + noise_amt * nz / (np.max(np.abs(nz)) + 1e-9)
    if sub:
        s += sub * np.sin(2 * np.pi * 41 * t) * np.exp(-t / 0.9) * np.clip(t / 0.01, 0, 1)
    k = int(0.001 * SR)
    s[:k] *= np.linspace(0, 1, k)
    return norm(s).astype(np.float32)


def timp_hit(midi, dur=3.0, strike=0.35):
    f0 = mtof(midi)
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for r, a, tau in zip([1, 1.504, 1.742, 2.0, 2.245, 2.494], [1, .5, .3, .35, .18, .12], [1.8, 1.1, .8, .9, .6, .5]):
        out += a * np.sin(2 * np.pi * f0 * r * t + rng.random() * 6.28) * np.exp(-t / tau)
    nz = bandf(rng.standard_normal(n), lo=60, hi=2000) * np.exp(-t / 0.02)
    out += strike * nz / (np.max(np.abs(nz)) + 1e-9) * 2
    k = int(0.002 * SR)
    out[:k] *= np.linspace(0, 1, k)
    return norm(out).astype(np.float32)


def crash(dur=4.5, tau=1.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros((2, n), np.float32)
    for c in range(2):
        nz = bandf(rng.standard_normal(n), lo=2500, hi=14000)
        e = np.exp(-t / tau) * (1 - np.exp(-t / 0.002))
        met = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) * np.exp(-t / (tau * 1.1)) * 0.08
                  for f in [3170, 4110, 5330, 6870, 8420])
        out[c] = (nz / (np.max(np.abs(nz)) + 1e-9) * 0.9 + met) * e
    return norm(out)


def swell(dur):
    c = crash(dur + 0.5, tau=dur * 0.45)[:, :int(dur * SR)][:, ::-1].copy()
    n = c.shape[1]
    c *= np.linspace(0, 1, n) ** 1.5
    return c


def boom(dur=3.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 27 + 34 * np.exp(-t / 0.22)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 1.2) * np.clip(t / 0.004, 0, 1)
    return norm(s).astype(np.float32)


def braam(dur=4.5, notes=(26, 38, 45)):
    tot = None
    for m in notes:
        s = ensemble('saw', m, dur * 0.35, p=12, voices=3, cents=18, vib=0, att=0.04, rel=dur * 0.65, width=0.7)
        tot = s if tot is None else tot + s
    n = tot.shape[1]
    t = np.arange(n) / SR
    tot *= np.exp(-t / (dur * 0.4))
    tot = np.tanh(norm(tot) * 2.4)
    tot = np.stack([bandf(tot[0], hi=2600), bandf(tot[1], hi=2600)])
    return norm(tot)


def riser(dur, f0=180.0, octaves=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * 2 ** (octaves * (t / dur) ** 1.6)
    tone = sum(np.sin(2 * np.pi * np.cumsum(f * r) / SR) / r for r in (1, 1.5, 2.0))
    e = (t / dur) ** 2.2
    out = np.zeros((2, n), np.float32)
    for c in range(2):
        nz = bandf(rng.standard_normal(n), lo=1500, hi=9000)
        out[c] = (0.35 * tone / 2 + nz / (np.max(np.abs(nz)) + 1e-9)) * e
    return norm(out)


def noise_fx(dur, lo, hi, att, tau, stereo=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = np.clip(t / att, 0, 1) * np.exp(-np.maximum(t - att, 0) / tau)
    out = np.zeros((2, n), np.float32)
    for c in range(2):
        nz = bandf(rng.standard_normal(n), lo=lo, hi=hi)
        out[c] = nz * e
    return norm(out)


def metal(dur=1.2, f0=520.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t / tau)
            for r, a, tau in zip([1, 2.76, 5.40, 8.93, 13.34], [1, .6, .4, .25, .15], [.6, .4, .3, .2, .15]))
    nz = bandf(rng.standard_normal(n), lo=2000, hi=9000) * np.exp(-t / 0.01)
    s = s + 0.5 * nz / (np.max(np.abs(nz)) + 1e-9)
    return norm(s).astype(np.float32)


def ambience(t0, dur, gain, fin=3.0, fout=3.0, wind=1.0, shimmer=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = env_ar(n, fin, fout)
    out = np.zeros((2, n), np.float32)
    if wind:
        for c in range(2):
            nz = bandf(rng.standard_normal(n), lo=110, hi=850, order=2)
            mod = 0.55 + 0.45 * np.sin(2 * np.pi * (0.045 + 0.02 * c) * t + rng.random() * 6.28)
            out[c] += wind * nz / (np.max(np.abs(nz)) + 1e-9) * mod
    if shimmer:
        for f in [1174.7, 1760.0, 2349.3, 2637.0, 3520.0]:
            am = np.clip(np.sin(2 * np.pi * (0.03 + 0.05 * rng.random()) * t + rng.random() * 6.28), 0, 1) ** 2
            s = np.sin(2 * np.pi * f * (1 + 0.0007 * np.sin(2 * np.pi * 0.3 * t)) * t) * am * 0.12 * shimmer
            pan = rng.uniform(-0.9, 0.9)
            a = (pan + 1) * np.pi / 4
            out[0] += s * np.cos(a)
            out[1] += s * np.sin(a)
    out *= e
    place(out, t0, gain, hall=0.1, cath=0.6)


def flute_phrase(t0, notes, beat, gain, pan=-0.25, rel=1.4):
    total = sum(b for _, b in notes) * beat
    n = int((total + rel) * SR)
    t = np.arange(n) / SR
    f = np.zeros(n)
    since = np.zeros(n)
    art = np.ones(n)
    pos = 0.0
    for m, b in notes:
        i0 = int(pos * SR)
        i1 = int((pos + b * beat) * SR)
        f[i0:i1] = mtof(m)
        since[i0:i1] = np.arange(i1 - i0) / SR
        k = min(int(0.035 * SR), i1 - i0)
        art[i0:i0 + k] = 0.55 + 0.45 * np.linspace(0, 1, k)
        pos += b * beat
    iend = int(total * SR)
    f[iend:] = mtof(notes[-1][0])
    since[iend:] = since[iend - 1] + np.arange(n - iend) / SR
    k = int(0.03 * SR)
    lf = np.convolve(np.pad(np.log(f), (k, k), mode='edge'), np.ones(k) / k, mode='same')[k:-k]
    vd = 0.0065 * np.clip((since - 0.22) / 0.45, 0, 1)
    f = np.exp(lf) * (1 + vd * np.sin(2 * np.pi * 5.6 * t))
    i, fr = phase_idx(f)
    tone = look(table('flute', notes[0][0]), i, fr)
    breath = bandf(rng.standard_normal(n), lo=1800, hi=7500)
    breath = breath / (np.max(np.abs(breath)) + 1e-9) * 0.09
    dyn = 0.85 + 0.15 * np.sin(np.pi * np.clip(t / max(total, 0.1), 0, 1))
    s = (tone + breath * (0.6 + 0.4 * (since < 0.08))) * art * dyn * env_ar(n, 0.07, rel)
    place(s.astype(np.float32), t0, gain, pan=pan, hall=0.35, cath=0.3)


# ------------------------------------------------------------------ pre-rendered one-shots
log('pre-rendering percussion')
TAIKO = [drum(150, 52, 0.04, 0.55, 2.5, 0.5, 40, 1200, 0.05, sub=0.5) for _ in range(3)]
TAIKO_BIG = drum(130, 44, 0.05, 0.8, 3.5, 0.45, 30, 1000, 0.07, sub=0.8)
FD_LO = [drum(240, 150, 0.02, 0.22, 0.9, 0.35, 300, 3000, 0.03) for _ in range(2)]
FD_HI = [drum(420, 330, 0.01, 0.08, 0.4, 0.8, 900, 6000, 0.02) for _ in range(2)]
SHAKER = noise_fx(0.12, 4000, 12000, 0.004, 0.03)
HEART = drum(90, 48, 0.03, 0.25, 1.0, 0.15, 30, 400, 0.04)
TIMP = {m: [timp_hit(m) for _ in range(2)] for m in (33, 36, 38, 41, 43, 45, 46)}
CRASH = crash()
BOOM = boom()
METAL = metal()


def taiko(t, g, pan=0.0, big=False):
    s = TAIKO_BIG if big else TAIKO[rng.integers(3)]
    place(s, t + rng.normal(0, 0.004), g * (0.92 + 0.16 * rng.random()), pan=pan, hall=0.3, cath=0.25)


def timp(t, m, g):
    place(TIMP[m][rng.integers(2)], t, g, pan=-0.1, hall=0.35, cath=0.15)


def timp_roll(t0, dur, m, g0, g1):
    k = 0
    t = t0
    while t < t0 + dur:
        x = (t - t0) / dur
        timp(t, m, (g0 + (g1 - g0) * x ** 1.7) * (0.75 + 0.25 * rng.random()) * 0.6)
        t += 0.062 + rng.normal(0, 0.004)
        k += 1


def impact(t, g=1.0, with_braam=False, notes=(26, 38, 45)):
    taiko(t, 0.95 * g, big=True)
    place(BOOM, t, 0.85 * g, hall=0.1, cath=0.3)
    place(CRASH, t, 0.32 * g, hall=0.3, cath=0.3)
    if with_braam:
        place(braam(4.5, notes), t, 0.55 * g, hall=0.25, cath=0.3)


# ------------------------------------------------------------------ harmony
CH = {
    'Dm': [38, 50, 57, 62, 65],
    'Bb': [34, 46, 53, 58, 62],
    'F': [41, 48, 57, 60, 65],
    'C': [36, 48, 55, 60, 64],
    'Gm': [43, 50, 55, 58, 62],
    'A': [45, 52, 57, 61, 64],
    'Asus': [45, 52, 57, 62, 64],
    'Dsus2': [38, 50, 57, 62, 64, 69],
    'Bbadd9': [34, 46, 53, 58, 60, 65],
}
TIMP_ROOT = {'Dm': 38, 'Bb': 46, 'F': 41, 'C': 36, 'Gm': 43, 'A': 45, 'Asus': 45}

# ================================================================== OPENING 0-21
log('opening')
ambience(0, 24.5, 0.22, fin=4.0, fout=4.5)
place(ensemble('saw', 26, 19, p=2.5, voices=4, cents=7, vib=0, att=6, rel=4, width=0.8), 0, 0.34, hall=0.2, cath=0.4)
place(ensemble('saw', 33, 19, p=2.5, voices=4, cents=7, vib=0, att=7, rel=4, width=0.8), 0, 0.22, hall=0.2, cath=0.4)
for tt, v in [(2.8, .42), (6.0, .58), (8.8, .62), (9.9, .32), (10.3, .4), (10.58, .48), (10.78, .56), (10.92, .64)]:
    taiko(tt, v)
place(noise_fx(2.2, 300, 6000, 1.9, 0.08), 8.85, 0.28, hall=0.2, cath=0.2)  # fast-push whoosh
impact(11.0, 1.0, with_braam=True, notes=(26, 38))
for a in (12.6, 14.2, 15.8):
    place(HEART, a, 0.5, hall=0.2, cath=0.2)
    place(HEART, a + 0.3, 0.3, hall=0.2, cath=0.2)
place(riser(3.0, 140, 2.5), 14.6, 0.22, hall=0.2, cath=0.3)
place(swell(2.0), 15.6, 0.3, hall=0.2, cath=0.3)
impact(17.6, 1.25, with_braam=True)
choir(17.6, [50, 57, 62, 65], 3.5, 0.2, att=0.6, rel=3.5)

# ================================================================== ACT 1 21-70
log('act 1')
b1 = 60 / 72
bar1 = 4 * b1
place(ensemble('saw', 38, 47, p=3, voices=4, cents=6, vib=0.001, att=4, rel=3, width=0.6), 20.5, 0.2, hall=0.25, cath=0.2)
place(ensemble('saw', 45, 47, p=3, voices=4, cents=6, vib=0.001, att=5, rel=3, width=0.6), 20.5, 0.13, hall=0.25, cath=0.2)
ambience(20.0, 50, 0.08, fin=4, fout=4, wind=0.6, shimmer=0.5)
bs = 21.0 + bar1
while bs < 69.9:
    prog = (bs - 24) / 46
    gm = 0.45 + 0.55 * prog
    for bt, kind, v in [(0, 'lo', 1.0), (1.5, 'hi', .45), (2, 'lo', .7), (3, 'hi', .5), (3.5, 'hi', .4)]:
        t = bs + bt * b1
        if t < 69.95:
            if kind == 'lo':
                place(FD_LO[rng.integers(2)], t, v * gm * 0.5, pan=-0.2, hall=0.3)
            else:
                place(FD_HI[rng.integers(2)], t, v * gm * 0.42, pan=0.3, hall=0.3)
    if bs >= 44:
        for k in range(8):
            place(SHAKER, bs + k * b1 / 2, 0.07 * gm * (1.3 if k % 2 == 0 else 0.8), pan=0.45, hall=0.2)
    if bs >= 54:
        taiko(bs, 0.36 * gm)
    if bs >= 61:
        taiko(bs + 2 * b1, 0.28 * gm)
    bs += bar1
P1 = [(74, 1.5), (72, .5), (74, 1), (77, 2), (79, 1), (77, .5), (74, 2.5)]
P2 = [(69, 1), (72, 1), (74, 1.5), (72, .5), (69, 1), (67, 1), (69, 3)]
P3 = [(81, 1.5), (79, .5), (77, 1), (79, 1), (81, 2), (84, 1), (81, .5), (79, .5), (77, 1), (74, 3)]
P4 = [(81, 2), (79, 1), (77, 1), (74, 4.5)]
flute_phrase(21.0 + 2 * bar1, P1, b1, 0.3)
flute_phrase(21.0 + 5 * bar1, P2, b1, 0.3)
flute_phrase(21.0 + 8 * bar1, P3, b1, 0.34)
flute_phrase(21.0 + 12 * bar1, P4, b1, 0.32)
for (t0, ch, d, g) in [(21 + 7 * bar1, 'Dm', 2 * bar1, .1), (21 + 9 * bar1, 'Bb', 2 * bar1, .12),
                       (21 + 11 * bar1, 'F', 2 * bar1, .14), (21 + 13 * bar1, 'C', bar1, .16),
                       (21 + 14 * bar1, 'Asus', 70 - (21 + 14 * bar1), .17)]:
    pad(t0, d, ch, gain=g, p=4.0, att=1.4, rel=1.4)
timp_roll(67.8, 2.2, 45, 0.1, 0.7)
place(swell(2.0), 68.0, 0.22)
impact(70.0, 0.7)

# ================================================================== ACT 2 70-120
log('act 2')
b2 = 0.75
chords2 = [(70, 'Dm', 6), (76, 'Bb', 6), (82, 'F', 6), (88, 'C', 6), (94, 'Dm', 6), (100, 'Bb', 6), (106, 'Gm', 6), (112, 'A', 8)]
padg = {70: .15, 76: .16, 82: .18, 88: .19, 94: .23, 100: .24, 106: .19, 112: .2}
for t0, ch, d in chords2:
    pad(t0, d, ch, gain=padg[t0], p=5.0 if t0 < 106 else 3.0, att=1.4 if t0 == 70 else 0.9, rel=1.6)
ARP = {'Dm': [62, 65, 69, 72, 74, 77], 'Bb': [62, 65, 67, 70, 74, 77], 'F': [65, 69, 72, 77, 81, 84],
       'C': [60, 67, 72, 74, 79, 84]}
pat = [0, 2, 4, 3, 1, 3, 5, 2]
for t0, ch, d in chords2:
    if t0 >= 106:
        break
    for br in range(2):
        for k in range(8):
            if t0 >= 100 and k % 2:
                continue
            t = t0 + br * 3 + k * 0.375
            m = ARP[ch][pat[(k + br * 3) % 8]]
            v = 0.9 if k % 4 == 0 else 0.55 + 0.25 * rng.random()
            place(pluck(m, 2.6, bright=1.0, tau=1.5), t, 0.16 * v, pan=0.32, hall=0.3, cath=0.1)
PENT = [62, 65, 67, 69, 72, 74, 77, 79, 81, 84, 86]
for tg in (81.4, 93.4):
    for j, m in enumerate(PENT[:10]):
        place(pluck(m, 2.6, bright=1.0, tau=1.5), tg + j * 0.055, 0.08 + 0.012 * j, pan=0.32, hall=0.35, cath=0.15)
LS = {}


def low_stac(m):
    if m not in LS:
        LS[m] = ensemble('saw', m, 0.22, p=5, voices=3, cents=7, vib=0, att=0.01, rel=0.14, width=0.3)
    return LS[m]


for t0, ch, d in chords2[1:7]:
    r = CH[ch][0] + 12 if CH[ch][0] < 40 else CH[ch][0]
    for k in range(16):
        m = [r, r, r + 12, r, r, r, r + 12, r + 7][k % 8]
        place(low_stac(m), t0 + k * 0.375, 0.13 * (1.2 if k % 2 == 0 else 0.8), hall=0.2)
for t0, ch, d in chords2[1:5]:
    timp(t0, TIMP_ROOT[ch], 0.45)
timp_roll(92.6, 1.4, 45, 0.1, 0.5)
timp(94, 38, 0.55)
timp(100, 46, 0.5)
timp_roll(104.6, 1.4, 45, 0.1, 0.5)
for t0 in np.arange(82, 106, 3.0):
    taiko(t0, 0.3)
    taiko(t0 + 2 * b2, 0.22)
    if t0 >= 94:
        taiko(t0 + 3.5 * b2, 0.17)
for t0, notes in [(94, [50, 57, 62]), (100, [50, 53, 58]), (106, [50, 55, 58])]:
    for m in notes:
        place(brass_note(m, 5.8, att=0.5, rel=1.0, swell=0.8), t0, 0.1, pan=-0.15, hall=0.35, cath=0.1)
flute_phrase(94.0, [(74, 2), (77, 1), (79, 1), (81, 4), (79, 1), (77, 1), (74, 2), (72, 2)], b2, 0.26, pan=-0.3)
impact(106.0, 0.75, with_braam=True, notes=(31, 43, 50))
for t0 in np.arange(106, 112, 1.5):
    place(HEART, t0, 0.35, hall=0.25, cath=0.2)
choir(114.0, [57, 61, 64], 6.0, 0.12, att=3.0, rel=0.5, vowels=('o',))
place(riser(6.0, 120, 3.0), 114.0, 0.25, hall=0.2, cath=0.3)
timp_roll(113.0, 7.0, 45, 0.05, 0.75)
place(swell(2.0), 118.0, 0.3)
impact(120.0, 1.15, with_braam=True)

# ================================================================== ACT 3 120-200
log('act 3')
b3 = 0.6
prog3 = ['Dm', 'Bb', 'F', 'C', 'Dm', 'Bb', 'F', 'C', 'Dm', 'Bb', 'F', 'C', 'Dm', 'Bb', 'F', 'C', 'A']
SPIC = {'Dm': [57, 62, 65, 69], 'Bb': [58, 62, 65, 70], 'F': [57, 60, 65, 69], 'C': [55, 60, 64, 67], 'A': [57, 61, 64, 69]}
BRS = {'Dm': [50, 57, 62], 'Bb': [50, 53, 58], 'F': [53, 57, 60], 'C': [52, 55, 60], 'A': [52, 57, 61]}
pat16 = [0, 2, 1, 2, 0, 2, 1, 3, 0, 2, 1, 2, 0, 3, 2, 1]
SP = {}


def spic(m):
    if m not in SP:
        SP[m] = ensemble('saw', m, 0.1, p=7, voices=3, cents=8, vib=0, att=0.006, rel=0.12, width=0.8)
    return SP[m]


def lvl3(t0):
    if t0 < 139:
        return 0.45
    if t0 < 158:
        return 0.65
    if t0 < 168:
        return 0.8
    if t0 < 187:
        return 1.0
    if t0 < 192:
        return 0.6
    if t0 < 196:
        return 0.42
    return 0.32


for i, ch in enumerate(prog3):
    t0 = 120 + i * 4.8
    d = 4.8 if i < 16 else 3.2
    L = lvl3(t0)
    pad(t0, d, ch, gain=0.08 + 0.13 * L, p=5.5, att=0.4 if i else 0.2, rel=1.0, bassgain=1.0)
    if t0 < 192:
        for k in range(int(round(d / 0.15))):
            m = SPIC[ch][pat16[k % 16]] + (12 if (L >= 1.0 and (k // 16) % 2 == 1) else 0)
            acc = 1.0 if k % 4 == 0 else 0.62
            place(spic(m), t0 + k * 0.15, 0.11 * L * acc, pan=0.25 * np.sin(k * 0.7), hall=0.25)
        r = CH[ch][0] + 12 if CH[ch][0] < 40 else CH[ch][0]
        for k in range(8):
            place(low_stac([r, r + 12][k % 2]), t0 + k * 0.6, 0.12 * L, hall=0.2)
    for br in range(2):
        bt0 = t0 + br * 2.4
        if 124.8 <= bt0 < 158.4:
            taiko(bt0, 0.34 * L / 0.65)
            taiko(bt0 + 2 * b3, 0.24 * L / 0.65)
        elif 158.4 <= bt0 < 168:
            for bt, v in [(0, .4), (1.5, .22), (2, .32), (3, .22)]:
                taiko(bt0 + bt * b3, v)
        elif 168 <= bt0 < 187.2:
            for bt, v in [(0, .5), (1, .25), (1.5, .3), (2, .42), (3, .28), (3.5, .32)]:
                taiko(bt0 + bt * b3, v)
            for k in range(8):
                place(FD_HI[k % 2], bt0 + k * b3 / 2, 0.1 * (1.3 if k % 2 == 0 else 0.8), pan=0.35, hall=0.2)
        if 153.6 <= bt0 < 168:
            for bt, pn in [(1, -0.5), (3, 0.5)]:
                place(METAL, bt0 + bt * b3, 0.05, pan=pn, hall=0.35)
    if 148.8 <= t0 < 192:
        g = 0.07 if t0 < 168 else 0.1
        if t0 >= 187.2:
            g = 0.06
        for m in BRS[ch]:
            place(brass_note(m, d, att=0.3, rel=0.8, swell=0.7), t0, g, pan=-0.2, hall=0.35, cath=0.1)
    if 172.8 <= t0 < 192:
        choir(t0, [m + 12 for m in BRS[ch]], d, 0.16 if t0 < 187 else 0.1, att=0.5, rel=1.4)
MEL3 = [(168.0, [(69, 2), (72, 2), (74, 2), (72, 2)]), (172.8, [(67, 3), (64, 1), (67, 2), (72, 2)]),
        (177.6, [(74, 4), (69, 2), (72, 2)]), (182.4, [(70, 3), (69, 1), (65, 2), (70, 2)]), (187.2, [(69, 8)])]
for t0, line in MEL3:
    t = t0
    for m, bt in line:
        d = bt * b3
        s = brass_note(m, d * 0.95, att=0.08, rel=0.35, swell=0.6, voices=4)
        place(s, t, 0.17 if t0 < 187 else 0.11, pan=0.15, hall=0.4, cath=0.15)
        place(brass_note(m - 12, d * 0.95, att=0.08, rel=0.35, swell=0.6), t, 0.1, pan=-0.15, hall=0.35)
        t += d
place(noise_fx(2.0, 2000, 11000, 0.06, 0.9), 152.4, 0.12, pan=0.0, hall=0.3)
for tc, g in [(139.2, .16), (158.4, .22), (168.0, .3), (187.2, .28)]:
    place(CRASH, tc, g, hall=0.3, cath=0.25)
place(riser(2.4, 160, 2.5), 165.6, 0.22, hall=0.2, cath=0.2)
place(riser(2.8, 160, 3.0), 174.8, 0.28, hall=0.2, cath=0.2)
impact(177.6, 1.15, with_braam=True)
place(noise_fx(10.5, 25, 220, 1.6, 4.0), 175.8, 0.42, hall=0.15, cath=0.2)  # rocket rumble
timp_roll(198.2, 1.8, 45, 0.04, 0.22)

# ================================================================== ACT 4 200-300
log('act 4')
prog4 = [(200, 8, 'Dm'), (208, 8, 'Bb'), (216, 8, 'Gm'), (224, 4, 'A'), (228, 6, 'Dm'), (234, 6, 'Bb'),
         (240, 6, 'F'), (246, 6, 'C'), (252, 3.5, 'Bb'), (255.5, 3.5, 'F'), (259, 3.5, 'C'), (262.5, 3.5, 'Dm')]
PIANO = {'Dm': [62, 65, 69, 74], 'Bb': [58, 62, 65, 70], 'Gm': [55, 58, 62, 67], 'A': [57, 61, 64, 69],
         'F': [60, 65, 69, 72], 'C': [60, 64, 67, 72]}
ppat = [0, 1, 2, 1, 3, 1, 2, 1]
timp(200.0, 38, 0.25)
place(ensemble('saw', 26, 26, p=2.5, voices=4, cents=7, vib=0, att=4, rel=4, width=0.8), 200, 0.22, hall=0.2, cath=0.4)
ambience(200, DUR - 200, 0.1, fin=6, fout=6, wind=0.35, shimmer=1.0)
for t0, d, ch in prog4:
    if t0 < 228:
        g, p = 0.09, 3.5
    elif t0 < 252:
        g, p = 0.12 + 0.07 * (t0 - 228) / 18, 4.5
    else:
        g, p = 0.27, 6.0
    pad(t0, d, ch, gain=g, p=p, att=2.0 if t0 < 228 else (1.0 if t0 < 252 else 0.3), rel=1.6 if t0 < 262 else 2.5)
    if t0 < 252:
        n8 = int(round(d / (1 / 3)))
        for k in range(n8):
            m = PIANO[ch][ppat[k % 8]]
            v = 1.0 if k % 4 == 0 else 0.7
            place(pluck(m, 2.4, bright=0.55, tau=1.3, pos=0.12), t0 + k / 3, (0.1 if t0 < 228 else 0.12) * v, pan=0.1, hall=0.45, cath=0.2)
    if 228 <= t0 < 252:
        choir(t0, [m + 12 for m in PIANO[ch][:3]], d, 0.06 + 0.06 * (t0 - 228) / 18, att=1.5, rel=1.2, vowels=('o',))
    if t0 >= 252:
        choir(t0, [m + 12 for m in PIANO[ch][:3]], d, 0.2, att=0.4, rel=2.2 if t0 >= 262 else 1.0)
        for m in BRS.get(ch, BRS['Dm']):
            place(brass_note(m, d, att=0.2, rel=1.2, swell=0.8), t0, 0.1, pan=-0.2, hall=0.4, cath=0.15)
for t0 in np.arange(240, 246, 8 / 3):
    taiko(t0, 0.3)
    taiko(t0 + 4 / 3, 0.22)
for k, t0 in enumerate(np.arange(246, 252, 2 / 3)):
    taiko(t0, 0.22 + 0.03 * k)
for t0 in np.arange(246, 252, 6):
    for m in BRS['C']:
        place(brass_note(m, 6, att=1.5, rel=0.4, swell=1.0), t0, 0.09, pan=-0.2, hall=0.4)
timp_roll(249.5, 2.5, 45, 0.1, 0.65)
place(riser(4.0, 150, 3.0), 248.0, 0.28, hall=0.2, cath=0.3)
impact(252.0, 1.2, with_braam=True, notes=(22, 34, 41))
for t0 in np.arange(252, 266, 8 / 3):
    for bt, v in [(0, .5), (1.5, .3), (2, .42), (3, .3)]:
        if t0 + bt * 2 / 3 < 265.8:
            taiko(t0 + bt * 2 / 3, v)
for tc, g in [(259.0, .3), (262.5, .3)]:
    place(CRASH, tc, g, hall=0.3, cath=0.3)
MEL4 = [(252.0, [(74, 2.0), (72, 0.75), (70, 0.75)]), (255.5, [(69, 2.5), (72, 1.0)]),
        (259.0, [(67, 1.75), (72, 1.75)]), (262.5, [(74, 3.5)])]
for t0, line in MEL4:
    t = t0
    for m, d in line:
        rl = 0.6 if d < 3 else 2.0
        place(brass_note(m, d * 0.96, att=0.1, rel=rl, swell=0.7, voices=4), t, 0.17, pan=0.15, hall=0.4, cath=0.2)
        place(brass_note(m - 12, d * 0.96, att=0.1, rel=rl, swell=0.7), t, 0.1, pan=-0.15, hall=0.4, cath=0.15)
        t += d
# landing at 266.3 (user's cut: station -> child cross-fade 266.4-266.7), then ethereal choir alone
place(CRASH, 266.3, 0.16, hall=0.3, cath=0.5)
timp(266.3, 38, 0.25)
place(BOOM, 266.3, 0.3, hall=0.1, cath=0.4)
log('ending choir')
# user's ending: question 1 at 271.2-274.6, question 2 at 275.7-278.3, hard cut to the end shot at 278.3
choir(266.3, CH['Dsus2'][1:], 9.5, 0.2, att=2.5, rel=3.0, hall=0.2, cath=0.8)
choir(275.6, CH['Bbadd9'][1:], 3.4, 0.19, att=1.5, rel=3.0, hall=0.2, cath=0.8)
choir(278.3, CH['Dsus2'][1:], 5.8, 0.19, att=2.5, rel=5.0, hall=0.2, cath=0.8)
t = 267.0
for m, d in [(81, 2.7), (79, 1.35), (77, 2.7), (74, 3.6), (81, 4.5)]:
    rl = 4.0 if t > 278 else 1.4
    s = ensemble('u', m, d, voices=3, cents=6, vib=0.005, vibrate=5.2, att=0.9, rel=rl, width=0.5)
    place(s, t, 0.09, hall=0.2, cath=0.9)
    t += d + (0.3 if d >= 2.7 else 0)

# ================================================================== REVERB + MASTER
log('reverb')


def make_ir(rt, dur, pre, seed):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    ir = np.zeros((2, n), np.float64)
    for c in range(2):
        nz = r.standard_normal(n)
        lo = bandf(nz, hi=700)
        mid = bandf(nz, lo=700, hi=3500)
        hi = bandf(nz, lo=3500, hi=12000)
        ir[c] = lo * np.exp(-6.91 * t / rt) + 0.8 * mid * np.exp(-6.91 * t / (rt * 0.7)) + 0.45 * hi * np.exp(-6.91 * t / (rt * 0.4))
        k = int(0.02 * SR)
        ir[c, :k] *= np.linspace(0, 1, k)
    ir = np.concatenate([np.zeros((2, int(pre * SR))), ir], axis=1)
    ir /= np.sqrt(np.sum(ir ** 2) / 2)
    return ir


def convolve(bus, ir):
    L = N + ir.shape[1]
    nfft = 1 << int(np.ceil(np.log2(L)))
    out = np.zeros((2, N), np.float32)
    for c in range(2):
        X = np.fft.rfft(bus[c].astype(np.float64), nfft)
        X *= np.fft.rfft(ir[c], nfft)
        out[c] = np.fft.irfft(X, nfft)[:N].astype(np.float32)
        del X
    return out


def movavg(x, k):
    cs = np.concatenate([[0.0], np.cumsum(x, dtype=np.float64)])
    y = (cs[k:] - cs[:-k]) / k
    pad_l = k // 2
    pad_r = len(x) - len(y) - pad_l
    return np.concatenate([np.full(pad_l, y[0]), y, np.full(pad_r, y[-1])])


hall_wet = convolve(HALL, make_ir(2.6, 4.5, 0.025, 11))
del HALL
log('hall done')
cath_wet = convolve(CATH, make_ir(5.5, 9.0, 0.045, 12))
del CATH
log('cathedral done')
mix = DRY + 0.9 * hall_wet + 0.85 * cath_wet
del hall_wet, cath_wet
log('master')
for c in range(2):
    mix[c] = bandf(mix[c], lo=28, order=2)
mix = norm(mix, 1.0)
p = (mix[0].astype(np.float64) ** 2 + mix[1].astype(np.float64) ** 2) / 2
rms = np.sqrt(np.maximum(movavg(p, int(0.05 * SR)), 1e-12))
lvl = 20 * np.log10(rms + 1e-9)
gr = -np.maximum(lvl - (-20.0), 0) * (1 - 1 / 2.5)
g = movavg(10 ** (gr / 20), int(0.12 * SR)).astype(np.float32)
mix *= g
mix = norm(mix, 1.0)
mix = np.tanh(mix * 1.25) / np.tanh(1.25)
fo = int(5 * SR)
mix[:, N_VIDEO - fo:N_VIDEO] *= (np.cos(np.linspace(0, np.pi / 2, fo)) ** 2).astype(np.float32)
mix[:, N_VIDEO:] = 0
fi = int(0.02 * SR)
mix[:, :fi] *= np.linspace(0, 1, fi).astype(np.float32)
mix = norm(mix, 0.94)
print('section loudness (start s, RMS dBFS, peak dBFS):')
for s in range(0, int(DUR), 10):
    seg = mix[:, s * SR:(s + 10) * SR]
    print(f'  {s:3d}  {20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9):6.1f}  {20 * np.log10(np.max(np.abs(seg)) + 1e-9):6.1f}')
pcm = (np.clip(mix.T, -1, 1) * 32767).astype('<i2')
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
log('wrote', OUT)

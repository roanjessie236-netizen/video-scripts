"""v3 time warp: v1/user time t (s) -> new output time u = W(t).
Piecewise-constant playback factors f (new duration / old) per music act, chosen so the narration has room where it was
dense and tightened where it was slack. Offsets at f=1 blocks and at the user's ending are whole frames (1/24 s)."""
import numpy as np
FPS = 24
T_END_A = 6393 / 24          # 266.375: start of the user's own ending cut (kept unchanged, only offset)
BLOCKS = [  # (t0, t1, f)
    (0.0, 21.0, 1.0),         # opening (music-led: taiko build, earth impact 11.0, title 17.6)
    (21.0, 70.0, 1.2),        # act 1 / chapter 1 (cognitive revolution): dense narration
    (70.0, 120.0, 1.25),      # act 2 / chapter 2 (agricultural revolution): densest -> slowest
    (120.0, 168.0, 1.2),      # act 3 / chapter 3 (unification, science, industry)
    (168.0, 187.2, 1 - 1.9 / 19.2),   # act 3 climax (electricity, rocket, moon): sped up (4:3 tempo shift)
    (187.2, 200.0, 1.0),      # act 3 tail (net earth)
    (200.0, T_END_A, 1 - (127 / 24) / (T_END_A - 200.0)),  # act 4 / chapter 4 (future): sped up slightly
]
_U = [0.0]
for t0, t1, f in BLOCKS:
    _U.append(_U[-1] + (t1 - t0) * f)
OFF_END = _U[-1] - T_END_A   # constant offset of the ending


def f_at(t):
    for t0, t1, f in BLOCKS:
        if t0 <= t < t1:
            return f
    return 1.0


def W(t):
    t = float(t)
    if t < 0:
        return t
    for (t0, t1, f), u0 in zip(BLOCKS, _U):
        if t < t1:
            return u0 + (t - t0) * f
    return t + OFF_END


def Winv(u):
    u = float(u)
    if u < 0:
        return u
    for (t0, t1, f), u0, u1 in zip(BLOCKS, _U, _U[1:]):
        if u < u1:
            return t0 + (u - u0) / f
    return u - OFF_END


N_OLD = 6819
J_END_OLD = 6393
J_END_NEW = int(round(_U[-1] * FPS))
N_NEW = N_OLD + (J_END_NEW - J_END_OLD)

if __name__ == '__main__':
    for (t0, t1, f), u0, u1 in zip(BLOCKS, _U, _U[1:]):
        print('%7.2f-%7.2f f=%.4f -> %7.3f-%7.3f  (%.2f s -> %.2f s, offset end %.4f s = %.3f fr)' % (
            t0, t1, f, u0, u1, t1 - t0, u1 - u0, u1 - t1, (u1 - t1) * 24))
    print('ending offset %.4f s (%d frames), new frames %d = %.3f s' % (OFF_END, J_END_NEW - J_END_OLD, N_NEW, N_NEW / 24))

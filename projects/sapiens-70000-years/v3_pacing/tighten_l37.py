"""v3.2: shorten the pause after 「成为」 in line 37 from ~0.19 s to ~0.10 s by removing 90 ms from the middle of the
silence (2.515-2.605 s in the trimmed TTS clip, all below -54 dB re peak), 5 ms equal-power crossfade; then +0.4 dB."""
import subprocess, sys, numpy as np
SR = 48000
src, dst = sys.argv[1], sys.argv[2]
x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', src, '-f', 'f32le', '-ac', '1', 'pipe:']), np.float32).astype(np.float64)
a, b, xf = int(2.515 * SR), int(2.605 * SR), int(0.005 * SR)
t = np.linspace(0, np.pi / 2, xf)
mid = x[a - xf // 2:a - xf // 2 + xf] * np.cos(t) + x[b - xf // 2:b - xf // 2 + xf] * np.sin(t)
y = np.concatenate([x[:a - xf // 2], mid, x[b - xf // 2 + xf:]]) * 10 ** (0.4 / 20)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f64le', '-ar', str(SR), '-ac', '1', '-i', 'pipe:', '-c:a', 'pcm_s16le', dst], input=y.tobytes(), check=True)
print('%.3f s -> %.3f s' % (len(x) / SR, len(y) / SR))

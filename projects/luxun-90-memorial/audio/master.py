# 母带：整体增益到约 -16 LUFS，限幅到 -1.5 dBTP；分轨用同一增益（不限幅）；切上下两段
import json, re, subprocess
def meas(src, ch=2):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-f', 'f32le', '-ar', '48000', '-ac', str(ch), '-i', src, '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return json.loads(r[r.rindex('{'):r.rindex('}') + 1])
j = meas('mix_full.f32'); gain = -16.0 - float(j['input_i']); print('input I', j['input_i'], 'TP', j['input_tp'], 'gain', round(gain, 2))
inp = ['-f', 'f32le', '-ar', '48000', '-ac', '2', '-i']
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['mix_full.f32', '-af', f'volume={gain:.2f}dB,alimiter=limit=0.80:attack=4:release=60:level=disabled:asc=1,aresample=48000',
                '-c:a', 'pcm_s16le', 'mix_full.wav'], check=True)
for s in ['stem_vo', 'stem_mus']:
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + [f'{s}_full.f32', '-af', f'volume={gain:.2f}dB', '-c:a', 'aac', '-b:a', '256k', f'{s}.m4a'], check=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', 'mix_full.wav', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
s = r[r.rindex('Summary:'):]
print('final I', re.search(r'I:\s+(-?[\d.]+)', s).group(1), 'LRA', re.search(r'LRA:\s+(-?[\d.]+)', s).group(1), 'TP', re.search(r'Peak:\s+(-?[\d.]+)', s).group(1))

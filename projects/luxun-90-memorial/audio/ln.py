import json, subprocess, sys
def ln(src, ch, out, extra):
    inp = ['-f', 'f32le', '-ar', '48000', '-ac', str(ch), '-i', src]
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats'] + inp + ['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    af = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000")
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-af', af] + extra + [out], check=True)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', out, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = r[r.rindex('Summary:'):]; import re
    print(out, 'I', re.search(r'I:\s+(-?[\d.]+)', s).group(1), 'peak', re.search(r'Peak:\s+(-?[\d.]+)', s).group(1))
for t in sys.argv[1:]:
    ln(f'mix_{t}.f32', 2, f'mix_{t}.wav', ['-c:a', 'pcm_s16le'])
    ln(f'long_{t}.f32', 1, f'long_{t}.mp3', ['-c:a', 'libmp3lame', '-b:a', '192k'])

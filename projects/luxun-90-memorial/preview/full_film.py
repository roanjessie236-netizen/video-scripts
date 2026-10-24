# 全片合成：六条分章样片＋全片片尾（credits_full.py）→ /tmp/full/luxun90_preview_v3_full.mp4
# 每章取到“正片结束−0.5 秒”（各章片尾交叉淡入从这里开始），末 0.4 秒淡出到黑，再补黑场到正片结束点，保持 B站母版时间点；
# 尾声取到 143.96 秒，与全片片尾叠化 1 秒。另写入章节标记（B站/播放器可跳转）。
import subprocess, sys
D = '/tmp/full/'; FPS = 25
CH = [('luxun90_preview_v3_S0-S1_r2.mp4', 179.5), ('luxun90_preview_v3_S2_r2.mp4', 153.25), ('luxun90_preview_v3_S3-S4_r2.mp4', 274.47),
      ('luxun90_preview_v3_S5.mp4', 117.48), ('luxun90_preview_v3_S6.mp4', 261.25)]
LAST, LAST_END, CR, XF = 'luxun90_preview_v3_S7.mp4', 3599, 'credits.mp4', 25      # 尾声帧数（143.96 秒）、叠化 1 秒
cum, F, segs = 0.0, [0], []
for f, tm in CH:
    cum += tm; F.append(int(cum * FPS + 0.5)); seg = F[-1] - F[-2]; segs.append((f, seg - 13, 13))   # 0.52 秒黑场
fc, labels = [], []
for i, (f, n, pad) in enumerate(segs):
    fc.append(f'[{i}:v]trim=end_frame={n},setpts=PTS-STARTPTS,settb=AVTB,fps=25,setsar=1,fade=t=out:start_frame={n-10}:nb_frames=10,'
              f'tpad=stop={pad}:stop_mode=add:color=black[c{i}]')
    labels.append(f'[c{i}]')
k = len(segs)
fc.append(f'[{k}:v]trim=end_frame={LAST_END},setpts=PTS-STARTPTS,settb=AVTB,fps=25,setsar=1[e0]')
fc.append(f'[{k+1}:v]setpts=PTS-STARTPTS,settb=AVTB,fps=25,setsar=1[e1]')
fc.append(f'[e0][e1]xfade=transition=fade:duration={XF/FPS}:offset={(LAST_END-XF)/FPS}[c{k}]')
labels.append(f'[c{k}]')
fc.append(''.join(labels) + f'concat=n={k+1}:v=1:a=0,format=yuv420p[v]')
crf = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames',
                          '-of', 'csv=p=0', D + CR], capture_output=True, text=True).stdout)
TOTAL = F[-1] + LAST_END - XF + crf
# 章节标记（秒）：序、一在第一条内 68.0；四在第三条内 102.8；片尾从叠化起
marks = [('序｜一份不让人纪念的遗嘱', 0), ('一｜绍兴　坠入困顿', 68.0), ('二｜南京·东京·仙台　弃医从文', F[1] / FPS), ('三｜北京　从沉默到呐喊', F[2] / FPS),
         ('四｜北京　彷徨与反抗绝望', F[2] / FPS + 102.8), ('五｜厦门·广州　思路轰毁', F[3] / FPS), ('六｜上海　新的信念与横站', F[4] / FPS),
         ('尾声｜1936　最后的光', F[5] / FPS), ('片尾', (F[5] + LAST_END - XF) / FPS)]
with open(D + 'chapters.txt', 'w', encoding='utf-8') as fh:
    fh.write(';FFMETADATA1\ntitle=忘记我——鲁迅逝世九十周年（样片 v3 全片，无配音）\n')
    for j, (t, s) in enumerate(marks):
        e = marks[j + 1][1] if j + 1 < len(marks) else TOTAL / FPS
        fh.write(f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(s*1000)}\nEND={int(e*1000)}\ntitle={t}\n')
for t, s in marks: print(f'{int(s//60):02d}:{s%60:05.2f}  {t}')
print('total frames', TOTAL, '=', TOTAL / FPS, 's')
if '--dry' in sys.argv: print(';\n'.join(fc)); sys.exit(0)
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-stats']
for f, _, _ in segs: cmd += ['-i', D + f]
cmd += ['-i', D + LAST, '-i', D + CR, '-f', 'ffmetadata', '-i', D + 'chapters.txt',
        '-filter_complex', ';'.join(fc), '-map', '[v]', '-map_metadata', str(k + 2), '-map_chapters', str(k + 2),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-maxrate', '4M', '-bufsize', '8M', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart', '-an', D + 'luxun90_preview_v3_full.mp4']
subprocess.run(cmd, check=True); print('done')

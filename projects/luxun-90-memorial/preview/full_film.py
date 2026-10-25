# 全片合成：六条分章样片＋全片片尾（credits_full.py）→ /tmp/full/luxun90_preview_v3_full.mp4
# 每章取到“正片结束−0.5 秒”（各章片尾交叉淡入从这里开始），末 0.4 秒淡出到黑，再补黑场到正片结束点，保持 B站母版时间点；
# 尾声取到 143.96 秒，与全片片尾叠化 1 秒。另写入章节标记（B站/播放器可跳转）。
# --part 1：序—四（0—607.24 秒）；--part 2：五—片尾（607.24 秒起）；两段首尾相接即全片。不带参数输出整片。
import subprocess, sys
D = '/tmp/full/'; FPS = 25
CH = [('luxun90_preview_v3_S0-S1_r2.mp4', 179.5), ('luxun90_preview_v3_S2_r2.mp4', 153.25), ('luxun90_preview_v3_S3-S4_r2.mp4', 274.47),
      ('luxun90_preview_v3_S5.mp4', 117.48), ('luxun90_preview_v3_S6.mp4', 261.25)]
LAST, LAST_END, CR, XF = 'luxun90_preview_v3_S7.mp4', 3599, 'credits.mp4', 25      # 尾声帧数（143.96 秒）、叠化 1 秒
SPLIT = 3                                                                              # 分段时第 2 段从第 4 条（S5）开始
cum, F, segs = 0.0, [0], []
for f, tm in CH:
    cum += tm; F.append(int(cum * FPS + 0.5)); seg = F[-1] - F[-2]; segs.append((f, seg - 13, 13))   # 0.52 秒黑场
CR_N = 450                                                                             # 片尾 18 秒
TOTAL = F[-1] + LAST_END - XF + CR_N
marks = [('序｜一份不让人纪念的遗嘱', 0), ('一｜绍兴　坠入困顿', 68.0), ('二｜南京·东京·仙台　弃医从文', F[1] / FPS), ('三｜北京　从沉默到呐喊', F[2] / FPS),
         ('四｜北京　彷徨与反抗绝望', F[2] / FPS + 102.8), ('五｜厦门·广州　思路轰毁', F[3] / FPS), ('六｜上海　新的信念与横站', F[4] / FPS),
         ('尾声｜1936　最后的光', F[5] / FPS), ('片尾', (F[5] + LAST_END - XF) / FPS)]
part = int(sys.argv[sys.argv.index('--part') + 1]) if '--part' in sys.argv else 0
use = {0: range(len(segs)), 1: range(SPLIT), 2: range(SPLIT, len(segs))}[part]
tail = part != 1                                                                       # 是否含尾声＋片尾
t0, t1 = (F[SPLIT] / FPS if part == 2 else 0.0), (F[SPLIT] / FPS if part == 1 else TOTAL / FPS)
out = D + {0: 'luxun90_preview_v3_full.mp4', 1: 'part1.mp4', 2: 'part2.mp4'}[part]
fc, labels, inputs = [], [], []
for i in use:
    f, n, pad = segs[i]; j = len(inputs); inputs.append(f)
    fc.append(f'[{j}:v]trim=end_frame={n},setpts=PTS-STARTPTS,settb=AVTB,fps=25,setsar=1,fade=t=out:start_frame={n-10}:nb_frames=10,'
              f'tpad=stop={pad}:stop_mode=add:color=black[c{j}]')
    labels.append(f'[c{j}]')
if tail:
    j = len(inputs); inputs += [LAST, CR]
    fc.append(f'[{j}:v]trim=end_frame={LAST_END},setpts=PTS-STARTPTS,settb=AVTB,fps=25,setsar=1[e0]')
    fc.append(f'[{j+1}:v]setpts=PTS-STARTPTS,settb=AVTB,fps=25,setsar=1[e1]')
    fc.append(f'[e0][e1]xfade=transition=fade:duration={XF/FPS}:offset={(LAST_END-XF)/FPS}[c{j}]')
    labels.append(f'[c{j}]')
fc.append(''.join(labels) + f'concat=n={len(labels)}:v=1:a=0,format=yuv420p[v]')
mk = [(t, s - t0) for t, s in marks if t0 <= s < t1]
with open(D + f'chapters{part}.txt', 'w', encoding='utf-8') as fh:
    fh.write(';FFMETADATA1\ntitle=忘记我——鲁迅逝世九十周年（样片 v3 全片' + {0: '', 1: '·上', 2: '·下'}[part] + '，无配音）\n')
    for j, (t, s) in enumerate(mk):
        e = mk[j + 1][1] if j + 1 < len(mk) else t1 - t0
        fh.write(f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(round(s*1000))}\nEND={int(round(e*1000))}\ntitle={t}\n')
for t, s in mk: print(f'{int(s//60):02d}:{s%60:05.2f}  {t}')
print('part', part, 'frames', int(round((t1 - t0) * FPS)), '=', round(t1 - t0, 2), 's')
if '--dry' in sys.argv: print(';\n'.join(fc)); sys.exit(0)
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-stats']
for f in inputs: cmd += ['-i', D + f]
k = len(inputs)
cmd += ['-f', 'ffmetadata', '-i', D + f'chapters{part}.txt',
        '-filter_complex', ';'.join(fc), '-map', '[v]', '-map_metadata', str(k), '-map_chapters', str(k),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-maxrate', '4M', '-bufsize', '8M', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart', '-an', out]
subprocess.run(cmd, check=True); print('done', out)

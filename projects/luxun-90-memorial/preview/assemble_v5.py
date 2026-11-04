# 全片 v5 合成：上段＝v4 上段的序—第二章（换水印）＋新渲染的第三、四章；下段＝v4 下段（换水印）；配 mix_full.wav；写章节
import subprocess, sys, json
D = '/tmp/full/'; FPS = 25
m = json.load(open('/tmp/vo/tl_meta.json')); F = m['F']; END = m['END']; ST = m['ST34']
SPLIT = F[3] / FPS                                   # 627.08
WM = 'delogo=x=1690:y=995:w=196:h=46:enable=\'{e}\''
OV = 'overlay=1789:994:enable=\'{e}\''
ENC = ['-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-maxrate', '4M', '-bufsize', '8M', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
       '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart']
def chap(path, title, mk, tot):
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(f';FFMETADATA1\ntitle={title}\n')
        for j, (t, s) in enumerate(mk):
            e = mk[j + 1][1] if j + 1 < len(mk) else tot
            fh.write(f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(round(s*1000))}\nEND={int(round(e*1000))}\ntitle={t}\n')
part = sys.argv[1]
if part == 'up':
    tot = SPLIT; n34 = F[3] - F[2]                     # 7358 帧
    mk = [('序｜一份不让人纪念的遗嘱', 0), ('一｜绍兴　坠入困顿', 68.0), ('二｜南京·东京·仙台　弃医从文', F[1] / FPS),
          ('三｜北京　从沉默到呐喊', F[2] / FPS), ('四｜北京　彷徨与反抗绝望', F[2] / FPS + ST['S4-01'])]
    chap(D + 'ch_up.txt', '忘记我——鲁迅逝世九十周年（全片 v5·上，配音版）', mk, tot)
    e_old = f'lt(t,{F[1]/FPS-0.54:.2f})+between(t,{F[1]/FPS},{F[2]/FPS-0.52:.2f})'
    fc = [f'[0:v]trim=end_frame={F[2]},setpts=PTS-STARTPTS,settb=AVTB,fps=25,setsar=1,format=yuv420p,{WM.format(e=e_old)}[a0]',
          f'[a0][3:v]{OV.format(e=e_old)}[u0]',
          f'[1:v][2:v]concat=n=2:v=1:a=0,trim=end_frame={n34-13},setpts=PTS-STARTPTS,settb=AVTB,fps=25,setsar=1,format=yuv420p,'
          f'fade=t=out:start_frame={n34-23}:nb_frames=10,tpad=stop=13:stop_mode=add:color=black[b]',
          '[u0][b]concat=n=2:v=1:a=0,format=yuv420p[v]',
          f'[4:a]atrim=0:{tot},asetpts=PTS-STARTPTS[a]']
    ins = ['-i', D + 'v4_up.mp4', '-i', D + 'r34/p0.mp4', '-i', D + 'r34/p1.mp4', '-i', D + 'wm_v5.png', '-i', '/tmp/vo/mix_full.wav',
           '-f', 'ffmetadata', '-i', D + 'ch_up.txt']; k = 5; out = D + 'out/忘记我_全片v5_上.mp4'
else:
    tot = END - SPLIT; r = lambda f: (f - F[3]) / FPS
    c6, c7 = r(F[4]), r(F[5]); cr = r(F[5] + 3574)    # 片尾起点（尾声 143.96 秒与片尾叠化 1 秒）
    mk = [('五｜厦门·广州　思路轰毁', 0), ('六｜上海　新的信念与横站', c6), ('尾声｜1936　最后的光', c7), ('片尾', cr)]
    chap(D + 'ch_lo.txt', '忘记我——鲁迅逝世九十周年（全片 v5·下，配音版）', mk, tot)
    e_del = f'lt(t,{c6-0.52:.2f})+between(t,{c6},{c7-0.52:.2f})+between(t,{c7},{cr+1:.2f})'
    e_new = f'lt(t,{c6-0.52:.2f})+between(t,{c6},{c7-0.52:.2f})+between(t,{c7},{cr+0.5:.2f})'
    fc = [f'[0:v]setpts=PTS-STARTPTS,settb=AVTB,fps=25,setsar=1,format=yuv420p,{WM.format(e=e_del)}[a0]',
          f'[a0][1:v]{OV.format(e=e_new)},format=yuv420p[v]',
          f'[2:a]atrim={SPLIT}:{END},asetpts=PTS-STARTPTS[a]']
    ins = ['-i', D + 'v4_lo.mp4', '-i', D + 'wm_v5.png', '-i', '/tmp/vo/mix_full.wav', '-f', 'ffmetadata', '-i', D + 'ch_lo.txt']
    k = 3; out = D + 'out/忘记我_全片v5_下.mp4'
for t, s in mk: print(f'{int(s//60):02d}:{s%60:05.2f}  {t}')
print(part, 'dur', round(tot, 2), out)
if '--dry' in sys.argv: print(';\n'.join(fc)); sys.exit(0)
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-stats'] + ins + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]',
       '-map_metadata', str(k), '-map_chapters', str(k), '-t', f'{tot:.3f}'] + ENC + [out]
subprocess.run(cmd, check=True); print('done', out)

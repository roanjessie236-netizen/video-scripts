"""Mix per-line narration into a film (score = the video's audio track) and write a mix report. (from 21-lessons-ai-era, reused for Sapiens v2)

Usage: python3 mix_tl.py VIDEO SUBS.srt CLIP_DIR OUT.mp4 [--music-db -5] [--duck-thr 0.05] [--duck-ratio 3]
                                                          [--voice-lufs -16] [--target-lufs -14] [--fit CLIP_DIR/fit.json]
Placement = sapiens mix_voice.py rule: start on the subtitle; a clip longer than its slot may lead by
<= LEAD s; later lines are pushed so nothing overlaps.
Chain: voice EQ/comp/room -> stereo stem at VOICE_LUFS; film score at MUSIC_DB + sidechain duck under voice;
sum -> gain to TARGET_LUFS -> limiter (-1.5 dBFS) -> AAC 256k / 48 kHz; video stream copied untouched.
Writes OUT, OUT-base.srt (voice timing), OUT-base_report.md, OUT-base_work/ (wav stems).
"""
import argparse, json, os, re, subprocess
import numpy as np

SR = 48000
VOICE_CHAIN = ('highpass=f=70,equalizer=f=150:t=q:w=1.2:g=1.5,equalizer=f=3000:t=q:w=1.5:g=1.5,'
               'acompressor=threshold=-20dB:ratio=3:attack=5:release=120,'
               'aecho=0.8:0.5:40|80:0.10|0.05,pan=stereo|c0=c0|c1=c0')


def run(cmd): subprocess.run(cmd, check=True)


def ts(s):
    h, m, r = s.strip().split(':'); a, b = r.split(',')
    return int(h) * 3600 + int(m) * 60 + int(a) + int(b) / 1000


def fts(t):
    ms = int(round(max(0, t) * 1000))
    return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def read_srt(p):
    out = []
    for b in open(p, encoding='utf-8-sig').read().strip().split('\n\n'):
        l = b.strip().split('\n')
        if len(l) < 3: continue
        a, z = l[1].split(' --> ')
        out.append(dict(i=int(l[0]), s=ts(a), e=ts(z), text='\n'.join(l[2:])))
    return out


def duration(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode())


def decode(p, ch=1):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', 'pipe:'])
    return np.frombuffer(raw, np.float32).reshape(-1, ch)


def write_f32(p, x, ch=1):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', str(ch), '-i', 'pipe:',
                    '-c:a', 'pcm_f32le', p], input=x.astype(np.float32).tobytes(), check=True)


def loud(p):
    r = subprocess.run(['ffmpeg', '-nostats', '-hide_banner', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    t = r[r.rfind('Summary:'):]
    I = float(re.search(r'I:\s+(-?[\d.]+) LUFS', t).group(1))
    lra = float(re.search(r'LRA:\s+(-?[\d.]+) LU', t).group(1))
    m = re.search(r'Peak:\s+(-?[\d.]+) dBFS', t)
    return I, lra, float(m.group(1)) if m else -99.0


def rms_db(x):
    return 10 * np.log10(np.mean(x.astype(np.float64) ** 2) + 1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video'); ap.add_argument('srt'); ap.add_argument('clips'); ap.add_argument('out')
    ap.add_argument('--music-db', type=float, default=-5.0, help='static gain on the film score')
    ap.add_argument('--duck-thr', type=float, default=0.05, help='sidechain threshold (linear)')
    ap.add_argument('--duck-ratio', type=float, default=3.0)
    ap.add_argument('--voice-lufs', type=float, default=-16.0)
    ap.add_argument('--target-lufs', type=float, default=-14.0)
    ap.add_argument('--min-vmr', type=float, default=10.0, help='voice should sit at least this many dB above the score')
    ap.add_argument('--max-ride', type=float, default=6.0, help='max extra score dip per line (dB)')
    ap.add_argument('--lead', type=float, default=0.8)
    ap.add_argument('--gap', type=float, default=0.35)
    ap.add_argument('--fit', default=None)
    a = ap.parse_args()
    fitp = a.fit or os.path.join(a.clips, 'fit.json')
    fit = json.load(open(fitp, encoding='utf-8')) if os.path.exists(fitp) else dict(lines=[])
    F = {L['i']: L for L in fit['lines']}
    total = duration(a.video); subs = read_srt(a.srt)
    base = os.path.splitext(a.out)[0]; work = base + '_work'; os.makedirs(work, exist_ok=True)

    # 1) place clips on the subtitle timeline
    track = np.zeros(int(total * SR), np.float32); place = []; prev_end = 0.0
    for k, s in enumerate(subs):
        nxt = subs[k + 1]['s'] if k + 1 < len(subs) else total
        p = os.path.join(a.clips, '%02d.wav' % s['i'])
        if not os.path.exists(p): place.append(dict(s, t=None)); continue
        x = decode(p)[:, 0]; d = len(x) / SR
        t = s['s'] if d <= nxt - s['s'] - a.gap else max(s['s'] - a.lead, 0)
        if prev_end: t = max(t, prev_end + a.gap)
        i0 = int(t * SR); n = max(0, min(len(x), len(track) - i0)); track[i0:i0 + n] += x[:n]
        prev_end = t + d
        place.append(dict(s, t=t, d=d, drift=t - s['s']))

    # 2) voice stem
    raw = os.path.join(work, 'voice_raw.wav'); write_f32(raw, track)
    proc = os.path.join(work, 'voice_proc.wav')
    run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', VOICE_CHAIN, '-c:a', 'pcm_f32le', proc])
    vg = a.voice_lufs - loud(proc)[0]
    voice = os.path.join(work, 'voice.wav')
    run(['ffmpeg', '-v', 'error', '-y', '-i', proc, '-af', 'volume=%.2fdB' % vg, '-c:a', 'pcm_f32le', voice])

    # 3) score: static gain + sidechain duck
    score = os.path.join(work, 'score.wav')
    run(['ffmpeg', '-v', 'error', '-y', '-i', a.video, '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', score])
    sI, sLRA, sTP = loud(score)
    duck = os.path.join(work, 'score_ducked.wav')
    fc = ('[0:a]volume=%.2fdB[m];[m][1:a]sidechaincompress=threshold=%g:ratio=%g:attack=40:release=700:detection=rms[d]'
          % (a.music_db, a.duck_thr, a.duck_ratio))
    run(['ffmpeg', '-v', 'error', '-y', '-i', score, '-i', voice, '-filter_complex', fc, '-map', '[d]', '-c:a', 'pcm_f32le', duck])

    # 3b) voice-priority ride: extra smooth score dip where a line would sit < MIN_VMR dB above the score.
    #     Built at 100 Hz: per-line dip -> 1.5 s min-hold (bridges short gaps, no pumping) -> 0.5 s smoothing.
    from numpy.lib.stride_tricks import sliding_window_view as swv
    V = decode(voice, 2).mean(1); D = decode(duck, 2)
    H = SR // 100; ec = np.ones(len(D) // H + 1, np.float64); rides = {}
    for P in place:
        if P.get('t') is None: continue
        i0, i1 = int(P['t'] * SR), min(len(V), int((P['t'] + P['d']) * SR))
        need = min(a.max_ride, max(0.0, a.min_vmr - (rms_db(V[i0:i1]) - rms_db(D[i0:i1].mean(1)))))
        if need < 0.5: continue
        rides[P['i']] = need
        ec[i0 // H:i1 // H + 1] = np.minimum(ec[i0 // H:i1 // H + 1], 10 ** (-need / 20))
    n = len(ec); ec = swv(np.pad(ec, (75, 74), mode='edge'), 150).min(1)
    ec = np.convolve(np.pad(ec, 25, mode='edge'), np.ones(50) / 50, mode='valid')[:n]
    env = np.interp(np.arange(len(D)) / H, np.arange(len(ec)), ec).astype(np.float32)
    ride = os.path.join(work, 'score_ride.wav'); write_f32(ride, D * env[:, None], ch=2)

    # 4) sum, loudness-match, limit, mux
    mix = os.path.join(work, 'mix.wav')
    run(['ffmpeg', '-v', 'error', '-y', '-i', ride, '-i', voice, '-filter_complex',
         '[0:a][1:a]amix=inputs=2:duration=first:normalize=0[a]', '-map', '[a]', '-c:a', 'pcm_f32le', mix])
    g = a.target_lufs - loud(mix)[0]
    fin = os.path.join(work, 'mix_final.wav')
    run(['ffmpeg', '-v', 'error', '-y', '-i', mix, '-af',
         'volume=%.2fdB,alimiter=limit=0.84:attack=5:release=60:level=0' % g, '-c:a', 'pcm_f32le', fin])
    run(['ffmpeg', '-v', 'error', '-y', '-i', a.video, '-i', fin, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
         '-c:a', 'aac', '-b:a', '256k', '-ar', str(SR), '-movflags', '+faststart', a.out])
    oI, oLRA, oTP = loud(a.out); odur = duration(a.out)

    # 5) balance metrics (RMS, approximate): voice vs ducked score inside each line
    M0 = decode(score, 2).mean(1) * 10 ** (a.music_db / 20); MD = (D * env[:, None]).mean(1)
    for P in place:
        if P.get('t') is None: continue
        i0, i1 = int(P['t'] * SR), min(len(V), int((P['t'] + P['d']) * SR))
        P['vmr'] = rms_db(V[i0:i1]) - rms_db(MD[i0:i1]); P['duck'] = rms_db(MD[i0:i1]) - rms_db(M0[i0:i1])
    gaps_change = a.music_db + g  # score level in narration gaps vs. original film
    vmr = np.array([P['vmr'] for P in place if 'vmr' in P]); dk = np.array([P['duck'] for P in place if 'duck' in P])
    voiced = [P for P in place if P.get('t') is not None]

    # 6) voice-timed SRT + report
    with open(base + '.srt', 'w', encoding='utf-8') as f:
        for n, P in enumerate(place, 1):
            s, e = (P['t'], P['t'] + P['d'] + 0.3) if P.get('t') is not None else (P['s'], P['e'])
            f.write('%d\n%s --> %s\n%s\n\n' % (n, fts(s), fts(e), P['text']))
    adj = [L for L in fit['lines'] if L.get('adjusted')]
    R = ['# 《人类简史》v2 旁白混音报告', '',
         '## 成片', '',
         '- 输出：`%s` · %.1f s · 视频流原样复制（2560×1440 · 24 fps · H.264），音频 AAC 256 kbps / 48 kHz 立体声' % (os.path.basename(a.out), odur),
         '- 旁白：%d 句（38 句旁白 + 2 句片尾字幕），音色 `%s`，全局语速偏移 %+d%%' % (len(voiced), fit.get('voice', '?'), fit.get('rate_offset', 0)),
         '- 对齐：全部从烧录字幕起点开始；最大偏移 %+.2f s；最长一句 %.1f s' % (max(abs(P['drift']) for P in voiced), max(P['d'] for P in voiced)),
         '', '## 响度与平衡', '',
         '| 项目 | 数值 |', '|---|---|',
         '| 原片配乐 | %.1f LUFS · LRA %.1f LU · 真峰值 %.1f dBTP |' % (sI, sLRA, sTP),
         '| 人声链路 | 高通 70 Hz → 150 Hz +1.5 dB（厚度）→ 3 kHz +1.5 dB（清晰度）→ 压缩 3:1 @ −20 dB → 轻微房间回声 → %.0f LUFS |' % a.voice_lufs,
         '| 配乐静态增益 | %+.1f dB |' % a.music_db,
         '| 旁白闪避 | sidechaincompress 阈值 %g · 比率 %g:1 · 起音 40 ms · 释放 700 ms；旁白时配乐再压低约 %.1f dB（中位） |' % (a.duck_thr, a.duck_ratio, -np.median(dk)),
         '| 人声优先补偿 | 人声高出配乐不足 %.0f dB 的句子，额外平滑压低配乐（最多 %.0f dB，1.5 s 保持 + 0.5 s 渐变，相邻句之间不回弹）：%s |' % (
             a.min_vmr, a.max_ride, '、'.join('#%d −%.1f dB' % (k, v) for k, v in sorted(rides.items())) or '无'),
         '| 人声高出配乐 | 中位 %.1f dB · 最小 %.1f dB（逐句 RMS 估算） |' % (np.median(vmr), vmr.min()),
         '| 旁白空隙的配乐 | 相对原片 %+.1f dB |' % gaps_change,
         '| 母带 | 增益 %+.2f dB → 限幅 −1.5 dBFS → 目标 %.0f LUFS |' % (g, a.target_lufs),
         '| 成片实测 | %.1f LUFS · LRA %.1f LU · 真峰值 %.1f dBTP |' % (oI, oLRA, oTP),
         '', '## 自动适配（语速 / 停顿调整）', '']
    if adj:
        for L in adj:
            R.append('- #%02d「%s」：语速 %+d%% → %+d%%，停顿 %.2f s（槽位 %.2f s，最终 %.2f s）' % (L['i'], L['t'].replace('‖', ''), L['rate_in'], L['rate'], L['pause'], L['slot'], L['dur']))
    else:
        R.append('- 无：全部句子按初始参数即可放进字幕槽位')
    R += ['', '## 逐句明细', '',
          '| # | 字幕起点 | 旁白起止 | 时长 / 槽位 | 语速 | 音高 | 音量 | 人声高出配乐 | 情绪 | 文本 |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for P in place:
        L = F.get(P['i'], {})
        if P.get('t') is None:
            R.append('| %d | %.1f s | 缺失 |  |  |  |  |  |  | %s |' % (P['i'], P['s'], P['text'])); continue
        R.append('| %d | %.1f s | %.2f–%.2f s | %.1f / %.1f s | %+d%% | %s | %s | %.1f dB | %s | %s |' % (
            P['i'], P['s'], P['t'], P['t'] + P['d'], P['d'], L.get('slot', 0), L.get('rate', 0), L.get('pitch', ''),
            L.get('vol', ''), P['vmr'], L.get('cue', ''), L.get('t', P['text']).replace('‖', ' ‖ ')))
    open(base + '_report.md', 'w', encoding='utf-8').write('\n'.join(R) + '\n')
    print('final: %.1f s  %.1f LUFS  TP %.1f dBTP  VMR median %.1f dB (min %.1f)  duck %.1f dB  gaps %+.1f dB' % (
        odur, oI, oTP, np.median(vmr), vmr.min(), -np.median(dk), gaps_change))
    print('done ->', a.out)


if __name__ == '__main__':
    main()
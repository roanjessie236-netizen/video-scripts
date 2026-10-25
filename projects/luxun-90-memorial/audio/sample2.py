# 第二轮试听：旁白定为云健；原文换三种候选声音（混响改为合成小房间，去掉 aecho 回声）
import json, sys, subprocess, numpy as np
src = open('/tmp/vo/sample.py', encoding='utf-8').read(); exec(src[:src.index("for tag, narr, quo in")])
import tts
CLEAN = 'highpass=f=80,acompressor=threshold=-20dB:ratio=2.2:attack=10:release=150:makeup=2'
OLD = 'highpass=f=200,lowpass=f=5200,equalizer=f=1800:t=q:w=1:g=3,acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=2,asoftclip=type=tanh:threshold=0.7'
CANDS = {'C1': ('zh-CN-YunxiNeural', dict(base=(-14, -4), flt=CLEAN, rev=(0.6, -15))),
         'C2': ('zh-CN-YunxiNeural', dict(base=(-16, -7), flt=OLD, rev=(0.45, -17))),   # 台湾云哲目前合成中文报错，改为云希·旧录音质感
         'C3': ('zh-CN-YunjianNeural', dict(base=(-16, -4), flt=OLD, rev=(0.45, -17)))}
QS = [l.split('\t') for l in open('/data/luxun90/quotes_src.tsv', encoding='utf-8')]
QS = {r[0]: r[1] for r in QS}
LONG = [QS[k].rstrip('。') + '。' for k in ('Q17', 'Q28', 'Q31', 'Q40')]
for tag in sys.argv[1:] or CANDS:
    quo, prof = CANDS[tag]; tts.QPROF.update(prof)
    v, rec = tts.build(lines, TOTAL, 'zh-CN-YunjianNeural', quo)
    json.dump(rec, open(f'/tmp/vo/rec_{tag}.json', 'w'), ensure_ascii=False, indent=0)
    m = music(); n = min(len(m), len(v)); g = duck(v, n)
    (m[:n] * g[:, None] + v[:n, None] * 0.98).astype(np.float32).tofile(f'/tmp/vo/mix_{tag}.f32')
    for r in rec:
        if r['kind'] != 'vo': print(tag, f"{r['t']:6.2f} win {r['win']:5.2f} dur {r['dur']:5.2f} next {r['next']:6.2f}", r['log'], r['txt'][:14])
    # 长段原文对比（干声＋混响，无配乐）
    parts = []
    for t in LONG:
        x = tts.gen(tts.speak_text(t), quo, *tts.QPROF['base']); y = tts.fx(x, 'q'); parts += [y, np.zeros(int(1.3 * tts.SR), np.float32)]
    np.concatenate([np.zeros(int(0.4 * tts.SR), np.float32)] + parts).astype(np.float32).tofile(f'/tmp/vo/long_{tag}.f32')
    print(tag, 'long', round(sum(len(p) for p in parts) / tts.SR, 1))

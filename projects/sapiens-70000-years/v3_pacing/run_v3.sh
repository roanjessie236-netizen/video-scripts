#!/bin/bash
# v3 = v2 2K film re-paced (warp.py) + rewritten line 37. Needs ../v2_from_film set up (plates built, user film linked).
#   bash run_v3.sh            (resumable: finished segs/seg_XX.mp4 are skipped)
set -e
cd "$(dirname "$0")"
mkdir -p segs audio out vo/clips
python3 warp.py                                        # print the pacing blocks
# narration: v2 clips + re-synthesized line 37 (same voice / params as lines.json #37)
python3 -c "import json;json.dump([x for x in json.load(open('vo/lines.json',encoding='utf-8')) if x['i']==37],open('vo/l37.json','w',encoding='utf-8'),ensure_ascii=False)"
python3 ../voiceover/v2/tts_line.py vo/l37.json vo/t37 --total 300 && cp vo/t37/37.wav vo/clips/37.wav   # other clips: ../voiceover/v2 clips
python3 timeline_v3.py                                 # VO starts, retimed subtitles, srt files
python3 mk_music_v3.py && python3 music_v3.py audio/score_v3.wav   # score re-timed at note level
CRF=18 python3 render_v3.py $(seq 0 7) & CRF=18 python3 render_v3.py $(seq 15 -1 8); wait
ls segs/seg_*.mp4 | sort | sed "s#^segs/#file '#;s/$/'/" > segs/list.txt
ffmpeg -v error -y -f concat -safe 0 -i segs/list.txt -c copy segs/picture.mp4
ffmpeg -v error -y -i segs/picture.mp4 -i audio/score_v3.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s16le -t 308.833 segs/pic_score.mov
python3 ../voiceover/v2/mix_tl.py segs/pic_score.mov vo/vo_starts_v3.srt vo/clips out/sapiens_v3_2K.mp4 \
  --fit vo/fit.json --music-db -5 --duck-thr 0.05 --duck-ratio 3 --voice-lufs -16 --target-lufs -14 --min-vmr 12 --max-ride 7

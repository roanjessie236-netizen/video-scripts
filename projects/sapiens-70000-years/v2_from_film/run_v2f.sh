#!/bin/bash
# v2 picture rebuilt from the user's finished film (no source images needed), resumable.
#   FILM=/path/to/《人类简史》.mp4 bash run_v2f.sh
# needs: python3 numpy opencv-python-headless pillow, ffmpeg, Noto Serif CJK fonts; v1core/ = repo render code + v1 shotlist
set -e
cd "$(dirname "$0")"
mkdir -p /data/film plates segs audio
[ -n "$FILM" ] && ln -sf "$FILM" /data/film/src.mp4
python3 cap_alpha.py                                   # alpha of the baked closing questions (ending)
[ -s plates/plan.json ] || python3 build_plates.py     # pass 1: clean per-shot plates under the old subtitles
CRF=18 python3 render_v2f.py $(seq 0 14)               # pass 2: 15 x 480-frame segments -> segs/seg_XX.mp4
ls segs/seg_*.mp4 | sort | sed "s/^/file '/;s/$/'/" | sed "s#file 'segs/#file '#" > segs/list.txt
ffmpeg -v error -y -f concat -safe 0 -i segs/list.txt -c copy segs/picture.mp4
(cd ../ && python3 v2_from_film/music_v2f.py v2_from_film/audio/score_v2f.wav)   # score re-timed to the user's ending
ffmpeg -v error -y -i segs/picture.mp4 -i audio/score_v2f.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s16le -t 284.125 segs/pic_score.mov
python3 ../voiceover/v2/mix_tl.py segs/pic_score.mov audio/vo_starts_v2f.srt ../voiceover/v2/clips out/sapiens_v2_2K.mp4 \
  --fit ../voiceover/v2/fit.json --music-db -5 --duck-thr 0.05 --duck-ratio 3 --voice-lufs -16 --target-lufs -14 --min-vmr 12 --max-ride 7

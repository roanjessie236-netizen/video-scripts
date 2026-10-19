#!/bin/bash
# v4: render homo_deus_future_v4 in segments (resumable), concat, mux with the narration mix.
# Usage: bash seg_render_v4.sh OUTNAME.mp4 [PRESET] [CRF]
cd /data/hd/v4/engine
OUTNAME=${1:-homo_deus_future_v4_2K.mp4}; PRESET=${2:-medium}; CRF=${3:-19}
DUR=$(python3 -c "import json;print(json.load(open('shotlist.json'))['duration'])")
STARTS=(0 60 120 180); ENDS=(60 120 180 $DUR)
SEG=../out/seg; mkdir -p $SEG
for i in "${!STARTS[@]}"; do
  if [ -f $SEG/seg_$i.done ]; then echo "SKIP $i"; continue; fi
  python3 render.py --video $SEG/seg_$i.mp4 --start ${STARTS[$i]} --end ${ENDS[$i]} --preset $PRESET --crf $CRF \
    > $SEG/seg_$i.log 2>&1 || { echo "SEGFAIL $i"; exit 1; }
  touch $SEG/seg_$i.done; echo "SEGDONE $i"
done
: > $SEG/list.txt
for i in "${!STARTS[@]}"; do echo "file 'seg_$i.mp4'" >> $SEG/list.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i $SEG/list.txt -i ../out/score_v4.wav -map 0:v -map 1:a -c:v copy \
  -c:a pcm_s16le ../out/video_score.mkv && echo CONCAT_OK

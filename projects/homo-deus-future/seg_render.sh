#!/bin/bash
# v2: render homo_deus_future_v2.mp4 (270.7 s) in independent segments, then mux with out/score.wav.
# Resumable: segments that have out/seg/seg_N.done are skipped (0-120 s is identical to v1 and can be reused).
cd /data/hd
STARTS=(0 60 120 180 240)
ENDS=(60 120 180 240 270.7)
OUTNAME=homo_deus_future_v2.mp4
mkdir -p out/seg
for i in "${!STARTS[@]}"; do
  if [ -f out/seg/seg_$i.done ]; then echo "SKIP $i"; continue; fi
  python3 render.py --video out/seg/seg_$i.mp4 --start ${STARTS[$i]} --end ${ENDS[$i]} --preset medium --crf 19 \
    > out/seg/seg_$i.log 2>&1 || { echo "SEGFAIL $i"; exit 1; }
  touch out/seg/seg_$i.done
  echo "SEGDONE $i"
done
: > out/seg/list.txt
for i in "${!STARTS[@]}"; do echo "file 'seg_$i.mp4'" >> out/seg/list.txt; done
if [ -f out/score.wav ]; then
  ffmpeg -y -loglevel error -f concat -safe 0 -i out/seg/list.txt -i out/score.wav -map 0:v -map 1:a -c:v copy \
    -c:a aac -b:a 256k -shortest -movflags +faststart out/$OUTNAME && echo ALLDONE
else
  echo VIDEO_SEGMENTS_DONE_NO_SCORE
fi

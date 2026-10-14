#!/bin/bash
# Render 《未来简史》 in ~60 s segments so an interrupted run can resume; then concat + mux audio.
cd /data/hd
mkdir -p out/seg
STARTS=(0 60 120 180)
ENDS=(60 120 180 234)
for i in 0 1 2 3; do
  s=${STARTS[$i]}; e=${ENDS[$i]}
  if [ -f out/seg/seg_$i.done ]; then continue; fi
  python3 render.py --video out/seg/seg_$i.mp4 --start $s --end $e --preset medium --crf 19 > out/seg/seg_$i.log 2>&1 \
    && echo ok > out/seg/seg_$i.done || { echo FAIL $i; exit 1; }
  echo SEGDONE $i
done
printf "file 'seg_%d.mp4'\n" 0 1 2 3 > out/seg/list.txt
if [ -f out/score.wav ]; then
  ffmpeg -y -loglevel error -f concat -safe 0 -i out/seg/list.txt -i out/score.wav -map 0:v -map 1:a \
    -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart out/homo_deus_future_2K.mp4 && echo ALLDONE
else
  echo VIDEO_SEGMENTS_DONE_NO_SCORE
fi

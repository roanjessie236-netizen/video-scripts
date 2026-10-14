#!/bin/bash
# Render the film in 60 s segments so an interrupted run can resume; then concat + mux audio.
cd /data/video
mkdir -p out/seg
for i in 0 1 2 3 4; do
  s=$((i*60)); e=$(((i+1)*60))
  if [ -f out/seg/seg_$i.done ]; then continue; fi
  python3 render.py --video out/seg/seg_$i.mp4 --start $s --end $e --preset medium --crf 20 > out/seg/seg_$i.log 2>&1 \
    && echo ok > out/seg/seg_$i.done || { echo FAIL $i; exit 1; }
done
printf "file 'seg_%d.mp4'\n" 0 1 2 3 4 > out/seg/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i out/seg/list.txt -i out/score.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart out/sapiens_70000_years_2K.mp4 && echo ALLDONE

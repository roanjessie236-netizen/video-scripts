#!/bin/bash
# Render 《明天属于谁》 in frame-exact segments (resumable, any order), concat, mux with the narration mix.
# Usage: bash seg_render_wt.sh render [IDX ...]   # render the given segment indices (default: all)
#        bash seg_render_wt.sh mux [OUTNAME.mp4]  # concat all segments + mux out/mix.mp4 audio
# Segment boundaries are in frames (24 fps) so segments can be re-rendered independently when an image changes.
cd "$(dirname "$0")/engine"
B=(0 957 1311 2010 2100 2667 2814 3450 3565 3834 3981 5136 5246)
END=$(python3 -c "import json;print(round(json.load(open('shotlist.json'))['duration']*24))"); B+=($END)
SEG=../out/seg; mkdir -p $SEG; PRESET=${PRESET:-medium}; CRF=${CRF:-19}
NS=$(( ${#B[@]} - 1 ))
if [ "$1" = "render" ]; then
  shift; IDX=("$@"); [ ${#IDX[@]} -eq 0 ] && IDX=($(seq 0 $((NS-1))))
  for i in "${IDX[@]}"; do
    if [ -f $SEG/seg_$i.done ]; then echo "SKIP $i"; continue; fi
    S=$(python3 -c "print(${B[$i]}/24)"); E=$(python3 -c "print(${B[$((i+1))]}/24)")
    python3 render.py --video $SEG/seg_$i.mp4 --start $S --end $E --preset $PRESET --crf $CRF \
      > $SEG/seg_$i.log 2>&1 || { echo "SEGFAIL $i"; exit 1; }
    touch $SEG/seg_$i.done; echo "SEGDONE $i"
  done
elif [ "$1" = "mux" ]; then
  OUTNAME=${2:-whose_tomorrow_2K.mp4}
  : > $SEG/list.txt
  for i in $(seq 0 $((NS-1))); do [ -f $SEG/seg_$i.done ] || { echo "MISSING $i"; exit 1; }; echo "file 'seg_$i.mp4'" >> $SEG/list.txt; done
  ffmpeg -y -loglevel error -f concat -safe 0 -i $SEG/list.txt -c copy $SEG/video.mp4 || exit 1
  D=$(python3 -c "print($END/24)")
  ffmpeg -y -loglevel error -i $SEG/video.mp4 -i ../out/mix.mp4 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k \
    -af apad=whole_dur=$D -t $D -movflags +faststart ../out/$OUTNAME && echo "MUX_OK ../out/$OUTNAME"
fi

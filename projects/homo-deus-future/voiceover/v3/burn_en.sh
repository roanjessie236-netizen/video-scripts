#!/bin/bash
# Burn the English line (en_overlay.ass) under the Chinese subtitles already in the picture.
# Usage: bash burn_en.sh IN.mp4 en_overlay.ass OUT.mp4   (45 s segments, resumable; audio copied from IN)
set -e
IN=$(readlink -f "$1"); ASS=$(readlink -f "$2"); OUT=$3
SEG=45; D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
N=$(python3 -c "import math; print(math.ceil($D/$SEG))")
mkdir -p out/seg; : > out/seg/list.txt
for k in $(seq 0 $((N-1))); do
  S=$((k*SEG)); F=out/seg/s$k.mp4
  if [ ! -s $F ]; then
    echo "segment $k / $N  (t=$S s)"
    ffmpeg -v error -y -ss $S -t $SEG -i "$IN" -an \
      -vf "setpts=PTS+$S/TB,subtitles=$ASS,setpts=PTS-STARTPTS" \
      -c:v libx264 -preset fast -crf 18 -profile:v high -pix_fmt yuv420p \
      -color_primaries bt709 -color_trc bt709 -colorspace bt709 out/seg/tmp_$k.mp4
    mv out/seg/tmp_$k.mp4 $F
  fi
  echo "file 's$k.mp4'" >> out/seg/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i out/seg/list.txt -i "$IN" -map 0:v -map 1:a -c copy -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"

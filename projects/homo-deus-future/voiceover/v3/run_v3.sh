#!/bin/bash
# Homo Deus v3: Yunjian male narration (same voice + rhythm as Sapiens v2 / 21 Lessons) + burned English subtitles + mix.
# Usage: bash run_v3.sh /path/to/homo_deus_future_v2.mp4      (the English burn is segmented and resumable)
set -e
IN=$(readlink -f "$1"); cd "$(dirname "$0")"
pip install -q edge-tts numpy
R=https://raw.githubusercontent.com/roanjessie236-netizen/video-scripts/main/projects/sapiens-70000-years/voiceover/v2
[ -s tts_line.py ] || curl -sfLO $R/tts_line.py
if [ ! -s mix_tl.py ]; then
  curl -sfLO $R/mix_tl.py
  sed -i 's/《人类简史》v2 旁白混音报告/《未来简史》v3 旁白混音报告/' mix_tl.py
fi
[ -s lines.json ] || python3 gen.py
mkdir -p out
# 1) narration: one edge-tts call per line (no splicing), prints any line that overruns its slot
python3 tts_line.py lines.json clips --total 270.7
# 2) English subtitles burned under the Chinese ones (video re-encoded once, x264 CRF 18)
[ -s out/hd_v3_en.mp4 ] || bash burn_en.sh "$IN" en_overlay.ass out/hd_v3_en.mp4
# 3) mix: same chain + settings as Sapiens v2 (video stream copied untouched)
python3 mix_tl.py out/hd_v3_en.mp4 vo_starts.srt clips out/homo_deus_future_v3_2K.mp4 \
  --music-db -5 --duck-thr 0.05 --duck-ratio 3 --voice-lufs -16 --target-lufs -14 --min-vmr 12 --max-ride 7
cp homo_deus_v3_subtitles_bilingual.srt out/
echo "done -> out/homo_deus_future_v3_2K.mp4"

#!/bin/bash
# Sapiens v2 one-shot build (resumable): shotlist -> score -> segmented render -> TTS -> voice mix.
# Needs assets/NN_name.jpg + assets/parchment.jpg in the project root.
set -e
cd "$(dirname "$0")/../.."
pip install -q numpy opencv-python-headless pillow edge-tts
python3 timeline.py
[ -s out/score.wav ] || { mkdir -p out; python3 music.py out/score.wav; }
bash seg_render.sh                       # -> out/sapiens_70000_years_2K.mp4 (picture + score)
cd voiceover/v2
python3 tts_line.py lines.json clips --total 287
python3 mix_tl.py ../../out/sapiens_70000_years_2K.mp4 vo_starts.srt clips ../../out/sapiens_70000_years_2K_v2.mp4 \
  --music-db -5 --duck-thr 0.05 --duck-ratio 3 --voice-lufs -16 --target-lufs -14 --min-vmr 12 --max-ride 7
echo "done -> out/sapiens_70000_years_2K_v2.mp4"

#!/bin/bash
# 今日简史 v2 一键复现：TTS（云健，每句一次合成）→ 合并句逗号停顿对齐 → 烧录英文字幕 → 混音（《人类简史》v2 同参数）
# 输入：v1 成片 ../../out/21_lessons_ai_era_2K.mp4（seg_render.sh 产出，已含中文字幕 + 配乐，无旁白）
set -e
cd "$(dirname "$0")"
pip install -q numpy opencv-python-headless pillow edge-tts
SRC=${1:-../../out/21_lessons_ai_era_2K.mp4}
python3 build_lines.py lines.json subs.json ../../narration.srt      # 分句 / 语速 / 音高 / 英文翻译
python3 tts_line.py lines.json clips --total 224                       # zh-CN-YunjianNeural，一句一次合成
python3 pause_fit.py lines.json subs.json clips clips_fit              # 6 组合并句：后半句对齐烧录字幕
python3 en_overlay.py "$SRC" subs.json ../../out/21_lessons_ai_era_2K_en.mp4 --crf 18   # 英文字幕（v2 排版）
python3 mix_tl.py ../../out/21_lessons_ai_era_2K_en.mp4 vo_starts.srt clips_fit ../../out/21_lessons_ai_era_2K_v2.mp4 \
  --fit clips_fit/fit.json --music-db -5 --duck-thr 0.05 --duck-ratio 3 --voice-lufs -16 --target-lufs -14 --min-vmr 12 --max-ride 7
# 全流程重跑已包含 v2.1 的第 5 句（lines.json 的 ctx）。交付的 v2.1 是在已交付的 v2 成片上只换第 5 句：
#   python3 replace_l5.py V2_DELIVERED.mp4 ../../out/21_lessons_ai_era_2K_v2_work/mix_final.wav ../../out/21_lessons_ai_era_2K_v2.1.mp4
echo "done -> out/21_lessons_ai_era_2K_v2.mp4"

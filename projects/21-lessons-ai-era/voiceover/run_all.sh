#!/bin/bash
# 今日简史 voice-over, one shot: (re)fetch inputs -> TTS auto-fit -> mix -> report.
# Safe to re-run after a sandbox reset (cached TTS parts are reused when present).
set -eo pipefail
# Env overrides: VIDEO, VOICE (zh-CN-YunjianNeural), RATE_OFFSET (%, 0), MUSIC_DB (dB, -5)
cd "$(dirname "$0")"
V="${VIDEO:-/data/.agent-service/files/524dd04e-1205-4d7f-9773-e72e90dc00cd/《今日简史》.mp4}"
[ -f "$V" ] || { echo "NO_VIDEO $V"; exit 2; }
python3 -c "import edge_tts" 2>/dev/null || pip install -q edge-tts
[ -s narration.srt ] || cp ../narration.srt . 2>/dev/null || curl -sfL -o narration.srt https://raw.githubusercontent.com/roanjessie236-netizen/video-scripts/main/projects/21-lessons-ai-era/narration.srt
mkdir -p out
echo "== TTS $(date +%T)"
python3 tts_fit.py lines.json narration.srt clips --voice "${VOICE:-zh-CN-YunjianNeural}" --rate-offset "${RATE_OFFSET:-0}" --total 224.0 | tee tts.log
echo "== MIX $(date +%T)"
python3 mix_tl.py "$V" narration.srt clips out/21_lessons_ai_era_2K_vo.mp4 --music-db "${MUSIC_DB:--5}" | tee mix.log
echo "== DONE $(date +%T)"
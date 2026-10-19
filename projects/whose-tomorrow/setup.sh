#!/bin/bash
# Restore the build environment for 《明天属于谁》 after a sandbox reset (idempotent).
set -e
cd /data
pip3 install -q gradio_client edge-tts 2>&1 | tail -1 || true
R=https://raw.githubusercontent.com/roanjessie236-netizen/video-scripts/main/projects
mkdir -p hd/v4/tools hd/v4/voiceover hd/tools hd/sapv2
for f in seg_render_v4.sh timeline_v4.py tools/build_music_v4.py tools/export_srt.py tools/patch_v4.py tools/score_v4.py tools/upscale_sr.py voiceover/stretch.py voiceover/tts_line.py; do
  [ -s hd/v4/$f ] || curl -sf -o hd/v4/$f $R/homo-deus-future/v4/$f; done
for f in patch_engine.py score.py; do [ -s hd/tools/$f ] || curl -sf -o hd/tools/$f $R/homo-deus-future/tools/$f; done
for f in render_core.py render.py music.py voiceover/v2/mix_tl.py; do b=$(basename $f); [ -s hd/sapv2/$b ] || curl -sf -o hd/sapv2/$b $R/sapiens-70000-years/$f; done
echo setup-code-ok

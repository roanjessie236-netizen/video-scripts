# 未来简史 v4（2K · 2560×1440 · 24 fps · 约 3:39）

v4 = v2 母版的干净画面（plates）+ 14 张新生成配图 + 重新合成、更连贯的旁白 + 跟随旁白重算的配乐。

## v4.1 更新
- **旁白连贯**：48 句统一语速（-6%，个别长句 -7～-9%）与音调（-2 Hz）；朗读文本与字幕一致，去掉句内多余停顿；
  句间停顿收紧到 0.3–1.0 s，章节停顿缩短到约 3 s；只在列举处的逗号停顿里略加长（饥荒 +0.15 s；长生不死、快乐 各 +0.15 s），
  “瘟疫和战争”之间不再插入静音（原来插 0.45 s 听起来像卡顿）。总时长 3:58 → 3:39。
- **新配图 2K 化**：原图 1672×941 → Real-ESRGAN（realesr-general-x4v3 + wdn，denoise 0.5，CPU 分块）4× 超分，
  再 Lanczos 缩到 2944×1656 板面尺寸（2560×1440 输出 + 运镜余量）。`tools/upscale_sr.py`
- 亮背景新图（超市、方糖）加深字幕/标注背后的暗角（timeline `SCRIM_BOOST`，引擎 `scrim_boost`）；阶层镜头运镜上移保住人物头部。
- 3:00 的“静默”不再硬切静音：高潮按 E→Am 终止落下（冲击音 + braam 自然衰减），提问句下保留很轻的 Am 合唱/铺底，
  音乐整体只压低约 4 dB，再平滑接入结尾段。
- 配乐结尾和弦、独唱旋律、第 2/3 章和弦改为相对旁白时间计算（不再写死秒数）。

## 流程
```bash
python3 voiceover/lines_v4.py                      # -> voiceover/lines.json
python3 voiceover/tts_line.py voiceover/lines.json voiceover/clips
python3 voiceover/stretch.py voiceover/clips voiceover/clips_v4
python3 tools/upscale_sr.py NEW_IMAGES_DIR engine/assets      # 新图超分到 2944×1656 jpg
python3 timeline_v4.py                              # -> engine/shotlist.json
python3 tools/build_music_v4.py && python3 music_v4.py out/score_v4.wav
python3 tools/export_srt.py                         # 旁白定位 srt + 中英/中文/英文字幕
ffmpeg -f lavfi -i color=c=black:s=320x180:r=2 -i out/score_v4.wav -t DUR -c:v libx264 -preset ultrafast -c:a pcm_s16le -shortest out/score_dummy.mkv
python3 ../sapiens-70000-years/voiceover/v2/mix_tl.py out/score_dummy.mkv out/voice_v4.srt voiceover/clips_v4 out/mix_dummy.mp4 \
  --music-db -5 --duck-thr 0.05 --duck-ratio 3 --voice-lufs -16 --target-lufs -14 --min-vmr 12 --max-ride 7 --lead 0 --gap 0.2
bash seg_render_v4.sh homo_deus_future_v4_2K.mp4 medium 19   # 分段渲染，然后与 mix_final.wav 合成
```
引擎：Sapiens `render_core.py`/`render.py` + `../tools/patch_engine.py` + `tools/patch_v4.py`。

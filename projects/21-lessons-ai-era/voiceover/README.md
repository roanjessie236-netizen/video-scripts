# 今日简史 · 旁白配音

- 成片 `21_lessons_ai_era_2K_vo.mp4`（视频不入库）：224.0 s · 2560×1440 · 24 fps；视频流与原片 `21_lessons_ai_era_2K.mp4` 完全一致，只替换音轨（AAC 256 kbps / 48 kHz）
- 音色：edge-tts `zh-CN-YunjianNeural`（解说男声）；43 句 = 41 句旁白 + 2 句片尾字幕，与烧录字幕逐句对齐
- 混音结果与逐句数据见 `mix_report.md`

## 文件

| 文件 | 作用 |
|---|---|
| `lines.json` | 43 句旁白：语速 `rate`、音高 `pitch`、音量 `vol`、情绪提示 `cue`；`‖` = 戏剧性停顿 |
| `tts_fit.py` | 逐句合成，并自动适配字幕槽位：超长时先把停顿从 0.45 s 缩到 0.25 s，再提速（上限 +12%） |
| `fit.json` | 本次合成的最终参数与时长（含自动调整记录） |
| `mix_tl.py` | 混音：人声链路 → 配乐静态增益 + 旁白闪避 + 人声优先补偿 → 母带 −14 LUFS；输出报告与按旁白重排的字幕 |
| `run_all.sh` | 一键：合成 → 混音 → 报告（环境重置后可直接重跑，已合成的片段会复用） |
| `mix_report.md` | 本次混音报告 |
| `narration_vo.srt` | 按实际旁白时间重排的字幕，可作平台 CC 字幕 |

## 运行

```bash
pip install edge-tts numpy            # 另需 ffmpeg；edge-tts 需要联网
VIDEO=/path/to/21_lessons_ai_era_2K.mp4 ./run_all.sh
# -> out/21_lessons_ai_era_2K_vo.mp4、out/*_report.md、out/*.srt
```

## 微调

- 语速：`RATE_OFFSET=-5 ./run_all.sh` 整体放慢 5%（正数加快）；单句改 `lines.json` 的 `rate`。超出字幕槽位的句子会被自动提速，并记在报告里
- 音色：`VOICE=zh-CN-YunxiNeural ./run_all.sh`（年轻、温和）或 `zh-CN-YunyangNeural`（新闻播音、沉稳）；默认 `zh-CN-YunjianNeural`（浑厚、有激情）
- 情绪：单句 `pitch`（±Hz）和 `vol`（±%）控制起伏；在句中加 `‖` 可以多一个停顿
- 背景音乐：`MUSIC_DB=-8 ./run_all.sh` 让配乐更轻，`-3` 更响（默认 −5 dB）；`mix_tl.py --min-vmr 12` 要求人声至少高出配乐 12 dB（默认 10）；`--duck-ratio` 控制旁白时的闪避深度

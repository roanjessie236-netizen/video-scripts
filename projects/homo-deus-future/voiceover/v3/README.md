# 《未来简史》v3：旁白配音 + 中英双语字幕

## 音色与节奏（沿用《人类简史》v2 / 《今日简史》）

- edge-tts `zh-CN-YunjianNeural`（云健男声），每句一次合成、不拼接，停顿交给标点。
- 基础语速 −5%，按情绪在 −4% ~ −8% 之间起伏；重句（#2、#18、#31）−10% ~ −12%；片尾两句 −15%。
- #20、#24 文字多、时间紧，用 +6%；#22 +3%，#26 0%。
- 音高 −5Hz ~ +3Hz、音量 −5% ~ +8% 按句设置，每句的情绪提示写在 gen.py 的最后一列。
- 混音沿用 sapiens v2 的 mix_tl.py 与参数：`--music-db -5 --duck-thr 0.05 --duck-ratio 3 --voice-lufs -16 --target-lufs -14 --min-vmr 12 --max-ride 7`，成片 −14 LUFS，TP ≤ −1 dBTP。

## 字幕

- 画面里原有的中文字幕保持不动，英文用 `en_overlay.ass` 烧录在中文下方：
  - 正文：中文中心 y=1290 → 英文中心 y=1360，Noto Serif 39 号，浅暖白，细描边 + 阴影。
  - 片尾两句大字幕（#33–34）：英文斜体 46 号，放在大字下方 y=478。
  - 已在 4.5 s、171 s（最长一句）、255.5 s 三帧核对过位置，不遮挡、不重叠。
- `homo_deus_v3_subtitles_bilingual.srt`：中英双语外挂字幕，上传视频号 / B 站 / 抖音时可选用。

## 文件

| 文件 | 作用 |
| --- | --- |
| gen.py | 34 句数据源（时间、中文字幕、朗读文本、英文、语速 / 音高 / 音量、情绪提示），生成 lines.json、vo_starts.srt、双语 srt、en_overlay.ass |
| burn_en.sh | 分 45 s 段烧录英文字幕（可断点续跑），音轨原样拷贝 |
| run_v3.sh | 一键：装 edge-tts → 拉取 sapiens v2 的 tts_line.py、mix_tl.py → 合成 → 烧录英文 → 混音 |

## 运行（需要能联网的环境）

```
bash run_v3.sh /path/to/homo_deus_future_v2.mp4
```

产出：`out/homo_deus_future_v3_2K.mp4`、`out/homo_deus_future_v3_2K.srt`、`out/homo_deus_future_v3_2K_report.md`、`out/homo_deus_v3_subtitles_bilingual.srt`。

微调：tts_line.py 会列出超出时间槽的句子。在 gen.py 里改该句的 rate（例如 −5 → 0），删掉 lines.json 后重跑即可；已烧好的英文画面不会重做。

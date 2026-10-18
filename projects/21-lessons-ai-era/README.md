# 今日简史：AI时代，人类如何重新定义自己

状态：**已完成剪辑 v1**（2026-10-15）· 224.0 s（3:44）· 2560×1440 · 24 fps · H.264 + AAC 立体声 · 字幕烧录，另附 `narration.srt`

**v2.1（2026-10-18）：中文旁白 + 英文字幕** · 音色、节奏与混音同《人类简史》v2 · `out/21_lessons_ai_era_2K_v2.1.mp4`（v2.1 只重配第 5 句「思考」），详见 `voiceover/v2/README.md`

分工：剪辑端（Notion AI）负责脚本、素材需求表、剪辑、调色、字幕、配乐与合成；素材端（GPT）按固定编号 S001–S056 生成图片。

## 结构

| 段落 | 时间 | 镜头 |
|---|---|---|
| 开场 | 0:00–0:23 | S001–S007 |
| 第一章 智能的诞生 | 0:23–1:01 | S008–S017 |
| 第二章 工作的重新定义 | 1:01–1:45 | S018–S028 |
| 第三章 创造力属于谁？ | 1:45–2:36 | S029–S040 |
| 第四章 AI时代的人类答案 | 2:36–3:44 | S041–S056 |

## 文件

| 文件 | 说明 |
|---|---|
| `asset_requirements.md` | 素材需求表（每个镜头的旁白、时长、画面、画幅、来源、字幕留白） |
| `gpt_brief.md` | 给素材端的说明 |
| `asset_status.csv` | 每个镜头的交付与使用状态 |
| `reorder.md` | 补单记录（第 0 轮 / 第 1 轮） |
| `assets_manifest.csv` | v1 实际使用的图片文件、尺寸与大小 |
| `narration.srt` | 字幕（41 条旁白 + 2 条片尾字幕） |
| `timeline.py` | 时间线：镜头时间、镜头运动、转场、字幕、章节卡、“想象”标注 → 生成 `shotlist.json` |
| `tools/patch_tl.py` | 把 homo-deus-future 的渲染引擎改造成本片版本（只需运行一次） |
| `tools/score_tl.py` | 配乐编排：各段乐器、停顿、高潮与尾声 |
| `tools/build_tl_music.py` | 把 `score_tl.py` 与 homo-deus-future 的音乐库合成为 `music.py` |
| `voiceover/v2/` | v2 旁白（zh-CN-YunjianNeural，每句一次合成）+ 英文字幕烧录 + 混音，含双语 / 英文 SRT 与混音报告 |
| `seg_render.sh` | 分 4 段渲染（0–60 / 60–120 / 120–180 / 180–224 s），可断点续跑；有 `out/score.wav` 时自动合成成片 |

## 构建

```
python3 timeline.py
python3 tools/patch_tl.py /path/to/homo-deus-future   # 只需一次
python3 tools/build_tl_music.py
./seg_render.sh            # 渲染画面
python3 music.py           # 生成 out/score.wav（不要与渲染同时运行，内存不够）
./seg_render.sh            # 合成 → out/21_lessons_ai_era_2K.mp4
bash voiceover/v2/run_v2.sh   # v2：旁白 + 英文字幕 → out/21_lessons_ai_era_2K_v2.mp4
```

- 图片放在 `assets/`，文件名见 `assets_manifest.csv`（图片不入库）
- 依赖 `../homo-deus-future`（渲染引擎与音乐库）；Python 3、numpy、Pillow、ffmpeg
- 替换返修图片：放入 `assets/`，在 `timeline.py` 中改图片映射，删除对应段的 `out/seg/seg_N.done` 后重跑即可，时间码与字幕不变

## 剪辑要点

- 连贯：每个镜头都有持续的推、拉、横移，相邻镜头重叠 1–1.8 s，用叠化、墨迹、径向、数字、变焦模糊等转场衔接，镜头运动跨转场不中断
- 质感：粒子与尘埃、光晕漏光、胶片颗粒、暗角；色调从冷灰深蓝（开场—第二章）过渡到金色、暖白与宇宙蓝（第三—四章）
- 节奏：关键问题后保留停顿（第三章 2:04–2:08、第四章 2:56–2:58），音乐同步留白
- 图形：片名卡、章节卡、19–21 世纪时间轴、未来科技镜头标注“想象”
- 配乐：低频电子 → 节奏与管弦叠加 → 钢琴与弦乐独奏 → 全管弦与克制的合唱 → 长尾余音

## 已知限制

- v1 无配音；v2 旁白为 edge-tts 神经语音（zh-CN-YunjianNeural）合成，中文字幕沿用 v1 烧录时间，英文字幕为新烧录
- 配乐为程序合成
- 图片为 1672×941，v1 升采样到 2K；高清返修见 `reorder.md` 第 1 轮

# 人类简史：七万年的文明觉醒（2K 纪录短片 · v2 配音版）

完全用脚本程序化生成的历史纪录短片：AI 生成的静帧 + 程序化镜头运动 / 调色 / 特效 / 字幕，配乐由 `music.py` 程序合成。

- 规格：2560×1440 · 24fps · 287s · H.264 + AAC
- 镜头数：38，旁白字幕：38 条 + 结尾字幕 2 条（中英双语）

## v2 改动（相对 v1 的 300 s 无配音版）

- 片尾孩子仰望星空的镜头由 27.5 s 剪到 14.5 s，全片 300 s → 287s；结尾两句字幕、片尾卡、片尾银河镜头相应提前
- 旁白重写为 38 句 + 2 句结尾字幕，全部配音（`voiceover/v2/`，edge-tts `zh-CN-YunjianNeural`，每句一次合成，语速 −4%~−8%）
- 字幕改为中英双语：中文在上，英文在下（`render_core.subtitle_layer / caption_layer`）；第 5 句“八卦”加引号
- 配乐：结尾合唱压缩进 266–287s（`music.py` 末段），DUR = 287
- 改动记录：`tools/patch_v2.py`（从 v1 文件一次性生成 v2，留档用）

## 文件

| 文件 | 作用 |
|---|---|
| `timeline.py` | **剪辑总表**：镜头、机位关键帧、调色、转场、字幕（含英文）、章节卡、标注、迁徙路线、闪光、羊皮纸纹理强度。改片子主要改这里 |
| `shotlist.json` | 由 `timeline.py` 生成，渲染器读取 |
| `render_core.py` | 调色 LUT、裁切、相机矩阵、颗粒 / 暗角 / 羊皮纸、星空粒子、火星、文字排版图层、文字遮罩 |
| `render.py` | 逐帧合成、转场（叠化 / 墨迹 / 径向 / 燃烧）、后期、ffmpeg 编码 |
| `music.py` | 合成 287 秒配乐 `out/score.wav`（鼓、宇宙氛围、弦乐、铜管、民族音色、合唱） |
| `seg_render.sh` | 分 5 段渲染（可断点续跑）→ 拼接 + 配乐 → `out/sapiens_70000_years_2K.mp4` |
| `voiceover/v2/` | 旁白台词与参数 `lines.json`、合成 `tts_line.py`、混音 `mix_tl.py`、一键脚本 `run_v2.sh` |
| `narration.srt` | 中英双语字幕（可导入剪映 / Premiere） |
| `script.md` | 分镜与旁白脚本 |
| `tools/` | 联系表、文字卡测试、文档生成、v2 补丁 |

素材图片不在仓库里（`assets/NN_name.jpg` + `assets/parchment.jpg`，1376×768），文件名见 `timeline.py`。

## 运行

```bash
pip install numpy opencv-python-headless pillow edge-tts   # 另需 ffmpeg 与 Noto Serif CJK 字体
bash voiceover/v2/run_v2.sh        # 一键：shotlist → 配乐 → 分段渲染 → 配音 → 混音 → out/sapiens_70000_years_2K_v2.mp4
# 或分步：
python3 timeline.py                                # 生成 shotlist.json
python3 music.py out/score.wav                     # 生成配乐
python3 render.py --stills 19,24,84 --sheet        # 预览静帧 -> frames/
bash seg_render.sh                                 # 分段渲染 + 配乐
python3 tools/make_docs.py                         # 重新生成 SRT / 脚本 / README
```

局部重渲染：`python3 render.py --video out/part.mp4 --start 150 --end 170`。

## 常见修改

- **改旁白文字 / 时间**：`voiceover/v2/lines.json`（起点 `s`、台词 `t`、英文 `en`、语速 / 音高 / 音量），再跑 `tools/patch_v2.py` 的字幕生成逻辑或直接改 `timeline.py` 的 `SUBS`
- **换镜头素材**：替换 `assets/` 中同名图片，或改 `shot(...)` 的文件名
- **镜头推拉**：`shot(...)` 的 `cam` = `[[起始缩放, cx, cy, 旋转], [结束缩放, cx, cy, 旋转]]`
- **调色**：`shot(...)` 的 grade（cosmos / ember / parch / earth / gold / goldblue / steel / future / mars），定义在 `render_core.GRADES`
- **配乐 / 人声比例**：`run_v2.sh` 里 `mix_tl.py` 的 `--music-db`（配乐静态增益）与 `--min-vmr`（人声至少高出配乐的 dB）

# 人类简史：七万年的文明觉醒（5 分钟 2K 纪录短片）

完全用脚本程序化生成的历史纪录短片：AI 生成的静帧 + 程序化镜头运动 / 调色 / 特效 / 字幕，配乐由 `music.py` 程序合成。

- 规格：2560×1440 · 24fps · 300s · H.264 + AAC
- 镜头数：38，旁白字幕：25 条

## 文件

| 文件 | 作用 |
|---|---|
| `timeline.py` | **剪辑总表**：镜头、机位关键帧、调色、转场、字幕、章节卡、标注、迁徙路线、闪光、羊皮纸纹理强度。改片子主要改这里 |
| `shotlist.json` | 由 `timeline.py` 生成，渲染器读取 |
| `render_core.py` | 调色 LUT、裁切、相机矩阵、颗粒 / 暗角 / 羊皮纸、星空粒子、火星、文字排版图层、文字遮罩 |
| `render.py` | 逐帧合成、转场（叠化 / 墨迹 / 径向 / 燃烧）、后期、ffmpeg 编码 |
| `music.py` | 合成 300 秒配乐 `out/score.wav`（鼓、宇宙氛围、弦乐、铜管、民族音色、合唱） |
| `narration.srt` | 旁白 + 结尾字幕（可导入剪映 / Premiere） |
| `script.md` | 分镜与旁白脚本 |
| `tools/` | 联系表、文字卡测试、文档生成 |

素材图片不在仓库里（`assets/NN_name.jpg` + `assets/parchment.jpg`，1376×768），文件名见 `timeline.py`。

## 运行

```bash
pip install numpy opencv-python-headless pillow   # 另需 ffmpeg 与 Noto Serif CJK 字体
python3 timeline.py                                # 生成 shotlist.json
python3 music.py                                   # 生成 out/score.wav
python3 render.py --stills 19,24,84 --sheet        # 预览静帧 -> frames/
python3 render.py --video out/video.mp4 --preset medium --crf 20
ffmpeg -i out/video.mp4 -i out/score.wav -c:v copy -c:a aac -b:a 256k -shortest \
       -movflags +faststart out/sapiens_70000_years_2K.mp4
python3 tools/make_docs.py                         # 重新生成 SRT / 脚本 / README
```

局部重渲染：`python3 render.py --video out/part.mp4 --start 150 --end 170`。

## 常见修改

- **改旁白文字 / 时间**：`timeline.py` 中的 `SUBS`
- **换镜头素材**：替换 `assets/` 中同名图片，或改 `shot(...)` 的文件名
- **镜头推拉**：`shot(...)` 的 `cam` = `[[起始缩放, cx, cy, 旋转], [结束缩放, cx, cy, 旋转]]`
- **调色**：`shot(...)` 的 grade（cosmos / ember / parch / earth / gold / goldblue / steel / future / mars），定义在 `render_core.GRADES`
- **配真人旁白**：把录音与 `narration.srt` 对齐，混音时将 `score.wav` 降低 6–8 dB

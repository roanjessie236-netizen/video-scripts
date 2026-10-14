# 未来简史：人类之后，会是谁？（3:54 2K 哲学纪录短片）

完全用脚本程序化生成：AI 生成的静帧 + 程序化镜头运动 / 调色 / 数据流与光晕特效 / 字幕，配乐由 `music.py` 程序合成。

- 规格：2560×1440 · 24fps · 234s · H.264 + AAC
- 镜头数：36，旁白字幕：23 条

## 与第一部的关系

渲染引擎沿用第一部 [`projects/sapiens-70000-years`](../sapiens-70000-years)：

1. 从第一部复制 `render_core.py`、`render.py`、`music.py`
2. `python3 tools/patch_engine.py` 给引擎打补丁（新增调色 void/cyan/lab/amber/dawn/tender、数据流 datastream、bloom、数字故障转场、prep 局部模糊等）
3. `python3 tools/build_music.py <第一部 music.py> music.py` 生成本片配乐脚本（第一部乐器库 + `tools/score.py` 新乐谱 + 第一部混响 / 母带）

## 文件

| 文件 | 作用 |
|---|---|
| `timeline.py` | **剪辑总表**：镜头、机位、调色、转场、特效、字幕、章节卡、标注。改片子主要改这里 |
| `shotlist.json` | 由 `timeline.py` 生成，渲染器读取 |
| `seg_render.sh` | 分 4 段渲染（可断点续渲），再拼接并混入配乐 |
| `tools/patch_engine.py` | 在第一部引擎上打补丁 |
| `tools/score.py` | 本片乐谱（开场电子氛围 → 交响电子 → 东方管弦史诗 → 钢琴合唱） |
| `tools/build_music.py` | 拼装 `music.py` |
| `tools/make_docs.py` | 由 `shotlist.json` 生成 `narration.srt`（`script.md` / `README.md` 手工维护） |
| `narration.srt` | 旁白 + 结尾字幕（可导入剪映 / Premiere） |
| `script.md` | 分镜与旁白脚本 |

素材图片不在仓库里（`assets/NN_name.jpg`，1376×768），文件名见 `timeline.py`。

## 运行

```bash
pip install numpy opencv-python-headless pillow   # 另需 ffmpeg 与 Noto Serif CJK 字体
python3 timeline.py                                # 生成 shotlist.json
python3 tools/make_docs.py                         # 生成 narration.srt
python3 tools/build_music.py ../sapiens-70000-years/music.py music.py
python3 music.py out/score.wav                     # 生成配乐
python3 render.py --stills 32,150,200              # 预览静帧 -> frames/
bash seg_render.sh                                 # 分段渲染 + 混音 -> out/homo_deus_future_2K.mp4
# 可选：放大为 4K
# ffmpeg -i out/homo_deus_future_2K.mp4 -vf "scale=3840:2160:flags=lanczos,unsharp=5:5:0.4" \
#        -c:v libx264 -preset veryfast -crf 19 -c:a copy out/homo_deus_future_4K.mp4
```

## 常见修改

- **改旁白文字 / 时间**：`timeline.py` 中的 `SUBS`，然后重新运行 `timeline.py` 与 `tools/make_docs.py`
- **换镜头素材**：替换 `assets/` 中同名图片
- **改配乐**：编辑 `tools/score.py` 后重新运行 `build_music.py` 与 `music.py`（各段和弦进行 P1–P5、旋律、音量曲线都在里面）
- **配真人旁白**：把录音与 `narration.srt` 对齐，混音时将 `score.wav` 降低 6–8 dB
- **注意中文乱码**：编辑后用 `grep -c $'\xef\xbf\xbd' timeline.py` 检查，结果应为 0

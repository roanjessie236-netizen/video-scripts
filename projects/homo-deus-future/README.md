# 未来简史：人类之后，会是谁？（2K 哲学纪录短片 · v2）

完全用脚本程序化生成：AI 生成的静帧 + 程序化镜头运动 / 调色 / 数据流与光晕特效 / 字幕，配乐由 `music.py` 程序合成。

- 当前版本 **v2**：`homo_deus_future_v2.mp4` · 2560×1440 · 24fps · 270.7s（4:30.7）· H.264 + AAC
- 镜头数：42，字幕：34 条（32 条旁白 + 2 条结尾字幕）
- 旧版 v1：`homo_deus_future_2K.mp4` · 234s · 36 个镜头

## v2 更新：“无用阶级”

- 插入位置：第三章“我们还是原来的自己吗？”（2:35.2–2:40.2）之后、第四章“人类的新纪元”之前，2:41.6–3:25.6，共 44 秒、7 个新镜头、9 条字幕，不加章节标题
- 画面：生命升级诊所 → 无人工厂 → 工人中近景 → 普通人的面孔 → 分化的城市 → 跟随人群 → 空间港大门，叠化接回第四章日出
- 立意：把“无用阶级”呈现为需要警惕的可能性；“无用”指劳动可能不再被需要，绝不意味着人失去价值
- 压缩：删去第三章义肢镜头（−4.8s）与月球→火星过渡中的一小节（−2.5s）；插入点之后的全部时间码已重新校准
- 音乐：插入段回落为低沉电子氛围 + 稀疏钢琴；第四章交响乐逐步恢复。`tools/score.py` 中的 `tmap()` 把 v1 乐谱自动映射到 v2 时间，插入段直接按 v2 时间书写
- 新素材：`assets/36_clinic.jpg` … `assets/42_toport.jpg`
- v1 → v2 时间码对照表见 `script.md` / `storyboard.md`

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
| `seg_render.sh` | 分段渲染（可断点续渲），再拼接并混入配乐 |
| `tools/patch_engine.py` | 在第一部引擎上打补丁 |
| `tools/score.py` | 本片乐谱（开场电子氛围 → 交响电子 → 钢琴脉冲 → “无用阶级”低沉电子 + 稀疏钢琴 → 东方管弦史诗 → 钢琴合唱） |
| `tools/build_music.py` | 拼装 `music.py` |
| `tools/make_docs.py` | 由 `shotlist.json` 生成 `narration.srt` |
| `tools/gen_docs_v2.py` | 由 `shotlist.json` 生成 `script.md` 与 `storyboard.md` |
| `narration.srt` | 旁白 + 结尾字幕（可导入剪映 / Premiere） |
| `script.md` | 分镜与旁白脚本（含音乐说明、v1→v2 对照） |
| `storyboard.md` | 逐镜头分镜表（素材、运镜、调色、转场、特效）+ 字幕时间轴 |

素材图片不在仓库里（`assets/NN_name.jpg`，1376×768），文件名见 `timeline.py`。

## 运行

```bash
pip install numpy opencv-python-headless pillow   # 另需 ffmpeg 与 Noto Serif CJK 字体
python3 timeline.py                                # 生成 shotlist.json
python3 tools/make_docs.py                         # 生成 narration.srt
python3 tools/gen_docs_v2.py                       # 生成 script.md / storyboard.md
python3 tools/build_music.py ../sapiens-70000-years/music.py music.py
python3 music.py out/score.wav                     # 生成配乐
python3 render.py --stills 170.5,231               # 预览静帧 -> frames/
bash seg_render.sh                                 # 分段渲染 + 混音 -> out/homo_deus_future_v2.mp4
```

## 常见修改

- **改旁白文字 / 时间**：`timeline.py` 中的 `SUBS`，然后重新运行 `timeline.py`、`tools/make_docs.py`、`tools/gen_docs_v2.py`
- **换镜头素材**：替换 `assets/` 中同名图片
- **改配乐**：编辑 `tools/score.py` 后重新运行 `build_music.py` 与 `music.py`（各段和弦进行、旋律、音量曲线都在里面；v1 部分按 v1 时间书写，由 `tmap()` 映射）
- **配真人旁白**：把录音与 `narration.srt` 对齐，混音时将 `score.wav` 降低 6–8 dB
- **注意中文乱码**：编辑后用 `grep -c $'\xef\xbf\xbd' timeline.py` 检查，结果应为 0

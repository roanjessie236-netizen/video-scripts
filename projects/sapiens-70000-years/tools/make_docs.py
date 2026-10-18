"""Generate narration.srt (bilingual), script.md and README.md from shotlist.json. (v2: 287 s, voiced, zh + en subs)"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'shotlist.json'), encoding='utf-8'))


def tc(t, srt=False):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}' if srt else f'{m}:{s:02d}'


# ------------------------------------------------------------------ SRT
cues = [(s, e, txt + ('\n' + x[0] if x else '')) for s, e, txt, _, *x in D['subtitles']] + \
       [(s, e, txt + ('\n' + x[0] if x else '')) for s, e, txt, *x in D['captions']]
cues.sort()
with open(os.path.join(ROOT, 'narration.srt'), 'w', encoding='utf-8') as f:
    for i, (s, e, txt) in enumerate(cues, 1):
        f.write(f'{i}\n{tc(s, True)} --> {tc(e, True)}\n{txt}\n\n')

# ------------------------------------------------------------------ script.md
ACTS = [
    ('开场 · 七万年前', 0, 21.8, '低沉鼓声 + 宇宙环境音；11.0s 与 17.6s 两次重击'),
    ('第一幕 · 认知革命', 21.8, 70.6, '史诗弦乐铺底，加入骨笛 / 手鼓式的民族音色'),
    ('第二幕 · 农业革命', 70.6, 120.6, '交响主题展开，106s 鼓点加强，节奏推进'),
    ('第三幕 · 帝国与科学革命', 120.6, 200.8, '铜管与定音鼓逐步叠加；177.6s 火箭升空为高潮重击'),
    ('第四幕 · 未来的选择', 200.8, D['duration'], f"大型管弦乐高潮（252s）→ 266s 后只留空灵合唱，至 {D['duration']:.0f}s 淡出"),
]
GRADE_CN = {'cosmos': '宇宙冷蓝', 'ember': '火焰橙 / 深褐', 'parch': '羊皮卷褐', 'earth': '岩石灰 / 土褐',
            'gold': '金色', 'goldblue': '金蓝', 'steel': '钢蓝', 'future': '未来银蓝', 'mars': '火星赭红'}
TRANS_CN = {'none': '—', 'fade': '叠化', 'inkmap': '墨迹晕染', 'radial': '径向光晕', 'burn': '羊皮卷燃烧', 'cut': '硬切'}

L = ['# 《人类简史：七万年的文明觉醒》— 分镜与旁白脚本', '',
     f'> 时长 {tc(D["duration"])} · 16:9 · 2560×1440 · 24fps · 灵感来自尤瓦尔·赫拉利《人类简史》', '',
     '核心思想：人类并不是因为力量而统治世界，而是因为拥有想象、合作和创造虚构秩序的能力。', '',
     '旁白标记：无标记 = 原稿旁白；☆ = 为衔接节奏补充的旁白（可删改）。全部旁白均已配音（v2），字幕为中英双语。', '']
for name, a, b, music in ACTS:
    L += [f'## {name}（{tc(a)}–{tc(b)}）', '', f'**音乐：** {music}', '']
    for c in D['chapters']:
        if a <= c[0] < b:
            L += [f'**章节卡：** {c[0]:.1f}s–{c[1]:.1f}s　{c[1 + 1]}「{c[3]}」/ {c[4]}', '']
    L += ['| 时间 | 镜头 | 画面 | 色调 | 转场 |', '|---|---|---|---|---|']
    for s in D['shots']:
        if a <= s['start'] < b or (a == 0 and s['start'] == 0):
            L.append(f"| {tc(s['start'])}–{tc(s['end'])} | `{s['id']}` | {s['desc']} | "
                     f"{GRADE_CN.get(s['grade'], s['grade'])} | {TRANS_CN.get(s['trans'], s['trans'])} |")
    L += ['', '**旁白：**', '']
    for s, e, txt, flag, *en in D['subtitles']:
        if a <= s < b:
            L.append(f"- `{tc(s)}` {txt}{'　☆' if flag == 'added' else ''}" + (f"<br>*{en[0]}*" if en else ''))
    labs = [lb for lb in D['labels'] if a <= lb[0] < b]
    if labs:
        L += ['', '**画面标注：**', '']
        L += [f'- `{tc(lb[0])}` {lb[2]} · {lb[3]}' for lb in labs]
    caps = [c for c in D['captions'] if a <= c[0] < b]
    if caps:
        L += ['', '**结尾字幕：**', ''] + [f'- `{tc(c[0])}` {c[2]}' + (f' / *{c[3]}*' if len(c) > 3 else '') for c in caps]
    L.append('')
L += ['## 片头 / 片尾', '',
      f"- 片名卡 {D['title_card'][0]}s–{D['title_card'][1]}s：人类简史 / 七万年的文明觉醒 / 70,000 YEARS OF AWAKENING",
      f"- 片尾卡 {D['endcard'][0]}s–{D['endcard'][1]}s：人类简史 · 七万年的文明觉醒 · 灵感来自尤瓦尔·赫拉利《人类简史》", '']
open(os.path.join(ROOT, 'script.md'), 'w', encoding='utf-8').write('\n'.join(L))

# ------------------------------------------------------------------ README
README = f'''# 人类简史：七万年的文明觉醒（2K 纪录短片 · v2 配音版）

完全用脚本程序化生成的历史纪录短片：AI 生成的静帧 + 程序化镜头运动 / 调色 / 特效 / 字幕，配乐由 `music.py` 程序合成。

- 规格：2560×1440 · 24fps · {D['duration']:.0f}s · H.264 + AAC
- 镜头数：{len(D['shots'])}，旁白字幕：{len(D['subtitles'])} 条 + 结尾字幕 {len(D['captions'])} 条（中英双语）

## v2 改动（相对 v1 的 300 s 无配音版）

- 片尾孩子仰望星空的镜头由 27.5 s 剪到 14.5 s，全片 300 s → {D['duration']:.0f}s；结尾两句字幕、片尾卡、片尾银河镜头相应提前
- 旁白重写为 38 句 + 2 句结尾字幕，全部配音（`voiceover/v2/`，edge-tts `zh-CN-YunjianNeural`，每句一次合成，语速 −4%~−8%）
- 字幕改为中英双语：中文在上，英文在下（`render_core.subtitle_layer / caption_layer`）；第 5 句“八卦”加引号
- 配乐：结尾合唱压缩进 266–{D['duration']:.0f}s（`music.py` 末段），DUR = {D['duration']:.0f}
- 改动记录：`tools/patch_v2.py`（从 v1 文件一次性生成 v2，留档用）

## 文件

| 文件 | 作用 |
|---|---|
| `timeline.py` | **剪辑总表**：镜头、机位关键帧、调色、转场、字幕（含英文）、章节卡、标注、迁徙路线、闪光、羊皮纸纹理强度。改片子主要改这里 |
| `shotlist.json` | 由 `timeline.py` 生成，渲染器读取 |
| `render_core.py` | 调色 LUT、裁切、相机矩阵、颗粒 / 暗角 / 羊皮纸、星空粒子、火星、文字排版图层、文字遮罩 |
| `render.py` | 逐帧合成、转场（叠化 / 墨迹 / 径向 / 燃烧）、后期、ffmpeg 编码 |
| `music.py` | 合成 {D['duration']:.0f} 秒配乐 `out/score.wav`（鼓、宇宙氛围、弦乐、铜管、民族音色、合唱） |
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
'''
open(os.path.join(ROOT, 'README.md'), 'w', encoding='utf-8').write(README)
print('wrote narration.srt (%d cues), script.md, README.md' % len(cues))

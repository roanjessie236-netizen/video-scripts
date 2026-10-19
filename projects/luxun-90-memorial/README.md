# 鲁迅逝世九十周年纪念视频《忘记我》

> 1936.10.19 — 2026.10.19。B站母版 **19:26**（20分钟以内）＋抖音合集《鲁迅的六次转身》＋视频号精华版。

- 📒 **完整分镜脚本（Notion）**：https://app.notion.com/p/83c3020dd0d0434db53f177cb4a40485
- 本目录是制作过程文件的存档（防止工作环境定时清除）。图片、视频等二进制文件不放进仓库，老照片可用 `tools/extract_assets.sh` 从本地 PDF 复现；网络素材由协作者按 `web_research_brief.md` 上传到 `assets/web/`。

## 状态
| 环节 | 状态 |
|---|---|
| 创意方案 | ✅ `01_concept.md` |
| 完整分镜（61 个镜头，含时码） | ✅ `script.md`（源数据 `storyboard.yaml`） |
| 鲁迅原文核对 | ✅ 93/93 与《鲁迅全集》2005年版逐字一致（`quotes.md`） |
| 三平台剪辑表 | ✅ `cuts.md` |
| 本地老照片索引 | ✅ `assets_index.md` |
| 网络素材搜集与史实核实 | ⏳ `web_research_brief.md` → `assets/web/` |
| 配音 / 木刻风动画 / 剪辑 | ⏳ 未开始 |

## 文件
| 文件 | 说明 |
|---|---|
| `01_concept.md` | 创意方案：回信结构、双声部、六次转身、AI 与版权红线 |
| `storyboard.yaml` | **分镜唯一数据源**（镜头、时长、画面、声音、素材码） |
| `assets.yaml` | 素材码说明（HZ／QJ／M／W） |
| `script.md` | 由 YAML 生成的完整分镜表（与 Notion 页面一致） |
| `cuts.md` | B站章节时间戳、抖音 9 集拆分、视频号精华版 |
| `quotes.md` / `quotes_src.tsv` / `quotes_checked.tsv` | 引文清单与全集核对结果（含全集 PDF 页码） |
| `assets_index.md` | 每张图／每段动画用于哪些镜头 |
| `web_research_brief.md` | 交给 GPT 的网络素材搜集与核实任务书 |
| `assets/web/` | 网络素材交付区（`index.csv`、`STATUS.md`、`W##/`） |
| `tools/render_script.py` | YAML → script.md / cuts.md / quotes.md / assets_index.md / 任务书；检查语速与时长 |
| `tools/verify_quotes.py` | 引文逐字核对 |
| `tools/extract_assets.sh` | 从本地 PDF 抽取分镜用到的老照片 |

## 工作流
```bash
# 1) 改分镜：只改 storyboard.yaml（或 assets.yaml）
# 2) 新增引文：追加到 quotes_src.tsv 后核对
pdftotext 鲁迅全集2005.pdf qj.txt && python3 tools/verify_quotes.py qj.txt quotes_src.tsv quotes_checked.tsv
# 3) 重新生成所有文档并检查时长（⚠️ 表示该镜头台词读不完）
python3 tools/render_script.py
# 4) 复现老照片
bash tools/extract_assets.sh 鲁迅画传.pdf 鲁迅全集2005.pdf out/
```

## 本地资料（不入库）
林贤治《鲁迅画传》（图文扫描版、文字版）、《鲁迅全集》2005年修订版18卷、钱理群《鲁迅作品十五讲》、孔庆东《正说鲁迅》。

## 版本
- v2.0（2026-10-19）：补强鲁迅思想与事业主线（立人、国民性、《灯下漫笔》“第三样时代”、从进化论到阶级论、左联、“引为同志”、事业总览、《亥年残秋偶作》、《新民主主义论》评价），参考公众号“子夜呐喊”文章《读懂毛主席才能真正读懂鲁迅》；新增引文 Q79—Q93；压缩部分生平细节，总长仍在20分钟以内；抖音新增思想专集 E7。采用与未采用的内容见 `01_concept.md` 第4节。
- v1.0（2026-10-19）：首版完整分镜、引文核对、三平台剪辑表、网络素材任务书。

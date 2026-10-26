# 配音

## 定稿（全片 v4 配音版）
- 旁白：云健 zh-CN-YunjianNeural（第一轮 A）；原文：云健·旧录音质感（第二轮 C3：-16%/-4Hz，200–5200 Hz＋1.8k 提升＋软削波，RT60 0.45 s 湿声 -17 dB）。
- `timeline_full.py`：打桩执行六个分章渲染脚本的“字幕排时”段（含转身字卡句；第二章经 M() 收紧映射），换算到全片时间 → tl_full.json（135 句：旁白 71、原文 64）。v3（序—一）须用旧版 storyboard（/data/luxun90/storyboard.yaml，S0 编号未重排），引文表用 GitHub 版 quotes_src.tsv。
- `tts_full.py`：语速三档——key（EMO 情感句、开篇首句、“第N次转身”字卡句）放慢降调；info（年份/数字、人名地名、书名、引号术语）正常语速，最多 -6% 补时；low（过渡/引出句，如“他说——”）+10%，不为凑字幕放慢（用户：信息量少的地方适当加快）。原文基础 -16%，最慢 -28%，最快 +10%（防压到下一句）。读音替换 PRON（只改配音稿）：许寿裳、阒寂、竦听、於菟、荷戟、憎恶、编校、正长、魏连殳、冯铿。
- `mix_full.py`：分章配乐 PLAN（见脚本），人声时压低 11 dB；输出 mix/stem_vo/stem_mus。
- `master.py`：整体增益到 -16 LUFS，alimiter 限幅（实测 TP -1.8 dBTP）；分轨同增益。
- `srt.py`：按配音实际起止生成 SRT（分行规则同成片 chunks）。
- `burl.js`：共享浏览器取 B站 BV1kf4y1a7Hm 两 P 的音频地址（下载需 Referer）。合集按原声大碟曲序：P1＝1–16 曲，P2＝17–32 曲。
- 画面不重编码：从 Notion“全片样片 v3”取上下两段，-c:v copy 换上音轨；上段 0–607.24 s，下段 607.24–1146.92 s。

## 试听阶段
- `timeline.py` / `tts.py` / `sample.py`（第一轮：旁白云健/云扬对调）/ `sample2.py`（第二轮：原文三候选）/ `ln.py`。

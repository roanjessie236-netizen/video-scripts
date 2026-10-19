"""从 storyboard.yaml + quotes_checked.tsv 生成 script.md / cuts.md / quotes.md，并检查语速。
用法: python3 tools/render_script.py [--notion notion.md]
规则: 旁白按 meta.vo_rate 字/秒、原文按 meta.quote_rate 字/秒估算；每段声音之间加 meta.gap 秒；
      所需时长 > 镜头时长 时标 ⚠️。"""
import yaml, csv, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sb = yaml.safe_load(open(os.path.join(ROOT, 'storyboard.yaml'), encoding='utf-8'))
Q = {r[0]: r for r in csv.reader(open(os.path.join(ROOT, 'quotes_checked.tsv'), encoding='utf-8'), delimiter='\t')}
M = sb['meta']; VR, QR, GAP = M['vo_rate'], M['quote_rate'], M['gap']
def n(s): return len(re.sub(r'\s', '', s))
def tc(s): s = round(s); return f"{s//60:02d}:{s%60:02d}"
shots, warn, t = {}, [], 0
for ch in sb['chapters']:
    ch['start'] = t
    for s in ch['shots']:
        need, sp = 0, 0
        for a in s['audio']:
            if 'vo' in a: need += n(a['vo'])/VR; sp += 1
            elif 'q' in a:
                k = n(Q[a['q']][1]) / QR
                need += k/2 if '前半' in a.get('voice', '') else k; sp += 1
            elif 'sil' in a: need += a['sil']
        need += GAP*max(sp-1, 0)
        s['need'], s['start'], s['ch'] = need, t, ch
        if need > s['dur'] + 0.05: warn.append(f"{s['id']} 需要{need:.1f}s > {s['dur']}s")
        t += s['dur']; shots[s['id']] = s
    ch['dur'] = t - ch['start']
TOTAL = t
def audio_lines(s, br):
    out = []
    for a in s['audio']:
        if 'vo' in a: out.append(f"【旁】{a['vo']}")
        elif 'q' in a:
            r = Q[a['q']]; v = f"（{a['voice']}）" if 'voice' in a else ''
            out.append(f"【原·{a['q']}】「{r[1]}」——{r[2]}{v}")
        elif 'sil' in a: out.append(f"【静】{a['sil']} 秒")
        elif 'sfx' in a: out.append(f"【效】{a['sfx']}")
        elif 'mus' in a: out.append(f"【乐】{a['mus']}")
    return br.join(out)
def shot_table(ch, br='<br />'):
    rows = ["| 镜号 | 时码 | 时长 | 画面 | 声音（旁白／原文／音效） | 素材／备注 |", "|---|---|---|---|---|---|"]
    for s in ch['shots']:
        assets = '、'.join(s['assets']); note = f"{br}注：{s['note']}" if s.get('note') else ''
        rows.append(f"| {s['id']} | {tc(s['start'])}–{tc(s['start']+s['dur'])} | {s['dur']}s | {s['visual']} | {audio_lines(s, br)} | {assets}{note} |")
    return '\n'.join(rows)
def cuts_md():
    L = ["## 三平台剪辑表", "", "### B站（母版）", f"- 16:9 横屏全片，总长 **{tc(TOTAL)}**（20 分钟以内）。章节时间戳可直接贴进简介：", ""]
    for ch in sb['chapters']: L.append(f"  - {tc(ch['start'])} {ch['title']}　{ch['theme']}")
    d = sb['cuts']['douyin']; L += ["", f"### 抖音合集《鲁迅的六次转身》", f"- {d['format']}；每集 = 钩子 {d['hook_sec']}s + 母版镜头 + 结尾“下一集”预告 {d['outro_sec']}s。", "",
         "| 集 | 标题 | 开头钩子（字幕＋旁白） | 使用镜头 | 估算时长 |", "|---|---|---|---|---|"]
    for e in d['episodes']:
        sec = d['hook_sec'] + d['outro_sec'] + sum(shots[i]['dur'] for i in e['shots'])
        L.append(f"| {e['id']} | {e['title']} | {e['hook']} | {'、'.join(e['shots'])} | {tc(sec)} |")
    w = sb['cuts']['shipinhao']; sec = sum(shots[i]['dur'] for i in w['shots'])
    L += ["", "### 视频号精华版", f"- {w['format']}", f"- 镜头：{'、'.join(w['shots'])}", f"- 估算时长：**{tc(sec)}**（另加 10 秒片头片尾）"]
    return '\n'.join(L)
def quotes_md():
    ok = sum(1 for r in Q.values() if r[5].startswith('✅'))
    L = [f"## 引文核对表（{ok}/{len(Q)} 条与《鲁迅全集》2005年修订版原文一致）", "",
         "核对方法：`tools/verify_quotes.py` 将全集 PDF 抽成文本，去除空白与注释角标后逐字精确匹配；页码为全集 PDF 页码。", "",
         "| 编号 | 原文 | 出处 | 收录 | 用于镜头 | 结果 | 全集PDF页 |", "|---|---|---|---|---|---|---|"]
    used = {}
    for s in shots.values():
        for a in s['audio']:
            if 'q' in a: used.setdefault(a['q'], []).append(s['id'])
    for r in Q.values():
        L.append('| ' + ' | '.join(r[:4] + ['、'.join(used.get(r[0], [])) or '备用'] + r[5:]) + ' |')
    return '\n'.join(L)
def script_md(br='<br />'):
    L = [f"# 《{M['title']}》——{M['subtitle']}｜完整分镜脚本 {M['version']}", "",
         f"- 版本日期：{M['date']}　｜　{M['master']}　｜　B站母版总长：**{tc(TOTAL)}**",
         f"- 语速基准：旁白 {VR} 字/秒，原文慢读 {QR} 字/秒；本表由 `tools/render_script.py` 从 `storyboard.yaml` 生成，**改脚本请改 YAML 再重新生成**。", "",
         "## 标记说明", "- 【旁】今天的旁白（第二人称“先生”只在序与尾声出现，其余用第三人称“他”）",
         "- 【原·Q##】只读鲁迅原文，编号对应引文核对表；**片中不让鲁迅“开口”，不做AI声音克隆或照片说话**；本版不用影视剧片段，也不用在版权期内的木刻作品",
         "- 【效】音效　【乐】音乐　【静】静音", "- 素材码：HZ-p## = 林贤治《鲁迅画传》图文版PDF页码；QJ-p#### = 《鲁迅全集》PDF页码（文前彩插）；W## = 需网络搜集（见 web_research_brief.md）；M## = 木刻风动画（AI辅助，须标识）", "",
         "## 章节总览", "", "| 章 | 时码 | 时长 | 主题 | 转身 |", "|---|---|---|---|---|"]
    for ch in sb['chapters']:
        L.append(f"| {ch['title']}（{ch['years']}） | {tc(ch['start'])}–{tc(ch['start']+ch['dur'])} | {tc(ch['dur'])} | {ch['theme']} | {ch.get('turn','—')} |")
    for ch in sb['chapters']:
        L += ["", f"## {ch['title']}　{ch['years']}｜{ch['theme']}（{tc(ch['start'])}–{tc(ch['start']+ch['dur'])}）", "", shot_table(ch, br)]
    return '\n'.join(L)
open(os.path.join(ROOT, 'script.md'), 'w', encoding='utf-8').write(script_md() + '\n')
open(os.path.join(ROOT, 'cuts.md'), 'w', encoding='utf-8').write('# 三平台剪辑表\n\n' + cuts_md().split('\n', 2)[2] + '\n')
open(os.path.join(ROOT, 'quotes.md'), 'w', encoding='utf-8').write('# 引文核对表\n\n' + quotes_md().split('\n', 2)[2] + '\n')
print('TOTAL', tc(TOTAL), TOTAL, 's')
for ch in sb['chapters']: print(f"  {ch['id']} {tc(ch['start'])} {ch['dur']}s")
print('WARN', len(warn)); print('\n'.join(warn))
slack = [(s['id'], s['dur'], round(s['need'],1)) for s in shots.values() if s['dur'] - s['need'] > 4]
print('SLACK>4s', slack)

# ---------- 素材索引 / 网络素材任务书 / 抽图脚本 / Notion 正文 ----------
A = yaml.safe_load(open(os.path.join(ROOT, 'assets.yaml'), encoding='utf-8'))
use = {}
for s in shots.values():
    for a in s['assets']: use.setdefault(a, []).append(s['id'])
missing = [a for a in use if (a.startswith('HZ-') and a[3:] not in A['HZ']) or (a.startswith('QJ-') and a[3:] not in A['QJ'])
           or (a[0] == 'M' and a not in A['M']) or (a[0] == 'W' and a not in A['W'])]
print('MISSING ASSET DESC', missing)
def key(a): return (a.split('-')[0] if '-' in a else a[0], int(re.sub(r'\D', '', a)))
def idx_md():
    L = ["# 素材索引（自动生成）", "", "图片文件不放进 Git 仓库（二进制、且来自受版权保护的出版物扫描）。需要时用 `tools/extract_assets.sh` 从本地 PDF 重新抽取。", ""]
    for k, title in [('HZ', '林贤治《鲁迅画传》图文版（PDF 页码）'), ('QJ', '《鲁迅全集》2005年修订版文前彩插（PDF 页码）')]:
        L += [f"## {k}｜{title}", "", "| 编号 | 内容 | 用于镜头 |", "|---|---|---|"]
        for a in sorted([x for x in use if x.startswith(k + '-')], key=key):
            L.append(f"| {a} | {A[k][a[3:]]} | {'、'.join(use[a])} |")
        L.append("")
    L += ["## M｜木刻风动画（AI 辅助生成，成片须按规定标识；风格参照1930年代新兴木刻，但不得临摹在版权期内的具体作品）", "", "| 编号 | 内容 | 用于镜头 |", "|---|---|---|"]
    for a in sorted([x for x in use if x[0] == 'M'], key=key): L.append(f"| {a} | {A['M'][a]} | {'、'.join(use[a])} |")
    L += ["", "## W｜网络素材与自拍（详见 web_research_brief.md；v2.5 起需向机构索取的一律停用，替代见 assets/web/ALTERNATIVES.md）", "", "| 编号 | 素材 | 用于镜头 | v2.5 处理 |", "|---|---|---|---|"]
    for a in sorted(A['W'], key=key): L.append(f"| {a} | {A['W'][a]['name']} | {'、'.join(use.get(a, ['—']))} | {A['W'][a].get('alt', '使用中')} |")
    return '\n'.join(L) + '\n'
PRI = {'P0': 'W01 W02 W11 W14 W16 W19 W22 W24 W25 W28 W33 W34 W36 W38'.split(), 'P2': 'W03 W05 W12 W17 W18 W23 W27 W37 W39 W41'.split()}
def pri(w): return 'P0' if w in PRI['P0'] else 'P2' if w in PRI['P2'] else 'P1'
def brief_md():
    L = ["# 网络素材搜集任务书｜《忘记我——鲁迅逝世九十周年》", "",
         "> 本文件交给 GPT（或其他有联网能力的助手）执行：按清单搜寻素材与核实史实，并把结果上传到本仓库。分镜脚本见同目录 `script.md`，镜号可在其中查到上下文。", "",
         "## 一、项目背景", f"- 纪念鲁迅逝世九十周年（1936.10.19—2026.10.19）的纪录短片，B站母版 {tc(TOTAL)}，另剪抖音合集和视频号精华版。",
         "- 风格：克制、真实；老照片＋原文朗读＋木刻风动画。**不使用 AI 生成的“老照片”，不让鲁迅“开口”，不做声音克隆。** 本版不用影视剧片段，也不用在版权期内的木刻作品。",
         "- **v2.5 起，凡需向机构核实、索取或申请授权的素材一律不再等待**，已改用《鲁迅画传》《鲁迅全集》彩插中的图、木刻风画面、自制字卡或自行实拍（对照表见 `assets/web/ALTERNATIVES.md`）；下表中标“停用”“已够用”的编号不必再找。", "",
         "## 二、交付规范（请严格遵守）",
         "1. **仓库与目录**：`roanjessie236-netizen/video-scripts`，分支 `main`，放在 `projects/luxun-90-memorial/assets/web/W##/`（每个编号一个文件夹）。",
         "2. **文件命名**：`W##-序号-简短英文或拼音描述.扩展名`，例如 `W16-01-kollwitz-das-opfer.jpg`。图片尽量 ≥ 1920px 长边、无水印。",
         "3. **每个文件夹必须有 `sources.md`**，逐个文件记录：文件名｜标题/内容｜来源页面 URL｜原始文件 URL｜作者/摄影者/收藏机构｜授权类型｜可否商用｜获取日期｜备注。",
         "4. **总索引**：同时追加到 `assets/web/index.csv`，表头：`id,file,title,source_url,author_or_holder,license,commercial_ok,grade,retrieved,notes`。",
         "5. **授权分级（grade）**：A＝公有领域/CC0；B＝CC BY 等需署名；C＝需向权利人申请；D＝不可用，仅作参考（不下载，只记链接）。",
         "6. **核实类任务**（W03、W09、W11、W14、W18、W23、W24、W25、W27、W33、W35、W36、W37、W38）交付 `findings.md`：结论一句话＋至少两个独立可靠来源（附链接与原文摘录/截图）＋可信度判断。",
         "7. **大文件**：单个文件超过 25 MB 不上传（GitHub 网页上传上限），视频一律只记链接、片段起止时间码和版权方。",
         "8. **不要**：上传带水印的图库预览图；把 AI 生成或上色修复的图当原始照片；引用来源不明的“鲁迅名言”。",
         "9. **影视作品片段**（W38、W40、W41）：在对应文件夹的 `clips.md` 里逐段记录：作品／年份／出品方或版权方／片源链接／起止时间码／画面内容／拟用镜号／画面中人物是否开口／授权状态（已获授权／申请中／仅参考）。视频文件一律不上传。", "",
         "## 三、任务清单", "", "优先级：P0＝播出前必须完成；P1＝重要；P2＝可选/补充。", "",
         "| 编号 | 优先级 | 素材/事项 | 要找什么 | 用于镜头 | 要求与授权提示 |", "|---|---|---|---|---|---|"]
    for w in sorted(A['W'], key=key):
        d = A['W'][w]
        if 'alt' in d: L.append(f"| {w} | {'已够用' if w in use else '停用'} | {d['name']} | v2.5 不再搜集：{d['alt']} | {'、'.join(use.get(w, ['—']))} | — |")
        else: L.append(f"| {w} | {pri(w)} | {d['name']} | {d['task']} | {'、'.join(use.get(w, ['核实/备用']))} | {d['rule']} |")
    L += ["", "## 四、已有素材（无需再找）", "- 林贤治《鲁迅画传》图文版与《鲁迅全集》2005年版文前彩插中的老照片已在本地抽取，编号见 `assets_index.md`（HZ-p##／QJ-p####）。如网上能找到同一照片更清晰的公有领域版本，可放进对应 W## 文件夹并在 sources.md 注明“替换 HZ-p##”。",
          f"- 片中引用的鲁迅原文 {len(Q)} 条已用《鲁迅全集》逐字核对（`quotes.md`），**不需要**再核对鲁迅原文；只有非鲁迅文字（萧红原话 W18、毛泽东评价 W33）需要核实。", "",
          "## 五、完成后", "- 在 `assets/web/STATUS.md` 里列出每个编号的状态：✅ 已完成／⚠️ 部分完成（说明缺什么）／❌ 找不到（说明尝试过的来源）。"]
    return '\n'.join(L) + '\n'
def extract_sh():
    hz = sorted({int(a[4:]) for a in use if a.startswith('HZ-')}); qj = sorted({int(a[4:]) for a in use if a.startswith('QJ-')})
    return f"""#!/usr/bin/env bash
# 从本地 PDF 复现分镜中用到的老照片（自动生成）。需要 poppler-utils（pdftoppm / pdfimages）。
# 用法: bash tools/extract_assets.sh 鲁迅画传.pdf 鲁迅全集2005.pdf out/
set -euo pipefail
HZ_PDF="$1"; QJ_PDF="$2"; OUT="${{3:-out}}"; mkdir -p "$OUT/HZ" "$OUT/QJ"
# 《鲁迅画传》是整页扫描：按页渲染 300dpi
for p in {' '.join(map(str, hz))}; do
  pdftoppm -f "$p" -l "$p" -r 300 -png "$HZ_PDF" "$OUT/HZ/HZ-p$p"
done
# 《鲁迅全集》文前彩插：直接抽取嵌入图片原始数据
for p in {' '.join(map(str, qj))}; do
  pdfimages -f "$p" -l "$p" -all "$QJ_PDF" "$OUT/QJ/QJ-p$p"
done
echo "done -> $OUT"
"""
open(os.path.join(ROOT, 'assets_index.md'), 'w', encoding='utf-8').write(idx_md())
open(os.path.join(ROOT, 'web_research_brief.md'), 'w', encoding='utf-8').write(brief_md())
open(os.path.join(ROOT, 'tools', 'extract_assets.sh'), 'w', encoding='utf-8').write(extract_sh())
if '--notion' in sys.argv:
    GH = 'https://github.com/roanjessie236-netizen/video-scripts/tree/main/projects/luxun-90-memorial'
    body = script_md().split('\n')
    body = '\n'.join(body[1:])  # 标题由页面标题承担
    PEND = [(1, "W33", "毛泽东评价原文：已据《毛选》第二卷第698页核对，改为引完整句"), (1, "W36", "翻译总量：毕生约三百万字，旁白已与“十八年”分开"),
            (1, "W14", "五烈士均未满三十周岁"), (1, "W35", "1935年12月5日书赠许寿裳，旁白改为“书赠”；手迹不再索取，用竖排字卡", "S7-01"),
            (1, "W18", "萧红原句已核（备用）"), (1, "W09", "三一八遇难人数：片中仍用原文“四十余”"), (1, "W03", "送葬人数：片中不写数字，不再另行核实", "S0-05"),
            (1, "HZ-p24", "《自题小像》手迹落款“二十一岁时作，五十一岁时写之，时辛未二月十六日也”，是1931年重写本，字幕注“1931年重写”"),
            (1, "HZ-p160", "确认是《惯于长夜过春时》手迹"), (1, "W30", "藤野赠照背面“惜别”题字：全集彩插 QJ-p496 已印出，不必索取", "S2-08"),
            (1, "W01／W02／W05／W06／W10／W11／W12／W13／W15／W17／W19／W21／W25／W29／W31／W32／W34", "需向机构索取、核实的素材全部改用画传、全集彩插、木刻风或字卡（对照表见 assets/web/ALTERNATIVES.md）", "—"),
            (1, "W38／W39／W40／W41／W42", "影像类素材（丧仪纪录影像、纪录片、影视剧、改编电影）与在版权期内的木刻作品默认不用；木刻作品将来取得授权时才替换对应木刻风画面", "—"),
            (0, "M02", "自制字卡：“民族魂”、日历纸、《亥年残秋偶作》、致内山完造绝笔（日文原文＋中译）、《答托洛斯基派的信》、《新民主主义论》、“落伍者”、《为了忘却的记念》；不仿任何人的笔迹", "S0-04、S0-05、S6-02、S6-08、S6-09、S7-01、S7-03、S7-06"),
            (0, "M03—M26", "木刻风动画（AI 辅助生成）：风格参照1930年代新兴木刻，不临摹在版权期内的具体作品", "—"),
            (0, "W26", "今日画面自行实拍：书店里的《呐喊》、翻书的手、读书人的背影、墓前鲜花；不拍未成年人正脸", "S7-06、S7-07"),
            (0, "W21／W22", "声音：算盘自录真木算盘，刻刀录真实木刻工序，上海街声与电车铃用拟音；古琴、木刻3条 CC BY 4.0 候选试听后在片尾署名；配乐用原创或平台曲库", "S6-01"),
            (0, "W04／W16", "片尾按许可证署名：W04 绍兴实景（作者与 CC 许可证）、W16 珂勒惠支《牺牲》（作者、作品、Städel 博物馆）"),
            (0, "HZ／QJ", "用画传、全集彩插图时裁掉书页版式与图注，只用图本身；字幕年份按原书图注", "—"),
            (0, "W28", "片名与字卡用 OFL 可商用字体，不用鲁迅集字"), (0, "W37", "参考文章中的轶事——未核实前不进正片", "—"),
            (0, "W24", "发布时三个平台都在投稿页主动声明AI生成内容")]
    pend = ["## 播出前待核清单"]
    for done, c, t, *fix in PEND:
        ss = [] if fix == ["—"] else (fix or sorted({x for k in c.split('／') for x in use.get(k, [])}, key=lambda z: (z.split('-')[0], int(z.split('-')[1]))))
        pend.append(f"- [{'x' if done else ' '}] {c} {t}" + (f"（{'、'.join(ss)}）" if ss else ""))
    head = [f"<callout icon=\"🎬\" color=\"gray_bg\">\nB站母版 **{tc(TOTAL)}**（20分钟以内）｜抖音合集 9 集｜视频号精华版约 5 分钟。全部 {len(Q)} 条鲁迅原文已用《鲁迅全集》2005年版逐字核对。制作文件存档：[GitHub · projects/luxun-90-memorial]({GH})\n</callout>", ""]
    chg = os.path.join(ROOT, 'notion_changes.md')
    if os.path.exists(chg): head.append(open(chg, encoding='utf-8').read())
    txt = '\n'.join(head) + body + '\n\n' + cuts_md() + '\n\n' + '\n'.join(pend) + '\n\n' + quotes_md() + '\n'
    open(sys.argv[sys.argv.index('--notion') + 1], 'w', encoding='utf-8').write(txt)

#!/usr/bin/env python3
"""Generate script.md and storyboard.md (v2) from shotlist.json.

Usage: python3 tools/gen_docs_v2.py      (run after python3 timeline.py)
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
D = json.load(open(os.path.join(ROOT, 'shotlist.json'), encoding='utf-8'))
GRADE = {'void': '深空黑蓝', 'cyan': '科技冷蓝', 'lab': '实验室青白', 'tender': '温柔蓝白',
         'dawn': '日出暖金', 'amber': '东方琥珀金'}
TRANS = {'none': '—', 'fade': '叠化', 'cut': '硬切', 'digital': '数字故障', 'radial': '径向光晕'}
FX = {'stars3d': '星空视差', 'datastream': '数据流', 'bloom': '光晕', 'shake': '震动', 'dim': '压暗'}
NEW = {'clinic', 'automation', 'worker', 'faces', 'divide', 'crowdwalk', 'toport'}
SECS = [
    ('开场', 0.0, 30.0,
     '低沉电子氛围 + 宇宙声音；13.0s 从地球冲入城市重击，城市亮灯钢片琴琶音，22.6s 片名重击'),
    ('第一章 · 智能革命', 30.0, 72.0,
     '96 BPM 合成器琶音 + 低频脉冲 + 电子鼓，弦乐旋律从 50s 进入；提问句处抽掉鼓点留白'),
    ('第二章 · 生命重塑', 72.0, 121.0,
     '交响乐融合电子：弦乐跳弓 + 钢片琴 DNA 动机 + 定音鼓；106s braam 重击，111s 起铜管'),
    ('第三章 · 人与机器融合', 121.0, 161.6,
     '温暖而不安的钢琴 + 电子脉冲 + 低音弦乐固定音型；地下城铜管；“如果……”段落只留钢琴、心跳与 u 音合唱。'
     'v2：删去义肢镜头对应的一小节，并去掉进入第四章前的上升音效，让音乐自然落入插入段'),
    ('插入段 · 谁能共享这个未来？（v2 新增，片中不加章节标题）', 161.6, 205.6,
     '音乐适度回落：低沉电子氛围（锯齿波持续低音 + 环境声）+ 稀疏钢琴（部分拍位留白）；'
     '2:48.2 数字故障切入无人工厂，淡入极轻的机械脉冲；3:00.4 普通人面孔处加入 u 音人声；'
     '3:08.6–3:17.4 分化的城市下是缓慢、不安的心跳；3:14.0 人群出发，钢琴改为逐拍前行；'
     '3:22.8 定音鼓轻击 + 缓慢上升音效（无重击），E 和弦交给第四章'),
    ('第四章 · 人类的新纪元', 205.6, 241.5,
     '交响乐逐步恢复：3:25.6 只有轻柔的镲片余响与古筝刮奏，弦乐铺底、合唱与主旋律由弱渐强，'
     '3:30.6 起定音鼓、3:33.1 起太鼓（渐强）；古筝、二胡、笛子、铜管、合唱依次回到全奏；'
     '月球到火星的过渡缩短一小节；3:54.5 空间港全奏高潮，接回“是否仍然知道如何成为人？”'),
    ('尾声', 241.5, 270.7,
     '温暖钢琴 + 合唱 + 女声独唱，264.9s 落在 Cadd9 和弦，最后 4.5 秒淡出'),
]
INSERT_NOTE = [
    '**立意：** 把“无用阶级”呈现为一种需要警惕的可能性，而不是预言：“无用”指劳动可能不再被经济体系需要，'
    '绝不意味着人失去价值。画面从宏大的科技奇观落到普通人的中近景，把“人类能成为什么”和“谁能共享这个未来”连在一起。',
    '**画面衔接：** 镜子（数字倒影）→ 同一座城市里的生命升级诊所（拉远露出城市）→ 数字故障切入无人工厂 → 工人中近景'
    ' → 街头普通人的面孔 → 金色高塔与阴影中的下层城市 → 跟随人群 → 走向空间港大门，叠化进第四章日出。',
    '**字幕：** 新增旁白按逗号拆为 9 条字幕，每条一行；字体、字号、位置与原片一致；“无用阶级”“无用”使用中文引号“”。',
]
EDITMAP = [
    ('0:00.0–2:12.0', '0:00.0–2:12.0', '不变'),
    ('2:12.0–2:16.8', '—', '删除义肢镜头（与握手、脑机接口重复）；字幕“身体的边界，正在被重新定义。”移到脑机接口镜头'),
    ('2:16.8–2:46.4', '2:12.0–2:41.6', '整体前移 4.8 秒'),
    ('—', '2:41.6–3:25.6', '新增 44 秒“无用阶级”段落（7 个镜头、9 条字幕）'),
    ('2:46.4–3:03.9', '3:25.6–3:43.1', '整体后移 39.2 秒'),
    ('3:03.9–3:06.4', '—', '删除月球→火星过渡中的一小节（太空展示重复）'),
    ('3:06.4–3:54.0', '3:43.1–4:30.7', '整体后移 36.7 秒'),
]


def tc(x):
    m, s = divmod(round(float(x), 1), 60)
    return '%d:%04.1f' % (int(m), s)


def cam_desc(cam):
    a, b = cam[0], cam[-1]
    p = []
    if b[0] - a[0] > 0.02:
        p.append('推近 %.2f→%.2f' % (a[0], b[0]))
    elif a[0] - b[0] > 0.02:
        p.append('拉远 %.2f→%.2f' % (a[0], b[0]))
    dx, dy = b[1] - a[1], b[2] - a[2]
    if dx > 0.015:
        p.append('右移')
    elif dx < -0.015:
        p.append('左移')
    if dy > 0.015:
        p.append('下摇')
    elif dy < -0.015:
        p.append('上摇')
    if abs(b[3] - a[3]) > 0.3:
        p.append('旋转 %.1f°' % (b[3] - a[3]))
    return ' · '.join(p) or '静止（微动）'


def fx_desc(s):
    p = [FX.get(k, k) for k in (s.get('fx') or {})]
    if (s.get('prep') or {}).get('blur'):
        p.append('招牌模糊')
    return '、'.join(p) or '—'


def in_sec(t, a, b):
    return a <= float(t) < b or (b >= D['duration'] and float(t) >= a)


SUBS = D['subtitles']
CAPS = D.get('captions', [])
shots = D['shots']
HEAD = ('> 时长 4:30.7 · 16:9 · 2560×1440 · 24fps · 灵感来自尤瓦尔·赫拉利《未来简史》\n'
        '> 版本 v2（homo_deus_future_v2.mp4）：在第三章“我们还是原来的自己吗？”与第四章“人类的新纪元”之间补入“无用阶级”段落\n')


def editmap(out):
    out.append('## v1 → v2 时间码对照\n')
    out.append('| v1 时间 | v2 时间 | 处理 |\n|---|---|---|')
    for r in EDITMAP:
        out.append('| %s | %s | %s |' % r)
    out.append('\nv1 片长 3:54.0 → v2 片长 4:30.7（+44.0 秒新增，−7.3 秒压缩）。插入点之后的字幕、章节卡、画面标注、闪白、片尾卡和配乐已全部按新时间重新校准。\n')


# ---------------------------------------------------------------- script.md
out = ['# 《未来简史：人类之后，会是谁？》— 分镜与旁白脚本（v2）\n', HEAD,
       '核心思想：未来最大的变化，不是机器超过人类，而是人类可能拥有重新设计生命和意识的能力。\n',
       '旁白标记：无标记 = 原稿旁白；☆ = 依据《未来简史》观点补充的旁白（可删改）；🆕 = v2 新增。每条旁白前为字幕起止时间。\n',
       '分镜细节（运镜、特效、素材文件）见 storyboard.md；字幕文件见 narration.srt。\n']
editmap(out)
for name, a, b, music in SECS:
    out.append('## %s（%s–%s）\n' % (name, tc(a), tc(b)))
    out.append('**音乐：** %s\n' % music)
    if a == 161.6:
        out.extend(x + '\n' for x in INSERT_NOTE)
    for c in D['chapters']:
        if in_sec(c[0], a, b):
            out.append('**章节卡：** %.1fs–%.1fs　%s「%s」/ %s\n' % (c[0], c[1], c[2], c[3], c[4]))
    out.append('| 时间 | 镜头 | 画面 | 色调 | 转场 |\n|---|---|---|---|---|')
    for s in shots:
        if in_sec(s['start'], a, b):
            sid = '`%s`' % s['id'] + (' 🆕' if s['id'] in NEW else '')
            out.append('| %s–%s | %s | %s | %s | %s |' % (tc(s['start']), tc(s['end']), sid, s.get('desc', ''),
                                                       GRADE.get(s['grade'], s['grade']), TRANS.get(s['trans'], s['trans'])))
    out.append('\n**旁白：**\n')
    for st, en, tx, src in SUBS:
        if in_sec(st, a, b):
            mark = '　☆' if src == 'added' else ''
            mark += '　🆕' if 161.6 <= st < 205.6 else ''
            out.append('- `%s–%s` %s%s' % (tc(st), tc(en), tx, mark))
    caps = [c for c in CAPS if in_sec(c[0], a, b)]
    if caps:
        out.append('\n**结尾字幕：**\n')
        out.extend('- `%s–%s` %s' % (tc(c[0]), tc(c[1]), c[2]) for c in caps)
    labs = [l for l in D['labels'] if in_sec(l[0], a, b)]
    if labs:
        out.append('\n**画面标注：**\n')
        out.extend('- `%s–%s` %s · %s' % (tc(l[0]), tc(l[1]), l[2], l[3]) for l in labs)
    out.append('')
out.append('## 片头 / 片尾\n')
out.append('- 片名卡 %.1fs–%.1fs：未来简史 / 人类之后，会是谁？' % tuple(D['title_card'][:2]))
out.append('- 片尾卡 %.1fs–%.1fs：未来简史 · 灵感来自尤瓦尔·赫拉利《未来简史》' % tuple(D['endcard'][:2]))
out.append('- 闪白：' + '、'.join('%.1fs' % f[0] for f in D['flashes']))
out.append('\n## 版本记录\n')
out.append('- v1（3:54）：homo_deus_future_2K.mp4')
out.append('- v2（4:30.7）：homo_deus_future_v2.mp4 — 新增“无用阶级”段落，压缩重复的科技与太空镜头，重校全部时间码\n')
open(os.path.join(ROOT, 'script.md'), 'w', encoding='utf-8').write('\n'.join(out))

# ---------------------------------------------------------------- storyboard.md
out = ['# 《未来简史》分镜表（v2）\n', HEAD,
       '由 shotlist.json 生成（`python3 tools/gen_docs_v2.py`）。所有镜头为 AI 静帧 + 虚拟运镜；运镜中的数字为缩放倍数。🆕 = v2 新增。\n']
editmap(out)
n = 0
for name, a, b, music in SECS:
    out.append('## %s（%s–%s）\n' % (name, tc(a), tc(b)))
    out.append('| # | 时间 | 时长 | 镜头 | 素材 | 画面 | 运镜 | 色调 | 转场 | 特效 |\n|---|---|---|---|---|---|---|---|---|---|')
    for s in shots:
        if in_sec(s['start'], a, b):
            n += 1
            sid = '`%s`' % s['id'] + (' 🆕' if s['id'] in NEW else '')
            out.append('| %d | %s–%s | %.1fs | %s | %s | %s | %s | %s | %s | %s |' % (
                n, tc(s['start']), tc(s['end']), s['end'] - s['start'], sid, s['image'], s.get('desc', ''),
                cam_desc(s['cam']), GRADE.get(s['grade'], s['grade']), TRANS.get(s['trans'], s['trans']), fx_desc(s)))
    out.append('')
out.append('## 字幕时间轴（与 narration.srt 一致）\n')
out.append('| # | 开始 | 结束 | 字幕 | 备注 |\n|---|---|---|---|---|')
cues = sorted([(s[0], s[1], s[2], s[3]) for s in SUBS] + [(c[0], c[1], c[2], 'caption') for c in CAPS])
for i, (st, en, tx, src) in enumerate(cues, 1):
    note = {'added': '补充旁白 ☆', 'brief': '原稿', 'caption': '结尾字幕'}.get(src, src)
    if 161.6 <= st < 205.6:
        note = 'v2 新增 🆕'
    out.append('| %d | %s | %s | %s | %s |' % (i, tc(st), tc(en), tx, note))
out.append('\n## 章节卡 / 画面标注 / 闪白\n')
for c in D['chapters']:
    out.append('- 章节卡 `%s–%s` %s「%s」' % (tc(c[0]), tc(c[1]), c[2], c[3]))
for l in D['labels']:
    out.append('- 标注 `%s–%s` %s · %s' % (tc(l[0]), tc(l[1]), l[2], l[3]))
out.append('- 片名卡 `%s–%s`，片尾卡 `%s–%s`' % (tc(D['title_card'][0]), tc(D['title_card'][1]), tc(D['endcard'][0]), tc(D['endcard'][1])))
out.append('- 闪白 ' + '、'.join('`%s`' % tc(f[0]) for f in D['flashes']) + '\n')
open(os.path.join(ROOT, 'storyboard.md'), 'w', encoding='utf-8').write('\n'.join(out))
print('wrote script.md and storyboard.md', n, 'shots', len(cues), 'cues')

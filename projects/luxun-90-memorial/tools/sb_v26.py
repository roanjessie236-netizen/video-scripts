"""v2.5 → v2.6：按样片 v3（各章 render 脚本里的 SEQ 与 README 时间线）同步 storyboard.yaml 与引文表。一次性迁移脚本。
- 旁白／原文：S3—S7 以各章 SEQ 为准（S0—S2 样片直接读 storyboard，未改）；sfx/mus 行保留
- 时长：S0 不变（样片重排，见 chapter note）；S1 用样片实测；S2 按 r2“声音结束＋0.5 秒切走”压缩；S3—S7 用样片实测（起点取 0.1 秒）
- 画面：按 README 各章时间线表，把落在镜头时段内的行用“→”串起来；素材写进 note
- 新增 S4-02a《在酒楼上》、S4-02b《孤独者》；引文表并入 Q94—Q97
用法：python3 tools/sb_v26.py [/tmp/gh]（第二个参数为 GitHub 上 preview/render_ch34.py 的本地副本目录）"""
import yaml, csv, re, sys, os, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = R + '/preview/'
GH = sys.argv[1] if len(sys.argv) > 1 else '/tmp/gh'
sb = yaml.safe_load(open(R + '/storyboard.yaml', encoding='utf-8'))
if sb['meta']['version'] != 'v2.5': sys.exit('storyboard.yaml 已不是 v2.5，不再重复迁移')
NEWQ = [('Q94', '飞了一个小圈子，便又回来停在原地点', '《在酒楼上》', '《彷徨》1924', '第四章', '514'),
        ('Q95', '我已经躬行我先前所憎恶，所反对的一切，拒斥我先前所崇仰，所主张的一切了。', '《孤独者》', '《彷徨》1925', '第四章', '567'),
        ('Q96', '这半年我又看见了许多血和许多泪，然而我只有杂感而已。', '《而已集·题辞》（1926年10月14日夜作）', '《而已集》1928', '第五章', '1120'),
        ('Q97', '应该和光阴偕逝，逐渐消亡，至多不过是桥梁中的一木一石', '《写在〈坟〉后面》', '《坟》1926', '第五章', '232')]
for fn, extra in (('quotes_src.tsv', False), ('quotes_checked.tsv', True)):
    rows = list(csv.reader(open(R + '/' + fn, encoding='utf-8'), delimiter='\t')); have = {r[0] for r in rows}
    for k, t, s, c, ch, pg in NEWQ:
        if k not in have: rows.append([k, t, s, c, ch] + (['✅ 原文一致', pg] if extra else []))
    with open(R + '/' + fn, 'w', encoding='utf-8', newline='') as f: csv.writer(f, delimiter='\t', lineterminator='\n').writerows(rows)
Q = {r[0]: r[1] for r in csv.reader(open(R + '/quotes_src.tsv', encoding='utf-8'), delimiter='\t')}
VR, QR, GAP, LEAD, TAIL = 4.2, 3.3, 0.6, 0.4, 0.5
def nchar(txt): return len(re.sub(r'[，。；：！？、—“”（）\s]', '', txt))
def SUB(t0, kind, txt=None): return t0 + nchar(txt or Q[kind]) / (QR if kind != 'vo' else VR)
def run(src):
    g = dict(Q=Q, QS={}, VR=VR, QR=QR, GAP=GAP, LEAD=LEAD, TAIL=TAIL, nchar=nchar, SUB=SUB)
    src = src[src.index('SEQ = ['):]; src = src[:src.index('\n', src.index('TOTAL_MAIN = round'))]
    exec(src, g); return g
CH = {}
CH['S34'] = run(open(GH + '/preview_render_ch34.py', encoding='utf-8').read())
CH['S5'] = run(open(P + 'parts/r5_body.py', encoding='utf-8').read())
CH['S6'] = run(open(P + 'parts6/body6.py', encoding='utf-8').read())
CH['S7'] = run(open(P + 'parts7/body7.py', encoding='utf-8').read())
SEQ = {sid: aud for g in CH.values() for sid, aud in g['SEQ']}
DUR = {}
for g in CH.values():
    for sid, _ in g['SEQ']: DUR[sid] = (g['ST'][sid], g['EN'][sid])
DUR['S7-08'] = (CH['S7']['TOTAL_MAIN'], CH['S7']['TOTAL_MAIN'] + 10.0)
SH = {s['id']: s for c in sb['chapters'] for s in c['shots']}
# 第二章 r2：按分镜原时长排，声音结束＋0.5 秒后的留白压掉；章节卡 5→4 秒
T = 0.0; ORIG2 = {}
for c in sb['chapters']:
    if c['id'] != 'S2': continue
    T2 = 0.0
    for s in c['shots']:
        t = T2 + 0.4
        for a in s['audio']:
            if 'sil' in a: t += a['sil']; continue
            if 'vo' in a: kind, txt = 'vo', a['vo']
            elif 'q' in a: kind, txt = a['q'], Q[a['q']]
            else: continue
            if s['id'] == 'S2-08': a1, a2 = txt.split('这是', 1); t = SUB(t, 'vo', a1) + GAP; t += nchar('这是' + a2) / VR + GAP; continue
            t = SUB(t, kind, txt) + GAP
        A = max(0.0, t - GAP - T2) if t > T2 + 0.4 + 1e-6 else 0.0
        ORIG2[s['id']] = (T2, s['dur']); T2 += s['dur']
        s['_nd'] = 4.0 if s['id'] == 'S2-01' else min(s['dur'], A + 0.5)
# README 时间线 → 画面
RD = open(P + 'README.md', encoding='utf-8').read()
def table(start, end):
    blk = RD[RD.index(start):]; blk = blk[:blk.index(end)] if end else blk
    out = []
    for ln in blk.split('\n'):
        m = re.match(r'\| ([\d.]+)[–-]([\d.]+) \| (.*?) \|(?: (.*?) \|)?', ln)
        if m: out.append((float(m.group(1)), float(m.group(2)), m.group(3).strip(), (m.group(4) or '').strip()))
    return out
TB = {'S01': table('# 样片 v3：真实素材为主', '## AI 情景再现（src3/a01'), 'S2': table('# 样片 v3·第二章', '## AI 情景再现（src3/b01'),
      'S34': table('### r2 时间线', '### AI 情景再现（r2'), 'S5': table('# 样片 v3·第五章', '# 样片 v3·第六章'),
      'S6': table('# 样片 v3·第六章', '## AI 情景再现（src6/'), 'S7': table('# 样片 v3·尾声', '## AI 情景再现（src7/')}
def rows_in(tb, a, b):
    return [r for r in tb if a - 0.15 <= r[0] < b - 0.15]
NEWSHOT = {'S4-02a': dict(id='S4-02a', dur=0, visual='', audio=[], assets=[], note='v2.6 新增（r2 用户意见：补《在酒楼上》《孤独者》对新文化运动的反思）'),
           'S4-02b': dict(id='S4-02b', dur=0, visual='', audio=[], assets=[], note='v2.6 新增；Q24 题《彷徨》由 S4-02 移来')}
for c in sb['chapters']:
    if c['id'] == 'S4':
        i = [s['id'] for s in c['shots']].index('S4-02'); c['shots'][i + 1:i + 1] = [NEWSHOT['S4-02a'], NEWSHOT['S4-02b']]
SH = {s['id']: s for c in sb['chapters'] for s in c['shots']}
S1W = dict(zip(['S1-01', 'S1-02', 'S1-03', 'S1-04', 'S1-05', 'S1-06', 'S1-07'], zip([68, 74, 87.6, 102, 123, 138, 155], [74, 87.6, 102, 123, 138, 155, 179.5])))
for c in sb['chapters']:
    if c['id'] == 'S0': c['note'] = '样片 v3 的序按“遗嘱大字‘忘记我’→葬仪→今日鲁迅墓→片名→《死》手稿七条→1936年10月→信笺‘先生：’”重排（见 preview/README.md「样片 v3」时间线），本分镜暂保留 v2.5 的镜头顺序与时长'
miss = []
t_ch = 0.0; T = 0.0; TL = []
for c in sb['chapters']:
    cid = c['id']; key = 'S01' if cid in ('S0', 'S1') else 'S34' if cid in ('S3', 'S4') else cid
    c0 = T
    for s in c['shots']:
        sid = s['id']
        if cid == 'S0': s['_nd'] = s['dur']; T += s['dur']; continue             # 序：样片 v3 重排了顺序（见 README），分镜保留 v2.5 顺序与时长
        if cid == 'S1': a, b = S1W[sid]; nd = b - a                              # 第一章：样片实测（章末《离家》多 1.5 秒）
        elif cid == 'S2': a, b = ORIG2[sid][0], ORIG2[sid][0] + ORIG2[sid][1]; nd = s.pop('_nd')
        else: a, b = DUR[sid]; nd = b - a
        if cid not in ('S0', 'S1'):
            pass
        rr = rows_in(TB[key], a, b)
        if rr:
            s['visual'] = ' → '.join(r[2] for r in rr)
            src = []
            for r in rr:
                for x in re.split(r'[；;]', r[3]):
                    x = x.strip()
                    if x and x not in ('—', '-') and x not in src: src.append(x)
            old = s.get('note', '')
            s['note'] = ('样片 v3 素材：' + '；'.join(src) if src else '样片 v3') + (('。' + old) if old and not old.startswith('v2.6') else ('。' + old if old else ''))
        else: miss.append(sid)
        if sid in SEQ:
            keep = [x for x in s['audio'] if 'sfx' in x or 'mus' in x]; new = []
            for x in SEQ[sid]:
                if 'vo' in x: new.append({'vo': x['vo']})
                elif 'q' in x: new.append({'q': x['q'], **({'txt': x['txt'], 'voice': '只读后半'} if 'txt' in x else {})})
                elif 'sil' in x: new.append({'sil': x['sil']})
            s['audio'] = new + keep
        s['_nd'] = nd; T += nd
# 起点取 0.1 秒，时长 = 相邻起点之差（累计不漂移）
t = 0.0; acc = 0.0
for c in sb['chapters']:
    for s in c['shots']:
        a = round(acc, 1); acc += s.pop('_nd'); s['dur'] = round(round(acc, 1) - a, 1)
TOTAL = acc
sb['meta']['version'] = 'v2.6'; sb['meta']['date'] = datetime.date(2026, 10, 22)
sb['meta']['sample'] = '时长、画面、旁白均按样片 v3 实测同步（序—第二章 r2、第三四章 r2、第五章、第六章、尾声）；镜头在最后一句声音结束后约 0.5 秒切走'
sb['meta']['timeline'] = {'S0—S1': '00:00—02:59.5', 'S2': '02:59.5—05:32.8', 'S3—S4': '05:32.8—10:07.2', 'S5': '10:07.2—12:04.7',
                          'S6': '12:04.7—16:25.9', 'S7': '16:25.9—18:50.4', '片尾': '18:50.4—19:00.4'}
yaml.safe_dump(sb, open(R + '/storyboard.yaml', 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=100000)
print('TOTAL', round(TOTAL, 2), 'miss', miss)

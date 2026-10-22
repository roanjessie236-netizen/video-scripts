"""v2.6 补：序按样片 v3 重排（preview/README.md「样片 v3」时间线；字幕起点见 render_preview_v3.py 第195—197行）。一次性脚本。
旧→新镜号：S0-01＋S0-03 → S0-01（“忘记我”大字）；S0-05 → S0-02（葬仪·民族魂）；S0-06 前半 → S0-03（今日鲁迅墓）；
S0-06 片名 → S0-04；S0-02 → S0-05（遗嘱）；S0-04 → S0-06（逝世）；S0-06 后半 → S0-07（信笺“先生：”）"""
import yaml, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sb = yaml.safe_load(open(R + '/storyboard.yaml', encoding='utf-8'))
S0 = sb['chapters'][0]; assert S0['id'] == 'S0'
if len(S0['shots']) != 6: sys.exit('序已重排，不再重复执行')
O = {s['id']: s for s in S0['shots']}
vo = lambda k: [a['vo'] for a in O[k]['audio'] if 'vo' in a][0]
v6a, v6b = vo('S0-06').split('。', 1); v6a += '。'
S0.pop('note', None)
S0['shots'] = [
 dict(id='S0-01', dur=7.0, visual='《死》手稿暗场，大字逐行显出“忘记我／管自己生活。／——倘不，那就真是胡涂虫。”',
      audio=[{'q': 'Q02'}, {'sfx': '钢笔划纸声；远处旧挂钟滴答'}, {'mus': '大提琴长音进入（极弱）'}], assets=['QJ-p2028', 'M01'],
      note='样片 v3 素材：QJ-p2028。由 v2.5 的 S0-01（钢笔写“死”）与 S0-03（“忘记我”放大）合并，开篇先亮出“忘记我”'),
 dict(id='S0-02', dur=12.6, visual='沙飞摄《鲁迅葬仪》相片卡 → 《新中华》1936年第4卷第21期《鲁迅先生的丧仪》 → 白旗“民族魂”字卡（闪白、震屏；小字“沈钧儒书”）',
      audio=[{'vo': vo('S0-05')}, {'sfx': '人群脚步声（拟音）'}], assets=['W02', 'M02'],
      note='样片 v3 素材：W02-01、W02-02；排字。原 S0-05。“民族魂”为沈钧儒书（已核）；白旗用字卡，不仿沈钧儒笔迹；送葬人数不写具体数字'),
 dict(id='S0-03', dur=4.4, visual='上海鲁迅墓今貌，年份 1936→2026 滚动', audio=[{'vo': v6a}], assets=['M02'],
      note='样片 v3 素材：Commons（上海鲁迅墓今貌）。原 S0-06 旁白前半'),
 dict(id='S0-04', dur=5.0, visual='片名“忘记我”（纸面墨字，闪白＋震屏；非鲁迅集字，见 W28），下方“鲁迅逝世九十周年 1936—2026”',
      audio=[{'mus': '主题旋律（钢琴+大提琴）第一次完整出现'}], assets=['M02'], note='样片 v3 素材：M02 遮罩。片名卡只有音乐'),
 dict(id='S0-05', dur=15.0, visual='大陆新村9号门（实拍） → 《死》手稿第12页（七条遗嘱，红圈原有） → 纸面竖排七条：第二条加深、第三条变红，最后第四条“忘记我，管自己生活”也变红',
      audio=[{'vo': vo('S0-02')}, {'q': 'Q71'}, {'q': 'Q01'}], assets=['W01', 'M02'],
      note='样片 v3 素材：Commons（大陆新村9号门）；W01-01；排字。原 S0-02。手稿图裁掉图注'),
 dict(id='S0-06', dur=14.0, visual='日历 1.5 秒翻完 44 页，“第 44 天”停 2 秒（背景故居卧室虚化） → 上海鲁迅故居二楼卧室（今貌） → 1936年10月留影相片卡，慢推到眼睛',
      audio=[{'vo': vo('S0-04')}], assets=['M02', 'W11', 'HZ-p231'],
      note='样片 v3 素材：排字＋W11；W11-01；HZ-p231。原 S0-04。旁白比画面早约 1.4 秒进入（压在七条遗嘱的尾巴上）'),
 dict(id='S0-07', dur=10.0, visual='信笺“先生：” → 绍兴水巷实拍渐褪为黑白，年份 2026→1881（转入第一章）',
      audio=[{'vo': v6b}], assets=['M02', 'W04'], note='样片 v3 素材：排字；W04-04。原 S0-06 旁白后半；水巷转场无旁白')]
assert abs(sum(s['dur'] for s in S0['shots']) - 68.0) < 1e-6
MAP = {'S0-02': 'S0-05', 'S0-03': 'S0-01', 'S0-04': 'S0-06', 'S0-05': 'S0-02'}
d = sb['cuts']['douyin']
for e in d['episodes']:
    if e['id'] == 'E0': e['shots'] = [f'S0-0{i}' for i in range(1, 8)]
    else: e['shots'] = [MAP.get(x, x) for x in e['shots']]
w = sb['cuts']['shipinhao']; w['shots'] = ['S0-01', 'S0-05', 'S0-06'] + [x for x in w['shots'] if not x.startswith('S0-')]
yaml.safe_dump(sb, open(R + '/storyboard.yaml', 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=100000)
# 其他文件里的旧镜号
for fn, pairs in (('assets.yaml', [('QJ-p2028《死》手稿首页（S0-02）', 'QJ-p2028《死》手稿首页（S0-01）'), ('“民族魂”白旗用字卡（S0-05）', '“民族魂”白旗用字卡（S0-02）')]),
                  ('tools/render_script.py', [('送葬人数：片中不写数字，不再另行核实", "S0-05")', '送葬人数：片中不写数字，不再另行核实", "S0-02")')])):
    s = open(R + '/' + fn, encoding='utf-8').read()
    for a, b in pairs: assert a in s, (fn, a); s = s.replace(a, b)
    open(R + '/' + fn, 'w', encoding='utf-8').write(s)
print('ok', [(s['id'], s['dur']) for s in S0['shots']])

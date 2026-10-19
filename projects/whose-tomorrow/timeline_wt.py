#!/usr/bin/env python3
"""《明天属于谁》(Whose Tomorrow?) - single source of truth for the edit. Run to (re)generate engine/shotlist.json.

VO-first (same method as homo-deus-future v4): every line sits on its measured take (voiceover/clips), separated by
scripted pauses; cuts are anchored to line starts and to word onsets (edge-tts WordBoundary).
Images: assets/NN_name.jpg = new Z-Image-Turbo frames (tools/prompts.py, graded here);
plates/hd_*.jpg = graded plates reused from 《未来简史》; plates/dg_*.jpg = diagrams (tools/diagrams.py).
cam = [[zoom, cx, cy, rot] start, [...] end]; trans = how a shot enters, tdur = overlap with the previous shot."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(HERE, 'voiceover')
ENG = os.path.join(HERE, 'engine')
LN = {x['i']: x for x in json.load(open(os.path.join(VO, 'lines.json'), encoding='utf-8'))}
DU = {int(k): v['dur'] for k, v in json.load(open(os.path.join(VO, 'clips', 'durs.json'))).items()}
BD = {int(k): v for k, v in json.load(open(os.path.join(VO, 'clips', 'bounds.json'), encoding='utf-8')).items()}

# ---------------------------------------------------------------- narration layout (pause before each line, s)
GAP = {1: 1.6, 2: 0.4, 3: 0.8, 4: 0.3, 5: 0.8,
       6: 6.4, 7: 0.4, 8: 0.5, 9: 0.2, 10: 0.5, 11: 0.2, 12: 0.8, 13: 1.0, 14: 0.7, 15: 0.4,     # 第一章
       16: 3.0, 17: 0.5, 18: 0.6, 19: 0.8, 20: 0.4, 21: 0.7, 22: 0.15,                          # 第二章
       23: 3.0, 24: 0.6, 25: 0.2, 26: 0.6, 27: 0.8, 28: 1.0, 29: 0.4, 30: 0.4, 31: 0.4,          # 第三章
       32: 3.0, 33: 0.6, 34: 0.5, 35: 0.4, 36: 0.9, 37: 0.9, 38: 0.5, 39: 0.5, 40: 0.9,          # 第四章
       41: 2.0, 42: 0.5, 43: 0.8, 44: 0.6, 45: 0.7, 46: 1.4, 47: 0.8}                            # 尾声
ST, cur = {}, 0.0
for i in sorted(LN):
    ST[i] = round(cur + GAP[i], 3)
    cur = ST[i] + DU[i]


def st(i):
    return ST[i]


def en(i):
    return round(ST[i] + DU[i], 3)


def w(i, word, occ=0):
    hits = [b[0] for b in BD[i] if b[2] == word]
    return round(ST[i] + max(0.0, hits[occ]), 3)


VOICE = [dict(i=i, start=st(i), dur=DU[i], file='%02d.wav' % i) for i in sorted(LN)]


# ---------------------------------------------------------------- camera presets (scaled to the shot length)
def push(z=1.04, rate=0.024, cx=.5, cy=.5, rot=0.0, dx=0.0, dy=0.0):
    return lambda d: [[z, cx, cy, 0], [z + rate * d, cx + dx, cy + dy, rot]]


def pull(z=1.04, rate=0.024, cx=.5, cy=.5, rot=0.0, dx=0.0, dy=0.0):
    return lambda d: [[z + rate * d, cx, cy, rot], [z, cx + dx, cy + dy, 0]]


def pan(z=1.12, sp=0.011, cy=.5, cx=.5, left=False, dz=0.0):
    k = -1 if left else 1
    return lambda d: [[z, cx - k * sp * d / 2, cy, 0], [z + dz * d, cx + k * sp * d / 2, cy, 0]]


def tilt(z=1.14, sp=0.012, cx=.5, cy=.5, up=True, dz=0.0):
    k = -1 if up else 1
    return lambda d: [[z, cx, cy - k * sp * d / 2, 0], [z + dz * d, cx, cy + k * sp * d / 2, 0]]


def fixed(a, b):
    return lambda d: [list(a), list(b)]


def have(img):
    return os.path.exists(os.path.join(ENG, 'assets', img))


# ---------------------------------------------------------------- shots
SH = []


def shot(id, image, start, cam, grade='none', trans='cut', tdur=0.0, ease=None, fx=None, desc=''):
    plate = image.startswith(('hd_', 'dg_'))
    p = {'plate': True} if plate else {}
    SH.append(dict(id=id, image=image, start=round(start, 3), cam=cam, grade='none' if plate else grade, trans=trans,
                   tdur=tdur, ease=ease, fx=fx or {}, prep=p, desc=desc))


BLUE = [255, 200, 90]      # BGR
CYAN = [255, 230, 120]
TITLE = [en(5) + 1.1, st(6) - 2.4]

# ---- 序 PROLOGUE
shot('keynes', '01_keynes1930.jpg', 0.0, push(1.03, 0.018, cx=.42, cy=.55), grade='sepia', trans='none',
     desc='London 1930: typewriter, manuscript, green lamp, rain')
shot('robotarms', '02_robotarms.jpg', w(2, '机器') - 0.04, pan(1.1, 0.012), grade='steel', ease='lin',
     desc='Automated car factory, orange robot arms')
shot('datacenter', '03_datacenter.jpg', st(3) - 0.06, pull(1.06, 0.03, cy=.52), grade='future',
     desc='Endless AI data-centre aisle, one engineer')
shot('overtime', '04_overtime.jpg', st(4) - 0.06, push(1.05, 0.03, cy=.52), grade='steel',
     desc='Office tower at night, exhausted workers still at desks')
shot('machinecity', '05_machinecity.jpg', st(5) - 0.5, push(1.03, 0.02, cy=.55), grade='amber', trans='fade',
     tdur=0.5, desc='Golden automated megacity, tiny human crowd looking up')
shot('earth', 'hd_02_earth.jpg', en(5) + 0.4, push(1.0, 0.03), trans='fade', tdur=0.9, ease='io',
     desc='Earth, night-side city lights (title)')
# ---- 第一章 磨坊与社会
shot('cave', '07_cave.jpg', st(6) - 2.5, push(1.03, 0.02, cy=.48), grade='ember', trans='fade', tdur=1.0,
     desc='Torch-lit cave paintings, hand stencils')
shot('campfire', '06_campfire.jpg', st(7) - 0.06, pan(1.1, 0.01), grade='ember', ease='lin',
     desc='Hunter-gatherers around a fire, an elder telling a story')
shot('wheat', '08_wheat.jpg', st(8) - 0.06, pan(1.1, 0.012, left=True), grade='gold', ease='lin',
     desc='Neolithic wheat harvest, first granaries')
shot('ziggurat', '09_ziggurat.jpg', st(9) - 0.06, tilt(1.12, 0.014, up=True), grade='earth', ease='lin',
     desc='Ziggurat city: labourers carry grain to the temple granary, nobles watch')
shot('steam', '12_steam.jpg', st(10) - 0.06, push(1.04, 0.035), grade='sepia', ease='punch',
     desc='Steam locomotive bursting out of steam, chimneys')
shot('textile', '13_textile.jpg', st(11) - 0.06, pan(1.1, 0.012), grade='sepia', ease='lin',
     desc='1850s cotton mill, power looms, women and child workers')
shot('quern', '10_quern.jpg', st(12) - 0.5, push(1.04, 0.02, cx=.42), grade='ember', trans='fade', tdur=0.5,
     desc='Medieval peasant at a hand quern, the lord\'s manor outside')
shot('steammill', '11_steammill.jpg', w(12, '蒸汽磨') - 0.04, push(1.04, 0.025), grade='sepia',
     desc='1840s steam flour mill: flywheel, belts, millstones')
shot('hm_a', 'dg_hm_a.jpg', st(13) - 0.4, fixed([1.0, .5, .5, 0], [1.012, .5, .5, 0]), trans='fade', tdur=0.5,
     ease='lin', desc='Diagram: productive forces')
shot('hm_b', 'dg_hm_b.jpg', w(13, '生产关系') - 0.1, fixed([1.012, .5, .5, 0], [1.05, .5, .5, 0]), trans='fade',
     tdur=0.35, ease='lin', desc='Diagram: forces -> relations -> superstructure')
shot('campfire2', '06_campfire.jpg', st(14) - 0.35, push(1.22, 0.02, cx=.6, cy=.52), grade='ember', trans='fade',
     tdur=0.45, desc='Callback: the storyteller, closer')
shot('owner', '14_owner.jpg', st(15) - 0.06, push(1.04, 0.02, cx=.55), grade='sepia', ease='lin',
     desc='Factory owner on an iron balcony above the workers')
shot('owner2', '14_owner.jpg', w(15, '占有') - 0.04, push(1.28, 0.02, cx=.8, cy=.42), grade='sepia',
     desc='The owner, closer')
# ---- 第二章 新的蒸汽机
shot('aiengine', '15_aiengine.jpg', st(16) - 2.6, push(1.04, 0.022), grade='steel', trans='digital', tdur=0.5,
     fx={'bloom': 0.25}, desc='An AI core shaped like a steam engine of light')
shot('aigrid', '16_aigrid.jpg', st(17) - 0.06, push(1.04, 0.03), grade='cyan',
     fx={'datastream': {'n': 380, 'y': 0.6, 'spread': 0.12, 'amp': 0.05, 'speed': 0.10, 'tilt': -0.04, 'col': BLUE,
                        'alpha': 0.55}}, desc='Night city with veins of blue light, like a power grid')
shot('ainetwork', 'hd_07_ainetwork.jpg', w(17, '渗入') - 0.04, push(1.06, 0.035, rot=-1.0), ease='lin',
     desc='Global AI network')
shot('automation', 'hd_37_automation.jpg', st(18) - 0.06, push(1.2, 0.02, cy=.41), ease='lin',
     desc='Lights-out automated factory')
shot('emptyoffice', '17_emptyoffice.jpg', w(18, '写字楼') - 0.3, push(1.04, 0.022), grade='steel',
     desc='Empty office at dawn, one employee carrying a box')
shot('switchboard', '18_switchboard.jpg', st(19) - 0.4, pan(1.1, 0.01, left=True), grade='mono', trans='fade',
     tdur=0.4, ease='lin', desc='1940s switchboard operators')
shot('station', '19_station.jpg', w(19, '创造') - 0.04, push(1.04, 0.03), grade='amber', ease='lin',
     desc='Rush hour in a giant station')
shot('metro', 'hd_12_metro.jpg', st(20) - 0.06, pan(1.12, 0.01), ease='lin', desc='Crowds in a smart metro hall')
shot('scaffold', '20_scaffold.jpg', st(21) - 0.06, tilt(1.12, 0.014, up=True), grade='gold', ease='lin',
     desc='Construction worker on high scaffolding at sunrise')
shot('humanoids', '21_humanoids.jpg', w(22, '具身') - 0.04, push(1.04, 0.025), grade='steel',
     desc='Humanoid robots in a logistics warehouse, one human supervisor')
# ---- 第三章 丰裕的悖论
shot('worker', 'hd_38_worker.jpg', st(23) - 2.6, push(1.04, 0.02, cx=.52), trans='fade', tdur=0.9,
     desc='A worker behind glass')
shot('worker2', 'hd_38_worker.jpg', w(23, '无用') - 0.04, push(1.2, 0.015, cx=.58, cy=.42), desc='Worker, closer')
shot('lonely', 'hd_48_lonely.jpg', st(24) - 0.06, pan(1.08, 0.008), grade='cyan', ease='lin',
     desc='Solitary figure on a rainy skybridge')
shot('paradox', '22_paradox.jpg', st(25) - 0.06, pull(1.04, 0.03, cy=.5), grade='ash',
     desc='Automated warehouse overflowing with goods behind a fence; jobless crowd outside in the rain')
shot('divide', 'hd_40_divide.jpg', st(26) - 0.06, tilt(1.2, 0.02, up=True), desc='Divided city: towers in sun, streets in shadow')
shot('conflict', 'dg_conflict.jpg', st(27) - 0.45, fixed([1.0, .5, .5, 0], [1.05, .52, .5, 0]), trans='fade',
     tdur=0.45, ease='lin', desc='Diagram: forces race ahead, relations stand still')
shot('luddites', '23_luddites.jpg', st(28) - 0.06, push(1.05, 0.03), grade='ember', ease='punch',
     fx={'shake': {'t0': w(28, '砸毁'), 'peak': en(28) + 0.3}}, desc='1812: Luddites smashing a power loom by torchlight')
shot('haijin', '24_haijin.jpg', st(29) - 0.06, pan(1.1, 0.01, left=True), grade='earth', ease='lin',
     desc='Ming harbour in fog, junks chained, soldiers block the port')
shot('flood', '25_flood.jpg', st(30) - 0.06, push(1.04, 0.05), grade='steel', ease='in',
     desc='A river in full flood through a gorge')
shot('dujiangyan', '26_dujiangyan.jpg', st(31) - 0.35, pull(1.04, 0.025), grade='gold', trans='fade', tdur=0.4,
     ease='out', desc='Ancient irrigation work splitting the river into calm channels')
# ---- 第四章 三种明天
shot('threeroads', '27_threeroads.jpg', st(32) - 2.6, push(1.03, 0.02, cy=.52), grade='dawn', trans='fade', tdur=1.0,
     desc='One road splitting into three, towards three cities')
shot('cloudcastle', '28_cloudcastle.jpg', st(33) - 0.06, tilt(1.1, 0.012, up=True), grade='cyan', ease='lin',
     desc='Fortress city of servers floating above the clouds')
shot('dataism', 'hd_56_dataism.jpg', st(34) - 0.06, push(1.03, 0.02), grade='cyan', desc='Everyone a node in a planetary data web')
shot('cloudserfs', '29_cloudserfs.jpg', st(35) - 0.06, push(1.04, 0.02), grade='void',
     desc='Endless hall of people labelling data under cold logos')
shot('queue', '30_queue.jpg', st(36) - 0.4, pan(1.1, 0.01), grade='ash', trans='fade', tdur=0.4, ease='lin',
     desc='Rainy queue at an automated welfare kiosk')
shot('assembly', '31_assembly.jpg', st(37) - 0.5, push(1.03, 0.022), grade='hope', trans='fade', tdur=0.6,
     desc='Citizens of a garden city voting in a circle')
shot('harvest', '32_harvest.jpg', st(38) - 0.06, pan(1.1, 0.011), grade='gold', ease='lin',
     desc='Robots harvest while families share a communal table')
shot('workshop', '33_workshop.jpg', st(39) - 0.06, push(1.04, 0.025), grade='hope',
     desc='Community workshop: teaching, music, building a boat')
shot('gardencity', '37_gardencity.jpg', st(40) - 0.8, push(1.02, 0.015, cy=.52), grade='dawn', trans='fade',
     tdur=0.9, desc='Harmonious future garden city at golden hour')
# ---- 尾声
shot('crossroads', '27_threeroads.jpg', st(41) - 1.0, pull(1.04, 0.02, cy=.52), grade='ash', trans='fade', tdur=0.9,
     fx={'dim': 0.75}, desc='Callback: the three roads, unresolved')
shot('march', '34_march1886.jpg', st(42) - 0.06, push(1.04, 0.03), grade='sepia', ease='lin',
     desc='Chicago 1886, workers marching for the eight-hour day')
shot('hands', '35_hands.jpg', st(43) - 0.5, push(1.04, 0.02), grade='gold', trans='fade', tdur=0.45,
     desc='Many hands lifting a beam together')
shot('bridge', '36_bridge.jpg', st(44) - 0.06, push(1.03, 0.025), grade='dawn', desc='People building a bridge toward a bright city')
shot('crowdwalk', 'hd_41_crowdwalk.jpg', st(45) - 0.06, pan(1.12, 0.012), ease='lin', desc='People walking together')
shot('toport', 'hd_42_toport.jpg', w(45, '历史') - 0.04, push(1.04, 0.03), ease='in', desc='The crowd streams toward the light')
shot('child', 'hd_34_child.jpg', st(46) - 0.9, push(1.02, 0.012, cy=.49), trans='fade', tdur=0.8, desc='A child looking at Earth')
shot('sunrise', 'hd_28_sunrise.jpg', st(47) - 0.35, push(1.04, 0.02), trans='fade', tdur=0.5, desc='Sun rising over the Earth')
shot('end', 'hd_28_sunrise.jpg', en(47) + 0.9, push(1.12, 0.006), trans='fade', tdur=1.4, fx={'dim': 0.5},
     desc='Sunrise, dimmed, for the end card')

ENDCARD = [en(47) + 1.4, en(47) + 7.0]
DUR = round(ENDCARD[1] + 1.2, 2)

for a, b in zip(SH, SH[1:]):
    a['end'] = round(b['start'] + (b['tdur'] if b['trans'] not in ('cut', 'none') else 0.0), 3)
SH[-1]['end'] = DUR
for s in SH:
    d = s['end'] - s['start']
    s['cam'] = [[round(v, 4) for v in c] for c in s['cam'](d)]
    if s['ease'] is None:
        s['ease'] = 'lin' if d < 4.0 else 'io'
    s.pop('tdur')

# ---------------------------------------------------------------- typography
SUBS, CAPS = [], []
for i in sorted(LN):
    x = LN[i]
    if x['kind'] == 'cap':
        CAPS.append([round(st(i) - 0.6, 3), round(en(i) + 1.0, 3), x['sub'], x['en']])
        continue
    zh, ee = x['sub'].split('|'), x['en'].split('|')
    if len(zh) == 1:
        SUBS.append([round(st(i) - 0.15, 3), round(en(i) + 0.35, 3), zh[0], x['src'], ee[0]])
    else:
        n1 = len(re.sub(r'[，。、：；？！“”《》\s]', '', zh[0]))
        c, t2 = 0, None
        for o, d, wd in BD[i]:
            if c >= n1:
                t2 = st(i) + o
                break
            c += len(re.sub(r'[，。、：；？！“”《》\s]', '', wd))
        SUBS.append([round(st(i) - 0.15, 3), round(t2 - 0.45, 3), zh[0], x['src'], ee[0]])
        SUBS.append([round(t2 - 0.15, 3), round(en(i) + 0.35, 3), zh[1], x['src'], ee[1]])
for X in (SUBS, CAPS):
    for a, b in zip(X, X[1:]):
        a[1] = round(min(a[1], b[0] - 0.1), 3)

CHAPTERS = [
    [st(6) - 2.2, st(6) + 0.1, '第一章', '磨坊与社会', 'THE MILL AND SOCIETY'],
    [st(16) - 2.3, st(16) + 0.1, '第二章', '新的蒸汽机', 'THE NEW STEAM ENGINE'],
    [st(23) - 2.4, st(23) + 0.05, '第三章', '丰裕的悖论', 'THE PARADOX OF ABUNDANCE'],
    [st(32) - 2.4, st(32) + 0.05, '第四章', '三种明天', 'THREE TOMORROWS'],
]
CHAPTERS = [[round(a, 3), round(b, 3), *r] for a, b, *r in CHAPTERS]
LABELS = [  # documentary lower-left labels [start, end, line1, line2, fade]
    [st(1) + 0.3, en(2) + 0.2, '凯恩斯 ·《我们后代的经济前景》· 1930', 'J. M. KEYNES · ECONOMIC POSSIBILITIES FOR OUR GRANDCHILDREN · 1930', 0.45],
    [st(12) + 0.3, en(12) + 0.5, '马克思 ·《哲学的贫困》· 1847', 'KARL MARX · THE POVERTY OF PHILOSOPHY · 1847', 0.4],
    [w(19, '创造') + 0.15, en(19) + 0.3, '2018 · 美国约 60% 的就业属于 1940 年还不存在的职业', 'AUTOR ET AL. · c. 60% OF US JOBS IN 2018 DID NOT EXIST IN 1940', 0.4],
    [st(20) + 0.4, en(20) + 0.4, '世界经济论坛 · 2025 · 到 2030 年新增 1.7 亿 · 减少 9200 万', 'WEF FUTURE OF JOBS 2025 · +170M CREATED · −92M DISPLACED · NET +78M', 0.4],
    [w(22, '具身') + 0.2, en(22) + 0.4, '三波替代 · 办公室 → 标准化体力 → 复杂体力', 'THREE WAVES · OFFICE (NOW–10 YRS) → ROUTINE MANUAL (5–20) → COMPLEX MANUAL (15+)', 0.4],
    [st(23) + 0.3, en(23) + 0.3, '赫拉利 ·《未来简史》· 2016', 'YUVAL NOAH HARARI · HOMO DEUS · "THE USELESS CLASS"', 0.4],
    [w(28, '卢德') - 0.1, en(28) + 0.3, '1811–1816 · 英格兰 · 卢德运动', 'THE LUDDITES · ENGLAND · 1811–1816', 0.35],
    [st(29) + 0.2, en(29) + 0.2, '明清海禁 · 始于 1371 年（洪武四年）', 'MING & QING MARITIME BANS · FROM 1371', 0.35],
    [w(31, '堤坝') - 0.2, en(31) + 0.5, '都江堰 · 约公元前 256 年 · 疏导而非堵塞', 'DUJIANGYAN · c. 256 BC · GUIDING THE RIVER, NOT DAMMING IT', 0.4],
    [st(34) + 0.3, en(34) + 0.3, '赫拉利 ·《今日简史》· 2018', 'HARARI · 21 LESSONS FOR THE 21ST CENTURY · 2018', 0.4],
    [w(35, '领主') - 0.1, en(35) + 0.3, '“技术封建主义” · 瓦鲁法基斯 · 2023', 'TECHNOFEUDALISM · YANIS VAROUFAKIS · 2023', 0.4],
    [w(38, '通过') + 0.1, en(38) + 0.3, '先例 · 阿拉斯加永久基金 · 1982 年起向每位居民分红', 'PRECEDENT · ALASKA PERMANENT FUND · A DIVIDEND FOR EVERY RESIDENT SINCE 1982', 0.4],
    [st(40) + 0.4, en(40) + 0.6, '马克思、恩格斯 ·《共产党宣言》· 1848', 'MARX & ENGELS · THE COMMUNIST MANIFESTO · 1848', 0.45],
    [st(42) + 0.2, en(42) + 0.3, '1886 年 5 月 1 日 · 芝加哥 · 争取八小时工作制大罢工', 'MAY 1, 1886 · CHICAGO · THE STRIKE FOR THE EIGHT-HOUR DAY', 0.4],
    [st(45) + 0.3, en(45) + 0.4, '马克思 ·《路易·波拿巴的雾月十八日》· 1852', 'MARX · THE EIGHTEENTH BRUMAIRE OF LOUIS BONAPARTE · 1852', 0.4],
]
LABELS = [[round(a, 3), round(b, 3), *r] for a, b, *r in LABELS]
FLASHES = [[TITLE[0], 0.35, 0.3], [w(12, '蒸汽磨') - 0.04, 0.16, 0.22], [st(16) - 2.6 + 0.3, 0.22, 0.3],
           [w(16, '蒸汽机'), 0.18, 0.25], [w(28, '砸毁'), 0.12, 0.2], [st(37) - 0.2, 0.18, 0.4]]
FLASHES = [[round(a, 3), b, c] for a, b, c in FLASHES]
SIL = en(40) + 1.2          # music thins to near-silence after the Manifesto line, rebuilds with the march
MARKS = dict(L={i: [st(i), en(i)] for i in LN}, title=TITLE[0], sil=SIL, end=DUR, endcard=ENDCARD[0],
             ch=[c[0] for c in CHAPTERS], steammill=w(12, '蒸汽磨'), engine=w(16, '蒸汽机'), smash=w(28, '砸毁'),
             turn=st(37), manifesto=st(40), march=st(42), final=st(46), shots={x['id']: x['start'] for x in SH},
             W={i: [[b[2], round(st(i) + max(0.0, b[0]), 3)] for b in BD[i]] for i in LN})

SCRIM_BOOST = {'robotarms': 1.6, 'gardencity': 1.5, 'harvest': 1.4, 'assembly': 1.4, 'scaffold': 1.3,
               'station': 1.3, 'machinecity': 1.3}
DATA = dict(title='明天属于谁', width=2560, height=1440, fps=24, duration=DUR,
            shots=SH, subtitles=SUBS, chapters=CHAPTERS, labels=LABELS, ticker={'windows': [], 'keys': []}, routes=[],
            title_card=[round(TITLE[0], 3), round(TITLE[1], 3)], captions=CAPS, endcard=[round(x, 3) for x in ENDCARD],
            parchment=[[0, 0.0], [DUR, 0.0]], flashes=FLASHES, voice=VOICE, marks=MARKS,
            scrim_boost=[[x['start'], x['end'], SCRIM_BOOST[x['id']]] for x in SH if x['id'] in SCRIM_BOOST])

if __name__ == '__main__':
    json.dump(DATA, open(os.path.join(ENG, 'shotlist.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    durs = [s['end'] - s['start'] for s in SH]
    print('DUR %.2f  shots %d  avg %.2f  min %.2f (%s)  subs %d caps %d  speech %.1f' % (
        DUR, len(SH), sum(durs) / len(durs), min(durs), SH[durs.index(min(durs))]['id'], len(SUBS), len(CAPS), sum(DU.values())))
    print('missing images:', sorted({s['image'] for s in SH if not s['prep'].get('plate') and not have(s['image'])}))

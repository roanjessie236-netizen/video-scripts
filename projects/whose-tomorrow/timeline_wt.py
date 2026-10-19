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
GAP = {1: 1.4, 2: 0.35, 3: 0.6, 4: 0.25, 5: 0.7,
       6: 6.0, 7: 0.35, 8: 0.4, 9: 0.15, 10: 0.45, 11: 0.15, 12: 0.7, 13: 0.8, 14: 0.6, 15: 0.35,   # 第一章
       16: 2.9, 17: 0.4, 18: 0.45, 19: 0.6, 20: 0.3, 21: 0.4,                                       # 第二章
       22: 2.9, 23: 0.5, 24: 0.3, 25: 0.35, 26: 0.5, 27: 0.6, 28: 0.7, 29: 0.8, 30: 0.3, 31: 0.3,   # 第三章
       32: 0.5,
       33: 2.9, 34: 0.5, 35: 0.45, 36: 0.35, 37: 0.6, 38: 0.9, 39: 0.45, 40: 0.7, 41: 0.6, 42: 0.8,  # 第四章
       43: 1.8, 44: 0.45, 45: 0.7, 46: 0.5, 47: 0.6, 48: 1.3, 49: 0.7}                               # 尾声
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


def crane(z=1.08, sp=0.012, dz=0.012, cx=.5, cy=.5, up=True):
    """rise (tilt) while pushing in."""
    k = -1 if up else 1
    return lambda d: [[z, cx, cy - k * sp * d / 2, 0], [z + dz * d, cx, cy + k * sp * d / 2, 0]]


def orbit(z=1.1, sp=0.008, rot=1.2, dz=0.008, cx=.5, cy=.5, left=False):
    """slow lateral arc: pan + roll + push."""
    k = -1 if left else 1
    return lambda d: [[z, cx - k * sp * d / 2, cy, -k * rot / 2], [z + dz * d, cx + k * sp * d / 2, cy, k * rot / 2]]


def fixed(a, b):
    return lambda d: [list(a), list(b)]


def have(img):
    return os.path.exists(os.path.join(ENG, 'assets', img))


# ---------------------------------------------------------------- shots
SH = []


def shot(id, image, start, cam, grade='none', trans='cut', tdur=0.0, ease=None, fx=None, desc=''):
    plate = image.startswith(('hd_', 'dg_'))
    p = {'plate': True} if plate else {}
    fx = dict(fx or {})
    if not plate:
        fx.setdefault('hand', 1.8)
    SH.append(dict(id=id, image=image, start=round(start, 3), cam=cam, grade='none' if plate else grade, trans=trans,
                   tdur=tdur, ease=ease, fx=fx, prep=p, desc=desc))


BLUE = [255, 200, 90]      # BGR
CYAN = [255, 230, 120]
WARM = [150, 205, 255]
TITLE = [en(5) + 1.1, st(6) - 2.4]
DUST = {'n': 70, 'v': [7, -4], 'size': [1.2, 5.5], 'col': [170, 215, 255], 'a': 0.5}
ASH = {'n': 60, 'v': [10, -14], 'size': [1.0, 4.0], 'col': [120, 170, 235], 'a': 0.55}
SNOW = {'n': 170, 'v': [26, 70], 'size': [1.5, 6.0], 'col': [250, 248, 245], 'a': 0.7, 'wob': 20}
STEAMF = {'a': 0.22, 'sp': 0.03, 'col': [215, 220, 225], 'thr': 0.4}
LOWFOG = {'a': 0.28, 'sp': 0.012, 'col': [200, 200, 196], 'y': 0.45, 'thr': 0.3}


def W_(i, word, occ=0, lead=0.04):
    return w(i, word, occ) - lead


# ---- 序 PROLOGUE
shot('keynes', '01_keynes1930.jpg', 0.0, push(1.03, 0.02, cx=.42, cy=.55), grade='sepia', trans='none',
     fx={'motes': dict(DUST, n=45, a=0.4)}, desc='London 1930: typewriter, manuscript, green lamp, rain')
shot('leisure', '40_leisure.jpg', w(2, '机器') - 0.25, orbit(1.1, 0.012, 1.0), grade='gold', trans='zoom', tdur=0.5,
     desc="Keynes's dream: 1930s leisure on a terrace while Art Deco robots work below")
shot('robotarms', '02_robotarms.jpg', st(3) - 0.06, pan(1.1, 0.016), grade='steel', ease='lin',
     fx={'sparks': {'src': [0.235, 0.62], 'rate': 40}}, desc='Automated car factory, orange robot arms')
shot('datacenter', '03_datacenter.jpg', W_(3, '越来越'), push(1.05, 0.045, cy=.52), grade='future',
     desc='Endless AI data-centre aisle, one engineer')
shot('overtime', '04_overtime.jpg', st(4) - 0.06, push(1.06, 0.035, cy=.52), grade='steel',
     fx={'rain': {'a': 0.14, 'n': 200, 'speed': 1100, 'ang': 0.05}}, desc='Office tower at night, exhausted workers')
shot('machinecity', '05_machinecity.jpg', st(5) - 0.5, crane(1.06, 0.012, 0.012, cy=.55), grade='amber', trans='leak',
     tdur=0.6, fx={'motes': dict(DUST, n=60)}, desc='Golden automated megacity, tiny human crowd looking up')
shot('earthnight', '41_earthnight.jpg', en(5) + 0.4, push(1.0, 0.03), grade='void', trans='fade', tdur=0.9, ease='io',
     fx={'par': 0, 'hand': 0}, desc='Earth at night from orbit (title)')
# ---- 第一章 磨坊与社会
shot('cave', '07_cave.jpg', st(6) - 2.5, push(1.03, 0.022, cy=.48), grade='ember', trans='fade', tdur=1.0,
     fx={'flicker': {'amp': 0.035}, 'motes': ASH}, desc='Torch-lit cave paintings, hand stencils')
shot('flint', '43_flint.jpg', W_(6, '劳动'), push(1.08, 0.05), grade='ember', ease='punch',
     fx={'flicker': {'amp': 0.03}, 'motes': dict(ASH, n=40)}, desc='Hands knapping a flint hand-axe')
shot('campfire', '06_campfire.jpg', st(7) - 0.06, pan(1.1, 0.012), grade='ember', ease='lin',
     fx={'flicker': {'amp': 0.03}}, desc='Hunter-gatherers around a fire, an elder telling a story')
shot('hunters', '42_hunters.jpg', W_(7, '大规模'), pan(1.12, 0.018, left=True), grade='steel', ease='lin',
     fx={'motes': SNOW}, desc='Dozens of hunters surround a mammoth: cooperation at scale')
shot('wheat', '08_wheat.jpg', st(8) - 0.06, pan(1.1, 0.014, left=True), grade='gold', ease='lin',
     fx={'motes': dict(DUST, n=80, v=[16, -3])}, desc='Neolithic wheat harvest, first granaries')
shot('scribe', '44_scribe.jpg', st(9) - 0.06, push(1.06, 0.04), grade='earth', fx={'motes': DUST},
     desc='Sumerian scribe recording grain in the temple storehouse')
shot('ziggurat', '09_ziggurat.jpg', W_(9, '阶级'), crane(1.1, 0.016, 0.01), grade='earth', ease='lin',
     desc='Ziggurat city: labourers carry grain, nobles watch')
shot('steam', '12_steam.jpg', st(10) - 0.2, push(1.04, 0.05), grade='sepia', ease='punch', trans='flash', tdur=0.3,
     fx={'fog': STEAMF}, desc='Steam locomotive bursting out of steam')
shot('millgate', '46_millgate.jpg', st(11) - 0.06, pan(1.1, 0.013), grade='sepia', ease='lin', fx={'fog': LOWFOG},
     desc='Former peasants file through the mill gates at dawn')
shot('textile', '13_textile.jpg', W_(11, '雇佣'), push(1.06, 0.045), grade='sepia', fx={'motes': dict(DUST, n=90)},
     desc='1850s cotton mill, power looms, women and child workers')
shot('quern', '10_quern.jpg', st(12) - 0.5, push(1.04, 0.02, cx=.42), grade='ember', trans='fade', tdur=0.5,
     fx={'motes': dict(DUST, n=60, a=0.45)}, desc='Medieval peasant at a hand quern')
shot('steammill', '11_steammill.jpg', w(12, '蒸汽磨') - 0.15, push(1.04, 0.03), grade='sepia', trans='flash', tdur=0.3,
     fx={'fog': dict(STEAMF, a=0.18)}, desc='1840s steam flour mill: flywheel, belts, millstones')
shot('hm_a', 'dg_hm_a.jpg', st(13) - 0.4, fixed([1.0, .5, .5, 0], [1.012, .5, .5, 0]), trans='fade', tdur=0.5,
     ease='lin', desc='Diagram: productive forces')
shot('hm_b', 'dg_hm_b.jpg', w(13, '生产关系') - 0.1, fixed([1.012, .5, .5, 0], [1.05, .5, .5, 0]), trans='fade',
     tdur=0.35, ease='lin', desc='Diagram: forces -> relations (= economic base) -> superstructure')
shot('myths', '47_myths.jpg', st(14) - 0.45, crane(1.08, 0.016, 0.012, up=True), grade='gold', trans='luma', tdur=0.7,
     desc='A crowd gazing up at colossal symbols: god, flag, gold')
shot('miners', '45_miners.jpg', st(15) - 0.06, push(1.06, 0.035, cy=.48), grade='ash', fx={'motes': ASH},
     desc='Soot-blackened miners: who does the work')
shot('owner', '14_owner.jpg', W_(15, '谁', 1), push(1.06, 0.035, cx=.62, cy=.45), grade='sepia',
     desc='Factory owner on an iron balcony: who owns')
# ---- 第二章 新的蒸汽机
shot('aiengine', '15_aiengine.jpg', st(16) - 2.6, push(1.04, 0.025), grade='steel', trans='glitch', tdur=0.4,
     fx={'bloom': 0.25}, desc='An AI core shaped like a steam engine of light')
shot('electric', '48_electric.jpg', st(17) - 0.06, pan(1.1, 0.014), grade='amber', ease='lin',
     fx={'flicker': {'amp': 0.02}}, desc='1900s street lit by electricity for the first time')
shot('aigrid', '16_aigrid.jpg', W_(17, '通用'), push(1.05, 0.04), grade='cyan', trans='zoom', tdur=0.4,
     fx={'datastream': {'n': 380, 'y': 0.6, 'spread': 0.12, 'amp': 0.05, 'speed': 0.10, 'tilt': -0.04, 'col': BLUE,
                        'alpha': 0.55}}, desc='Night city with veins of blue light, like a power grid')
shot('officetower', '50_officetower.jpg', st(18) - 0.06, crane(1.1, 0.016, 0.014), grade='steel',
     fx={'glitch': {'t': [w(18, '冲击')], 'd': 0.35}}, desc='Glass office tower under a storm sky')
shot('fordline', '51_fordline.jpg', st(19) - 0.06, pan(1.1, 0.016), grade='sepia', ease='lin',
     desc='1913 assembly line: machines replaced hands')
shot('switchboard', '18_switchboard.jpg', W_(19, '人'), pan(1.1, 0.012, left=True), grade='mono', ease='lin',
     desc='1940s switchboard operators: work moved to the mind')
shot('aimind', '49_aimind.jpg', st(20) - 0.2, push(1.05, 0.045), grade='cyan', trans='glitch', tdur=0.3,
     fx={'bloom': 0.2}, desc='A head of light and neural lines above a city')
shot('humanoids', '21_humanoids.jpg', W_(20, '具身'), push(1.05, 0.035), grade='steel',
     desc='Humanoid robots in a logistics warehouse')
shot('darkfactory', '52_darkfactory.jpg', st(21) - 0.06, push(1.06, 0.05), grade='void',
     fx={'sparks': {'src': [0.27, 0.66], 'rate': 50}}, desc='Lights-out factory, no humans')
shot('robotfarm', '53_robotfarm.jpg', w(21, '无人', 1) - 0.18, pan(1.1, 0.016), grade='gold', trans='whip', tdur=0.36,
     ease='lin', fx={'fog': dict(LOWFOG, a=0.2)}, desc='Autonomous tractors and drones, no farmers')
shot('emptyoffice', '17_emptyoffice.jpg', w(21, '无人', 2) - 0.18, pan(1.1, 0.014), grade='steel', trans='whip',
     tdur=0.36, ease='lin', fx={'motes': dict(DUST, n=40, a=0.35)}, desc='Empty office at dawn')
shot('station', '19_station.jpg', W_(21, '大部分'), pull(1.04, 0.035), grade='ash',
     desc='Rush-hour crowds: most jobs will be replaced')
# ---- 第三章 丰裕的悖论
shot('workerportrait', '54_workerportrait.jpg', st(22) - 2.6, push(1.03, 0.022, cx=.36), grade='steel', trans='dip',
     tdur=0.8, desc='A tired worker; robot arms keep working behind him')
shot('idlecrowd', '55_idlecrowd.jpg', W_(22, '庞大'), pull(1.04, 0.035), grade='cyan',
     desc='The "useless class": idle crowds under giant screens')
shot('hiring', '56_hiring.jpg', W_(23, '而'), pan(1.1, 0.012), grade='sepia', ease='lin', fx={'fog': LOWFOG},
     desc='Factory gate: a foreman picks a few workers from the crowd')
shot('scaffold', '20_scaffold.jpg', W_(24, '只能'), crane(1.1, 0.016, 0.01), grade='gold', ease='lin',
     desc='Selling labour power: a worker high on the scaffold')
shot('lockedgate', '57_lockedgate.jpg', st(25) - 0.06, push(1.04, 0.03), grade='ash',
     fx={'rain': {'a': 0.2, 'n': 260}}, desc='Laid-off workers at a locked gate; robots work on inside')
shot('paradox', '22_paradox.jpg', st(26) - 0.06, pull(1.04, 0.035, cy=.5), grade='ash',
     fx={'rain': {'a': 0.16, 'n': 200}}, desc='Warehouse overflowing behind a fence; jobless crowd outside')
shot('dividedcity', '58_dividedcity.jpg', W_(26, '多数'), tilt(1.16, 0.02, up=False), grade='earth', ease='lin',
     desc='Towers in the sun, streets in shadow')
shot('unsold', '59_unsold.jpg', W_(26, '机器'), push(1.05, 0.03), grade='ash', fx={'motes': dict(DUST, n=50, a=0.4)},
     desc='Warehouse of unsold goods gathering dust')
shot('scale', '61_scale.jpg', st(27) - 0.06, push(1.05, 0.03), grade='gold', desc='Gold outweighs bread')
shot('conflict_a', 'dg_conflict_a.jpg', st(28) - 0.45, fixed([1.0, .5, .5, 0], [1.03, .5, .5, 0]), trans='fade',
     tdur=0.45, ease='lin', desc='Diagram: the forces of production race ahead')
shot('conflict', 'dg_conflict.jpg', w(28, '生产关系') - 0.1, fixed([1.03, .5, .5, 0], [1.05, .52, .5, 0]), trans='fade',
     tdur=0.35, ease='lin', desc='Diagram: ...while the relations stand still')
shot('brake', '62_brake.jpg', st(29) - 0.06, push(1.06, 0.04), grade='ember', ease='punch',
     fx={'shake': {'t0': w(29, '刹车'), 'peak': w(29, '刹车') + 0.8}, 'sparks': {'src': [0.22, 0.06], 'rate': 55}},
     desc='A hand hauls on a locomotive brake, sparks fly')
shot('luddites', '23_luddites.jpg', st(30) - 0.06, push(1.05, 0.03), grade='ember', ease='punch',
     fx={'shake': {'t0': w(30, '砸毁'), 'peak': w(30, '砸毁') + 0.5}, 'flicker': {'amp': 0.03}},
     desc='1812: Luddites smashing a power loom by torchlight')
shot('looms', '63_looms.jpg', W_(30, '机器'), pan(1.12, 0.03), grade='sepia', ease='lin', trans='whip', tdur=0.3,
     desc='Endless rows of power looms: the machines multiplied')
shot('haijin', '24_haijin.jpg', st(31) - 0.06, pan(1.1, 0.012, left=True), grade='earth', ease='lin',
     fx={'fog': LOWFOG}, desc='Ming harbour in fog, junks chained')
shot('gunboats', '64_gunboats.jpg', W_(31, '换'), push(1.05, 0.04), grade='ember', ease='punch',
     fx={'shake': {'t0': w(31, '挨打'), 'peak': w(31, '挨打') + 0.4}, 'fog': dict(STEAMF, a=0.2)},
     desc='1840: steam warships shell the junks')
shot('flood', '25_flood.jpg', st(32) - 0.06, push(1.05, 0.06), grade='steel', ease='in', fx={'fog': dict(STEAMF, a=0.18)},
     desc='A river in full flood through a gorge')
shot('dujiangyan', '26_dujiangyan.jpg', w(32, '我们') - 0.35, pull(1.05, 0.03), grade='gold', trans='fade', tdur=0.45,
     ease='out', desc='Dujiangyan: the river guided into calm channels')
# ---- 第四章 三种明天
shot('threeroads', '27_threeroads.jpg', st(33) - 2.6, push(1.03, 0.022, cy=.52), grade='dawn', trans='fade', tdur=1.0,
     fx={'fog': dict(LOWFOG, a=0.22)}, desc='One road splitting into three, towards three cities')
shot('cloudcastle', '28_cloudcastle.jpg', st(34) - 0.06, crane(1.1, 0.014, 0.01), grade='cyan', ease='lin',
     desc='Fortress city of servers above the clouds')
shot('datalords', '65_datalords.jpg', W_(34, '少数'), push(1.06, 0.04), grade='void', desc='A few figures in a penthouse over a sea of data')
shot('dataweb', '66_dataweb.jpg', st(35) - 0.2, push(1.03, 0.03), grade='cyan', trans='glitch', tdur=0.3,
     fx={'bloom': 0.2, 'par': 0.5}, desc='Everyone a node in a planetary data web')
shot('cloudserfs', '29_cloudserfs.jpg', st(36) - 0.06, push(1.05, 0.03), grade='void',
     desc='Endless hall of people labelling data under cold logos')
shot('queue', '30_queue.jpg', W_(36, '施舍'), pan(1.1, 0.012), grade='ash', ease='lin', fx={'rain': {'a': 0.18}},
     desc='Rainy queue at an automated welfare kiosk')
shot('patcheddam', '67_patcheddam.jpg', st(37) - 0.06, push(1.05, 0.03), grade='steel', fx={'fog': dict(STEAMF, a=0.16)},
     desc='An old dam patched with sandbags, leaking')
shot('capitalflight', '68_capitalflight.jpg', W_(37, '税高'), pan(1.1, 0.014, left=True), grade='amber', ease='lin',
     desc='Capital leaves: ships and a jet depart, factories dark')
shot('emptymall', '60_emptymall.jpg', W_(37, '税低'), push(1.05, 0.035), grade='ash', fx={'flicker': {'amp': 0.03}},
     desc='An abandoned mall: the market cannot hold')
shot('deadend', '69_deadend.jpg', W_(37, '走'), push(1.04, 0.05), grade='ash', fx={'fog': dict(LOWFOG, a=0.3)},
     desc='The road ends at a cliff in fog')
shot('assembly', '31_assembly.jpg', st(38) - 0.6, push(1.03, 0.022), grade='hope', trans='leak', tdur=0.9,
     desc='Citizens of a garden city deciding together')
shot('coowners', '70_coowners.jpg', W_(38, '人人'), orbit(1.1, 0.012, 1.0), grade='hope',
     desc='Workers and engineers, co-owners of the machines')
shot('planning', '71_planning.jpg', st(39) - 0.06, push(1.05, 0.035), grade='hope', fx={'bloom': 0.15},
     desc='Public planning centre: a holographic map of supply')
shot('harvest', '32_harvest.jpg', W_(39, '为了'), pan(1.1, 0.013), grade='gold', ease='lin',
     desc='Robots harvest while families share a communal table')
shot('publichall', '72_publichall.jpg', st(40) - 0.5, push(1.03, 0.02), grade='dawn', trans='fade', tdur=0.5,
     fx={'motes': dict(DUST, n=50, a=0.4)}, desc='A public hall: basic needs freely provided')
shot('workshop', '33_workshop.jpg', st(41) - 0.06, push(1.05, 0.03), grade='hope', desc='Community workshop')
shot('care', '73_care.jpg', W_(41, '照顾'), push(1.05, 0.03), grade='dawn', desc='Caring for one another')
shot('gardencity', '37_gardencity.jpg', st(42) - 0.8, crane(1.04, 0.008, 0.008, cy=.52), grade='dawn', trans='fade',
     tdur=0.9, fx={'motes': dict(DUST, n=50, a=0.35)}, desc='Harmonious future garden city at golden hour')
# ---- 尾声
shot('darkdawn', '74_darkdawn.jpg', st(43) - 1.0, push(1.03, 0.02), grade='ash', trans='fade', tdur=0.9,
     fx={'dim': 0.8, 'fog': dict(LOWFOG, a=0.2)}, desc='A crowd on a hill before dawn')
shot('march', '34_march1886.jpg', st(44) - 0.06, push(1.05, 0.035), grade='sepia', ease='lin',
     desc='Chicago 1886, workers marching for the eight-hour day')
shot('hands', '35_hands.jpg', st(45) - 0.5, push(1.04, 0.025), grade='gold', trans='fade', tdur=0.45,
     desc='Many hands lifting a beam together')
shot('bridge', '36_bridge.jpg', st(46) - 0.06, push(1.04, 0.03), grade='dawn', desc='People building a bridge toward a bright city')
shot('forward', '75_forward.jpg', st(47) - 0.06, push(1.04, 0.04), grade='gold', fx={'motes': dict(DUST, n=60)},
     desc='People walking forward together toward the light')
shot('childhill', '76_childhill.jpg', st(48) - 0.9, push(1.02, 0.015, cy=.49), grade='dawn', trans='fade', tdur=0.8,
     desc='A child on a hill looking at the dawn horizon')
shot('sunrisecrowd', '77_sunrisecrowd.jpg', st(49) - 0.35, push(1.04, 0.025), grade='dawn', trans='fade', tdur=0.5,
     desc='The crowd raises its hands as the sun rises')
shot('earthdawn', '78_earthdawn.jpg', en(49) + 0.9, push(1.08, 0.008), grade='void', trans='fade', tdur=1.4,
     fx={'dim': 0.5, 'par': 0, 'hand': 0, 'flare': {'src': [0.37, 0.40], 'a': 0.45}}, desc='Sunrise over the Earth, dimmed, for the end card')

ENDCARD = [en(49) + 1.4, en(49) + 7.0]
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
        n1 = len(re.sub(r'[，。、：；？！“”《》—\s]', '', zh[0]))
        c, t2 = 0, None
        for o, d, wd in BD[i]:
            if c >= n1:
                t2 = st(i) + o
                break
            c += len(re.sub(r'[，。、：；？！“”《》—\s]', '', wd))
        SUBS.append([round(st(i) - 0.15, 3), round(t2 - 0.45, 3), zh[0], x['src'], ee[0]])
        SUBS.append([round(t2 - 0.15, 3), round(en(i) + 0.35, 3), zh[1], x['src'], ee[1]])
for X in (SUBS, CAPS):
    for a, b in zip(X, X[1:]):
        a[1] = round(min(a[1], b[0] - 0.1), 3)

CHAPTERS = [
    [st(6) - 2.2, st(6) + 0.1, '第一章', '磨坊与社会', 'THE MILL AND SOCIETY'],
    [st(16) - 2.3, st(16) + 0.1, '第二章', '新的蒸汽机', 'THE NEW STEAM ENGINE'],
    [st(22) - 2.4, st(22) + 0.05, '第三章', '丰裕的悖论', 'THE PARADOX OF ABUNDANCE', 0.215],
    [st(33) - 2.4, st(33) + 0.05, '第四章', '三种明天', 'THREE TOMORROWS'],
]
CHAPTERS = [[round(a, 3), round(b, 3), *r] for a, b, *r in CHAPTERS]
LABELS = [  # documentary lower-left labels [start, end, line1, line2, fade]
    [st(1) + 0.3, en(2) + 0.2, '凯恩斯 ·《我们后代的经济前景》· 1930', 'J. M. KEYNES · ECONOMIC POSSIBILITIES FOR OUR GRANDCHILDREN · 1930', 0.45],
    [st(12) + 0.3, en(12) + 0.5, '马克思 ·《哲学的贫困》· 1847', 'KARL MARX · THE POVERTY OF PHILOSOPHY · 1847', 0.4],
    [w(20, '人工智能') + 0.1, en(20) + 0.4, 'AI 替代脑力 · 具身智能替代体力', 'AI REPLACES MENTAL LABOUR · EMBODIED AI REPLACES MANUAL LABOUR', 0.4],
    [st(22) + 0.3, en(22) + 0.3, '赫拉利 ·《未来简史》· 2016', 'YUVAL NOAH HARARI · HOMO DEUS · "THE USELESS CLASS"', 0.4],
    [w(30, '卢德') + 0.1, en(30) + 0.3, '1811–1816 · 英格兰 · 卢德运动', 'THE LUDDITES · ENGLAND · 1811–1816', 0.35],
    [st(31) + 0.2, w(31, '换') - 0.1, '明清海禁 · 始于 1371 年（洪武四年）', 'MING & QING MARITIME BANS · FROM 1371', 0.3],
    [w(31, '换') + 0.05, en(31) + 0.3, '1840 · 鸦片战争', 'THE FIRST OPIUM WAR · 1840', 0.3],
    [w(32, '堤坝') - 0.2, en(32) + 0.5, '都江堰 · 约公元前 256 年 · 疏导而非堵塞', 'DUJIANGYAN · c. 256 BC · GUIDING THE RIVER, NOT DAMMING IT', 0.4],
    [st(35) + 0.3, en(35) + 0.3, '赫拉利 ·《今日简史》· 2018', 'HARARI · 21 LESSONS FOR THE 21ST CENTURY · 2018', 0.4],
    [w(36, '领主') - 0.1, en(36) + 0.3, '“技术封建主义” · 瓦鲁法基斯 · 2023', 'TECHNOFEUDALISM · YANIS VAROUFAKIS · 2023', 0.4],
    [st(40) + 0.4, en(40) + 0.6, '马克思 ·《哥达纲领批判》· 1875 ·「各尽所能，按需分配」', 'MARX · CRITIQUE OF THE GOTHA PROGRAMME · 1875 · "TO EACH ACCORDING TO NEEDS"', 0.45],
    [st(42) + 0.4, en(42) + 0.6, '马克思、恩格斯 ·《共产党宣言》· 1848', 'MARX & ENGELS · THE COMMUNIST MANIFESTO · 1848', 0.45],
    [st(44) + 0.2, en(44) + 0.3, '1886 年 5 月 1 日 · 芝加哥 · 争取八小时工作制大罢工', 'MAY 1, 1886 · CHICAGO · THE STRIKE FOR THE EIGHT-HOUR DAY', 0.4],
    [st(47) + 0.3, en(47) + 0.4, '马克思 ·《路易·波拿巴的雾月十八日》· 1852', 'MARX · THE EIGHTEENTH BRUMAIRE OF LOUIS BONAPARTE · 1852', 0.4],
]
LABELS = [[round(a, 3), round(b, 3), *r] for a, b, *r in LABELS]
FLASHES = [[TITLE[0], 0.35, 0.3], [st(16) - 2.6 + 0.3, 0.22, 0.3], [w(16, '蒸汽机'), 0.18, 0.25],
           [w(30, '砸毁'), 0.12, 0.2], [w(31, '挨打'), 0.1, 0.18], [st(38) - 0.2, 0.18, 0.4]]
FLASHES = [[round(a, 3), b, c] for a, b, c in FLASHES]
SIL = en(42) + 1.2          # music thins to near-silence after the Manifesto line, rebuilds with the march
SHOTS_AT = {x['id']: x['start'] for x in SH}
ALIAS = {  # v1 shot ids still used as cue points by tools/score_wt.py -> the v2 moment playing the same role
    'ziggurat': SHOTS_AT['scribe'], 'textile': SHOTS_AT['millgate'], 'campfire2': SHOTS_AT['myths'],
    'owner': SHOTS_AT['miners'], 'owner2': SHOTS_AT['owner'], 'aigrid': SHOTS_AT['electric'],
    'ainetwork': SHOTS_AT['aigrid'], 'automation': SHOTS_AT['officetower'], 'emptyoffice': w(18, '写字楼'),
    'switchboard': SHOTS_AT['fordline'], 'station': SHOTS_AT['switchboard'], 'metro': SHOTS_AT['aimind'],
    'scaffold': SHOTS_AT['darkfactory'], 'humanoids': SHOTS_AT['robotfarm'], 'worker': SHOTS_AT['workerportrait'],
    'worker2': SHOTS_AT['idlecrowd'], 'lonely': SHOTS_AT['hiring'], 'divide': SHOTS_AT['scale'],
    'conflict': SHOTS_AT['conflict_a'], 'luddites': SHOTS_AT['brake'], 'dataism': SHOTS_AT['dataweb'],
    'queue': SHOTS_AT['patcheddam'], 'harvest': SHOTS_AT['planning'], 'crossroads': SHOTS_AT['darkdawn'],
    'crowdwalk': SHOTS_AT['forward'], 'toport': w(47, '历史'), 'child': SHOTS_AT['childhill'],
    'sunrise': SHOTS_AT['sunrisecrowd'], 'end': SHOTS_AT['earthdawn'],
    'v2_scaffold': SHOTS_AT['scaffold'], 'v2_lockedgate': SHOTS_AT['lockedgate'], 'v2_queue': SHOTS_AT['queue'],
    'v2_harvest': SHOTS_AT['harvest'], 'v2_publichall': SHOTS_AT['publichall'], 'v2_humanoids': SHOTS_AT['humanoids'],
}
MARKS = dict(L={i: [st(i), en(i)] for i in LN}, title=TITLE[0], sil=SIL, end=DUR, endcard=ENDCARD[0],
             ch=[c[0] for c in CHAPTERS], steammill=w(12, '蒸汽磨'), engine=w(16, '蒸汽机'), smash=w(30, '砸毁'),
             turn=st(38), manifesto=st(42), march=st(44), final=st(48), shots={**SHOTS_AT, **ALIAS},
             W={i: [[b[2], round(st(i) + max(0.0, b[0]), 3)] for b in BD[i]] for i in LN})

SCRIM_BOOST = {'robotarms': 1.6, 'gardencity': 1.5, 'harvest': 1.4, 'assembly': 1.4, 'scaffold': 1.3,
               'station': 1.3, 'machinecity': 1.3, 'leisure': 1.3, 'publichall': 1.4, 'sunrisecrowd': 1.4,
               'coowners': 1.3, 'planning': 1.3, 'wheat': 1.3, 'care': 1.3, 'quern': 1.3, 'steammill': 1.6}
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

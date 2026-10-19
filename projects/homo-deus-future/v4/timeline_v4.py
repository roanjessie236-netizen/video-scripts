#!/usr/bin/env python3
"""《未来简史：人类之后，会是谁？》v4 - single source of truth for the edit. Run to (re)generate engine/shotlist.json.

VO-first: every line is placed on its measured take (voiceover/clips_v4, Yunjian), separated by scripted pauses;
cuts are anchored to line starts and to word onsets (edge-tts WordBoundary), so the picture moves with the voice.
Plates = the v2 images rebuilt clean from the v2 master (tools/extract_plates.py, already graded -> grade 'none').
New images (assets/43_..56_) are graded here; a missing image renders as a '待补图' placeholder (or uses its fallback).
cam = [[zoom, cx, cy, rot] start, [...] end]; trans = how a shot enters, tdur = overlap with the previous shot.
Subtitles lead the voice by 0.15 s, captions by 0.6 s (hold +1.0 s)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(HERE, 'voiceover')
ENG = os.path.join(HERE, 'engine')
LN = {x['i']: x for x in json.load(open(os.path.join(VO, 'lines.json'), encoding='utf-8'))}
DU = {int(k): v['dur'] for k, v in json.load(open(os.path.join(VO, 'clips_v4', 'durs.json'))).items()}
BD = {int(k): v for k, v in json.load(open(os.path.join(VO, 'clips_v4', 'bounds.json'), encoding='utf-8')).items()}

# ---------------------------------------------------------------- narration layout (pause before each line, s)
GAP = {1: 1.8, 2: 0.6, 3: 5.4, 4: 0.7, 5: 0.35, 6: 0.35, 7: 0.6, 8: 0.7, 9: 0.4,      # v4.1: tighter, continuous read
       10: 3.0, 11: 0.4, 12: 0.4, 13: 0.35, 14: 0.45, 15: 0.8, 16: 0.4, 17: 0.35, 18: 0.6,
       19: 3.0, 20: 0.4, 21: 0.4, 22: 0.45, 23: 0.6, 24: 0.35, 25: 0.3, 26: 0.3, 27: 0.6, 28: 0.9, 29: 0.45,
       30: 0.4, 31: 0.4, 32: 0.5, 33: 0.4, 34: 0.45,
       35: 2.9, 36: 0.4, 37: 0.4, 38: 0.7, 39: 0.3, 40: 1.0, 41: 0.9,
       42: 1.0, 43: 0.4, 44: 0.7, 45: 1.0, 46: 1.0, 47: 1.2, 48: 1.0}
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


def have(img):
    return os.path.exists(os.path.join(ENG, 'assets', img))


# ---------------------------------------------------------------- shots
SH = []


def shot(id, image, start, cam, grade='none', trans='cut', tdur=0.0, ease=None, fx=None, prep=None, desc='',
         plate=None, alt=None):
    """plate: image is a v2 plate (plates/NN_name.jpg). alt = (image, cam, grade) used when an optional new image
    has not been delivered."""
    if plate is None:
        plate = int(image[:2]) <= 42
    if not plate and alt and not have(image):
        image, cam, grade = alt
        plate = int(image[:2]) <= 42
        desc += ' [fallback]'
    p = dict(prep or {})
    if plate:
        p['plate'] = True
    SH.append(dict(id=id, image=image, start=round(start, 3), cam=cam, grade=grade, trans=trans, tdur=tdur,
                   ease=ease, fx=fx or {}, prep=p, desc=desc))


BLUE = [255, 200, 90]      # BGR
CYAN = [255, 230, 120]
TITLE = [en(2) + 0.3, st(3) - 2.4]
SIL = en(39) + 0.45        # music + picture cut to silence before L40

# ---- 序
shot('cosmos', '01_cosmos.jpg', 0.0, push(1.0, 0.02), trans='none', fx={'stars3d': {'k1': 0.03, 'k2': 0.01}},
     desc='Dark universe, deep star field')
shot('earth', '02_earth.jpg', 3.0, lambda d: [[1.0, .5, .5, 0], [1.75, .55, .45, 0]], trans='fade', tdur=0.8,
     ease='in', fx={'zoomblur': {'t0': st(2) - 0.9}}, desc='Earth, night-side city lights')
shot('citylights', '03_citylights.jpg', st(2) - 0.25, pull(1.04, 0.035, cy=.52), ease='out',
     fx={'lights_on': {'t0': st(2) + 0.35, 't1': st(2) + 2.6, 'glow': 0.3}}, desc='Eastern megacity, lights switching on')
shot('drones', '05_drones.jpg', TITLE[0], pan(1.1, 0.012), ease='lin', desc='Uncrewed craft piercing the cloud sea (title)')
# ---- 第一章 新的人类议程
shot('famine', '43_famine.jpg', st(3) - 2.5, push(1.03, 0.02, cy=.52), grade='ash', trans='fade', tdur=0.8,
     desc='1690s famine: parched farmland, emaciated farmer, empty bowl')
shot('plague', '44_plague.jpg', w(3, '瘟疫') - 0.04, push(1.06, 0.03), grade='ash', desc='Black Death: foggy medieval alley, plague doctor')
shot('war', '45_war.jpg', w(3, '战争') - 0.04, pan(1.1, 0.01, left=True), grade='ash', desc='Ancient battlefield at sunset, smoke, banners')
shot('abundance', '46_abundance.jpg', st(4) - 0.1, push(1.03, 0.022), grade='sodium',
     desc='Endless supermarket aisle of sugary drinks / fast food, lone shopper')
shot('oldage', '47_oldage.jpg', st(5) - 0.08, push(1.04, 0.025), grade='dawn',
     desc='A 90-year-old by a hospital window over a future city, granddaughter holding his hand')
shot('lonely', '48_lonely.jpg', st(6) - 0.08, pan(1.08, 0.008), grade='cyan',
     desc='Solitary figure on a rainy skybridge at night, crowds blurred',
     alt=('12_metro.jpg', pan(1.14, 0.01), 'none'))
shot('sugar', '55_sugar.jpg', st(7) - 0.5, push(1.04, 0.03), grade='ash', ease='punch',
     desc='Macro: sugar cubes stacked like ammunition next to spilled gunpowder, hard light',
     alt=('46_abundance.jpg', push(1.3, 0.03, cx=.6, cy=.48), 'sodium'))
shot('sunrise', '28_sunrise.jpg', en(7) + 0.45, push(1.04, 0.02), trans='fade', tdur=0.8, desc='Sun rising over the Earth')
shot('immortality', '49_immortality.jpg', st(9) - 0.05, push(1.04, 0.04), grade='lab', ease='lin',
     desc='Immortality: an ageless face beside her own regenerating cells')
shot('bliss', '50_bliss.jpg', w(9, '幸福') - 0.04, push(1.04, 0.04), grade='tender', ease='lin',
     desc='Bliss: eyes closed, neural headband, golden molecules')
shot('divinity', '51_divinity.jpg', w(9, '化身') - 0.04, push(1.03, 0.05), grade='gold', ease='punch',
     desc='Divinity: figure raising hands to a newborn life form of light')
# ---- 第二章 生命重塑
shot('dna', '14_dna.jpg', st(10) - 2.4, push(1.04, 0.02, rot=1.5), trans='fade', tdur=1.0, desc='Glowing DNA double helix')
shot('lab', '13_lab.jpg', st(11) - 0.08, push(1.06, 0.03), desc='Future bio-laboratory')
shot('nanobots', '17_nanobots.jpg', st(12) - 0.35, push(1.03, 0.05), trans='radial', tdur=0.7, ease='in',
     fx={'radial': {'c': [0.5, 0.5]}}, desc='Nanobots in a blood vessel')
shot('editing', '15_editing.jpg', st(13) - 0.06, pull(1.06, 0.04), ease='lin', desc='Gene editing of a helix strand')
shot('hands', '20_hands.jpg', w(13, '与') - 0.04, push(1.06, 0.04), ease='lin', desc='Old hand and child hand, holographic body scan')
shot('artlife', '16_artlife.jpg', w(13, '创造') - 0.04, push(1.06, 0.04), ease='lin', desc='Artificial life forming in a vessel')
shot('cellplanets', '18_cellplanets.jpg', st(14) - 0.4, push(1.04, 0.025, rot=-2.0), trans='radial', tdur=0.8,
     fx={'radial': {'c': [0.5, 0.5]}, 'stars3d': {'k1': 0.01, 'k2': 0.0}}, desc='Cells orbiting like planets')
shot('upload', '25_upload.jpg', st(15) - 0.5, push(1.04, 0.03), trans='digital', tdur=0.5,
     fx={'datastream': {'n': 320, 'y': 0.5, 'spread': 0.14, 'amp': 0.06, 'speed': 0.12, 'tilt': 0.0, 'col': CYAN,
                        'alpha': 0.45}}, desc='Consciousness dissolving into digital light')
shot('ar', '22_ar.jpg', st(16) - 0.06, pull(1.06, 0.035), ease='lin', desc='Augmented-reality street')
shot('stationin', '26_stationin.jpg', st(17) - 0.06, push(1.06, 0.04), ease='lin', desc='Space-station garden')
shot('mirror', '27_mirror.jpg', st(18) - 0.9, push(1.03, 0.018, cy=.48), trans='fade', tdur=0.7,
     desc='A person facing a digital reflection of themself')
# ---- 第三章 智能革命
shot('bluecity', '06_bluecity.jpg', st(19) - 2.8, push(1.06, 0.03, cy=.48), trans='digital', tdur=0.5,
     fx={'datastream': {'n': 380, 'y': 0.62, 'spread': 0.10, 'amp': 0.05, 'speed': 0.10, 'tilt': -0.04, 'col': BLUE,
                        'alpha': 0.75}}, desc='Blue high-tech city')
shot('ainetwork', '07_ainetwork.jpg', st(19) - 0.06, push(1.06, 0.035, rot=-1.0), desc='Global AI network')
shot('robotwork', '08_robotwork.jpg', st(20) - 0.06, pan(1.12, 0.012), ease='lin', desc='Robots working beside humans')
shot('datacenter', '11_datacenter.jpg', st(21) - 0.06, pull(1.22, 0.02, cy=.41), desc='Data-centre corridor')
shot('neurons', '19_neurons.jpg', st(22) - 0.06, push(1.04, 0.03), desc='Neural network of light')
shot('neurons2', '19_neurons.jpg', w(22, '生物') - 0.04, push(1.22, 0.03, cx=.55, cy=.46, rot=1.0),
     fx={'datastream': {'n': 600, 'y': 0.52, 'spread': 0.18, 'amp': 0.07, 'speed': 0.14, 'tilt': -0.05, 'col': CYAN,
                        'alpha': 0.7}}, desc='Neurons dissolving into data streams')
shot('humanism', '52_humanism.jpg', st(23) - 0.5, push(1.03, 0.02), grade='gold', trans='fade', tdur=0.5,
     desc='Humanism: a woman alone before a Renaissance painting, warm skylight')
shot('bci', '21_bci.jpg', st(24) - 0.3, pull(1.04, 0.04), trans='digital', tdur=0.35, desc='Brain-computer interface')
shot('algochoice', '53_algochoice.jpg', st(25) - 0.06, push(1.04, 0.03), grade='cyan', ease='lin',
     desc='Self-driving car at night: holographic choices (route, books, match)')
shot('assistant', '09_assistant.jpg', st(26) - 0.04, push(1.06, 0.035), ease='punch', desc='Holographic assistant')
shot('elevator', '04_elevator.jpg', st(27) - 0.5, tilt(1.18, 0.02, cy=.5, up=True), trans='fade', tdur=0.5,
     desc='Space elevator rising into orbit')
# useless class
shot('clinic', '36_clinic.jpg', st(28) - 0.7, pull(1.04, 0.03, cx=.55, cy=.47), trans='fade', tdur=0.8,
     desc='Life-upgrade clinic above the city')
shot('automation', '37_automation.jpg', st(29) - 0.4, push(1.2, 0.02, cy=.41), trans='digital', tdur=0.4, ease='lin',
     desc='Lights-out automated factory')
shot('worker', '38_worker.jpg', w(29, '一些') - 0.04, push(1.04, 0.02, cx=.52), desc='A worker behind glass')
shot('worker2', '38_worker.jpg', st(30) - 0.06, push(1.2, 0.015, cx=.58, cy=.42), desc='Worker, closer')
shot('faces', '39_faces.jpg', st(31) - 0.06, pan(1.1, 0.008), ease='lin', desc='Ordinary people looking up')
shot('faces2', '39_faces.jpg', w(31, '绝不') - 0.04, push(1.24, 0.015, cx=.62, cy=.45), desc='Mother and child, closer')
shot('divide', '40_divide.jpg', st(32) - 0.06, tilt(1.2, 0.02, up=True), desc='Divided city: towers in sun, streets in shadow')
shot('castes', '54_castes.jpg', st(33) - 0.06, push(1.03, 0.015, cy=.485, dy=-0.03), grade='steel',  # keep her head in frame
     desc='An upgraded person in a white tower vs an ordinary worker in the rain',
     alt=('40_divide.jpg', push(1.3, 0.02, cy=.7), 'none'))
shot('crowdwalk', '41_crowdwalk.jpg', st(34) - 0.06, pan(1.12, 0.012), ease='lin', desc='People walking together')
shot('toport', '42_toport.jpg', w(34, '也') - 0.04, push(1.04, 0.03), ease='in', desc='The crowd streams toward the light')
# ---- 第四章 人类的新纪元
shot('dataism', '56_dataism.jpg', st(35) - 2.8, push(1.03, 0.02), grade='cyan', trans='fade', tdur=0.9,
     desc='Dataism: a megacity where every person is a node in a planetary neural web')
shot('datagalaxy', '10_datagalaxy.jpg', st(36) - 0.06, push(1.04, 0.025, rot=1.0),
     fx={'datastream': {'n': 700, 'y': 0.55, 'spread': 0.16, 'amp': 0.08, 'speed': 0.14, 'tilt': -0.05, 'col': CYAN,
                        'alpha': 0.8}}, desc='Data streams like the Milky Way')
shot('metro', '12_metro.jpg', w(36, '万物') - 0.04, pan(1.12, 0.01), ease='lin', desc='Crowds in a smart metro hall')
shot('underground', '24_underground.jpg', st(37) - 0.06, pan(1.12, 0.012, left=True), ease='lin', desc='Giant underground city')
shot('futureearth', '29_futureearth.jpg', st(38) - 0.5, push(1.04, 0.025, rot=1.0), trans='fade', tdur=0.5,
     desc='Future Earth ringed with orbital structures')
shot('moonbase', '30_moonbase.jpg', w(38, '机器') - 0.04, pan(1.12, 0.014), ease='lin', desc='Moon base')
shot('marscity', '31_marscity.jpg', st(39) - 0.06, push(1.04, 0.04), ease='lin', desc='Domed city on Mars')
shot('starship', '32_starship.jpg', w(39, '创造') - 0.04, push(1.04, 0.07), ease='in',
     fx={'shake': {'t0': w(39, '创造') + 0.1, 'peak': SIL}}, desc='Starship leaving the solar system')
shot('mirror2', '27_mirror.jpg', SIL, push(1.1, 0.01, cy=.48), fx={'dim': 0.8}, desc='Callback: the digital reflection, in silence')
shot('spaceport', '33_spaceport.jpg', st(41) - 0.9, pull(1.04, 0.03), trans='fade', tdur=1.0, ease='out',
     desc='Humanity at an Eastern space port')
# ---- 尾声
shot('child', '34_child.jpg', st(42) - 1.0, push(1.02, 0.012, cy=.49), trans='fade', tdur=1.2, desc='A child looking at Earth')
shot('child2', '34_child.jpg', st(44) - 0.7, push(1.2, 0.012, cx=.6, cy=.45), trans='fade', tdur=0.6,
     desc='The child, closer, as the three questions appear')
shot('eye', '35_eye.jpg', en(45) + 0.5, push(1.02, 0.018), trans='fade', tdur=1.0, desc="Earth reflected in the child's eye")
shot('end', '01_cosmos.jpg', st(48) - 1.2, push(1.08, 0.006, rot=0.5), trans='fade', tdur=1.6,
     fx={'stars3d': {'k1': 0.01, 'k2': 0.0}, 'dim': 0.5}, desc='Back to the cosmos for the end card')

ENDCARD = [en(48) + 1.4, en(48) + 7.0]
DUR = round(ENDCARD[1] + 1.2, 2)

# shot ends: hard cut = next start; dissolve = next start + its overlap
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
    else:  # split subtitle: second half timed from the word onset of its first word
        import re
        n1 = len(re.sub(r'[，。、：；？！“”\s]', '', zh[0]))
        c, t2 = 0, None
        for o, d, wd in BD[i]:
            if c >= n1:
                t2 = st(i) + o
                break
            c += len(re.sub(r'[，。、：；？！“”\s]', '', wd))
        SUBS.append([round(st(i) - 0.15, 3), round(t2 - 0.45, 3), zh[0], x['src'], ee[0]])
        SUBS.append([round(t2 - 0.15, 3), round(en(i) + 0.35, 3), zh[1], x['src'], ee[1]])
for X in (SUBS, CAPS):                    # never overlap two subtitles / two captions
    for a, b in zip(X, X[1:]):
        a[1] = round(min(a[1], b[0] - 0.1), 3)

CHAPTERS = [
    [st(3) - 2.2, st(3) + 0.1, '第一章', '新的人类议程', 'THE NEW HUMAN AGENDA'],
    [st(10) - 2.3, st(10) + 0.1, '第二章', '生命重塑', 'REDESIGNING LIFE'],
    [st(19) - 2.5, st(19) - 0.1, '第三章', '智能革命', 'THE INTELLIGENCE REVOLUTION'],
    [st(35) - 2.5, st(35) + 0.05, '第四章', '人类的新纪元', 'A NEW ERA FOR HUMANKIND'],
]
CHAPTERS = [[round(a, 3), round(b, 3), *r] for a, b, *r in CHAPTERS]
LABELS = [  # documentary lower-left labels (facts from Homo Deus, ch. 1) [start, end, line1, line2, fade]
    [st(3) + 0.15, w(3, '瘟疫') - 0.1, '1692–1694 · 法国大饥荒 · 约 280 万人饿死', 'FRANCE · c. 2.8 MILLION STARVED · 15% OF THE POPULATION', 0.35],
    [w(3, '瘟疫') + 0.02, w(3, '战争') - 0.08, '黑死病 · 7500 万至 2 亿人死亡', 'THE BLACK DEATH · 75–200 MILLION DEAD', 0.2],
    [w(3, '战争') + 0.08, en(3) + 0.5, '古代农业社会 · 约 15% 的死亡源于暴力', 'ANCIENT FARMING SOCIETIES · c. 15% OF ALL DEATHS · TODAY ≈ 1%', 0.4],
    [st(4) + 0.5, en(4) + 0.2, '2014 · 超重 21 亿人 · 营养不良 8.5 亿人', '2.1 BILLION OVERWEIGHT · 850 MILLION MALNOURISHED', 0.5],
    [st(6) + 0.6, en(6) + 0.2, '2012 · 暴力致死 62 万人 · 自杀 80 万人', 'DEATHS IN 2012 · VIOLENCE 620,000 · SUICIDE 800,000', 0.5],
    [st(7) - 0.2, en(7) + 0.9, '2012 · 糖尿病致死 150 万人 · 战争 12 万人', 'DIABETES 1.5 MILLION · WAR 120,000', 0.5],
]
LABELS = [[round(a, 3), round(b, 3), *r] for a, b, *r in LABELS]
FLASHES = [[TITLE[0], 0.35, 0.3], [w(3, '瘟疫') - 0.04, 0.10, 0.2], [w(3, '战争') - 0.04, 0.14, 0.22],
           [w(9, '神'), 0.45, 0.4], [st(19) - 2.8 + 0.25, 0.22, 0.3], [st(26) - 0.04, 0.28, 0.3]]
FLASHES = [[round(a, 3), b, c] for a, b, c in FLASHES]
MARKS = dict(L={i: [st(i), en(i)] for i in LN}, title=TITLE[0], sil=SIL, end=DUR, endcard=ENDCARD[0],
             ch=[c[0] for c in CHAPTERS], god=w(9, '神'), authority=st(26), plague=w(3, '瘟疫'), war=w(3, '战争'),
             bliss=w(9, '幸福'), divinity=w(9, '化身'), lights=st(2) + 0.35, starship=w(39, '创造'),
             shots={x['id']: x['start'] for x in SH},
             W={i: [[b[2], round(st(i) + max(0.0, b[0]), 3)] for b in BD[i]] for i in LN})

SCRIM_BOOST = {'abundance': 1.7, 'sugar': 1.9}   # bright new images: darker scrim behind label/caption
DATA = dict(title='未来简史：人类之后，会是谁？ v4', width=2560, height=1440, fps=24, duration=DUR,
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

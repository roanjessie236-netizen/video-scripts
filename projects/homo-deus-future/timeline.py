#!/usr/bin/env python3
"""未来简史：人类之后，会是谁？ -- single source of truth for the edit. Run to (re)generate shotlist.json.

cam = [[zoom, cx, cy, rot_deg] at shot start, [...] at shot end]; cx/cy are normalized
coordinates of the view centre inside the (16:9-cropped) source still.
trans = how this shot enters over the previous one; its duration = overlap with the previous shot.
Engine = Film-1 engine (projects/sapiens-70000-years) + tools/patch_engine.py
(adds grades void/cyan/lab/tender/dawn/amber, fx datastream/bloom, transition 'digital').
"""
import json, os

S = []
DUR = 234.0


def shot(id, image, start, end, cam, grade, trans='fade', ease='io', fx=None, prep=None, desc=''):
    S.append(dict(id=id, image=image, start=start, end=end, cam=cam, grade=grade, trans=trans, ease=ease,
                  fx=fx or {}, prep=prep or {}, desc=desc))


BLUE = [255, 200, 90]      # BGR
CYAN = [255, 230, 120]
WHITE = [255, 236, 210]

# ---------------------------------------------------------------- OPENING 0:00-0:30
shot('cosmos', '01_cosmos.jpg', 0.0, 8.0, [[1.0, .5, .5, 0], [1.25, .5, .5, 1.5]], 'void', trans='none',
     fx={'stars3d': {'k1': 0.03, 'k2': 0.01}}, desc='Dark universe, deep star field')
shot('earth', '02_earth.jpg', 7.0, 14.2, [[1.0, .5, .5, 0], [2.4, .55, .45, 0]], 'void', ease='in',
     fx={'zoomblur': {'t0': 13.2}}, desc='Earth slowly rotating, night-side city lights')
shot('citylights', '03_citylights.jpg', 12.95, 19.0, [[1.25, .5, .52, 0], [1.06, .5, .5, 0]], 'cyan', trans='cut',
     ease='out', fx={'lights_on': {'t0': 13.6, 't1': 16.4}}, desc='Future Eastern megacity, lights switching on')
shot('elevator', '04_elevator.jpg', 18.0, 24.6, [[1.2, .5, .65, 0], [1.2, .5, .38, 0]], 'cyan',
     desc='Giant space elevator rising from the city into orbit')
shot('drones', '05_drones.jpg', 23.6, 30.4, [[1.12, .44, .5, 0], [1.12, .56, .48, 0]], 'cyan', ease='lin',
     desc='Uncrewed craft piercing the cloud sea')
# ---------------------------------------------------------------- CH1 智能革命 0:30-1:12
shot('bluecity', '06_bluecity.jpg', 29.6, 37.6, [[1.05, .5, .5, 0], [1.22, .5, .46, 0]], 'cyan', trans='digital',
     fx={'datastream': {'n': 380, 'y': 0.62, 'spread': 0.10, 'amp': 0.05, 'speed': 0.10, 'tilt': -0.04,
                        'col': BLUE, 'alpha': 0.75}}, desc='Blue high-tech city at night')
shot('ainetwork', '07_ainetwork.jpg', 36.6, 44.0, [[1.08, .5, .5, 0], [1.28, .5, .5, -2.0]], 'cyan',
     desc='Global AI network wrapping the Earth')
shot('robotwork', '08_robotwork.jpg', 43.0, 50.0, [[1.14, .43, .5, 0], [1.14, .57, .5, 0]], 'lab', ease='lin',
     desc='Robots working side by side with humans')
shot('assistant', '09_assistant.jpg', 49.0, 56.0, [[1.04, .5, .5, 0], [1.2, .52, .46, 0]], 'tender',
     desc='Holographic assistant anticipating needs')
shot('datagalaxy', '10_datagalaxy.jpg', 55.0, 63.6, [[1.0, .5, .5, 0], [1.24, .5, .52, 1.0]], 'cyan',
     fx={'datastream': {'n': 900, 'y': 0.55, 'spread': 0.16, 'amp': 0.08, 'speed': 0.14, 'tilt': -0.05,
                        'col': CYAN, 'alpha': 1.0}, 'bloom': 0.2}, desc='Data streams flowing like the Milky Way')
shot('datacenter', '11_datacenter.jpg', 62.6, 68.6, [[1.2, .5, .5, 0], [1.04, .5, .5, 0]], 'cyan',
     desc='Endless data-centre corridor')
shot('metro', '12_metro.jpg', 67.6, 72.8, [[1.12, .42, .5, 0], [1.12, .58, .5, 0]], 'cyan', ease='lin',
     desc='Crowds in a smart metro hall')
# ---------------------------------------------------------------- CH2 生命重塑 1:12-2:01
shot('lab', '13_lab.jpg', 71.8, 80.0, [[1.04, .5, .5, 0], [1.22, .5, .48, 0]], 'lab', trans='digital',
     desc='Future bio-laboratory')
shot('dna', '14_dna.jpg', 79.0, 87.0, [[1.06, .5, .5, 0], [1.3, .5, .5, 3.0]], 'lab', fx={'bloom': 0.3},
     desc='Glowing DNA double helix')
shot('editing', '15_editing.jpg', 86.0, 93.0, [[1.22, .5, .5, 0], [1.05, .5, .5, 0]], 'lab',
     desc='Gene editing of a helix strand')
shot('artlife', '16_artlife.jpg', 92.0, 99.0, [[1.05, .5, .52, 0], [1.22, .5, .5, 0]], 'lab',
     desc='Artificial life forming in a vessel')
shot('nanobots', '17_nanobots.jpg', 98.0, 105.6, [[1.0, .5, .5, 0], [1.35, .5, .5, 0]], 'cyan', trans='radial',
     ease='in', fx={'radial': {'c': [0.5, 0.5]}}, desc='Nanobots travelling through a blood vessel')
shot('cellplanets', '18_cellplanets.jpg', 104.6, 113.0, [[1.06, .5, .5, 0], [1.26, .5, .5, -2.5]], 'void',
     trans='radial', fx={'radial': {'c': [0.5, 0.5]}, 'stars3d': {'k1': 0.01, 'k2': 0.0}},
     desc='Cells orbiting like planets, micro meets cosmos')
shot('neurons', '19_neurons.jpg', 112.0, 121.8, [[1.04, .5, .5, 0], [1.24, .52, .48, 0]], 'cyan',
     fx={'bloom': 0.25}, desc='Neural network of light')
# ---------------------------------------------------------------- CH3 人与机器融合 2:01-2:46
shot('hands', '20_hands.jpg', 120.8, 127.8, [[1.04, .5, .5, 0], [1.2, .5, .5, 0]], 'tender', trans='digital',
     desc='Human hand meeting a robotic hand')
shot('bci', '21_bci.jpg', 126.8, 133.0, [[1.2, .5, .46, 0], [1.05, .5, .5, 0]], 'cyan',
     desc='Brain-computer interface')
shot('prosthetic', '23_prosthetic.jpg', 132.0, 137.8, [[1.06, .5, .5, 0], [1.22, .5, .48, 0]], 'cyan',
     desc='Smart prosthetic arm')
shot('underground', '24_underground.jpg', 136.8, 143.8, [[1.14, .43, .5, 0], [1.14, .57, .5, 0]], 'cyan',
     ease='lin', desc='Giant Eastern underground city, Wandering-Earth scale')
shot('upload', '25_upload.jpg', 142.8, 149.6, [[1.04, .5, .5, 0], [1.24, .5, .5, 0]], 'cyan', trans='digital',
     fx={'datastream': {'n': 420, 'y': 0.5, 'spread': 0.14, 'amp': 0.06, 'speed': 0.12, 'tilt': 0.0,
                        'col': CYAN, 'alpha': 0.6}}, desc='Consciousness dissolving into digital light')
shot('ar', '22_ar.jpg', 148.6, 154.8, [[1.16, .5, .5, 0], [1.04, .5, .5, 0]], 'cyan',
     prep={'blur': [[145, 160, 210, 310], [484, 208, 544, 352], [718, 40, 788, 184], [796, 235, 928, 343],
                    [162, 406, 230, 462]]},
     desc='Augmented-reality street')
shot('stationin', '26_stationin.jpg', 153.8, 160.0, [[1.04, .5, .5, 0], [1.2, .5, .5, 0]], 'cyan',
     desc='Space station interior')
shot('mirror', '27_mirror.jpg', 159.0, 167.4, [[1.02, .5, .5, 0], [1.16, .5, .48, 0]], 'tender',
     fx={'dim': 0.9}, desc='A person facing a digital reflection of themself')
# ---------------------------------------------------------------- CH4 人类的新纪元 2:46-3:25
shot('sunrise', '28_sunrise.jpg', 166.4, 174.0, [[1.04, .5, .5, 0], [1.22, .5, .5, 0]], 'dawn', fx={'bloom': 0.35},
     desc='Sun rising over the curve of the Earth')
shot('futureearth', '29_futureearth.jpg', 173.0, 180.0, [[1.06, .5, .5, 0], [1.24, .5, .5, 1.5]], 'dawn',
     desc='Future Earth ringed with orbital structures')
shot('moonbase', '30_moonbase.jpg', 179.0, 186.0, [[1.14, .44, .5, 0], [1.14, .56, .5, 0]], 'cyan', ease='lin',
     desc='Permanent Moon base')
shot('marscity', '31_marscity.jpg', 185.0, 191.0, [[1.04, .5, .5, 0], [1.2, .5, .5, 0]], 'amber',
     desc='Domed city on Mars')
shot('starship', '32_starship.jpg', 190.0, 197.8, [[1.04, .5, .5, 0], [1.3, .5, .5, 0]], 'void', ease='in',
     fx={'shake': {'t0': 190.6, 'peak': 197.8}}, desc='Starship leaving the solar system')
shot('spaceport', '33_spaceport.jpg', 197.75, 205.8, [[1.2, .5, .5, 0], [1.04, .5, .5, 0]], 'amber', trans='cut',
     ease='out', prep={'blur': [[400, 262, 436, 380], [1235, 338, 1272, 422], [72, 88, 156, 148], [262, 362, 330, 406]]},
     desc='Crowds of humanity at an Eastern space port')
# ---------------------------------------------------------------- ENDING 3:25-3:54
shot('child', '34_child.jpg', 204.8, 222.0, [[1.0, .5, .5, 0], [1.22, .5, .48, 0]], 'tender',
     desc='A child in a space station looking at Earth')
shot('eye', '35_eye.jpg', 221.0, 229.0, [[1.0, .5, .5, 0], [1.3, .5, .5, 0]], 'tender', fx={'bloom': 0.3},
     desc="Earth's blue light reflected in the child's eye")
shot('end', '01_cosmos.jpg', 226.6, DUR, [[1.1, .5, .5, 0], [1.2, .5, .5, 0.5]], 'void',
     fx={'stars3d': {'k1': 0.01, 'k2': 0.0}, 'dim': 0.45}, desc='Back to the cosmos for the end card')

SUBS = [  # [start, end, text, source]  source: 'brief' = user's script, 'added' = added line based on Homo Deus
    [2.6, 6.6, '过去，人类最大的梦想，是改变世界。', 'brief'],
    [8.0, 12.2, '未来，人类可能开始改变自己。', 'brief'],
    [36.8, 40.6, '人类第一次创造了一种新的智能。', 'brief'],
    [42.0, 45.6, '它不需要生命，却能够学习。', 'brief'],
    [47.6, 51.6, '智能，正在与意识分道扬镳。', 'added'],
    [53.0, 57.0, '算法，也许会比你自己更了解你。', 'added'],
    [62.8, 68.8, '当机器开始理解世界，人类的位置将发生什么变化？', 'brief'],
    [78.0, 81.8, '过去，人类接受自然赋予的生命。', 'brief'],
    [83.4, 87.2, '未来，人类可能开始设计生命。', 'brief'],
    [88.8, 93.0, '四十亿年来，生命一直由自然选择塑造。', 'added'],
    [94.4, 98.6, '如今，智能设计开始取代自然选择。', 'added'],
    [106.0, 112.6, '疾病、衰老，甚至身体本身，都可能成为可以修改的对象。', 'brief'],
    [114.2, 119.2, '新的人类议程：长生不死、幸福快乐、化身为神。', 'added'],
    [133.6, 137.6, '身体的边界，正在被重新定义。', 'added'],
    [144.8, 148.6, '如果意识可以被复制。', 'brief'],
    [150.6, 154.2, '如果记忆可以被保存。', 'brief'],
    [154.8, 158.8, '如果生命可以无限延续。', 'brief'],
    [160.0, 165.0, '我们还是原来的自己吗？', 'brief'],
    [173.4, 177.0, '未来最大的挑战。', 'brief'],
    [178.4, 182.4, '不是机器是否会超越人类。', 'brief'],
    [186.6, 191.0, '而是当我们拥有创造神的能力。', 'brief'],
    [192.4, 197.2, '是否仍然知道如何成为人？', 'brief'],
    [199.6, 204.4, '智人，也许正在走向“神人”。', 'added'],
]
CHAPTERS = [
    [30.8, 35.2, '第一章', '智能革命', 'THE INTELLIGENCE REVOLUTION'],
    [72.4, 76.8, '第二章', '生命重塑', 'REDESIGNING LIFE'],
    [121.4, 126.0, '第三章', '人与机器融合', 'HUMANS  &  MACHINES'],
    [167.2, 171.8, '第四章', '人类的新纪元', 'A NEW ERA FOR HUMANKIND'],
]
LABELS = [  # static lower-left labels [start, end, line1, line2]
    [18.6, 22.4, '近未来', '太空电梯 · 连接地球与轨道'],
    [139.0, 142.8, '未来', '地下城'],
    [180.4, 184.2, '未来', '月球基地 · 永久前哨'],
    [186.0, 189.8, '未来', '火星城市 · 第二家园'],
]
TICKER = {'windows': [], 'keys': []}
ROUTES = []
TITLE = [22.6, 27.6]
CAPTIONS = [[216.2, 220.6, '下一章人类历史。'], [221.0, 225.6, '正在等待我们书写。']]
ENDCARD = [227.4, 233.4]
PARCHMENT = [[0, 0.0], [DUR, 0.0]]
FLASHES = [[13.0, 0.9, 0.16], [30.4, 0.25, 0.3], [72.0, 0.2, 0.3], [121.0, 0.25, 0.3], [166.9, 0.3, 0.4],
           [197.8, 0.45, 0.45]]

DATA = dict(title='未来简史：人类之后，会是谁？', width=2560, height=1440, fps=24, duration=DUR,
            shots=S, subtitles=SUBS, chapters=CHAPTERS, labels=LABELS, ticker=TICKER, routes=ROUTES,
            title_card=TITLE, captions=CAPTIONS, endcard=ENDCARD, parchment=PARCHMENT, flashes=FLASHES)

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shotlist.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(DATA, f, ensure_ascii=False, indent=1)
    print('wrote', out, len(S), 'shots', len(SUBS), 'subtitles')

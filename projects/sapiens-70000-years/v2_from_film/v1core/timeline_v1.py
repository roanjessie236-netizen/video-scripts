#!/usr/bin/env python3
"""Single source of truth for the edit. Run to (re)generate shotlist.json.

cam = [[zoom, cx, cy, rot_deg] at shot start, [...] at shot end]; cx/cy are normalized
coordinates of the view centre inside the (16:9-cropped) source still.
trans = how this shot enters over the previous one; its duration = overlap with the previous shot.
"""
import json, os

S = []


def shot(id, image, start, end, cam, grade, trans='fade', ease='io', fx=None, prep=None, desc=''):
    S.append(dict(id=id, image=image, start=start, end=end, cam=cam, grade=grade, trans=trans, ease=ease,
                  fx=fx or {}, prep=prep or {}, desc=desc))


# ---------------------------------------------------------------- OPENING 0:00-0:21
shot('galaxy', '01_galaxy.jpg', 0.0, 7.0, [[1.0, .5, .5, 0], [1.38, .53, .47, 2.5]], 'cosmos', trans='none',
     fx={'stars3d': {'k1': 0.03, 'k2': 0.012}},
     desc='Full-bleed Milky Way core, deep space, cinematic, no text, no black bars')
shot('earth', '02_earth.jpg', 6.0, 11.0, [[1.0, .5, .5, 0], [2.7, .62, .37, 0]], 'cosmos', ease='in',
     fx={'zoomblur': {'t0': 10.3}},
     desc='Blue Earth from orbit with sunrise rim, Africa visible upper right, photoreal')
shot('wasteland', '03_wasteland.jpg', 10.95, 17.0, [[1.38, .5, .64, 0], [1.08, .5, .58, 0]], 'ember', trans='cut',
     ease='out', fx={'embers': {'src': [.49, .80], 'rate': 22, 'spread': 40}, 'flicker': {'amp': .035}},
     desc='Prehistoric wasteland at dusk, lone human silhouette beside a small fire')
shot('firevisions', '04_firevisions.jpg', 15.8, 21.8, [[1.05, .5, .56, 0], [1.24, .5, .5, 0]], 'ember',
     fx={'embers': {'src': [.5, .62], 'rate': 40, 'spread': 120}, 'flicker': {'amp': .04}},
     desc='Campfire whose flames reveal cave paintings, ziggurats and a rocket launch')
# ---------------------------------------------------------------- ACT 1  0:21-1:10
shot('savanna', '05_savanna.jpg', 20.8, 28.6, [[1.12, .44, .5, 0], [1.12, .56, .5, 0]], 'ember', ease='lin',
     desc='Golden African savanna, a small band of Homo sapiens, acacias, elephants')
shot('campfire', '06_campfire.jpg', 27.6, 35.2, [[1.05, .45, .56, 0], [1.2, .4, .5, 0]], 'ember',
     fx={'embers': {'src': [.47, .86], 'rate': 26, 'spread': 60}, 'flicker': {'amp': .045}},
     desc='Elder telling a story around a campfire under the stars')
shot('cave', '07_cave.jpg', 34.2, 40.6, [[1.08, .42, .44, 0], [1.2, .58, .42, 0]], 'ember',
     fx={'flicker': {'amp': .05}}, desc='Lascaux-style cave wall lit by a torch')
shot('bison', '08_bison.jpg', 39.0, 46.0, [[1.16, .5, .5, 0], [1.05, .5, .5, 0]], 'ember',
     fx={'painted': {'t0': 41.0, 't1': 42.8}}, desc='Bison herd stampeding through orange dust')
shot('tools', '09_tools.jpg', 45.0, 50.8, [[1.04, .5, .52, 0], [1.16, .5, .47, 0]], 'ember',
     desc='Palaeolithic stone tools on museum pedestals, dramatic museum lighting')
shot('mammoth', '10_mammoth.jpg', 49.8, 55.8, [[1.1, .45, .5, 0], [1.1, .55, .5, 0]], 'ember', ease='lin',
     desc='Ice-age hunters on a snowy ridge watching a mammoth herd')
shot('map', '11_map.jpg', 54.6, 63.6, [[1.55, .582, .456, 0], [1.06, .5, .47, 0]], 'parch', trans='inkmap',
     fx={'routes': {}}, desc='Antique parchment world map, hand drawn, no text')
shot('startribe', '12_startribe.jpg', 62.4, 70.8, [[1.0, .5, .5, 0], [1.14, .5, .45, 0]], 'earth',
     desc='Tribe on a ridge under the Milky Way, one figure pointing to the stars')
# ---------------------------------------------------------------- ACT 2  1:10-2:00
shot('seed', '13_seed.jpg', 70.0, 77.0, [[1.0, .5, .5, 0], [1.22, .52, .45, 0]], 'earth',
     desc='Macro: a wheat seed falling into dark soil, a sprout, god rays')
shot('farm', '14_farm.jpg', 76.0, 83.5, [[1.06, .45, .52, 0], [1.16, .55, .5, 0]], 'earth', trans='radial',
     fx={'radial': {'c': [.52, .45]}}, desc='Neolithic wheat harvest by a river, mud-brick village')
shot('mesopotamia', '15_mesopotamia.jpg', 82.3, 89.5, [[1.0, .5, .5, 0], [1.16, .66, .42, 0]], 'gold',
     trans='radial', fx={'radial': {'c': [.5, .4]}}, desc='Aerial view of a Mesopotamian ziggurat city on a river')
shot('cuneiform', '16_cuneiform.jpg', 88.5, 95.0, [[1.0, .5, .5, 0], [1.12, .5, .48, 0]], 'gold',
     prep={'crop': [180, 62, 1200, 636]}, desc='Sumerian cuneiform clay tablet under museum light')
shot('pyramids', '17_pyramids.jpg', 94.0, 101.5, [[1.14, .5, .5, 0], [1.02, .5, .5, 0]], 'gold',
     desc='Giza pyramids under construction, thousands of workers, golden dust')
shot('bronze', '18_bronze.jpg', 100.5, 107.5, [[1.1, .6, .5, 0], [1.2, .64, .5, 0]], 'gold',
     prep={'blur': [[270, 245, 450, 315]]}, desc='Shang dynasty bronze ding vessels and oracle bones in a museum')
shot('terracotta', '19_terracotta.jpg', 106.5, 120.6, [[1.0, .5, .5, 0], [1.24, .5, .45, 0]], 'gold',
     desc='Terracotta army excavation hall with shafts of light')
# ---------------------------------------------------------------- ACT 3  2:00-3:20
shot('silkroad', '20_silkroad.jpg', 119.6, 129.6, [[1.1, .42, .5, 0], [1.1, .58, .5, 0]], 'gold', ease='lin',
     desc='Silk Road camel caravan crossing dunes at golden hour')
shot('roman', '21_roman.jpg', 128.6, 137.0, [[1.15, .5, .5, 0], [1.04, .5, .5, 0]], 'gold',
     desc='Roman road and aqueduct with a marching legion')
shot('sail', '22_sail.jpg', 136.0, 145.0, [[1.06, .5, .5, 0], [1.16, .5, .5, -0.8]], 'goldblue',
     desc='Age of Sail galleons on the open ocean with god rays')
shot('manuscript', '23_manuscript.jpg', 144.0, 154.0, [[1.08, .5, .56, 0], [1.26, .5, .54, 0]], 'goldblue',
     prep={'blur': [[640, 5, 790, 55]]}, desc='Renaissance astronomical manuscript, armillary sphere and telescope')
shot('steam', '24_steam.jpg', 152.4, 161.0, [[1.16, .5, .5, 0], [1.04, .5, .5, 0]], 'steel', trans='burn',
     desc='Steam engine hall, giant flywheel, steam and sparks')
shot('factory', '25_factory.jpg', 160.0, 168.0, [[1.05, .5, .5, 0], [1.15, .5, .48, 0]], 'steel',
     desc='Industrial revolution smokestacks and a steam train on a bridge')
shot('electric', '26_electric.jpg', 167.0, 176.0, [[1.1, .47, .55, 0], [1.22, .47, .53, 0]], 'goldblue',
     fx={'lights_on': {'t0': 167.8, 't1': 170.2}}, desc='Boulevard c.1900 as electric street lights switch on')
shot('rocket', '27_rocket.jpg', 175.0, 187.0, [[1.25, .5, .6, 0], [1.25, .5, .4, 0]], 'steel',
     fx={'shake': {'t0': 176.4, 'peak': 177.6}}, desc='Night Saturn-V-style rocket launch watched by crowds')
shot('netearth', '28_netearth.jpg', 186.0, 200.8, [[1.02, .5, .5, 0], [1.22, .5, .5, -2.0]], 'future',
     desc='Night-side Earth wrapped in glowing network arcs')
# ---------------------------------------------------------------- ACT 4  3:20-5:00
shot('citynight', '29_citynight.jpg', 199.8, 209.6, [[1.16, .5, .5, 0], [1.03, .5, .5, 0]], 'future',
     desc='Aerial night view of a modern megacity')
shot('ai', '30_ai.jpg', 208.6, 217.0, [[1.0, .5, .5, 0], [1.15, .5, .5, 0]], 'future',
     desc='AI data centre with threads of light and an engineer')
shot('gene', '31_gene.jpg', 216.0, 224.0, [[1.05, .5, .5, 0], [1.15, .5, .5, 0]], 'future',
     prep={'blur': [[420, 120, 570, 270], [770, 320, 870, 390]]}, desc='Gene-editing lab, holographic DNA helix')
shot('robot', '32_robot.jpg', 223.0, 230.6, [[1.12, .5, .5, 0], [1.22, .5, .5, 0]], 'future',
     desc='A human hand and a robot hand almost touching')
shot('moon', '33_moon.jpg', 229.6, 237.6, [[1.1, .55, .5, 0], [1.1, .45, .5, 0]], 'future', ease='lin',
     desc='Realistic lunar base, Earth hanging in the black sky')
shot('mars', '34_mars.jpg', 236.6, 244.6, [[1.05, .5, .5, 0], [1.15, .5, .5, 0]], 'mars',
     desc='Astronauts, rover and a habitat dome on Mars')
shot('futurecity', '35_futurecity.jpg', 243.6, 252.6, [[1.0, .5, .5, 0], [1.2, .5, .47, 0]], 'future',
     desc='Wandering-Earth-scale megastructures rising above the clouds')
shot('station', '36_station.jpg', 251.6, 267.0, [[1.35, .5, .37, 0], [1.35, .46, .63, 0]], 'future',
     desc='Astronaut at a porthole facing a giant ring station, Earth below with sunrise flare')
shot('child', '37_child.jpg', 266.0, 293.5, [[1.0, .52, .5, 0], [1.2, .53, .42, 0]], 'future',
     desc='A child on a rooftop of a future city looking up at the Milky Way')
shot('end', '01_galaxy.jpg', 292.0, 300.0, [[1.2, .5, .5, 0], [1.32, .5, .5, 1.0]], 'cosmos',
     fx={'stars3d': {'k1': 0.01, 'k2': 0.0}, 'dim': 0.45}, desc='End card over the Milky Way')

SUBS = [  # [start, end, text, source]  source: 'brief' = user's script, 'added' = added line based on Sapiens
    [2.6, 6.4, '七万年前，他们只是地球上不起眼的一群动物。', 'brief'],
    [7.2, 10.8, '没有锋利的爪牙，没有强壮的身体。', 'brief'],
    [12.2, 16.6, '但他们拥有一种力量——创造不存在的世界。', 'brief'],
    [26.6, 30.8, '大约七万年前，智人的大脑里发生了一场无声的革命。', 'added'],
    [31.4, 34.8, '语言让陌生人成为伙伴。', 'brief'],
    [36.6, 40.6, '他们开始谈论从未见过的事物——神灵、祖先与传说。', 'added'],
    [50.4, 54.6, '共同的故事，让数万人能够共同合作。', 'brief'],
    [56.2, 60.2, '从非洲出发，他们走遍了整个世界。', 'added'],
    [64.2, 69.4, '神话、国家、文明，都诞生于人类共同相信的想象。', 'brief'],
    [78.2, 81.0, '人类驯服了植物。', 'brief'],
    [81.6, 86.2, '我们以为驯化了小麦，其实是小麦驯化了我们。', 'added'],
    [90.2, 94.4, '文字诞生了——人类第一次把想象刻进泥土。', 'added'],
    [96.0, 100.6, '村落变成城市，城市变成王国，王国变成帝国。', 'added'],
    [111.8, 116.8, '却也开始被自己创造的秩序束缚。', 'brief'],
    [126.6, 131.4, '金钱、帝国与宗教，把陌生人联结成一个全球网络。', 'added'],
    [132.4, 136.0, '人类不断突破自己的边界。', 'brief'],
    [138.4, 143.6, '科学革命始于一个伟大的发现——承认我们的无知。', 'added'],
    [146.2, 150.8, '从相信神明，到探索宇宙。', 'brief'],
    [155.2, 159.8, '科学、帝国与资本结盟，世界开始加速运转。', 'added'],
    [189.8, 195.2, '从仰望星空，到成为改变星球的力量。', 'brief'],
    [206.0, 209.8, '过去七万年，我们改变了世界。', 'brief'],
    [211.4, 215.8, '但未来，我们是否还能理解自己？', 'brief'],
    [218.4, 224.6, '当人工智能、基因技术和宇宙探索改变生命本身……', 'brief'],
    [231.6, 237.2, '我们正获得近乎神的力量，却仍不清楚自己想要什么。', 'added'],
    [256.6, 262.0, '下一章人类历史，将由谁书写？', 'brief'],
]
CHAPTERS = [
    [21.8, 26.0, '第一章', '认知革命', 'THE COGNITIVE REVOLUTION'],
    [70.6, 75.0, '第二章', '农业革命', 'THE AGRICULTURAL REVOLUTION'],
    [120.6, 125.6, '第三章', '帝国与科学革命', 'EMPIRES  &  THE SCIENTIFIC REVOLUTION'],
    [200.8, 205.6, '第四章', '未来的选择', 'THE CHOICE AHEAD'],
]
LABELS = [  # static lower-left labels [start, end, line1, line2]
    [23.0, 27.4, '约 7 万年前', '东非 · 智人'],
    [36.0, 40.2, '约 3 万年前', '欧洲 · 洞穴壁画'],
    [46.0, 50.2, '旧石器时代', '石器 · 人类最早的技术'],
    [51.0, 55.0, '冰河时期', '猛犸象草原'],
    [205.9, 209.6, '今天', '八十亿智人'],
    [230.6, 235.4, '未来', '月球基地'],
    [237.6, 242.4, '未来', '火星前哨'],
]
TICKER = {
    'windows': [[71.6, 119.8], [125.9, 198.8]],
    'keys': [
        [71.6, -9500, '新月沃地 · 农业起源'],
        [76.6, -7000, '新石器时代 · 农耕村落'],
        [82.9, -3500, '美索不达米亚 · 城市诞生'],
        [89.0, -3200, '苏美尔 · 楔形文字'],
        [94.5, -2560, '古埃及 · 吉萨金字塔'],
        [101.0, -1300, '中国 · 商代青铜与甲骨'],
        [107.0, -221, '中国 · 秦统一天下'],
        [125.9, -130, '丝绸之路'],
        [129.1, 117, '罗马帝国 · 大道与水渠'],
        [136.5, 1492, '大航海时代'],
        [144.5, 1543, '科学革命'],
        [153.0, 1776, '蒸汽机 · 工业革命'],
        [160.5, 1850, '工业时代'],
        [167.5, 1882, '电灯点亮城市'],
        [175.5, 1969, '人类登月'],
        [186.5, 1991, '互联网连接世界'],
    ],
}
# migration routes on 11_map.jpg, in ORIGINAL image pixels (1376x768); [t_start, t_end, points, label, label_offset]
ROUTES = [
    [55.9, 57.2, [[770, 425], [805, 385], [822, 335], [805, 292]], '东非 · 约7万年前', [-250, 40], 'start'],
    [57.0, 58.4, [[805, 292], [770, 258], [722, 228], [662, 214]], '欧洲 · 约4.5万年前', [-120, -70], 'end'],
    [57.3, 58.9, [[805, 292], [880, 266], [960, 250], [1040, 266], [1072, 292]], '东亚 · 约4万年前', [20, -70], 'end'],
    [57.6, 59.4, [[805, 292], [870, 330], [932, 352], [1010, 386], [1072, 422], [1118, 468], [1135, 508]],
     '澳大利亚 · 约4.5万年前', [-60, 50], 'end'],
    [59.0, 61.8, [[1072, 292], [1150, 222], [1250, 166], [1340, 140], None, [36, 136], [110, 166], [200, 232],
                  [272, 302], [332, 372], [400, 432], [440, 500], [420, 582]], '美洲 · 约1.6万年前', [30, 10], 'end'],
]
TITLE = [17.6, 21.3]
CAPTIONS = [[274.0, 279.6, '我们从哪里来？'], [281.0, 287.6, '我们将走向哪里？']]
ENDCARD = [292.8, 299.2]
PARCHMENT = [[0, 0.0], [10.8, 0.0], [11.6, 0.34], [70, 0.3], [120, 0.22], [152, 0.12], [200, 0.05], [300, 0.0]]
FLASHES = [[11.0, 1.0, 0.16], [17.6, 0.35, 0.35], [70.0, 0.12, 0.3], [120.0, 0.22, 0.3], [177.6, 0.3, 0.45], [252.0, 0.18, 0.4]]

DATA = dict(title='人类简史：七万年的文明觉醒', width=2560, height=1440, fps=24, duration=300.0,
            shots=S, subtitles=SUBS, chapters=CHAPTERS, labels=LABELS, ticker=TICKER, routes=ROUTES,
            title_card=TITLE, captions=CAPTIONS, endcard=ENDCARD, parchment=PARCHMENT, flashes=FLASHES)

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shotlist.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(DATA, f, ensure_ascii=False, indent=1)
    print('wrote', out, len(S), 'shots', len(SUBS), 'subtitles')

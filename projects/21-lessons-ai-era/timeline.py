#!/usr/bin/env python3
"""今日简史：AI时代，人类如何重新定义自己 -- single source of truth for the edit (film 3).
Run to (re)generate shotlist.json. Shot IDs S001-S056 are fixed; spec times come from asset_requirements.md.

Each row: id, spec_start, spec_end, cam_start, cam_end, grade, trans, overlap, ease, fx
  cam = [zoom, cx, cy, rot_deg]; zoom 1.0 = full still. Motion is mostly linear so the virtual camera never
  stops between shots (no slideshow 'settle'). The outgoing shot keeps moving through the overlap.
  overlap = seconds the previous shot keeps running under this one (dissolve / push-through length).
Engine = film-2 engine (sapiens-70000-years + homo-deus-future/tools/patch_engine.py) + tools/patch_tl.py
(adds grades grey/warm, fx reveal/haze, global dust & embers, light leaks, chapter-1 timeline overlay).
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DUR = 224.0
BLUE = [255, 200, 90]   # BGR
CYAN = [255, 230, 120]
GOLDC = [120, 200, 255]

IMG = {i: f'S{i:03d}.png' for i in range(1, 57)}
for i in (20, 24, 30, 31, 32):
    IMG[i] = f'S{i:03d}_r1.png'

R = [
 # ---------------- OPENING 0:00-0:23  fire -> writing -> machine -> chip -> screens -> servers -> title
 (1, 0.0, 3.6, [1.0, .5, .52, 0], [1.12, .5, .48, 0], 'ember', 'none', 0, 'lin', {}),
 (2, 3.6, 7.2, [1.13, .45, .5, 0], [1.13, .56, .5, 0], 'parch', 'fade', 1.0, 'lin', {}),
 (3, 7.2, 10.8, [1.06, .5, .5, 0], [1.2, .52, .48, 0], 'steel', 'fade', 1.0, 'lin', {}),
 (4, 10.8, 13.4, [1.08, .5, .5, 0], [1.24, .5, .5, 0], 'future', 'fade', 0.8, 'lin', {}),
 (5, 13.4, 15.8, [1.1, .5, .5, 0], [1.34, .5, .5, 0], 'cyan', 'fade', 0.7, 'in', {'zoomblur': {'t0': 15.1}}),
 (6, 15.8, 18.4, [1.0, .5, .5, 0], [1.5, .5, .5, 0], 'cyan', 'cut', 0, 'in', {'zoomblur': {'t0': 17.5}}),
 (7, 18.4, 23.0, [1.36, .5, .5, 0], [1.04, .5, .5, 0], 'future', 'fade', 0.35, 'out', {}),
 # ---------------- CH1 智能的诞生 0:23-1:01
 (8, 23.0, 27.6, [1.14, .44, .5, 0], [1.14, .56, .5, 0], 'goldblue', 'fade', 1.4, 'lin', {}),
 (9, 27.6, 31.4, [1.14, .45, .5, 0], [1.14, .56, .5, 0], 'cyan', 'fade', 1.2, 'lin',
  {'datastream': {'n': 420, 'y': 0.55, 'spread': 0.12, 'amp': 0.05, 'speed': 0.12, 'tilt': -0.03, 'col': CYAN, 'alpha': 0.6}}),
 (10, 31.4, 35.4, [1.04, .5, .5, 0], [1.22, .5, .5, 0], 'cyan', 'fade', 1.2, 'lin', {'bloom': 0.22}),
 (11, 35.4, 40.4, [1.04, .5, .5, 0], [1.26, .5, .5, 2.0], 'void', 'radial', 1.4, 'lin', {'bloom': 0.25, 'radial': {'c': [0.5, 0.5]}}),
 (12, 40.4, 44.4, [1.24, .5, .5, 0], [1.06, .5, .5, 0], 'cyan', 'fade', 1.2, 'lin',
  {'datastream': {'n': 360, 'y': 0.62, 'spread': 0.10, 'amp': 0.05, 'speed': 0.10, 'tilt': -0.04, 'col': BLUE, 'alpha': 0.55}}),
 (13, 44.4, 47.6, [1.14, .56, .5, 0], [1.14, .44, .5, 0], 'lab', 'fade', 1.0, 'lin', {}),
 (14, 47.6, 50.8, [1.05, .5, .5, 0], [1.2, .48, .5, 0], 'lab', 'fade', 1.0, 'lin', {}),
 (15, 50.8, 53.8, [1.14, .44, .5, 0], [1.14, .56, .5, 0], 'cyan', 'digital', 0.8, 'lin', {}),
 (16, 53.8, 57.4, [1.05, .5, .5, 0], [1.2, .5, .48, 0], 'steel', 'fade', 1.0, 'lin', {}),
 (17, 57.4, 61.0, [1.04, .5, .5, 0], [1.36, .5, .5, 0], 'steel', 'fade', 1.0, 'in', {'zoomblur': {'t0': 60.2}}),
 # ---------------- CH2 工作的重新定义 1:01-1:45   cold grey-blue, warming from S025
 (18, 61.0, 66.0, [1.32, .5, .5, 0], [1.06, .5, .5, 0], 'grey', 'fade', 0.4, 'out', {}),
 (19, 66.0, 69.6, [1.14, .56, .5, 0], [1.14, .44, .5, 0], 'grey', 'fade', 1.2, 'lin', {}),
 (20, 69.6, 72.4, [1.04, .5, .5, 0], [1.17, .5, .48, 0], 'grey', 'fade', 1.0, 'lin', {}),
 (21, 72.4, 75.0, [1.14, .45, .5, 0], [1.14, .55, .5, 0], 'grey', 'fade', 1.0, 'lin', {}),
 (22, 75.0, 77.6, [1.05, .5, .5, 0], [1.18, .5, .5, 0], 'grey', 'fade', 1.0, 'lin', {}),
 (23, 77.6, 82.0, [1.02, .5, .5, 0], [1.15, .5, .48, 0], 'grey', 'fade', 1.4, 'lin', {'dim': 0.93}),
 (24, 82.0, 86.2, [1.16, .5, .5, 0], [1.04, .5, .5, 0], 'grey', 'fade', 1.4, 'lin', {'dim': 0.93}),
 (25, 86.2, 91.6, [1.0, .5, .5, 0], [1.14, .5, .47, 0], 'tender', 'fade', 1.6, 'lin', {}),
 (26, 91.6, 95.2, [1.13, .45, .5, 0], [1.13, .55, .5, 0], 'tender', 'fade', 1.2, 'lin', {}),
 (27, 95.2, 99.0, [1.04, .5, .5, 0], [1.18, .5, .5, 0], 'tender', 'fade', 1.2, 'lin', {}),
 (28, 99.0, 105.0, [1.02, .5, .5, 0], [1.2, .5, .48, 0], 'tender', 'fade', 1.4, 'lin', {}),
 # ---------------- CH3 创造力属于谁？ 1:45-2:36   warm white / gold
 (29, 105.0, 109.6, [1.22, .5, .5, 0], [1.04, .5, .5, 0], 'gold', 'inkmap', 1.6, 'lin', {}),
 (30, 109.6, 113.0, [1.13, .45, .5, 0], [1.13, .55, .5, 0], 'gold', 'fade', 1.2, 'lin', {}),
 (31, 113.0, 116.0, [1.04, .5, .5, 0], [1.18, .5, .5, 0], 'gold', 'fade', 1.0, 'lin', {}),
 (32, 116.0, 120.0, [1.13, .55, .5, 0], [1.13, .45, .5, 0], 'gold', 'fade', 1.2, 'lin', {}),
 (33, 120.0, 125.0, [1.02, .5, .5, 0], [1.15, .5, .48, 0], 'warm', 'fade', 1.6, 'lin', {}),
 (34, 125.0, 128.4, [1.06, .5, .5, 0], [1.14, .5, .5, 0], 'warm', 'fade', 1.4, 'lin', {}),
 (35, 128.4, 132.4, [1.04, .5, .5, 0], [1.17, .5, .48, 0], 'warm', 'fade', 1.4, 'lin', {}),
 (36, 132.4, 137.4, [1.13, .45, .5, 0], [1.13, .55, .5, 0], 'warm', 'fade', 1.4, 'lin', {}),
 (37, 137.4, 142.4, [1.02, .5, .5, 0], [1.16, .5, .48, 0], 'warm', 'fade', 1.4, 'lin', {}),
 (38, 142.4, 147.6, [1.13, .55, .5, 0], [1.13, .45, .5, 0], 'warm', 'fade', 1.4, 'lin', {}),
 (39, 147.6, 151.8, [1.04, .5, .5, 0], [1.16, .5, .5, 0], 'warm', 'fade', 1.2, 'lin', {}),
 (40, 151.8, 156.0, [1.04, .5, .5, 0], [1.5, .5, .45, 0], 'goldblue', 'fade', 1.2, 'in', {'zoomblur': {'t0': 154.9}, 'bloom': 0.2}),
 # ---------------- CH4 AI时代的人类答案 2:36-3:44   dawn gold -> cosmic blue
 (41, 156.0, 160.6, [1.42, .5, .5, 0], [1.04, .5, .5, 0], 'dawn', 'fade', 0.45, 'out', {'stars3d': {'k1': 0.01, 'k2': 0.0}, 'bloom': 0.2}),
 (42, 160.6, 165.0, [1.04, .5, .5, 0], [1.2, .5, .5, 0], 'dawn', 'fade', 1.4, 'lin', {'reveal': {'t0': 160.6, 't1': 164.0, 'a0': 0.62}, 'bloom': 0.25}),
 (43, 165.0, 169.2, [1.13, .45, .5, 0], [1.13, .55, .5, 0], 'dawn', 'fade', 1.2, 'lin', {'bloom': 0.25}),
 (44, 169.2, 173.2, [1.0, .5, .5, 0], [1.38, .5, .5, 0], 'dawn', 'fade', 1.2, 'in', {'zoomblur': {'t0': 172.3}}),
 (45, 173.2, 177.6, [1.32, .5, .5, 0], [1.06, .5, .5, 0], 'goldblue', 'fade', 0.45, 'out', {'stars3d': {'k1': 0.01, 'k2': 0.0}}),
 (46, 177.6, 182.2, [1.03, .5, .5, 0], [1.16, .5, .48, 0], 'tender', 'fade', 1.4, 'lin', {}),
 (47, 182.2, 186.2, [1.13, .45, .5, 0], [1.13, .55, .5, 0], 'goldblue', 'fade', 1.2, 'lin', {}),
 (48, 186.2, 190.2, [1.04, .5, .5, 0], [1.17, .5, .48, 0], 'tender', 'fade', 1.2, 'lin', {}),
 (49, 190.2, 195.0, [1.04, .5, .5, 0], [1.28, .5, .5, 0], 'void', 'fade', 1.2, 'in', {'stars3d': {'k1': 0.02, 'k2': 0.005}}),
 (50, 195.0, 199.2, [1.1, .47, .5, -1.0], [1.22, .54, .5, 1.0], 'goldblue', 'fade', 0.6, 'lin', {'bloom': 0.2}),
 (51, 199.2, 202.2, [1.04, .5, .5, 0], [1.17, .5, .46, 0], 'dawn', 'fade', 1.0, 'lin', {}),
 (52, 202.2, 205.0, [1.04, .5, .5, 0], [1.2, .5, .5, 0], 'dawn', 'fade', 1.0, 'lin', {'bloom': 0.3}),
 (53, 205.0, 208.0, [1.04, .5, .5, 0], [1.16, .5, .5, 0], 'tender', 'fade', 1.2, 'lin', {}),
 (54, 208.0, 211.0, [1.03, .5, .5, 0], [1.14, .5, .48, 0], 'tender', 'fade', 1.2, 'lin', {}),
 (55, 211.0, 216.4, [1.5, .5, .5, 0], [1.04, .5, .5, 0], 'goldblue', 'fade', 1.4, 'lin', {'stars3d': {'k1': 0.01, 'k2': 0.0}}),
 (56, 216.4, DUR, [1.3, .5, .5, 0], [1.0, .5, .5, 0], 'dawn', 'fade', 1.8, 'lin',
  {'reveal': {'t0': 216.4, 't1': 221.0, 'a0': 0.55}, 'bloom': 0.3, 'stars3d': {'k1': 0.008, 'k2': 0.0}}),
]

def clampcam(c):
    z, cx, cy, r = c
    z = max(1.0, z)
    hx, hy = 0.5 * (1 + 0.032 * abs(r)) / z, 0.5 * (1 + 0.018 * abs(r)) / z
    return [round(z, 4), round(min(max(cx, hx), 1 - hx), 4), round(min(max(cy, hy), 1 - hy), 4), r]


S = []
for k, (i, st, en, c0, c1, g, tr, ov, ez, fx) in enumerate(R):
    nxt = R[k + 1] if k + 1 < len(R) else None
    end = en + (nxt[7] if nxt else 0.0)       # outgoing shot keeps moving under the next one
    cam1 = c1
    if nxt and nxt[7] > 0:                    # extrapolate the move linearly through the overlap
        f = (end - st) / (en - st)
        cam1 = [c0[j] + (c1[j] - c0[j]) * f for j in range(4)]
    S.append(dict(id=f'S{i:03d}', image=IMG[i], start=st, end=round(end, 3), cam=[clampcam(c0), clampcam(cam1)], grade=g, trans=tr,
                  ease=ez, fx=fx, prep={}, desc=''))


def load_srt(p):
    out = []
    for blk in re.split(r'\n\s*\n', open(p, encoding='utf-8').read().strip()):
        ln = blk.strip().split('\n')
        m = re.findall(r'(\d+):(\d+):(\d+),(\d+)', ln[1])
        ts = [int(h) * 3600 + int(mi) * 60 + int(s) + int(ms) / 1000 for h, mi, s, ms in m]
        out.append([ts[0], ts[1], ''.join(ln[2:])])
    return out


CUES = load_srt(os.path.join(HERE, 'narration.srt'))
SUBS = [[a, b, t, 'brief'] for a, b, t in CUES[:41]]
CAPTIONS = [[a, b if j else 215.8, t] for j, (a, b, t) in enumerate(CUES[41:43])]
CAPTIONS[1][1] = 219.6
CHAPTERS = [
    [23.4, 27.4, '第一章', '智能的诞生', 'THE BIRTH OF INTELLIGENCE'],
    [61.4, 65.6, '第二章', '工作的重新定义', 'REDEFINING WORK'],
    [105.4, 109.6, '第三章', '创造力属于谁？', 'WHO OWNS CREATIVITY?'],
    [156.4, 160.6, '第四章', 'AI时代的人类答案', 'THE HUMAN ANSWER'],
]
LABELS = [[165.6, 168.8, '想象', '未来聚变能源设施'], [182.6, 185.8, '想象', '月球基地'], [190.8, 194.4, '想象', '深空航行']]
TIMELINE = dict(win=[26.6, 35.4], y=1100, x0=560, x1=2000, grow=[26.8, 33.2],
                nodes=[[27.0, 640, '19世纪', '机械计算'], [29.6, 1280, '20世纪', '互联网'], [32.4, 1920, '21世纪', '人工智能']])
TICKER = {'windows': [], 'keys': []}
ROUTES = []
TITLE = [18.8, 22.8]
ENDCARD = [219.8, DUR]
PARCHMENT = [[0, 0.0], [DUR, 0.0]]
FLASHES = [[15.8, 0.35, 0.10], [18.4, 0.55, 0.16], [23.0, 0.18, 0.3], [61.0, 0.3, 0.25], [156.0, 0.38, 0.35],
           [173.2, 0.22, 0.25], [195.0, 0.2, 0.5]]
# light leaks: [start, duration, BGR colour, direction(+1 l->r, -1 r->l), strength]
LEAKS = [[0.4, 3.2, [40, 120, 255], 1, 0.30], [21.6, 2.6, [90, 170, 255], -1, 0.32], [59.8, 2.4, [255, 220, 170], 1, 0.30],
         [85.4, 3.0, [110, 190, 255], -1, 0.22], [103.6, 3.2, [120, 205, 255], 1, 0.38], [127.6, 2.6, [150, 215, 255], -1, 0.22],
         [154.6, 3.0, [170, 225, 255], 1, 0.36], [194.2, 3.0, [110, 200, 255], -1, 0.34], [214.6, 5.0, [130, 210, 255], 1, 0.26]]
# floating dust: [t, intensity, B, G, R]; embers: [t, intensity]
DUST = [[0, 0.0, 200, 210, 230], [4.0, 0.18, 230, 215, 200], [23.0, 0.32, 255, 210, 150], [61.0, 0.22, 225, 215, 205],
        [86.0, 0.26, 200, 220, 245], [105.0, 0.45, 160, 215, 255], [156.0, 0.32, 190, 225, 255], [195.0, 0.5, 150, 215, 255],
        [DUR, 0.3, 200, 225, 250]]
EMBERS = [[0, 0.85], [3.0, 0.85], [4.8, 0.0], [DUR, 0.0]]

DATA = dict(title='今日简史：AI时代，人类如何重新定义自己', width=2560, height=1440, fps=24, duration=DUR,
            shots=S, subtitles=SUBS, chapters=CHAPTERS, labels=LABELS, ticker=TICKER, routes=ROUTES,
            title_card=TITLE, captions=CAPTIONS, endcard=ENDCARD, parchment=PARCHMENT, flashes=FLASHES,
            leaks=LEAKS, dust=DUST, embers_g=EMBERS, timeline=TIMELINE)

if __name__ == '__main__':
    with open(os.path.join(HERE, 'shotlist.json'), 'w', encoding='utf-8') as f:
        json.dump(DATA, f, ensure_ascii=False, indent=1)
    print('wrote shotlist.json', len(S), 'shots', len(SUBS), 'subtitles', len(CAPTIONS), 'captions')

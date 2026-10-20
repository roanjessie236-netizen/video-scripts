#!/usr/bin/env python3
"""v3 edits for 《明天属于谁》 (apply once on top of v2):
1) line 23: 雇佣劳动的生产关系 -> 资本主义的生产关系
2) old line 37 (tax & subsidy) rewritten (税低了，补贴少，市场撑不住; '走不通' dropped) and moved to tomorrow #1;
   'computing power & data' becomes tomorrow #2 (lines 34-37 reordered), TTS cache re-keyed for moved lines
3) chapter-4 shots / labels / music cues follow the new order
4) depth parallax off on every shot with people (NOPAR), 0.6 gain elsewhere
5) diagram: left label of the 生产关系 -> 上层建筑 arrow 决定 -> 基础"""
import os, glob, shutil
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(R)


def edit(p, pairs):
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:60], s.count(a))
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8').write(s)
    return s


# ---------------------------------------------------------------- 1+2 narration
p = 'voiceover/lines_wt.py'
s = open(p, encoding='utf-8').read()
s = s.replace("而在雇佣劳动的生产关系：', '可无用的根源不在技术，而在雇佣劳动的生产关系：', 'Yet the root of \"uselessness\" lies not in technology, but in the relations of wage labour:'",
              "而在资本主义的生产关系：', '可无用的根源不在技术，而在资本主义的生产关系：', 'Yet the root of \"uselessness\" lies not in technology, but in capitalist relations of production:'")
assert s.count('资本主义的生产关系') == 2
L = s.split('\n')
J = [next(j for j, l in enumerate(L) if l.startswith('(%d, 4,' % i)) for i in (34, 35, 36, 37)]
o34, o35, o36 = L[J[0]], L[J[1]], L[J[2]]
assert '算力' in o34 and '今日简史' in o35 and '领主' in o36 and '征税' in L[J[3]]
L[J[0]] = ("(34, 4, 'sub', '第一种：征税、发补贴，修修补补。|可税高了资本不干，税低了，补贴少，市场撑不住。', "
           "'第一种：征税、发补贴，修修补补。可税高了，资本不干；税低了，补贴少，市场撑不住。', "
           "'In the first, tax and subsidy patch things up.|But tax too high and capital balks; too low, subsidies shrink and the market cannot hold.', -4, '', 'pdf'),")
L[J[1]] = o34.replace('(34, 4,', '(35, 4,').replace('第一种', '第二种').replace('In the first', 'In the second')
L[J[2]] = o35.replace('(35, 4,', '(36, 4,')
L[J[3]] = o36.replace('(36, 4,', '(37, 4,')
open(p, 'w', encoding='utf-8').write('\n'.join(L))
T = 'voiceover/clips/_tmp'
for old, new in ((36, 37), (35, 36)):          # unchanged takes that moved: reuse the cached edge-tts output
    for f in glob.glob(f'{T}/{old:02d}_*'):
        shutil.copy(f, f'{T}/{new:02d}_' + os.path.basename(f)[3:])

# ---------------------------------------------------------------- 3 timeline
p = 'timeline_wt.py'
s = open(p, encoding='utf-8').read()
s = s.replace("33: 2.9, 34: 0.5, 35: 0.45, 36: 0.35, 37: 0.6,", "33: 2.9, 34: 0.5, 35: 0.6, 36: 0.45, 37: 0.35,")
a, b = s.index("shot('cloudcastle'"), s.index("shot('assembly'")
s = s[:a] + '''# v3: tomorrow #1 = patching the old order (tax & subsidy), #2 = cloud lords
shot('patcheddam', '67_patcheddam.jpg', st(34) - 0.06, push(1.05, 0.03), grade='steel', fx={'fog': dict(STEAMF, a=0.16)},
     desc='An old dam patched with sandbags, leaking')
shot('capitalflight', '68_capitalflight.jpg', W_(34, '税高'), pan(1.1, 0.014, left=True), grade='amber', ease='lin',
     desc='Capital leaves: ships and a jet depart, factories dark')
shot('emptymall', '60_emptymall.jpg', W_(34, '税'), push(1.05, 0.03), grade='ash', fx={'flicker': {'amp': 0.03}},
     desc='An abandoned mall: subsidies shrink, the market cannot hold')
shot('cloudcastle', '28_cloudcastle.jpg', st(35) - 0.15, crane(1.1, 0.014, 0.01), grade='cyan', ease='lin',
     trans='glitch', tdur=0.3, desc='Fortress city of servers above the clouds')
shot('datalords', '65_datalords.jpg', W_(35, '少数'), push(1.06, 0.04), grade='void', desc='A few figures in a penthouse over a sea of data')
shot('dataweb', '66_dataweb.jpg', st(36) - 0.3, push(1.03, 0.03), grade='cyan', trans='luma', tdur=0.4,
     fx={'bloom': 0.2, 'par': 0.5}, desc='Everyone a node in a planetary data web')
shot('cloudserfs', '29_cloudserfs.jpg', st(37) - 0.06, push(1.05, 0.03), grade='void',
     desc='Endless hall of people labelling data under cold logos')
shot('queue', '30_queue.jpg', W_(37, '施舍'), pan(1.1, 0.012), grade='ash', ease='lin', fx={'rain': {'a': 0.18}},
     desc='Rainy queue at an automated welfare kiosk')
''' + s[b:]
assert s.count("shot('patcheddam'") == 1 and "shot('deadend'" not in s
for x, y in [("[st(35) + 0.3, en(35) + 0.3, '赫拉利 ·《今日简史》", "[st(36) + 0.3, en(36) + 0.3, '赫拉利 ·《今日简史》"),
             ("[w(36, '领主') - 0.1, en(36) + 0.3, '“技术封建主义”", "[w(37, '领主') - 0.1, en(37) + 0.3, '“技术封建主义”"),
             ("    'queue': SHOTS_AT['patcheddam'], ", "    ")]:
    assert s.count(x) == 1, x
    s = s.replace(x, y)
a = s.index("for a, b in zip(SH, SH[1:]):")
s = s[:a] + '''# v3: 2.5D depth parallax OFF wherever people / hands / humanoid figures are in frame (the per-pixel depth warp
# stretched faces and bodies during camera moves) -> those shots move as rigid 2D plates; gentler parallax elsewhere.
NOPAR = {'leisure', 'overtime', 'machinecity', 'cave', 'flint', 'campfire', 'hunters', 'wheat', 'scribe', 'ziggurat',
         'millgate', 'textile', 'quern', 'steammill', 'myths', 'miners', 'owner', 'electric', 'fordline', 'switchboard',
         'humanoids', 'station', 'workerportrait', 'idlecrowd', 'hiring', 'scaffold', 'lockedgate', 'paradox', 'brake',
         'luddites', 'looms', 'haijin', 'gunboats', 'datalords', 'cloudserfs', 'queue', 'assembly', 'coowners',
         'planning', 'harvest', 'publichall', 'workshop', 'care', 'darkdawn', 'march', 'hands', 'bridge', 'forward',
         'childhill', 'sunrisecrowd', 'datacenter', 'robotarms', 'gardencity', 'aimind', 'keynes', 'emptyoffice', 'cloudcastle', 'patcheddam'}
for s_ in SH:
    if s_['id'] in NOPAR:
        s_['fx']['par'] = 0
    else:
        s_['fx']['par'] = min(0.6, s_['fx'].get('par', 0.6))

''' + s[a:]
open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- 3 music (chapter 4 in the new order)
p = 'tools/score_wt.py'
s = open(p, encoding='utf-8').read()
a, b = s.index("T_CC, T_DS, T_CS, T_QU = SH['cloudcastle']"), s.index("# third tomorrow: common owners")
s = s[:a] + '''T_PD, T_CC, T_DS, T_CS, T_QU = SH['patcheddam'], SH['cloudcastle'], SH['dataism'], SH['cloudserfs'], SH['queue']
T_AS, T_HV, T_WS, T_GC = SH['assembly'], SH['harvest'], SH['workshop'], SH['gardencity']
impact(C4, 0.4, notes=(33, 45))
pad(C4, T_PD - C4, 'Am9', gain=0.07, p=2.6, att=1.2, rel=0.8, hall=0.4, cath=0.4)
for k, m in enumerate([76, 81, 84]):                           # three roads: three chimes
    celesta(w(33, '三') + k * 0.42, m, 0.04, pan=-0.5 + 0.5 * k)
ambience(C4, T_PD - C4 + 1.0, 0.07, fin=1.5, fout=1.0, wind=0.4, shimmer=1.2)
# v3: first tomorrow = patching the old order (thin, grey, rain on the leaking dam)
PQ = chain([(T_PD, 'Dm'), (T_PD + 3.0, 'Am')], T_CC)
pad_prog(PQ, [(T_PD, 0.04), (T_CC, 0.035)], p=2.0, att=0.8, rel=1.0, hall=0.4, cath=0.35)
for k, m in enumerate([62, 60, 57, 60, 62, 60, 57, 55]):
    if T_PD + 0.3 + k * BEAT < T_CC - 0.4:
        piano(T_PD + 0.3 + k * BEAT, m, 0.05 if k % 2 == 0 else 0.04)
ambience(T_PD, T_CC - T_PD, 0.05, fin=0.5, fout=0.8, wind=0.2, shimmer=0.2)
for t in np.arange(T_PD, T_CC, 0.04):                            # rain
    if np.random.rand() < 0.5:
        place(SHAKER, t, 0.006 + 0.006 * np.random.rand(), pan=np.random.uniform(-0.8, 0.8), hall=0.2)
# v3: second tomorrow = cloud lords (cold, digital) -> straight into the warm turn
P4a = chain([(T_CC, 'Am9'), (T_CC + 4 * BEAT, 'Fmaj7'), (T_DS, 'Dm'), (T_DS + 4 * BEAT, 'Am9'), (T_CS, 'F'),
             (T_CS + 3.0, 'Esus')], T_AS)
glitch(T_CC - 0.05, 0.7, 0.07, 41)
place(ensemble('saw', 81, T_AS - T_CC, p=1.0, voices=3, cents=18, vib=0.0, att=1.0, rel=1.0, width=1.0), T_CC,
      0.018, hall=0.2, cath=0.7)
place(ensemble('saw', 28, T_AS - T_CC, p=1.2, voices=3, cents=6, vib=0.0, att=0.6, rel=0.8, width=0.3), T_CC,
      0.06, hall=0.05)
arp(P4a, BEAT / 2, [(T_CC, 0.025), (T_CS, 0.045)], [0, 2, 1, 3, 0, 2, 1, 3], bright_pts=[(T_CC, 0.5), (T_CS, 0.9)])
subpulse(P4a, BEAT / 2, [(T_CC, 0.03), (T_CS, 0.05)], T_CC, T_AS - 0.6)
beat_kit(T_DS, T_AS - 0.6, [(T_DS, 0.06), (T_CS, 0.09)], kick=False)
pad_prog(P4a, [(T_CC, 0.05), (T_CS, 0.07)], p=2.6, att=1.0, rel=0.8, hall=0.4, cath=0.4)
for i, m in enumerate([88, 84, 81, 79, 76, 74, 72, 69]):
    celesta(T_DS + 0.1 + i * 0.14, m, 0.035, pan=0.7 - 0.2 * i)
for t in np.arange(T_CS, T_AS - 0.6, BEAT):                      # identical screens: mechanical ticks
    place(METAL, t, 0.01, pan=0.4, hall=0.1)
place(BOOM, w(37, '施舍'), 0.15, hall=0.1, cath=0.3)
for t in np.arange(T_QU, T_AS - 0.3, 0.05):                       # soft rain under the welfare queue
    if np.random.rand() < 0.35:
        place(SHAKER, t, 0.004 + 0.004 * np.random.rand(), pan=np.random.uniform(-0.8, 0.8), hall=0.2)
''' + s[b:]
s = s.replace("# (cloud lords) -> warm I-V-vi-IV turn", "# (v3: patching, then cloud lords) -> warm I-V-vi-IV turn")
open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- 5 diagram label
edit('tools/diagrams.py', [("text(d, (cx - 200 * S, (yb + yt) / 2), '决定', F('SemiBold', 40), GOLDT + (255,), 'rm')",
                            "text(d, (cx - 200 * S, (yb + yt) / 2), '基础' if k == 0 else '决定', F('SemiBold', 40), GOLDT + (255,), 'rm')  # v3")])
print('PATCH_V3_OK')

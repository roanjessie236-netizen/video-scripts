#!/usr/bin/env python3
"""《明天属于谁》engine = Sapiens render_core.py/render.py + homo-deus-future/tools/patch_engine.py (without its
silver-blue recolour / title text: this film keeps the Sapiens gold typography) + homo-deus-future/v4/tools/patch_v4.py
+ this patch: title / end card text, grades 'sepia' 'mono' 'hope'.
Usage: python3 tools/patch_wt.py engine_dir   (idempotent)"""
import os, sys
D = sys.argv[1]
p = os.path.join(D, 'render_core.py')
s = open(p, encoding='utf-8').read()
if 'WHOSE-TOMORROW' in s:
    sys.exit('already patched')


def rep(s, a, b):
    assert a in s, 'missing: ' + a[:80]
    return s.replace(a, b, 1)


s = rep(s, "        l1 = text_layer('人类简史', font('Black', 200), tracking=46,",
        "        l1 = text_layer('明天属于谁', font('Black', 200), tracking=40,")
s = rep(s, "        l2 = text_layer('七万年的文明觉醒', font('Regular', 62), (240, 224, 192), tracking=26,",
        "        l2 = text_layer('从磨坊到算法 · 简史三部曲终章', font('Regular', 58), (240, 224, 192), tracking=20,")
s = rep(s, "        l3 = text_layer('70,000 YEARS OF AWAKENING', font('Medium', 30),",
        "        l3 = text_layer('WHOSE TOMORROW?  ·  FROM THE MILL TO THE ALGORITHM', font('Medium', 30),")
a = s[s.index('def endcard_layer():'):s.index('def lower_layer(')]
s = s.replace(a, '''def endcard_layer():
    def mk():
        l1 = text_layer('明天属于谁', font('Bold', 140), tracking=36, grad=(GOLD_T, GOLD_B),
                        glow=((255, 180, 90), 24, 0.30), shadow=(12, 0.5, 6))
        orn = ornament(560, GOLD)
        l2 = text_layer('简史三部曲 · 终章', font('Regular', 50), (240, 230, 210), tracking=22)
        l3 = text_layer('灵感来自赫拉利《人类简史》《今日简史》《未来简史》与马克思、恩格斯的著作', font('Light', 30),
                        (214, 206, 190), tracking=6)
        l4 = text_layer('画面由 AI 生成 · 未来场景为想象 · 非官方作品', font('Light', 26), (180, 176, 168), tracking=6)
        return stack([l1, orn, l2, l3, l4], [-80, -16, -10, -14])
    return cached(('end',), mk)


''')
s = rep(s, "\n\ndef grade(img, g):\n", """
GRADES.update({
    'sepia': dict(exp=1.0, con=.28, sat=.45, sh=(.035, .018, -.01), hi=(.06, .035, -.02), lift=(.035, .026, .016)),
    'mono': dict(exp=1.0, con=.32, sat=.0, sh=(.012, .01, .006), hi=(.02, .018, .012), lift=(.025, .024, .022)),
    'hope': dict(exp=1.03, con=.24, sat=.95, sh=(-.005, .008, .03), hi=(.07, .045, .0), lift=(.016, .016, .018)),
})


def grade(img, g):
""")
s += '\n# WHOSE-TOMORROW\n'
open(p, 'w', encoding='utf-8').write(s)
print('patched', D)

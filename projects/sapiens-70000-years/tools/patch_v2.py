"""v2 patch: narration v2 (40 voiced lines, bilingual subs), child shot -13 s (300 -> 287 s), score ending re-timed.
Usage: python3 tools/patch_v2.py vo2/lines.json vo2/clips/durs.json   (run once on the v1 files)"""
import json, re, sys, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(sys.argv[1], encoding='utf-8')); D = json.load(open(sys.argv[2]))
TOTAL = 287.0
LEAD, TAILS, MIN = 0.15, 0.5, 1.6
OLD = {'七万年前，他们只是地球上不起眼的一群动物。', '没有锋利的爪牙，没有强壮的身体。', '但他们拥有一种力量——创造不存在的世界。',
       '大约七万年前，智人的大脑里发生了一场无声的革命。', '神话、国家、文明，都诞生于人类共同相信的想象。', '我们以为驯化了小麦，其实是小麦驯化了我们。',
       '村落变成城市，城市变成王国，王国变成帝国。', '从相信神明，到探索宇宙。', '从仰望星空，到成为改变星球的力量。', '过去七万年，我们改变了世界。',
       '但未来，我们是否还能理解自己？', '当人工智能、基因技术和宇宙探索改变生命本身……', '我们正获得近乎神的力量，却仍不清楚自己想要什么。', '下一章人类历史，将由谁书写？'}
BRIEF = {'七万年前，他们只是地球上不起眼的一群动物。', '没有锋利的爪牙，没有强壮的身体。', '但他们拥有一种力量——创造不存在的世界。',
         '神话、国家、文明，都诞生于人类共同相信的想象。', '从相信神明，到探索宇宙。', '从仰望星空，到成为改变星球的力量。', '过去七万年，我们改变了世界。',
         '但未来，我们是否还能理解自己？', '当人工智能、基因技术和宇宙探索改变生命本身……', '下一章人类历史，将由谁书写？'}
subs, caps = [], []
for k, l in enumerate(L):
    text = l.get('sub', l['t']); d = D[str(l['i'])]['dur']
    s = round(l['s'] - LEAD, 2)
    nxt = L[k + 1]['s'] - LEAD - 0.1 if k + 1 < len(L) else TOTAL
    e = round(min(max(l['s'] + d + TAILS, s + MIN), nxt), 2)
    if l.get('cap'):
        caps.append([round(l['s'] - 0.6, 2), None, text, l['en'], d])
    else:
        subs.append([s, e, text, 'brief' if text in BRIEF else 'added', l['en']])
caps[0][1] = 272.4; caps[1][1] = 278.4
caps = [c[:4] for c in caps]

def sub(src, a, b, n=1):
    assert src.count(a) == n, (a[:60], src.count(a)); return src.replace(a, b)

p = os.path.join(HERE, 'timeline.py'); T = open(p, encoding='utf-8').read()
i0 = T.index('SUBS = ['); i1 = T.index('CHAPTERS = [')
body = 'SUBS = [  # [start, end, text, source, english]  source: \'brief\' = user\'s script, \'added\' = added line based on Sapiens\n'
body += ''.join('    [%.2f, %.2f, %s, %r, %s],\n' % (s, e, json.dumps(t, ensure_ascii=False), src, json.dumps(en, ensure_ascii=False)) for s, e, t, src, en in subs) + ']\n'
T = T[:i0] + body + T[i1:]
T = sub(T, "shot('child', '37_child.jpg', 266.0, 293.5, [[1.0, .52, .5, 0], [1.2, .53, .42, 0]]",
        "shot('child', '37_child.jpg', 266.0, 280.5, [[1.0, .52, .5, 0], [1.11, .525, .46, 0]]")
T = sub(T, "shot('end', '01_galaxy.jpg', 292.0, 300.0,", "shot('end', '01_galaxy.jpg', 279.0, 287.0,")
T = sub(T, "CAPTIONS = [[274.0, 279.6, '我们从哪里来？'], [281.0, 287.6, '我们将走向哪里？']]",
        'CAPTIONS = [  # [start, end, text, english]\n' + ''.join('    [%.2f, %.2f, %s, %s],\n' % (s, e, json.dumps(t, ensure_ascii=False), json.dumps(en)) for s, e, t, en in caps) + ']')
T = sub(T, 'ENDCARD = [292.8, 299.2]', 'ENDCARD = [279.8, 286.2]')
T = sub(T, '[200, 0.05], [300, 0.0]]', '[200, 0.05], [287.0, 0.0]]')
T = sub(T, 'duration=300.0,', 'duration=287.0,')
open(p, 'w', encoding='utf-8').write(T)

p = os.path.join(HERE, 'render.py'); R = open(p, encoding='utf-8').read()
R = sub(R, """    if t > 297.0:
        g *= 1 - smooth((t - 297.0) / 3.0)""", """    if t > DUR - 3.0:
        g *= 1 - smooth((t - (DUR - 3.0)) / 3.0)""")
R = sub(R, "for s, e, _ in TL['captions']", "for s, e, *_ in TL['captions']")
R = sub(R, "for s, e, _, _ in TL['subtitles']", "for s, e, *_ in TL['subtitles']")
R = sub(R, """    for s, e, text, _ in TL['subtitles']:
        a = window(t, s, e, 0.35, 0.35)
        if a:
            blit_center(frame, subtitle_layer(text), W / 2, H - 150, a)""", """    for s, e, text, _, *en in TL['subtitles']:
        a = window(t, s, e, 0.35, 0.35)
        if a:
            Ls = subtitle_layer(text, en[0] if en else '')
            blit(frame, Ls, W / 2 - Ls.shape[1] / 2, H - 150 - SUB_ZH_H / 2, a)""")
R = sub(R, """    for s, e, text in TL['captions']:
        a = window(t, s, e, 1.0, 1.0)
        if a:
            blit_center(frame, caption_layer(text), W / 2, H * 0.27, a)""", """    for s, e, text, *en in TL['captions']:
        a = window(t, s, e, 1.0, 1.0)
        if a:
            Lc = caption_layer(text, en[0] if en else '')
            blit(frame, Lc, W / 2 - Lc.shape[1] / 2, H * 0.27 - CAP_ZH_H / 2, a)""")
R = sub(R, "if __name__ == '__main__':", "SUB_ZH_H = subtitle_layer('字').shape[0]\nCAP_ZH_H = caption_layer('字').shape[0]\n\n\nif __name__ == '__main__':") if "if __name__ == '__main__':" in R else R
open(p, 'w', encoding='utf-8').write(R)

p = os.path.join(HERE, 'render_core.py'); C = open(p, encoding='utf-8').read()
C = sub(C, "def text_layer(text, fnt, color=(255, 255, 255), tracking=0, grad=None, glow=None, shadow=None):",
        "def text_layer(text, fnt, color=(255, 255, 255), tracking=0, grad=None, glow=None, shadow=None, whole=False):")
C = sub(C, """    widths = [fnt.getlength(c) for c in text]
    tw = sum(widths) + tracking * max(0, len(text) - 1)""", """    widths = [fnt.getlength(c) for c in text]
    tw = sum(widths) + tracking * max(0, len(text) - 1)
    if whole:  # draw the run in one call so Latin text keeps its kerning
        tw = fnt.getlength(text)""")
C = sub(C, """    x = pad
    for c, cw in zip(text, widths):
        d.text((x, pad), c, font=fnt, fill=255)
        x += cw + tracking""", """    x = pad
    if whole:
        d.text((x, pad), text, font=fnt, fill=255)
    else:
        for c, cw in zip(text, widths):
            d.text((x, pad), c, font=fnt, fill=255)
            x += cw + tracking""")
C = sub(C, """def subtitle_layer(text):
    return cached(('sub', text), lambda: text_layer(text, font('Medium', 56), WARMW, tracking=3, shadow=(7, 0.9, 3)))""",
"""EN_SUB = (226, 218, 202)


def subtitle_layer(text, en=''):
    # Chinese line on top, English translation underneath (bilingual subtitles, v2)
    def mk():
        zh = text_layer(text, font('Medium', 56), WARMW, tracking=3, shadow=(7, 0.9, 3))
        if not en:
            return zh
        e = text_layer(en, font('Regular', 36), EN_SUB, shadow=(6, 0.9, 2), whole=True)
        return stack([zh, e], [-50])
    return cached(('sub', text, en), mk)""")
C = sub(C, """def caption_layer(text):
    return cached(('cap', text), lambda: text_layer(text, font('Light', 92), (238, 242, 250), tracking=30,""",
"""def caption_layer(text, en=''):
    if en:
        def mk2():
            zh = caption_layer(text)
            e = text_layer(en, font('Light', 42), (214, 222, 236), shadow=(8, 0.8, 2), whole=True)
            return stack([zh, e], [-int(zh.shape[0] * 0.22) - int(e.shape[0] * 0.25)])
        return cached(('cap2', text, en), mk2)
    return cached(('cap', text), lambda: text_layer(text, font('Light', 92), (238, 242, 250), tracking=30,""")
open(p, 'w', encoding='utf-8').write(C)

p = os.path.join(HERE, 'music.py'); M = open(p, encoding='utf-8').read()
M = sub(M, 'DUR = 300.0', 'DUR = 287.0  # v2: child shot cut by 13 s')
M = sub(M, 'choir alone 266-300', 'choir alone 266-287 (v2)')
M = sub(M, 'ambience(200, 100, 0.1,', 'ambience(200, DUR - 200, 0.1,')
M = sub(M, 'for s in range(0, 300, 10):', 'for s in range(0, int(DUR), 10):')
a = M.index("log('ending choir')"); b = M.index('# ================================================================== REVERB')
M = M[:a] + """log('ending choir')
# v2: the child shot is 13 s shorter -> choir + solo line compressed into 266-287
choir(266.0, CH['Dsus2'][1:], 7.5, 0.2, att=2.5, rel=3.0, hall=0.2, cath=0.8)
choir(273.0, CH['Bbadd9'][1:], 7.0, 0.19, att=2.5, rel=3.0, hall=0.2, cath=0.8)
choir(279.5, CH['Dsus2'][1:], 6.5, 0.19, att=2.5, rel=5.0, hall=0.2, cath=0.8)
t = 267.5
for m, d in [(81, 3.0), (79, 1.5), (77, 3.0), (74, 4.0), (81, 5.0)]:
    rl = 4.0 if t > 279 else 1.4
    s = ensemble('u', m, d, voices=3, cents=6, vib=0.005, vibrate=5.2, att=0.9, rel=rl, width=0.5)
    place(s, t, 0.09, hall=0.2, cath=0.9)
    t += d + (0.4 if d >= 3 else 0)

""" + M[b:]
open(p, 'w', encoding='utf-8').write(M)
print('patched: %d subs, %d captions, total %.1f s' % (len(subs), len(caps), TOTAL))
for s in subs: print(s[:3])
print(caps)

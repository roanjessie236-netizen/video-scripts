# 组装 render_ch6.py：r5_head（改素材目录、分句去尾冒号）+ 说明 + body6 + r5_help + r5_fx + shots6 + r5_tail
P = '/data/luxun90/preview/parts/'; P6 = '/data/luxun90/preview/parts6/'
tail = open(P + 'r5_tail.py').read()
tail = tail.replace("DUSTR = [(t_17, ST['S3-04']), (ST['S4-05'], EN['S4-05'])]", "DUSTR = [DUST_A, DUST_B]   # “进化的链子”、柔石的记念两镜带浮尘")
tail = tail.replace("print('TOTAL_MAIN', TOTAL_MAIN, 'TURN', round(TURN3, 2), round(TURN4, 2))", "print('TOTAL_MAIN', TOTAL_MAIN, 'TURN', round(TURN6, 2))")
assert 'DUST_A' in tail and 'TURN6' in tail
head = open(P + 'r5_head.py').read()
head = head.replace("S3 = ROOT + 'preview/src5/'   # 第五章素材目录（prep_ch5.py 输出；变量名沿用）", "S3 = ROOT + 'preview/src6/'   # 第六章素材目录（prep_ch6.py 输出；变量名沿用）")
head = head.replace("while s and s[-1] in '，。；、—'", "while s and s[-1] in '，。；：、—'")
assert 'src6' in head and "'，。；：、—'" in head
doc = open(P6 + 'doc6.txt').read()
lines = head.split('\n', 3)
src = '\n'.join(lines[:3]) + '\n' + doc + lines[3] + open(P6 + 'body6.py').read() + open(P + 'r5_help.py').read() + open(P + 'r5_fx.py').read() + open(P6 + 'shots6.py').read() + '\n' + tail
open('/data/luxun90/preview/render_ch6.py', 'w').write(src)

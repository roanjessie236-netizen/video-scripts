# 组装 render_ch7.py：r5_head（改素材目录、分句去尾冒号）+ 说明 + body7 + r5_help + r5_fx + shots7 + r5_tail
P = '/data/luxun90/preview/parts/'; P7 = '/data/luxun90/preview/parts7/'
tail = open(P + 'r5_tail.py').read()
tail = tail.replace("DUSTR = [(t_17, ST['S3-04']), (ST['S4-05'], EN['S4-05'])]", "DUSTR = [DUST_A]   # 街灯光里的浮尘")
tail = tail.replace("print('TOTAL_MAIN', TOTAL_MAIN, 'TURN', round(TURN3, 2), round(TURN4, 2))", "print('TOTAL_MAIN', TOTAL_MAIN)")
assert 'DUST_A' in tail and "print('TOTAL_MAIN', TOTAL_MAIN)" in tail
head = open(P + 'r5_head.py').read()
head = head.replace("S3 = ROOT + 'preview/src5/'   # 第五章素材目录（prep_ch5.py 输出；变量名沿用）", "S3 = ROOT + 'preview/src7/'   # 尾声素材目录（prep_ch7.py 输出，实际在 /tmp/src7；变量名沿用）")
head = head.replace("while s and s[-1] in '，。；、—'", "while s and s[-1] in '，。；：、—'")
assert 'src7' in head and "'，。；：、—'" in head
doc = open(P7 + 'doc7.txt').read()
lines = head.split('\n', 3)
src = '\n'.join(lines[:3]) + '\n' + doc + lines[3] + open(P7 + 'body7.py').read() + open(P + 'r5_help.py').read() + open(P + 'r5_fx.py').read() + open(P7 + 'shots7.py').read() + '\n' + tail
open('/data/luxun90/preview/render_ch7.py', 'w').write(src)

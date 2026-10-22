# 组装 render_ch5.py：r5_head + 说明 + r5_body + r5_help + r5_fx + r5_shots5 + r5_tail（与 2026-10-21 第五章样片所用脚本一致；框架同第六章）
P = '/data/luxun90/preview/parts/'
tail = open(P + 'r5_tail.py').read()
tail = tail.replace("DUSTR = [(t_17, ST['S3-04']), (ST['S4-05'], EN['S4-05'])]", "DUSTR = [(t_29, t_97)]   # “进化的链子”一镜带浮尘")
tail = tail.replace("print('TOTAL_MAIN', TOTAL_MAIN, 'TURN', round(TURN3, 2), round(TURN4, 2))", "print('TOTAL_MAIN', TOTAL_MAIN, 'TURN', round(TURN5, 2))")
assert 'DUSTR = [(t_29' in tail and 'TURN5' in tail
head = open(P + 'r5_head.py').read(); assert 'src5' in head
doc = open(P + 'doc5.txt').read()
lines = head.split('\n', 3)
fx = open(P + 'r5_fx.py').read(); fx = fx if fx.endswith('\n') else fx + '\n'
src = '\n'.join(lines[:3]) + '\n' + doc + lines[3] + open(P + 'r5_body.py').read() + open(P + 'r5_help.py').read() + fx + open(P + 'r5_shots5.py').read() + '\n' + tail
open('/data/luxun90/preview/render_ch5.py', 'w').write(src)

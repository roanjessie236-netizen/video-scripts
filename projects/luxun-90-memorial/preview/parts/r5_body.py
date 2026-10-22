# ---------- 第五章时间线（按紧凑时长直接排；本章从 0 秒起算） ----------
OFF = 607.22   # 第三、四章 r2（332.75 + 274.47）之后，本章在 B站母版中的起点（v2.6 分镜同步）
SEQ = [('S5-01', [{'vo': '1926年8月，他和许广平一同南下。她去广州，他到了厦门大学。他在信里对她说——'}, {'q': 'Q61'}]),
 ('S5-02', [{'vo': '在厦门，他为文集《坟》写了后记。'}, {'q': 'Q30'}, {'q': 'Q29'}, {'q': 'Q97'}]),
 ('S5-03', [{'vo': '1927年1月，他来到“革命策源地”广州，在中山大学任教。'}, {'vo': '4月12日，“清党”从上海开始；4月15日，广州军警搜捕中大学生。他营救无果，愤而辞职。'}, {'q': 'Q53'}]),
 ('S5-04', [{'q': 'Q52', 'txt': '总以为将来必胜于过去，青年必胜于老人'}, {'sil': 1.0}, {'q': 'Q34'}, {'vo': '这一年的杂文，后来编成了《而已集》。题辞写道——'}, {'q': 'Q96'}]),
 ('S5-05', [{'vo': '9月底，他和许广平离开广州。'}, {'vo': '这是他的第五次转身：“青年必胜于老人”的信念碎了，可他没有离开青年——'}, {'q': 'Q54'}])]
EXTRA = {'S5-05': 0.6}   # 章末多留一点
T = 0.0; TURN, ST, EN = {}, {}, {}
for sid, aud in SEQ:
    ST[sid] = T; t = T + LEAD
    for a in aud:
        if 'sil' in a: t += a['sil']; continue
        kind, txt = ('vo', a['vo']) if 'vo' in a else (a['q'], a.get('txt') or Q[a['q']])
        if kind == 'vo' and '转身' in txt and '这是' in txt:   # “这是他的第N次转身……”由转身字卡呈现
            a1, a2 = txt.split('这是', 1)
            if a1: t = SUB(t, 'vo', a1) + GAP
            TURN[sid] = t; t += nchar('这是' + a2) / VR + GAP; continue
        if kind == 'Q52': Q52_T = (t, t + nchar(txt) / QR)   # 这一句不走底部字幕，做成“字幕浮起—碎裂”
        t = SUB(t, kind, txt) + GAP
    T = t - GAP + TAIL + EXTRA.get(sid, 0); EN[sid] = T
TURN5 = TURN['S5-05']
TOTAL_MAIN = round(T, 2); CRED = 7.0; TOTAL = TOTAL_MAIN + CRED
assert 100 < TOTAL_MAIN < 135, TOTAL_MAIN

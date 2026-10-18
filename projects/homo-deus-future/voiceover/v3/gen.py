import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # writes lines.json, vo_starts.srt, bilingual srt, en_overlay.ass next to this file
# i, start, end, subtitle (burned Chinese, unchanged), spoken text (pauses via punctuation), English, rate, pitch, vol, cue
L = [
(1, 2.6, 6.6, '过去，人类最大的梦想，是改变世界。', '过去，人类最大的梦想，是改变世界。', "In the past, humanity's greatest dream was to change the world.", -8, '-2Hz', '+0%', '庄重开篇，像翻开一部史书'),
(2, 8.0, 12.2, '未来，人类可能开始改变自己。', '未来，人类可能，开始改变自己。', 'In the future, humanity may begin to change itself.', -10, '-4Hz', '+0%', '压低声音，留悬念'),
(3, 36.8, 40.6, '人类第一次创造了一种新的智能。', '人类第一次，创造了一种新的智能。', 'For the first time, humans have created a new kind of intelligence.', -5, '+0Hz', '+5%', '惊叹'),
(4, 42.0, 45.6, '它不需要生命，却能够学习。', '它不需要生命，却能够学习。', 'It needs no life, yet it can learn.', -6, '-2Hz', '+0%', '转折，后半句放慢'),
(5, 47.6, 51.6, '智能，正在与意识分道扬镳。', '智能，正在与意识分道扬镳。', 'Intelligence is parting ways with consciousness.', -7, '-3Hz', '+0%', '冷静、深沉'),
(6, 53.0, 57.0, '算法，也许会比你自己更了解你。', '算法，也许会比你自己，更了解你。', 'Algorithms may come to know you better than you know yourself.', -6, '-3Hz', '-5%', '低声，像在耳边提醒'),
(7, 62.8, 68.8, '当机器开始理解世界，人类的位置将发生什么变化？', '当机器开始理解世界，人类的位置，将发生什么变化？', "When machines begin to understand the world, what becomes of humanity's place?", -5, '+2Hz', '+0%', '发问，尾音上扬'),
(8, 78.0, 81.8, '过去，人类接受自然赋予的生命。', '过去，人类接受自然赋予的生命。', 'In the past, humans accepted the life that nature gave them.', -6, '-2Hz', '+0%', '平静叙述'),
(9, 83.4, 87.2, '未来，人类可能开始设计生命。', '未来，人类可能开始设计生命。', 'In the future, humans may begin to design life.', -5, '+0Hz', '+5%', '对比，语气加重'),
(10, 88.8, 93.0, '四十亿年来，生命一直由自然选择塑造。', '四十亿年来，生命一直由自然选择塑造。', 'For four billion years, life has been shaped by natural selection.', -5, '-2Hz', '+0%', '宏大、沉稳'),
(11, 94.4, 98.6, '如今，智能设计开始取代自然选择。', '如今，智能设计，开始取代自然选择。', 'Now, intelligent design is beginning to replace natural selection.', -4, '+2Hz', '+5%', '转折、有力'),
(12, 106.0, 112.6, '疾病、衰老，甚至身体本身，都可能成为可以修改的对象。', '疾病、衰老，甚至身体本身，都可能成为可以修改的对象。', 'Disease, ageing, even the body itself, may all become things we can edit.', -4, '+0Hz', '+0%', '层层递进'),
(13, 114.2, 119.2, '新的人类议程：长生不死、幸福快乐、化身为神。', '新的人类议程：长生不死，幸福快乐，化身为神。', 'A new human agenda: immortality, bliss, and divinity.', -7, '+3Hz', '+8%', '激昂，三个词逐个加重'),
(14, 127.6, 131.6, '身体的边界，正在被重新定义。', '身体的边界，正在被重新定义。', 'The boundaries of the body are being redrawn.', -7, '-2Hz', '+0%', '回落、凝重'),
(15, 140.0, 143.8, '如果意识可以被复制。', '如果，意识可以被复制。', 'If consciousness could be copied,', -8, '-3Hz', '-5%', '轻声假设'),
(16, 145.8, 149.4, '如果记忆可以被保存。', '如果，记忆可以被保存。', 'if memories could be preserved,', -7, '-2Hz', '+0%', '排比，略升'),
(17, 150.0, 154.0, '如果生命可以无限延续。', '如果，生命可以无限延续。', 'if life could go on forever,', -6, '-1Hz', '+5%', '排比，再升'),
(18, 155.2, 160.2, '我们还是原来的自己吗？', '我们，还是原来的自己吗？', 'would we still be who we were?', -12, '-5Hz', '+0%', '停顿后低沉发问'),
(19, 162.4, 167.0, '但还有一个问题：这样的未来，会属于每个人吗？', '但还有一个问题：这样的未来，会属于每个人吗？', 'But one question remains: will such a future belong to everyone?', -4, '+0Hz', '+0%', '转折，冷静'),
(20, 168.6, 174.6, '当算法承担越来越多工作，一些人可能难以在经济体系中重新找到位置。', '当算法承担越来越多工作，一些人可能难以在经济体系中重新找到位置。', 'As algorithms take on more and more work, some people may struggle to find a place in the economy.', 6, '-1Hz', '+0%', '克制、略带忧虑（时间紧，语速稍快）'),
(21, 175.2, 179.4, '赫拉利将这种风险称为“无用阶级”。', '赫拉利将这种风险，称为“无用阶级”。', 'Harari calls this risk "the useless class".', -6, '-2Hz', '+0%', '“无用阶级”放慢'),
(22, 180.8, 184.6, '这里的“无用”，指劳动可能不再被需要，', '这里的“无用”，指劳动可能不再被需要，', '"Useless" here means their labour may no longer be needed,', 3, '+0Hz', '+0%', '解释'),
(23, 184.9, 188.0, '绝不意味着人失去了价值。', '绝不意味着，人失去了价值。', 'never that people have lost their worth.', -6, '+2Hz', '+8%', '坚定、温暖'),
(24, 188.6, 193.4, '如果少数人获得升级生命的能力，更多人却被留在身后，', '如果少数人获得升级生命的能力，更多人却被留在身后，', 'If a few gain the power to upgrade life while many are left behind,', 6, '+0Hz', '+0%', '对比（时间紧，语速稍快）'),
(25, 193.7, 197.6, '技术的进步，将把我们带向怎样的社会？', '技术的进步，将把我们带向怎样的社会？', 'what kind of society will technological progress lead us to?', -3, '-2Hz', '+0%', '沉重发问'),
(26, 198.4, 201.2, '当我们追问人类能成为什么，', '当我们追问人类能成为什么，', 'As we ask what humans can become,', 0, '+0Hz', '+0%', '铺垫'),
(27, 201.5, 205.2, '也必须追问：谁能共享这个未来？', '也必须追问：谁能共享这个未来？', 'we must also ask: who will share this future?', -6, '+2Hz', '+5%', '恳切'),
(28, 212.6, 216.2, '未来最大的挑战。', '未来最大的挑战，', 'The greatest challenge ahead', -8, '-3Hz', '+0%', '沉下来，进入尾声'),
(29, 217.6, 221.6, '不是机器是否会超越人类。', '不是机器，是否会超越人类。', 'is not whether machines will surpass us,', -6, '-1Hz', '+0%', '否定，平稳'),
(30, 223.3, 227.7, '而是当我们拥有创造神的能力。', '而是当我们，拥有创造神的能力，', 'but whether, once we can create gods,', -6, '+2Hz', '+8%', '渐强'),
(31, 229.1, 233.9, '是否仍然知道如何成为人？', '是否仍然知道，如何成为人？', 'we will still know how to be human.', -12, '-4Hz', '+0%', '全片最重的一句：放慢、低沉、留白'),
(32, 236.3, 241.1, '智人，也许正在走向“神人”。', '智人，也许正在走向“神人”。', 'Homo sapiens may be on its way to becoming Homo Deus.', -8, '-2Hz', '+0%', '意味深长'),
(33, 252.9, 257.3, '下一章人类历史。', '下一章人类历史，', 'The next chapter of human history', -15, '-4Hz', '+0%', '片尾字幕，极慢'),
(34, 257.7, 262.3, '正在等待我们书写。', '正在等待我们书写。', 'is waiting for us to write.', -15, '-5Hz', '+0%', '尾音落在音乐里'),
]
assert len(L) == 34

def fts(t):
    ms = int(round(t * 1000))
    return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)

def ats(t):
    cs = int(round(t * 100))
    return '%d:%02d:%02d.%02d' % (cs // 360000, cs // 6000 % 60, cs // 100 % 60, cs % 100)

json.dump([dict(i=i, s=s, e=e, t=t, sub=sub, en=en, rate=r, pitch=p, vol=v, cue=c) for i, s, e, sub, t, en, r, p, v, c in L],
          open('lines.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
with open('vo_starts.srt', 'w', encoding='utf-8') as f:
    for i, s, e, sub, *_ in L:
        f.write('%d\n%s --> %s\n%s\n\n' % (i, fts(s), fts(e), sub))
with open('homo_deus_v3_subtitles_bilingual.srt', 'w', encoding='utf-8') as f:
    for i, s, e, sub, t, en, *_ in L:
        f.write('%d\n%s --> %s\n%s\n%s\n\n' % (i, fts(s), fts(e), sub, en))

# English-only overlay, burned under the existing Chinese lines.
# Chinese subtitles: centre (1280, H-150=1290), Noto Serif CJK Medium 56 -> English centre y=1360.
# Closing captions (#33-34): centre (1280, 0.27H=389), Light 92 -> English centre y=478.
head = '''[Script Info]
ScriptType: v4.00+
PlayResX: 2560
PlayResY: 1440
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EN,Noto Serif CJK SC,39,&H00F4ECE4,&H00F4ECE4,&HA0140C08,&H78000000,0,0,0,0,100,100,1.5,0,1,1.4,2.4,5,0,0,0,1
Style: ENCAP,Noto Serif CJK SC,46,&H00FAF2EE,&H00FAF2EE,&H00000000,&H78000000,0,1,0,0,100,100,4,0,1,0,2.5,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
with open('en_overlay.ass', 'w', encoding='utf-8') as f:
    f.write(head)
    for i, s, e, sub, t, en, *_ in L:
        if i >= 33:
            f.write('Dialogue: 0,%s,%s,ENCAP,,0,0,0,,{\\an5\\pos(1280,478)\\fad(600,600)}%s\n' % (ats(s + 0.15), ats(e), en))
        else:
            f.write('Dialogue: 0,%s,%s,EN,,0,0,0,,{\\an5\\pos(1280,1360)\\fad(300,300)}%s\n' % (ats(s), ats(e), en))
print('ok', len(L))

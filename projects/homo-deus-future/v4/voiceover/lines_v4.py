#!/usr/bin/env python3
"""《未来简史》v4 narration — single source of truth for the voice-over, subtitles and English.
Fields: i, sec, kind ('sub' = bottom subtitle, 'cap' = large caption, '/' = line break inside a caption), sub (burned Chinese; '|' = split into two
subtitle lines, timed from the WordBoundary of the spoken take), t (spoken text, pauses via punctuation),
en (English; '|' matches the Chinese split), rate %, pitch, vol, cue, src ('brief' = kept from v2, 'book' = new, from Homo Deus).
Voice rules = Sapiens v2 / 21 Lessons: zh-CN-YunjianNeural, one edge-tts call per sentence, rate -4..-8 (heavy -10..-12,
closing captions -15), VO-first: the edit is laid out on the measured takes, nothing is sped up to fit a slot."""
import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
L = [
# ---- 序
(1, 0, 'sub', '过去，人类最大的梦想，是改变世界。', None, "In the past, humanity's greatest dream was to change the world.", -8, '-2Hz', '+0%', '庄重开篇', 'brief'),
(2, 0, 'sub', '未来，人类可能开始改变自己。', '未来，人类可能，开始改变自己。', 'In the future, humanity may begin to change itself.', -10, '-4Hz', '+0%', '压低，留悬念', 'brief'),
# ---- 第一章 新的人类议程
(3, 1, 'sub', '几千年来，饥荒、瘟疫和战争，一直是人类最大的三个敌人。', None, "For thousands of years, famine, plague and war were humanity's three greatest enemies.", -6, '-3Hz', '+0%', '沉重，像在讲一部苦难史', 'book'),
(4, 1, 'sub', '而今天，死于吃得太多的人，比死于吃得太少的人还多；', None, 'Today, more people die from eating too much than from eating too little;', -4, '+0Hz', '+3%', '转折，略带讽刺', 'book'),
(5, 1, 'sub', '死于衰老的人，比死于传染病的人还多；', None, 'more die of old age than of infectious disease;', -4, '+0Hz', '+3%', '递进', 'book'),
(6, 1, 'sub', '自杀的人，比死于士兵、恐怖分子和罪犯之手的人加起来还多。', None, 'and more people take their own lives than are killed by soldiers, terrorists and criminals combined.', -4, '-1Hz', '+0%', '递进，收住', 'book'),
(7, 1, 'cap', '如今，糖比火药更危险。', None, 'Sugar is now more dangerous than gunpowder.', -8, '-2Hz', '+5%', '冷峻的一记', 'book'),
(8, 1, 'sub', '当旧的威胁退去，人类开始为自己设定新的目标：', None, 'As the old threats recede, humanity is setting itself new goals:', -5, '+0Hz', '+0%', '铺垫，向上', 'book'),
(9, 1, 'sub', '长生不死、幸福快乐、化身为神。', '长生不死，幸福快乐，化身为神。', 'immortality, bliss and divinity.', -8, '+3Hz', '+8%', '激昂，三个词逐个加重', 'brief'),
# ---- 第二章 生命重塑
(10, 2, 'sub', '过去，人类接受自然赋予的生命。', None, 'In the past, humans accepted the life that nature gave them.', -6, '-2Hz', '+0%', '平静叙述', 'brief'),
(11, 2, 'sub', '未来，人类可能开始设计生命。', None, 'In the future, humans may begin to design life.', -5, '+0Hz', '+5%', '对比，语气加重', 'brief'),
(12, 2, 'sub', '赫拉利设想了三条“升级”之路：', '赫拉利设想了三条，升级之路：', 'Harari sees three paths to "upgrading" ourselves:', -5, '+0Hz', '+0%', '解释', 'book'),
(13, 2, 'sub', '改写基因，与机器融合，创造非有机的生命。', None, 'rewriting our genes, merging with machines, creating non-organic life.', -5, '+2Hz', '+5%', '三拍，逐个推进', 'book'),
(14, 2, 'sub', '疾病、衰老，甚至身体本身，都可能成为可以修改的对象。', None, 'Disease, ageing, even the body itself, may all become things we can edit.', -4, '+0Hz', '+0%', '层层递进', 'brief'),
(15, 2, 'sub', '如果意识可以被复制，', '如果，意识可以被复制，', 'If consciousness could be copied,', -6, '-3Hz', '-5%', '轻声假设', 'brief'),
(16, 2, 'sub', '如果记忆可以被保存，', '如果，记忆可以被保存，', 'if memories could be preserved,', -5, '-2Hz', '+0%', '排比，略升', 'brief'),
(17, 2, 'sub', '如果生命可以无限延续，', '如果，生命可以无限延续，', 'if life could go on forever,', -4, '-1Hz', '+5%', '排比，再升', 'brief'),
(18, 2, 'sub', '我们还是原来的自己吗？', '我们，还是原来的自己吗？', 'would we still be who we were?', -12, '-5Hz', '+0%', '停顿后低沉发问', 'brief'),
# ---- 第三章 智能革命
(19, 3, 'sub', '人类第一次创造了一种新的智能。', '人类第一次，创造了一种新的智能。', 'For the first time, humans have created a new kind of intelligence.', -5, '+0Hz', '+5%', '惊叹', 'brief'),
(20, 3, 'sub', '它不需要生命，却能够学习。', None, 'It needs no life, yet it can learn.', -6, '-2Hz', '+0%', '转折', 'brief'),
(21, 3, 'sub', '智能，正在与意识分道扬镳。', None, 'Intelligence is decoupling from consciousness.', -7, '-3Hz', '+0%', '冷静、深沉', 'brief'),
(22, 3, 'sub', '而生命科学告诉我们：|生物本身就是算法，生命就是数据处理。', None, 'And the life sciences tell us:|organisms are algorithms, and life is data processing.', -5, '-1Hz', '+0%', '冷峻地陈述结论', 'book'),
(23, 3, 'sub', '几百年来，人文主义告诉我们：倾听你自己。', None, 'For centuries, humanism has told us: listen to yourself.', -6, '+0Hz', '+0%', '温和、笃定', 'book'),
(24, 3, 'sub', '可当算法比你自己更了解你，', None, 'But when algorithms know you better than you know yourself,', -5, '-2Hz', '-3%', '低声，像在耳边提醒', 'brief'),
(25, 3, 'sub', '从走哪条路、读哪本书，到和谁共度一生，', None, 'from the road you take and the books you read to the person you marry,', -3, '+0Hz', '+0%', '列举，节奏加快', 'book'),
(26, 3, 'sub', '权威，就会从人类转移到算法手中。', None, 'authority will shift from humans to algorithms.', -7, '-2Hz', '+5%', '落锤', 'book'),
(27, 3, 'sub', '当机器开始理解世界，人类的位置将发生什么变化？', '当机器开始理解世界，人类的位置，将发生什么变化？', "When machines begin to understand the world, what becomes of humanity's place?", -5, '+2Hz', '+0%', '发问，尾音上扬', 'brief'),
(28, 3, 'sub', '但还有一个问题：这样的未来，会属于每个人吗？', None, 'But one question remains: will such a future belong to everyone?', -4, '+0Hz', '+0%', '转折，冷静', 'brief'),
(29, 3, 'sub', '当算法承担越来越多工作，|一些人可能难以在经济体系中重新找到位置。', None, 'As algorithms take on more and more work,|some people may struggle to find a place in the economy.', -3, '-1Hz', '+0%', '克制、略带忧虑', 'brief'),
(30, 3, 'sub', '赫拉利将这种风险称为“无用阶级”。', '赫拉利将这种风险，称为“无用阶级”。', 'Harari calls this risk "the useless class".', -6, '-2Hz', '+0%', '“无用阶级”放慢', 'brief'),
(31, 3, 'sub', '这里的“无用”，指劳动可能不再被需要，|绝不意味着人失去了价值。', None, '"Useless" here means their labour may no longer be needed,|never that people have lost their worth.', -4, '+1Hz', '+3%', '解释，后半句坚定温暖', 'brief'),
(32, 3, 'sub', '如果少数人获得升级生命的能力，更多人却被留在身后，', None, 'If a few gain the power to upgrade life while many are left behind,', -3, '+0Hz', '+0%', '对比', 'brief'),
(33, 3, 'sub', '人类可能第一次在生物学意义上，分裂成不同的阶层。', '人类，可能第一次在生物学意义上，分裂成不同的阶层。', 'humankind may, for the first time, split into biological castes.', -6, '-2Hz', '+0%', '沉重', 'book'),
(34, 3, 'sub', '当我们追问人类能成为什么，|也必须追问：谁能共享这个未来？', None, 'As we ask what humans can become,|we must also ask: who will share this future?', -5, '+2Hz', '+5%', '恳切', 'brief'),
# ---- 第四章 人类的新纪元
(35, 4, 'sub', '与此同时，一种新的信仰正在兴起：数据主义。', None, 'Meanwhile, a new creed is rising: Dataism.', -6, '-2Hz', '+0%', '神秘、冷', 'book'),
(36, 4, 'sub', '它相信，宇宙由数据流构成；|万物的价值，取决于它对数据处理的贡献。', None, 'It holds that the universe consists of data flows,|and the value of anything lies in its contribution to data processing.', -4, '-1Hz', '+0%', '平静陈述', 'book'),
(37, 4, 'sub', '在这张巨网里，智人也许只是一个正在过时的算法。', None, 'In this vast web, Homo sapiens may be just an obsolete algorithm.', -6, '-3Hz', '+0%', '冷峻', 'book'),
(38, 4, 'sub', '未来最大的挑战，不是机器是否会超越人类，', None, 'The greatest challenge ahead is not whether machines will surpass us,', -7, '-3Hz', '+0%', '沉下来', 'brief'),
(39, 4, 'sub', '而是当我们拥有创造神的能力，', '而是当我们，拥有创造神的能力，', 'but whether, once we can create gods,', -6, '+2Hz', '+8%', '渐强', 'brief'),
(40, 4, 'cap', '是否仍然知道如何成为人？', '是否仍然知道，如何成为人？', 'will we still know how to be human?', -12, '-4Hz', '+0%', '全片最重的一句：放慢、低沉、留白', 'brief'),
(41, 4, 'sub', '智人，也许正在走向“神人”。', None, 'Homo sapiens may be on its way to becoming Homo Deus.', -8, '-2Hz', '+0%', '意味深长', 'brief'),
# ---- 尾声
(42, 5, 'sub', '这不是预言，而是可能。', None, 'These are not prophecies, but possibilities.', -8, '-2Hz', '+0%', '平静', 'book'),
(43, 5, 'sub', '赫拉利在书的最后，留下了三个问题：', None, 'At the end of the book, Harari leaves us three questions:', -6, '+0Hz', '+0%', '引出', 'book'),
(44, 5, 'cap', '生物真的只是算法吗？', None, 'Are organisms really just algorithms?', -10, '-2Hz', '+0%', '慢，留白', 'book'),
(45, 5, 'cap', '智能与意识，哪一个更有价值？', None, 'Which is more valuable: intelligence or consciousness?', -10, '-2Hz', '+0%', '慢，留白', 'book'),
(46, 5, 'cap', '当算法比我们更了解自己，/生活会变成什么样？', '当算法比我们更了解自己，生活会变成什么样？', 'What happens when algorithms know us better than we know ourselves?', -10, '-1Hz', '+0%', '慢，留白', 'book'),
(47, 5, 'cap', '下一章人类历史，', '下一章人类历史，', 'The next chapter of human history', -15, '-4Hz', '+0%', '片尾，极慢', 'brief'),
(48, 5, 'cap', '正在等待我们书写。', None, 'is waiting for us to write.', -15, '-5Hz', '+0%', '尾音落在音乐里', 'brief'),
]
out = []
for i, sec, kind, sub, t, en, r, p, v, cue, src in L:
    spoken = t if t else sub.replace('|', '').replace('/', '')
    assert sub.count('|') == en.count('|'), i
    out.append(dict(i=i, sec=sec, kind=kind, sub=sub, t=spoken, en=en, rate=r, pitch=p, vol=v, cue=cue, src=src, s=i * 10.0))
json.dump(out, open('lines.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
import re
n = sum(len(re.sub(r'[，。、：；？！“”|/\s]', '', x['sub'])) for x in out)
print(len(out), 'lines', n, 'chars;', sum(x['src'] == 'book' for x in out), 'new from the book')

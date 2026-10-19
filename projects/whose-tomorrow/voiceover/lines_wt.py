#!/usr/bin/env python3
"""《明天属于谁》narration — single source of truth for voice-over, subtitles and English.
Fields as Homo Deus v4 lines_v4.py: i, sec, kind ('sub' bottom subtitle | 'cap' large caption, '/' = caption line break),
sub (burned Chinese; '|' = split into two subtitles), t (spoken text; None = sub without '|' '/'), en, rate %, cue, src.
Voice = the trilogy's voice: zh-CN-YunjianNeural, one edge-tts call per sentence, pitch -2 Hz, rate -6 % (captions slower)."""
import json, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
L = [
# ---- 序
(1, 0, 'sub', '1930年，经济学家凯恩斯写下一个预言：', '一九三零年，经济学家凯恩斯写下一个预言：', 'In 1930, the economist John Maynard Keynes made a prediction:', -4, '娓娓道来', 'keynes'),
(2, 0, 'sub', '百年之后，机器将承担大部分工作，人们每周只需工作十五小时。', None, 'a century on, machines would do most of the work, and people would need to work just fifteen hours a week.', -4, '', 'keynes'),
(3, 0, 'sub', '一百年快到了，机器越来越能干，', None, 'The century is nearly up, and machines have indeed grown ever more capable,', -4, '', ''),
(4, 0, 'sub', '我们却并没有因此变得轻松。', None, 'yet we are no more at ease.', -4, '转折', ''),
(5, 0, 'cap', '当机器能生产一切，/财富该属于谁？', '当机器能生产一切，财富，该属于谁？', 'When machines can produce everything, who should the wealth belong to?', -9, '全片的问题', 'pdf'),
# ---- 第一章 磨坊与社会
(6, 1, 'sub', '回望七万年，人类的每一次飞跃，都伴随着劳动方式的巨变。', None, 'Looking back over seventy thousand years, every leap humankind made came with a great change in the way we work.', -4, '', 'sapiens'),
(7, 1, 'sub', '认知革命，让智人学会用故事组织大规模的协作。', None, 'The Cognitive Revolution taught Sapiens to organise hundreds, even thousands, through shared stories.', -4, '', 'sapiens'),
(8, 1, 'sub', '农业革命带来了剩余的粮食，', None, 'The Agricultural Revolution brought surplus grain,', -4, '', 'sapiens'),
(9, 1, 'sub', '也带来了粮仓、私有财产、阶级和国家。', None, 'and with it granaries, private property, classes and the state.', -4, '列举', 'sapiens'),
(10, 1, 'sub', '工业革命用蒸汽取代了肌肉，', None, 'The Industrial Revolution replaced muscle with steam,', -4, '', 'sapiens'),
(11, 1, 'sub', '也把千百万农民变成了工厂里的雇佣工人。', None, 'and turned millions of peasants into wage workers in factories.', -4, '', 'sapiens'),
(12, 1, 'cap', '手推磨产生的是封建主的社会，/蒸汽磨产生的是工业资本家的社会。', '马克思说：手推磨产生的是封建主的社会，蒸汽磨产生的是工业资本家的社会。', 'The hand-mill gives you society with the feudal lord; the steam-mill, society with the industrial capitalist.', -7, '引文', 'marx'),
(13, 1, 'sub', '生产力变了，生产关系迟早也要跟着改变。', None, 'When the forces of production change, the relations of production must sooner or later follow.', -4, '', 'marx'),
(14, 1, 'sub', '赫拉利说，人类靠共同相信的故事团结在一起；', None, 'Harari says humans are bound together by the stories they share;', -4, '', 'sapiens'),
(15, 1, 'sub', '历史唯物主义还要追问：故事的背后，是谁在劳动，谁在占有？', None, 'historical materialism asks further: behind the stories, who does the work, and who owns the wealth?', -4, '追问', 'marx'),
# ---- 第二章 新的蒸汽机
(16, 2, 'sub', '今天，一台新的“蒸汽机”正在轰鸣。', '今天，一台新的蒸汽机，正在轰鸣。', 'Today, a new "steam engine" is roaring to life.', -4, '', '21'),
(17, 2, 'sub', '人工智能像电力一样，是一种通用技术，会渗入每个行业。', None, 'Like electricity, AI is a general-purpose technology; it will seep into every industry.', -4, '', 'pdf'),
(18, 2, 'sub', '这一次，最先被冲击的不是工厂，而是写字楼。', None, 'This time, the first to be hit is not the factory, but the office tower.', -4, '', 'pdf'),
(19, 2, 'sub', '历史上，技术总在消灭旧岗位的同时，创造出新岗位。', None, 'Throughout history, technology has created new jobs even as it destroyed old ones.', -4, '', 'pdf'),
(20, 2, 'sub', '预测显示，到2030年，全球将新增1.7亿个岗位，减少9200万个。', '预测显示，到二零三零年，全球将新增一亿七千万个岗位，减少九千二百万个。', 'One forecast says that by 2030 the world will gain 170 million jobs and lose 92 million.', -4, '', 'pdf'),
(21, 2, 'sub', '而就连体力劳动这条最后的退路，', None, 'And even the last refuge, manual work,', -4, '', 'pdf'),
(22, 2, 'sub', '也随着具身智能走进仓库、工地和厨房，正在慢慢收窄。', None, 'is narrowing, as embodied AI moves into warehouses, building sites and kitchens.', -4, '', 'pdf'),
# ---- 第三章 丰裕的悖论
(23, 3, 'sub', '《未来简史》担心，21世纪会出现一个庞大的“无用阶级”。', '未来简史担心，二十一世纪会出现一个庞大的无用阶级。', 'Homo Deus fears the twenty-first century may create a vast "useless class".', -4, '', 'deus'),
(24, 3, 'sub', '可真正的危险，不是人没用了，', None, 'But the real danger is not that people become useless;', -4, '', 'pdf'),
(25, 3, 'sub', '而是财富堆积如山，多数人却失去了收入。', None, 'it is that wealth piles up like mountains, while most people lose their income.', -4, '', 'pdf'),
(26, 3, 'sub', '问题，从“还有没有工作”，变成了“财富如何分配”。', '问题，从还有没有工作，变成了财富如何分配。', 'The question shifts from "Will there be work?" to "How will the wealth be shared?"', -4, '', 'pdf'),
(27, 3, 'sub', '这正是历史唯物主义揭示的矛盾：|生产力一路飞奔，生产关系却原地踏步。', None, 'This is the contradiction historical materialism reveals:|the forces of production race ahead, while the relations of production stand still.', -4, '', 'marx'),
(28, 3, 'sub', '有人想踩刹车：两百年前，卢德派砸毁了织布机；', None, "Some have tried to slam on the brakes: two hundred years ago, the Luddites smashed the looms;", -4, '', 'pdf'),
(29, 3, 'sub', '明清两代的海禁，也曾锁住港口。', None, 'the sea bans of the Ming and Qing dynasties once locked the ports.', -4, '', 'pdf'),
(30, 3, 'sub', '可技术的洪流，从来挡不住。', None, 'But the flood of technology has never been held back.', -4, '', 'pdf'),
(31, 3, 'sub', '我们能决定的，是修建怎样的堤坝，让水流向哪里。', None, 'What we can decide is what kind of channels to build, and where the water will flow.', -4, '', 'pdf'),
# ---- 第四章 三种明天
(32, 4, 'sub', '摆在我们面前的，是三种明天。', None, 'Before us lie three tomorrows.', -4, '', 'pdf'),
(33, 4, 'sub', '第一种：算力和数据，集中在少数人手中。', None, 'In the first, computing power and data are concentrated in a few hands.', -4, '', 'pdf'),
(34, 4, 'sub', '《今日简史》早就警告过：谁拥有数据，谁就拥有未来。', '今日简史早就警告过：谁拥有数据，谁就拥有未来。', '21 Lessons warned long ago: whoever owns the data owns the future.', -4, '', '21'),
(35, 4, 'sub', '少数人成了云端的领主，其余的人得到的是施舍，而不是权利。', None, 'A few become lords of the cloud; everyone else receives charity, not rights.', -4, '', 'pdf'),
(36, 4, 'sub', '第二种：发点补贴，征点税，让旧秩序修修补补地维持下去。', None, 'In the second, a little welfare, a little tax, and the old order is patched up and kept running.', -4, '', 'pdf'),
(37, 4, 'sub', '第三种：让每一个人，都成为机器的共同主人。', None, 'In the third, every one of us becomes a co-owner of the machines.', -4, '加重，转暖', 'pdf'),
(38, 4, 'sub', 'AI创造的财富，通过公共基金、全民分红和更短的工时，回到每个人手里。', '人工智能创造的财富，通过公共基金、全民分红和更短的工时，回到每个人手里。', "The wealth AI creates flows back to everyone, through public funds, citizens' dividends and shorter working hours.", -4, '', 'pdf'),
(39, 4, 'sub', '劳动不再只是谋生的手段，人们可以去创造、学习、照顾彼此。', None, 'Work is no longer merely a means of survival; people are free to create, to learn, and to care for one another.', -4, '温暖', 'marx'),
(40, 4, 'cap', '每个人的自由发展，/是一切人的自由发展的条件。', '在马克思设想的联合体里，每个人的自由发展，是一切人的自由发展的条件。', 'The free development of each is the condition for the free development of all.', -7, '引文', 'marx'),
# ---- 尾声
(41, 5, 'sub', '但这样的明天，不会自动到来。', None, 'But such a tomorrow will not arrive on its own.', -4, '沉下来', ''),
(42, 5, 'sub', '八小时工作制，是工人们一次次走上街头争取来的；', None, 'The eight-hour day was won by workers taking to the streets, again and again;', -4, '', 'pdf'),
(43, 5, 'cap', '技术决定可能性，/制度决定结果。', '技术决定可能性，制度决定结果。', 'Technology decides what is possible; institutions decide what happens.', -8, '核心结论', 'pdf'),
(44, 5, 'sub', '而制度，由人选择，靠人争取。', None, 'And institutions are chosen by people, and won by people.', -4, '', ''),
(45, 5, 'sub', '马克思说：人们自己创造自己的历史。', None, 'As Marx wrote, people make their own history.', -4, '', 'marx'),
(46, 5, 'cap', '明天属于谁？', '那么，明天属于谁？', 'So, whose tomorrow is it?', -9, '片名回扣', ''),
(47, 5, 'cap', '属于每一个/为它共同奋斗的人。', '属于每一个为它共同奋斗的人。', 'It belongs to everyone who strives for it, together.', -9, '尾音落在音乐里', ''),
]
out = []
for i, sec, kind, sub, t, en, r, cue, src in L:
    spoken = t if t else sub.replace('|', '').replace('/', '')
    assert sub.count('|') == en.count('|'), i
    out.append(dict(i=i, sec=sec, kind=kind, sub=sub, t=spoken, en=en, rate=r, pitch='-2Hz', vol='+0%', cue=cue, src=src, s=i * 10.0))
json.dump(out, open('lines.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
n = sum(len(re.sub(r'[，。、：；？！“”《》|/\s]', '', x['t'])) for x in out)
print(len(out), 'lines', n, 'spoken chars ~ %.0f s at 4.48 c/s' % (n / 4.48))

# 《今日简史：AI时代，人类如何重新定义自己》素材需求表（v1）

> 片长 3:43（223.0s）· 16:9 · 2560×1440 · 24fps · 56 个镜头（S001–S056）· 43 条字幕
> 灵感来自尤瓦尔·赫拉利《今日简史》中关于就业、终身学习与认识自我的讨论

## 分工与编号规则

- 脚本、剪辑、调色、字幕、配乐：剪辑端（Notion AI）
- 生成图片、搜集网络素材：素材端（GPT）
- 编号 S001–S056 固定，不改号、不合并、不挪用。素材按编号交付，剪辑按编号套用
- 缺失或不合格的素材写入 `reorder.md` 补单，保留原编号；返修文件命名 `S0xx_r1.jpg`、`S0xx_r2.jpg`

## 通用规格

- 画幅 16:9。生成图片 ≥2560×1440，建议 3840×2160（剪辑端会做 1.05–1.3 倍虚拟推拉摇移，需要余量）
- 网络视频 ≥1920×1080（建议 4K），长度 ≥ 镜头时长 + 2 秒（前后各 1 秒用于叠化），无水印；网络图片宽度 ≥2560
- 格式：图片 JPG（质量 ≥90）或 PNG；视频 MP4（H.264 / H.265），24 / 25 / 30fps 均可
- 画面中不得出现可读文字、伪文字、Logo、水印、品牌标识、名人肖像；所有人物均为成年人
- 未来科技场景作为“想象”呈现：真实质感，但不伪装成新闻实拍
- 主体放在画面中部 80% 以内，四边各留约 10% 可裁切余量

## 字幕留白代码

- **A 底部字幕区**：画面下方 22%（1440 高度中 y ≥ 1120）保持较暗、干净、低细节，不放人脸、手、关键物体或强光源。**所有镜头默认要求 A**
- **B 中央标题区**：画面中央约 60%×30% 为暗部或负空间，用于片名、章节卡、片尾卡
- **C 时间轴区**：画面下方 35% 干净，S008–S010 叠加“机械计算—互联网—人工智能”时间轴动画
- 字幕样式（剪辑端执行）：Noto Serif CJK，白字加柔和阴影，单行居中，底边距约 120px；每条 ≥2 秒；关键问题后留 1.5–3.5 秒空白，不快速堆叠

## 素材类型

- 【生成】由 GPT 生成图片
- 【网络】网络实拍视频或照片，需记录来源与授权（见 `gpt_brief.md`）
- 【生成/网络】两者皆可，写在前面的优先；【网络/生成】同理
- 时间轴、片名、章节卡、字幕、光效、粒子、转场由剪辑端制作，不需要素材

## 统一风格后缀（生成图片时附在每条提示词后）

```
cinematic documentary still, photorealistic, shot on ARRI Alexa with anamorphic lens, 16:9, natural film grain, BBC documentary realism, volumetric light, epic civilisation scale, keep the bottom fifth of the frame dark and uncluttered, no text, no letters, no logos, no watermark
```

## 固定角色（多镜头保持同一外观）

- **劳动者**：约 50 岁东亚男性，花白短发，藏青色工装外套 — S023、S025、S026、S027
- **画家**：约 40 岁东亚女性，齐耳短发，亚麻围裙 — S037、S038、S039、S040
- **宇航员**：白色舱外航天服，金色面罩，无任何标志或国旗 — S050、S052、S055

## 色彩与音乐

| 段落 | 时间 | 色调 | 音乐 |
|---|---|---|---|
| 开场 · 文明转折 | 0:00–0:23 | 火光暖橙 → 冷灰 → 深蓝 | 低沉电子氛围；“思考。”处抽空 |
| 第一章 · 智能的诞生 | 0:23–1:01 | 深蓝、科技蓝 | 电子脉冲加入节奏，弦乐渐入 |
| 第二章 · 工作的重新定义 | 1:01–1:45 | 冷灰蓝，后段渐入暖光 | 节奏 + 交响层次；“无用阶级”处回落 |
| 第三章 · 创造力属于谁？ | 1:45–2:36 | 暖白、金色 | 机械声融入大提琴 / 钢琴独奏，停顿留白 |
| 第四章 · AI时代的人类答案 | 2:36–3:43 | 金色晨光 → 宇宙蓝 | 独奏扩展为管弦乐；2:56.6 回落；3:15 管弦乐 + 克制合唱高潮；3:32 起余韵 |

## 片名、章节卡与片尾（剪辑端制作）

- 片名卡 0:18.8–0:22.8（S007）：今日简史 / AI时代，人类如何重新定义自己
- 第一章「智能的诞生」0:23.4–0:27.4（S008）
- 第二章「工作的重新定义」1:01.4–1:05.6（S018）
- 第三章「创造力属于谁？」1:45.4–1:49.6（S029）
- 第四章「AI时代的人类答案」2:36.4–2:40.6（S041）
- 片尾卡 3:40.0–3:43.0（S056）：今日简史 · 灵感来自尤瓦尔·赫拉利《今日简史》

## 镜头总览

| 编号 | 时间码 | 时长 | 内容 | 素材 | 留白 |
|---|---|---|---|---|---|
| S001 | 0:00.0–0:03.6 | 3.6s | 火光 | 网络/生成 | A |
| S002 | 0:03.6–0:07.2 | 3.6s | 古代文字 | 网络/生成 | A |
| S003 | 0:07.2–0:10.8 | 3.6s | 工业机器 | 网络/生成 | A |
| S004 | 0:10.8–0:13.4 | 2.6s | 芯片 | 网络/生成 | A |
| S005 | 0:13.4–0:15.8 | 2.4s | 黑暗中屏幕亮起 | 生成 | A |
| S006 | 0:15.8–0:18.4 | 2.6s | 穿过服务器 | 生成/网络 | A |
| S007 | 0:18.4–0:23.0 | 4.6s | 庞大数据中心（片名） | 生成 | A+B |
| S008 | 0:23.0–0:27.6 | 4.6s | 机械计算机（章节卡） | 网络/生成 | A+B+C |
| S009 | 0:27.6–0:31.4 | 3.8s | 互联网 | 生成/网络 | A+C |
| S010 | 0:31.4–0:35.4 | 4.0s | 人工智能 | 生成 | A+C |
| S011 | 0:35.4–0:40.4 | 5.0s | 神经网络如星系 | 生成 | A |
| S012 | 0:40.4–0:44.4 | 4.0s | 网络连接实验室、医院与城市 | 生成 | A |
| S013 | 0:44.4–0:47.6 | 3.2s | AI辅助设计 | 生成 | A |
| S014 | 0:47.6–0:50.8 | 3.2s | AI科学研究 | 生成 | A |
| S015 | 0:50.8–0:53.8 | 3.0s | 图像生成 | 生成 | A |
| S016 | 0:53.8–0:57.4 | 3.6s | 机器人工作 | 生成/网络 | A |
| S017 | 0:57.4–1:01.0 | 3.6s | 数据网络化为生产线 | 生成 | A |
| S018 | 1:01.0–1:06.0 | 5.0s | 传统流水线（章节卡） | 网络/生成 | A+B |
| S019 | 1:06.0–1:09.6 | 3.6s | 自动化工厂 | 生成/网络 | A |
| S020 | 1:09.6–1:12.4 | 2.8s | 医生与AI | 生成 | A |
| S021 | 1:12.4–1:15.0 | 2.6s | 设计师与AI | 生成 | A |
| S022 | 1:15.0–1:17.6 | 2.6s | 科学家与AI | 生成 | A |
| S023 | 1:17.6–1:22.0 | 4.4s | 劳动者隔窗看机器 | 生成 | A |
| S024 | 1:22.0–1:26.2 | 4.2s | 人群中的普通人 | 生成 | A |
| S025 | 1:26.2–1:31.6 | 5.4s | 劳动者面部特写 | 生成 | A |
| S026 | 1:31.6–1:35.2 | 3.6s | 学习新技能 | 生成 | A |
| S027 | 1:35.2–1:39.0 | 3.8s | 重新进入工作场景 | 生成 | A |
| S028 | 1:39.0–1:45.0 | 6.0s | 夜里凝视设计图 | 生成 | A |
| S029 | 1:45.0–1:49.6 | 4.6s | 设计图化为画作（章节卡） | 生成 | A+B |
| S030 | 1:49.6–1:53.0 | 3.4s | AI写诗 | 生成 | A |
| S031 | 1:53.0–1:56.0 | 3.0s | AI绘画 | 生成 | A |
| S032 | 1:56.0–2:00.0 | 4.0s | AI电影画面与音乐 | 生成 | A |
| S033 | 2:00.0–2:05.0 | 5.0s | 大提琴家演奏 | 网络/生成 | A |
| S034 | 2:05.0–2:08.4 | 3.4s | 画家落笔（停顿） | 网络/生成 | A |
| S035 | 2:08.4–2:12.4 | 4.0s | 科学家凝望实验结果 | 生成 | A |
| S036 | 2:12.4–2:17.4 | 5.0s | 钢琴家的手与眼睛 | 网络/生成 | A |
| S037 | 2:17.4–2:22.4 | 5.0s | 画家凝视画布 | 生成 | A |
| S038 | 2:22.4–2:27.6 | 5.2s | 画家借助AI完善作品 | 生成 | A |
| S039 | 2:27.6–2:31.8 | 4.2s | 画家停下思考 | 生成 | A |
| S040 | 2:31.8–2:36.0 | 4.2s | 亲手完成最后一笔 | 生成 | A |
| S041 | 2:36.0–2:40.6 | 4.6s | 宇宙中的地球（章节卡） | 网络/生成 | A+B |
| S042 | 2:40.6–2:45.0 | 4.4s | 未来城市亮起 | 生成 | A |
| S043 | 2:45.0–2:49.2 | 4.2s | 巨型能源设施 | 生成 | A |
| S044 | 2:49.2–2:53.2 | 4.0s | 穿过云层 | 网络/生成 | A |
| S045 | 2:53.2–2:57.6 | 4.4s | 空间站 | 生成 | A |
| S046 | 2:57.6–3:02.2 | 4.6s | 科研人员合作 | 生成/网络 | A |
| S047 | 3:02.2–3:06.2 | 4.0s | 月球基地 | 生成 | A |
| S048 | 3:06.2–3:10.2 | 4.0s | 医护照护病人 | 生成/网络 | A |
| S049 | 3:10.2–3:15.0 | 4.8s | 深空探索 | 生成 | A |
| S050 | 3:15.0–3:19.2 | 4.2s | 宇航员舱外移动 | 生成 | A |
| S051 | 3:19.2–3:22.2 | 3.0s | 地面工程师抬头 | 生成 | A |
| S052 | 3:22.2–3:25.0 | 2.8s | 头盔映出地球 | 生成 | A |
| S053 | 3:25.0–3:28.0 | 3.0s | 握住患者的手 | 生成/网络 | A |
| S054 | 3:28.0–3:31.0 | 3.0s | 人们相拥 | 生成/网络 | A |
| S055 | 3:31.0–3:36.4 | 5.4s | 越过宇航员拉远 | 生成 | A |
| S056 | 3:36.4–3:43.0 | 6.6s | 晨昏线与第一缕阳光（片尾） | 网络/生成 | A+B |

---

## 开场 · 文明转折（0:00.0–0:23.0）

### S001 火光
- 时间 0:00.0–0:03.6 · 时长 3.6s · 画幅 16:9
- 旁白 / 字幕：“火，改变了我们的生存。”（0:00.6–0:03.4）
- 画面：漆黑中燃起篝火，远古人类的手伸向火焰，火星升腾。特写，缓慢推近。暖橙火光，周围漆黑
- 素材：【网络/生成】搜索：campfire night close up, hands warming by fire, sparks slow motion
- 提示词：`Extreme close-up of a prehistoric campfire in total darkness, rough human hands reaching toward the flames, sparks rising, warm orange firelight, deep black surroundings`
- 留白：A

### S002 古代文字
- 时间 0:03.6–0:07.2 · 时长 3.6s · 画幅 16:9
- 旁白 / 字幕：“文字，延伸了我们的记忆。”（0:04.0–0:07.0）
- 画面：油灯照亮刻有楔形文字的泥板（或甲骨、竹简），侧光显出刻痕。微距，缓慢横移。冷灰暗部 + 一点暖光
- 素材：【网络/生成】优先博物馆真实文物照片（公有领域）。搜索：cuneiform clay tablet museum, oracle bone inscription, bamboo slips
- 提示词：`Macro shot of an ancient clay tablet covered in carved cuneiform marks, lit by a single oil lamp, raking light revealing the carvings, museum realism, cold grey shadows with a warm glow`
- 留白：A（刻痕可见即可，不要出现可识读的现代文字）

### S003 工业机器
- 时间 0:07.2–0:10.8 · 时长 3.6s · 画幅 16:9
- 旁白 / 字幕：“机器，放大了我们的力量。”（0:07.6–0:10.6）
- 画面：19 世纪巨型蒸汽机，活塞与飞轮运转，厂房里蒸汽与光柱。中景，轻微仰拍。冷灰 + 黄铜高光
- 素材：【网络/生成】视频优先。搜索：steam engine flywheel pistons, industrial revolution machine museum
- 提示词：`Massive nineteenth-century steam engine with polished pistons and a huge flywheel in motion, industrial hall filled with steam and shafts of light, low angle, cold grey with brass highlights`
- 留白：A

### S004 芯片
- 时间 0:10.8–0:13.4 · 时长 2.6s · 画幅 16:9
- 旁白 / 字幕：“而人工智能，正在改变一种更深层的东西——”（0:11.2–0:15.0，延续到 S005）
- 画面：硅芯片微距，金色电路纹路微微发光，浅景深。冷蓝灰
- 素材：【网络/生成】搜索：microchip macro, silicon wafer close up, processor circuit macro
- 提示词：`Macro shot of a silicon microchip, fine gold circuit traces glowing faintly, extremely shallow depth of field, cold blue-grey light`
- 留白：A

### S005 黑暗中的屏幕亮起
- 时间 0:13.4–0:15.8 · 时长 2.4s · 画幅 16:9
- 旁白 / 字幕：（S004 字幕延续至 0:15.0）
- 画面：漆黑房间里一块屏幕闪亮，淡蓝光洒在桌面与人物剪影上。屏幕内容只有抽象光，不出现界面文字
- 素材：【生成】
- 提示词：`Pitch-dark room, a single computer screen flickering on, pale blue light spilling across a desk and the silhouette of a person, the screen shows only abstract light`
- 留白：A

### S006 穿过服务器
- 时间 0:15.8–0:18.4 · 时长 2.6s · 画幅 16:9
- 旁白 / 字幕：“思考。”（0:15.8–0:18.2，单独一条，前后留白）
- 画面：镜头低位穿过狭长服务器通道，成千上万蓝色指示灯，冷雾，强烈一点透视。剪辑端做快速推进
- 素材：【生成/网络】搜索：server room aisle, data center corridor lights
- 提示词：`Low camera gliding down a narrow aisle between towering server racks, thousands of tiny blue status lights, cold mist, strong one-point perspective`
- 留白：A

### S007 庞大的数据中心（片名）
- 时间 0:18.4–0:23.0 · 时长 4.6s · 画幅 16:9
- 旁白 / 字幕：无。片名卡 0:18.8–0:22.8
- 画面：从服务器拉远，露出山谷中巨型数据中心，无尽的机房发着蓝光，极小的人影作比例。《流浪地球》式文明尺度
- 素材：【生成】
- 提示词：`Aerial wide shot of a colossal data centre complex filling a mountain valley at night, endless rows of server halls glowing blue, tiny human figures for scale, dark empty sky in the centre of the frame`
- 留白：A+B（中央上方天空留给片名）

## 第一章 · 智能的诞生（0:23.0–1:01.0）

### S008 机械计算机（章节卡）
- 时间 0:23.0–0:27.6 · 时长 4.6s · 画幅 16:9
- 旁白 / 字幕：无。章节卡「第一章 智能的诞生」0:23.4–0:27.4；时间轴节点 1“机械计算”
- 画面：昏暗博物馆中的黄铜机械计算机（差分机式），数百个齿轮与立柱，侧光。缓慢横移
- 素材：【网络/生成】搜索：Babbage difference engine, mechanical calculator museum brass gears
- 提示词：`Brass mechanical calculating engine with hundreds of gears and columns in the style of the Babbage difference engine, dim museum, side light, dark negative space in the centre and lower third`
- 留白：A+B+C

### S009 互联网
- 时间 0:27.6–0:31.4 · 时长 3.8s · 画幅 16:9
- 旁白 / 字幕：“过去的机器，延伸人的双手。”（0:27.8–0:31.2）；时间轴节点 2“互联网”
- 画面：光纤束中光脉冲奔向黑暗，象征互联网把世界连起来。蓝白
- 素材：【生成/网络】搜索：optical fiber light pulses, fiber optic cable macro
- 提示词：`Bundle of optical fibres glowing with pulses of light racing into darkness, symbol of the early internet, blue and white, dark lower third`
- 留白：A+C

### S010 人工智能
- 时间 0:31.4–0:35.4 · 时长 4.0s · 画幅 16:9
- 旁白 / 字幕：“今天的机器，开始参与创造、设计与发现。”（0:31.8–0:36.0）；时间轴节点 3“人工智能”
- 画面：黑暗中悬浮的发光神经核心，细丝向外延伸。深蓝。抽象，不要机器人脸
- 素材：【生成】
- 提示词：`Abstract artificial intelligence: a luminous neural core of light suspended in darkness, delicate glowing filaments reaching outward, deep blue, dark lower third`
- 留白：A+C

### S011 神经网络如星系
- 时间 0:35.4–0:40.4 · 时长 5.0s · 画幅 16:9
- 旁白 / 字幕：S010 字幕延续至 0:36.0；“那些曾被视为人类独有的能力，”从 0:38.8 开始
- 画面：神经网络像旋涡星系一样展开，亿万发光节点与突触般的丝线。宇宙尺度，深空蓝
- 素材：【生成】
- 提示词：`A neural network unfolding like a spiral galaxy, billions of glowing nodes and synapse-like threads, deep space blue, cosmic scale`
- 留白：A

### S012 网络连接实验室、医院与城市
- 时间 0:40.4–0:44.4 · 时长 4.0s · 画幅 16:9
- 旁白 / 字幕：“那些曾被视为人类独有的能力，”（0:38.8–0:41.8）“正在被重新审视。”（0:42.0–0:44.4）
- 画面：未来城市夜景，光线把科研实验室、医院与住宅楼连接起来，数据流在天际线上划出弧线
- 素材：【生成】
- 提示词：`Night view of a future city where arcs of light connect a research laboratory, a hospital and residential towers, data streams curving across the skyline, deep blue`
- 留白：A

### S013 AI辅助设计
- 时间 0:44.4–0:47.6 · 时长 3.2s · 画幅 16:9
- 旁白 / 字幕：无
- 画面：建筑师在昏暗工作室端详 AI 生成的全息建筑模型，多种设计方案在光中分叉展开。中景，蓝白光照在脸上
- 素材：【生成】
- 提示词：`Architect in a dim studio studying a holographic building model generated by AI, many design variations branching out in light, blue-white glow on the face, medium shot`
- 留白：A

### S014 AI科学研究
- 时间 0:47.6–0:50.8 · 时长 3.2s · 画幅 16:9
- 旁白 / 字幕：“当智能走出实验室，进入每个人的生活，”（0:48.0–0:52.0）
- 画面：科学家注视大屏上 AI 解析出的发光蛋白质结构，镜片反光。中近景，冷蓝
- 素材：【生成】
- 提示词：`Scientist in a laboratory looking at a large display of a glowing protein structure revealed by AI, reflections on the glasses, medium close-up, cool blue`
- 留白：A

### S015 图像生成
- 时间 0:50.8–0:53.8 · 时长 3.0s · 画幅 16:9
- 旁白 / 字幕：S014 字幕延续；“人类的位置，也开始发生变化。”从 0:52.4 开始
- 画面：暗室大屏上，一幅写实风景从数字噪点中浮现，人物剪影在看。屏幕上只有画面，没有文字
- 素材：【生成】
- 提示词：`Large screen in a dark room where a photorealistic mountain landscape emerges from digital noise, a person silhouetted watching, no text on screen`
- 留白：A

### S016 机器人工作
- 时间 0:53.8–0:57.4 · 时长 3.6s · 画幅 16:9
- 旁白 / 字幕：“人类的位置，也开始发生变化。”（0:52.4–0:56.4）
- 画面：明亮洁净的机器人实验室，机械臂精准作业，后景有工程师。冷蓝白
- 素材：【生成/网络】搜索：robot arm laboratory, industrial robot precision
- 提示词：`Industrial robot arms working with precision in a clean bright robotics lab, a human engineer in the background, cool blue-white`
- 留白：A

### S017 数据网络化为生产线（衔接）
- 时间 0:57.4–1:01.0 · 时长 3.6s · 画幅 16:9
- 旁白 / 字幕：无
- 画面：俯视，发光数据线落向工厂生产线与办公工位，网络变成传送带。由科技蓝过渡到钢灰
- 素材：【生成】
- 提示词：`Top-down view of streams of glowing data lines descending onto a factory production line and rows of office workstations, the network turning into conveyor belts, cool blue fading to steel grey`
- 留白：A

## 第二章 · 工作的重新定义（1:01.0–1:45.0）

### S018 传统流水线（章节卡）
- 时间 1:01.0–1:06.0 · 时长 5.0s · 画幅 16:9
- 旁白 / 字幕：无。章节卡「第二章 工作的重新定义」1:01.4–1:05.6
- 画面：20 世纪中叶的工业流水线，工人穿工装，成排机器。纪录片档案质感，低饱和冷灰，全景
- 素材：【网络/生成】优先公有领域档案照片或影像。搜索：1950s assembly line archive, factory workers vintage public domain
- 提示词：`Mid-twentieth-century industrial assembly line with workers in overalls and rows of machines, archival documentary realism, desaturated cold grey, wide shot, dark empty area in the centre`
- 留白：A+B

### S019 自动化工厂
- 时间 1:06.0–1:09.6 · 时长 3.6s · 画幅 16:9
- 旁白 / 字幕：无（让画面呼吸）
- 画面：无人自动化工厂，长排机械臂在没有人的车间作业，火花与冷光。对称全景，钢灰蓝
- 素材：【生成/网络】搜索：automated factory robots, lights-out manufacturing
- 提示词：`Lights-out automated factory, long rows of robot arms working without people, sparks and cold LED light, symmetrical wide shot, steel grey-blue`
- 留白：A

### S020 医生与AI协作
- 时间 1:09.6–1:12.4 · 时长 2.8s · 画幅 16:9
- 旁白 / 字幕：“新的工作可能诞生，”（1:09.8–1:12.2）
- 画面：医生端详 AI 辅助生成的半透明三维心脏影像，神情专注。中景，冷白蓝
- 素材：【生成】
- 提示词：`Doctor in a hospital reviewing a translucent AI-assisted 3D scan of a human heart, calm focused face, medium shot, cool white-blue`
- 留白：A

### S021 设计师与AI协作
- 时间 1:12.4–1:15.0 · 时长 2.6s · 画幅 16:9
- 旁白 / 字幕：“旧的技能也可能迅速贬值。”（1:12.6–1:15.6）
- 画面：设计师伏案手绘，AI 界面在旁边以光的形式投出多个备选造型。中景，冷蓝灰 + 台灯暖光
- 素材：【生成】
- 提示词：`Product designer sketching at a desk while an AI interface projects alternative design forms in light beside the sketch, medium shot, cool blue-grey with a warm desk lamp`
- 留白：A

### S022 科学家与AI协作
- 时间 1:15.0–1:17.6 · 时长 2.6s · 画幅 16:9
- 旁白 / 字幕：S021 字幕延续至 1:15.6
- 画面：科学家与实验室机器人并肩在实验台前处理发光样品。中景，冷蓝
- 素材：【生成】
- 提示词：`Scientist and a laboratory robot working side by side at a bench with glowing samples, medium shot, cool blue`
- 留白：A

### S023 劳动者隔窗看机器（固定角色：劳动者）
- 时间 1:17.6–1:22.0 · 时长 4.4s · 画幅 16:9
- 旁白 / 字幕：“赫拉利担忧，一些人可能长期难以在经济体系中重新找到位置”（1:16.4–1:21.8）
- 画面：劳动者站在玻璃墙后，看着机器人做他原来的工作，玻璃上映出机械臂。中近景，低沉灰蓝。表现为忧虑而非绝望
- 素材：【生成】
- 提示词：`Middle-aged East Asian factory worker about 50 with grey-streaked short hair and a navy work jacket, standing behind a glass wall watching robots do his former job, reflections of robot arms on the glass, medium close-up, subdued grey-blue, dignified not despairing`
- 留白：A

### S024 人群中的普通人
- 时间 1:22.0–1:26.2 · 时长 4.2s · 画幅 16:9
- 旁白 / 字幕：“——这就是“无用阶级”的风险。”（1:22.2–1:25.6）
- 画面：黄昏繁忙的城市斑马线，人群中一张清晰的脸望向高楼上抽象的光屏，神情迟疑。中近景，冷灰蓝。作为风险提示，不渲染悲惨
- 素材：【生成】
- 提示词：`Ordinary adults on a busy city crosswalk at dusk, one face in sharp focus looking up uncertainly at towering screens of abstract light, medium close-up, cold grey-blue, contemplative`
- 留白：A

### S025 劳动者面部特写（固定角色：劳动者）
- 时间 1:26.2–1:31.6 · 时长 5.4s · 画幅 16:9
- 旁白 / 字幕：“劳动不再被需要，绝不意味着一个人失去了价值。”（1:26.6–1:31.6）
- 画面：劳动者饱经风霜的面部特写，平静、有尊严，窗光柔和，脸侧开始出现一点暖光。浅景深
- 素材：【生成】
- 提示词：`Close-up portrait of the same middle-aged East Asian worker with grey-streaked short hair, weathered face calm and dignified, soft window light with a first hint of warm light on one side, shallow depth of field`
- 留白：A（脸部放在画面中上部）

### S026 学习新技能（固定角色：劳动者）
- 时间 1:31.6–1:35.2 · 时长 3.6s · 画幅 16:9
- 旁白 / 字幕：“持续学习需要机会，”（1:32.6–1:35.0）
- 画面：夜间培训教室，不同年龄的成年学员；劳动者用平板学习操作协作机器人。暖色实景光
- 素材：【生成】
- 提示词：`Evening training class with adult learners of different ages, the same middle-aged worker in a navy jacket learning to operate a collaborative robot with a tablet, warm practical light`
- 留白：A

### S027 重新进入工作场景（固定角色：劳动者）
- 时间 1:35.2–1:39.0 · 时长 3.8s · 画幅 16:9
- 旁白 / 字幕：“技术创造的财富也需要被分享。”（1:35.2–1:38.6）
- 画面：劳动者以新岗位回到现代车间，操作机器人控制台，同事在旁，晨光从高窗照入
- 素材：【生成】
- 提示词：`The same middle-aged worker returning to a modern workplace in a new role, operating a robot control console with colleagues around him, warm morning light through high windows, medium shot`
- 留白：A

### S028 夜里凝视设计图
- 时间 1:39.0–1:45.0 · 时长 6.0s · 画幅 16:9
- 旁白 / 字幕：“当工作发生改变，我们将如何重新理解自身的价值？”（1:39.6–1:44.8），之后留白进入第三章
- 画面：夜里独自在办公室的设计师，屏幕上精细的建筑线稿照亮脸庞（无可读文字），若有所思。中近景，由蓝转暖
- 素材：【生成】
- 提示词：`Designer alone in an office at night, face lit by a screen showing a fine architectural blueprint line drawing without readable text, contemplative, medium close-up, blue light slowly turning warm`
- 留白：A

## 第三章 · 创造力属于谁？（1:45.0–2:36.0）

### S029 设计图化为画作（章节卡）
- 时间 1:45.0–1:49.6 · 时长 4.6s · 画幅 16:9
- 旁白 / 字幕：无。章节卡「第三章 创造力属于谁？」1:45.4–1:49.6；机械声在此融入大提琴
- 画面：建筑线稿从左到右逐渐变成有笔触肌理的油画，一半技术图纸、一半绘画。暖白、金色
- 素材：【生成】（如可能，另交一张纯线稿版 S029_a 和纯油画版 S029_b，剪辑端做渐变）
- 提示词：`Transition image, an architectural blueprint line drawing gradually turning into a textured oil painting from left to right, half technical drawing and half painting, warm white and gold, dark centre for a title`
- 留白：A+B

### S030 AI写诗
- 时间 1:49.6–1:53.0 · 时长 3.4s · 画幅 16:9
- 旁白 / 字幕：“如果机器可以写诗。”（1:50.0–1:52.6）
- 画面：暗色工作室，屏幕散出光粒子，在空中汇成水墨般的笔触。诗意、抽象，不出现可识读的字
- 素材：【生成】
- 提示词：`Dark studio, a screen releasing particles of light that drift into the air and form ink-like brush strokes, poetic and abstract, no readable characters, warm white glow`
- 留白：A

### S031 AI绘画
- 时间 1:53.0–1:56.0 · 时长 3.0s · 画幅 16:9
- 旁白 / 字幕：“可以绘画。”（1:53.4–1:55.4）
- 画面：机械臂在画布上落下细腻笔触，旁边屏幕发光。暖白
- 素材：【生成】
- 提示词：`Robotic arm painting delicate strokes onto a canvas beside a softly glowing screen, artist studio, warm white light`
- 留白：A

### S032 AI电影画面与音乐
- 时间 1:56.0–2:00.0 · 时长 4.0s · 画幅 16:9
- 旁白 / 字幕：“甚至帮助我们发现新的知识。”（1:56.4–1:59.6）
- 画面：暗色剪辑室，巨幕播放 AI 生成的电影级风景画面，发光的音频波形在画面上起伏，前景观众剪影
- 素材：【生成】
- 提示词：`Dark editing suite, a giant screen showing an AI-generated cinematic landscape while glowing audio waveforms ripple across it, a silhouetted viewer in the foreground`
- 留白：A

### S033 大提琴家演奏
- 时间 2:00.0–2:05.0 · 时长 5.0s · 画幅 16:9
- 旁白 / 字幕：“那么，创造力还是人类的专属吗？”（2:01.0–2:05.0）
- 画面：成年大提琴家独自在暗场舞台演奏，一束暖光，闭眼，琴弓正在运弓。中景，金色
- 素材：【网络/生成】视频优先。搜索：cellist playing dark stage spotlight, cello performance slow motion
- 提示词：`Adult cellist performing alone on a dark stage under a single warm spotlight, eyes closed, bow mid-stroke, medium shot, golden tones`
- 留白：A

### S034 画家落笔（停顿）
- 时间 2:05.0–2:08.4 · 时长 3.4s · 画幅 16:9
- 旁白 / 字幕：无（短暂停顿）
- 画面：蘸满颜料的画笔触到画布，微距，慢动作质感，油彩肌理。暖光
- 素材：【网络/生成】视频优先。搜索：paintbrush on canvas macro slow motion, oil painting brush stroke close up
- 提示词：`Macro close-up of a paintbrush loaded with oil paint touching a canvas, slow-motion feel, rich paint texture, warm light`
- 留白：A

### S035 科学家凝望实验结果
- 时间 2:08.4–2:12.4 · 时长 4.0s · 画幅 16:9
- 旁白 / 字幕：“也许，我们需要重新理解创造。”（2:08.6–2:12.2）
- 画面：科学家凝望发光的实验结果，眼中有惊奇。面部大特写，暖光与蓝光交织
- 素材：【生成】
- 提示词：`Extreme close-up of a scientist's face gazing at a glowing experimental result, wonder in the eyes, warm light mixing with soft blue`
- 留白：A（眼睛放在画面上三分之一）

### S036 钢琴家的手与眼睛
- 时间 2:12.4–2:17.4 · 时长 5.0s · 画幅 16:9
- 旁白 / 字幕：“一首歌，可以承载一个人的思念。”（2:13.0–2:16.8）
- 画面：成年钢琴家的双手落在琴键上，闭着的双眼，柔和暖色逆光，亲密、浅景深
- 素材：【网络/生成】搜索：pianist hands close up warm light, piano performance emotional
- 提示词：`Close-up of an adult pianist's hands on the keys and closed eyes in soft focus, warm backlight, intimate, shallow depth of field`
- 留白：A

### S037 画家凝视画布（固定角色：画家）
- 时间 2:17.4–2:22.4 · 时长 5.0s · 画幅 16:9
- 旁白 / 字幕：“一幅画，可以留下一个时代的追问。”（2:17.8–2:21.6）
- 画面：画家凝视一幅巨大的星空画作，工作室暖光。中近景
- 素材：【生成】
- 提示词：`East Asian woman painter about 40 with a short bob and a linen apron, looking at her large canvas of a painted starry night sky, warm studio light, medium close-up`
- 留白：A

### S038 画家借助AI完善作品（固定角色：画家）
- 时间 2:22.4–2:27.6 · 时长 5.2s · 画幅 16:9
- 旁白 / 字幕：“未来的创造，也将发生在人与新的智能之间。”（2:22.8–2:27.0）
- 画面：画家手持平板，AI 建议以柔光投在画布旁，她对比、调整星空画作。暖白
- 素材：【生成】
- 提示词：`The same painter holding a tablet while AI suggestions are softly projected beside the canvas, comparing and refining the starry painting, warm white light`
- 留白：A

### S039 画家停下思考（固定角色：画家）
- 时间 2:27.6–2:31.8 · 时长 4.2s · 画幅 16:9
- 旁白 / 字幕：“而我们，仍要寻找自己真正想表达的东西。”（2:28.2–2:32.6）
- 画面：画家放下画笔，停下来思考，目光落在画布上。安静的瞬间，金色窗光，中近景
- 素材：【生成】
- 提示词：`The same painter pausing with the brush lowered, thinking, eyes on the canvas, a quiet moment, golden window light, medium close-up`
- 留白：A

### S040 亲手完成最后一笔（固定角色：画家）
- 时间 2:31.8–2:36.0 · 时长 4.2s · 画幅 16:9
- 旁白 / 字幕：S039 字幕延续至 2:32.6
- 画面：画家的手亲自落下最后一笔，画中的星空占满大半画面；剪辑端推近让画中星空铺满屏幕，接 S041
- 素材：【生成】
- 提示词：`Close-up of the same painter's hand adding the final brush stroke to a painted starry sky, the painted stars filling most of the frame, warm gold and cosmic blue`
- 留白：A

## 第四章 · AI时代的人类答案（2:36.0–3:43.0）

### S041 宇宙中的地球（章节卡）
- 时间 2:36.0–2:40.6 · 时长 4.6s · 画幅 16:9
- 旁白 / 字幕：无。章节卡「第四章 AI时代的人类答案」2:36.4–2:40.6；音乐从独奏扩展为交响
- 画面：深空中的地球，薄薄的蓝色大气层发光，群星。《星际穿越》式静谧
- 素材：【网络/生成】NASA 公有领域图片可用。搜索：NASA earth from space high resolution
- 提示词：`Earth floating in deep space, thin blue atmosphere glowing, stars, cosmic stillness, dark empty space in the centre-left of the frame`
- 留白：A+B

### S042 未来城市亮起
- 时间 2:40.6–2:45.0 · 时长 4.4s · 画幅 16:9
- 旁白 / 字幕：“人工智能可能改变世界。”（2:41.0–2:43.8）
- 画面：黎明时分的未来巨型城市，街区一片接一片亮起，高塔与空中连廊。《流浪地球》尺度，金色 + 深蓝
- 素材：【生成】
- 提示词：`Future megacity at dawn, districts lighting up wave after wave, towers and sky bridges, vast civilisation scale, gold and deep blue`
- 留白：A

### S043 巨型能源设施
- 时间 2:45.0–2:49.2 · 时长 4.2s · 画幅 16:9
- 旁白 / 字幕：“但它无法替代人类提出的问题。”（2:44.6–2:48.0）
- 画面：巨型聚变能源设施，环形结构与等离子光，极小的人影作比例。金色，宽银幕全景
- 素材：【生成】
- 提示词：`Colossal fusion energy facility with giant ring structures and a plasma glow, tiny human figures for scale, golden light, cinematic wide shot`
- 留白：A

### S044 穿过云层
- 时间 2:49.2–2:53.2 · 时长 4.0s · 画幅 16:9
- 旁白 / 字幕：“我们为什么存在？”（2:49.6–2:52.2）
- 画面：日出时镜头穿过云海升向高层大气，下方金色、上方宇宙蓝
- 素材：【网络/生成】视频优先。搜索：flying through clouds sunrise aerial, above clouds stratosphere
- 提示词：`Camera rising through a sea of clouds at sunrise toward the upper atmosphere, golden light below and deep space blue above`
- 留白：A

### S045 空间站
- 时间 2:53.2–2:57.6 · 时长 4.4s · 画幅 16:9
- 旁白 / 字幕：“我们希望创造怎样的未来？”（2:53.4–2:56.6），之后音乐回落、留白
- 画面：地球轨道上的大型环形空间站，阳光在太阳能板上闪烁。宇宙蓝
- 素材：【生成】
- 提示词：`Large rotating ring-shaped space station in orbit above Earth, sunlight glinting on the solar arrays, cosmic blue`
- 留白：A

### S046 科研人员合作
- 时间 2:57.6–3:02.2 · 时长 4.6s · 画幅 16:9
- 旁白 / 字幕：“当算法越来越了解我们，”（2:59.0–3:01.6）
- 画面：不同背景的成年科研人员围着全息桌讨论合作，地面实验室，暖光。中景
- 素材：【生成/网络】搜索：scientists collaborating lab team discussion
- 提示词：`Adult researchers from different backgrounds collaborating around a holographic table in a ground laboratory, warm light, medium shot`
- 留白：A

### S047 月球基地
- 时间 3:02.2–3:06.2 · 时长 4.0s · 画幅 16:9
- 旁白 / 字幕：“我们也需要重新认识自己。”（3:01.9–3:04.8）
- 画面：月面上的永久基地，穹顶与亮着的窗，黑色天空中地球升起。宇宙蓝 + 窗内暖光
- 素材：【生成】
- 提示词：`Permanent Moon base with domes and lit windows on the lunar surface, Earth rising in the black sky, cosmic blue with warm window light`
- 留白：A

### S048 医护照护病人
- 时间 3:06.2–3:10.2 · 时长 4.0s · 画幅 16:9
- 旁白 / 字幕：“我们真正渴望什么？”（3:06.4–3:09.0）
- 画面：护士在安静的病房照护年长病人，轻抚其肩，晨光温暖。中景
- 素材：【生成/网络】搜索：nurse caring elderly patient warm light
- 提示词：`Nurse caring for an elderly patient in a calm hospital room, a gentle hand on the shoulder, warm morning light, medium shot`
- 留白：A

### S049 深空探索
- 时间 3:10.2–3:15.0 · 时长 4.8s · 画幅 16:9
- 旁白 / 字幕：“又愿意为了怎样的未来，承担责任？”（3:10.2–3:14.2）
- 画面：长舰体、引擎发光的深空探索飞船驶离太阳系，远处有一颗带环行星。宇宙蓝
- 素材：【生成】
- 提示词：`Deep space exploration ship with a long hull and glowing engines leaving the solar system, a ringed planet in the distance, cosmic blue`
- 留白：A

### S050 宇航员舱外移动（固定角色：宇航员）
- 时间 3:15.0–3:19.2 · 时长 4.2s · 画幅 16:9
- 旁白 / 字幕：“人类真正的优势。”（3:15.6–3:17.8）
- 画面：成年宇航员系着安全绳在空间站外缓慢移动，面罩映出蓝色地球，太阳光晕
- 素材：【生成】
- 提示词：`Adult astronaut in a white spacesuit with a gold visor and no insignia, moving slowly outside a space station on a tether, the visor reflecting the blue Earth, sun flare, cosmic blue`
- 留白：A

### S051 地面工程师抬头
- 时间 3:19.2–3:22.2 · 时长 3.0s · 画幅 16:9
- 旁白 / 字幕：“从来不是比机器更快。”（3:18.6–3:21.0）
- 画面：夜里在发射场的地面工程师抬头望天，脸被柔光照亮。中近景，暖 + 蓝
- 素材：【生成】
- 提示词：`Ground engineer at a launch site at night looking up at the sky, face softly lit, medium close-up, warm and blue light`
- 留白：A

### S052 头盔映出地球（固定角色：宇航员）
- 时间 3:22.2–3:25.0 · 时长 2.8s · 画幅 16:9
- 旁白 / 字幕：“而是拥有梦想。”（3:22.0–3:24.2）
- 画面：宇航员面罩大特写，映出蓝色地球，面罩后隐约可见面孔
- 素材：【生成】
- 提示词：`Extreme close-up of the astronaut's gold helmet visor reflecting the blue Earth, a faint face visible behind the glass, cosmic blue`
- 留白：A

### S053 握住患者的手
- 时间 3:25.0–3:28.0 · 时长 3.0s · 画幅 16:9
- 旁白 / 字幕：“拥有爱。”（3:25.2–3:27.0）
- 画面：特写，护士的手握住病床上年长患者的手，柔和暖光
- 素材：【生成/网络】搜索：nurse holding patient hand close up
- 提示词：`Close-up of a nurse's hand holding an elderly patient's hand on a hospital bed, warm soft light`
- 留白：A（双手放在画面中部）

### S054 人们相拥
- 时间 3:28.0–3:31.0 · 时长 3.0s · 画幅 16:9
- 旁白 / 字幕：“拥有选择未来的能力。”（3:28.2–3:31.0）
- 画面：黎明时分，两个成年人在到达大厅或街头紧紧相拥，金色逆光。中景
- 素材：【生成/网络】搜索：adults embracing reunion airport, hug golden hour
- 提示词：`Two adults embracing in an arrivals hall at dawn, emotional reunion, warm golden backlight, medium shot`
- 留白：A

### S055 越过宇航员拉远（固定角色：宇航员）
- 时间 3:31.0–3:36.4 · 时长 5.4s · 画幅 16:9
- 旁白 / 字幕：“未来尚未写定。”（3:32.6–3:35.8）
- 画面：从宇航员身后越肩，下方地球铺满画面。剪辑端做缓慢拉远
- 素材：【生成】（建议 4K，拉远需要余量）
- 提示词：`Over-the-shoulder view from behind the astronaut floating outside the station, Earth below filling most of the frame, wide, room to pull back`
- 留白：A

### S056 晨昏线与第一缕阳光（片尾）
- 时间 3:36.4–3:43.0 · 时长 6.6s · 画幅 16:9
- 旁白 / 字幕：“我们的选择，正在成为历史。”（3:36.4–3:39.8）；片尾卡 3:40.0–3:43.0
- 画面：轨道视角的地球晨昏线，夜面城市灯火与地平线上的第一缕阳光同时出现。金色 + 宇宙蓝
- 素材：【网络/生成】NASA 国际空间站拍摄的晨昏线照片可用。搜索：ISS earth terminator sunrise city lights
- 提示词：`Earth from orbit at the day-night terminator, city lights glowing on the night side while the first sunlight breaks over the horizon, gold and cosmic blue, dark space above`
- 留白：A+B

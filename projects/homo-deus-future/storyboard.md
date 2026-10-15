# 《未来简史》分镜表（v2）

> 时长 4:30.7 · 16:9 · 2560×1440 · 24fps · 灵感来自尤瓦尔·赫拉利《未来简史》
> 版本 v2（homo_deus_future_v2.mp4）：在第三章“我们还是原来的自己吗？”与第四章“人类的新纪元”之间补入“无用阶级”段落

由 shotlist.json 生成（`python3 tools/gen_docs_v2.py`）。所有镜头为 AI 静帧 + 虚拟运镜；运镜中的数字为缩放倍数。🆕 = v2 新增。

## v1 → v2 时间码对照

| v1 时间 | v2 时间 | 处理 |
|---|---|---|
| 0:00.0–2:12.0 | 0:00.0–2:12.0 | 不变 |
| 2:12.0–2:16.8 | — | 删除义肢镜头（与握手、脑机接口重复）；字幕“身体的边界，正在被重新定义。”移到脑机接口镜头 |
| 2:16.8–2:46.4 | 2:12.0–2:41.6 | 整体前移 4.8 秒 |
| — | 2:41.6–3:25.6 | 新增 44 秒“无用阶级”段落（7 个镜头、9 条字幕） |
| 2:46.4–3:03.9 | 3:25.6–3:43.1 | 整体后移 39.2 秒 |
| 3:03.9–3:06.4 | — | 删除月球→火星过渡中的一小节（太空展示重复） |
| 3:06.4–3:54.0 | 3:43.1–4:30.7 | 整体后移 36.7 秒 |

v1 片长 3:54.0 → v2 片长 4:30.7（+44.0 秒新增，−7.3 秒压缩）。插入点之后的字幕、章节卡、画面标注、闪白、片尾卡和配乐已全部按新时间重新校准。

## 开场（0:00.0–0:30.0）

| # | 时间 | 时长 | 镜头 | 素材 | 画面 | 运镜 | 色调 | 转场 | 特效 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0:00.0–0:08.0 | 8.0s | `cosmos` | 01_cosmos.jpg | Dark universe, deep star field | 推近 1.00→1.25 · 旋转 1.5° | 深空黑蓝 | — | 星空视差 |
| 2 | 0:07.0–0:14.2 | 7.2s | `earth` | 02_earth.jpg | Earth slowly rotating, night-side city lights | 推近 1.00→2.40 · 右移 · 上摇 | 深空黑蓝 | 叠化 | zoomblur |
| 3 | 0:12.9–0:19.0 | 6.1s | `citylights` | 03_citylights.jpg | Future Eastern megacity, lights switching on | 拉远 1.25→1.06 · 上摇 | 科技冷蓝 | 硬切 | lights_on |
| 4 | 0:18.0–0:24.6 | 6.6s | `elevator` | 04_elevator.jpg | Giant space elevator rising from the city into orbit | 上摇 | 科技冷蓝 | 叠化 | — |
| 5 | 0:23.6–0:30.4 | 6.8s | `drones` | 05_drones.jpg | Uncrewed craft piercing the cloud sea | 右移 · 上摇 | 科技冷蓝 | 叠化 | — |
| 6 | 0:29.6–0:37.6 | 8.0s | `bluecity` | 06_bluecity.jpg | Blue high-tech city at night | 推近 1.05→1.22 · 上摇 | 科技冷蓝 | 数字故障 | 数据流 |

## 第一章 · 智能革命（0:30.0–1:12.0）

| # | 时间 | 时长 | 镜头 | 素材 | 画面 | 运镜 | 色调 | 转场 | 特效 |
|---|---|---|---|---|---|---|---|---|---|
| 7 | 0:36.6–0:44.0 | 7.4s | `ainetwork` | 07_ainetwork.jpg | Global AI network wrapping the Earth | 推近 1.08→1.28 · 旋转 -2.0° | 科技冷蓝 | 叠化 | — |
| 8 | 0:43.0–0:50.0 | 7.0s | `robotwork` | 08_robotwork.jpg | Robots working side by side with humans | 右移 | 实验室青白 | 叠化 | — |
| 9 | 0:49.0–0:56.0 | 7.0s | `assistant` | 09_assistant.jpg | Holographic assistant anticipating needs | 推近 1.04→1.20 · 右移 · 上摇 | 温柔蓝白 | 叠化 | — |
| 10 | 0:55.0–1:03.6 | 8.6s | `datagalaxy` | 10_datagalaxy.jpg | Data streams flowing like the Milky Way | 推近 1.00→1.24 · 下摇 · 旋转 1.0° | 科技冷蓝 | 叠化 | 数据流、光晕 |
| 11 | 1:02.6–1:08.6 | 6.0s | `datacenter` | 11_datacenter.jpg | Endless data-centre corridor | 拉远 1.20→1.04 | 科技冷蓝 | 叠化 | — |
| 12 | 1:07.6–1:12.8 | 5.2s | `metro` | 12_metro.jpg | Crowds in a smart metro hall | 右移 | 科技冷蓝 | 叠化 | — |
| 13 | 1:11.8–1:20.0 | 8.2s | `lab` | 13_lab.jpg | Future bio-laboratory | 推近 1.04→1.22 · 上摇 | 实验室青白 | 数字故障 | — |

## 第二章 · 生命重塑（1:12.0–2:01.0）

| # | 时间 | 时长 | 镜头 | 素材 | 画面 | 运镜 | 色调 | 转场 | 特效 |
|---|---|---|---|---|---|---|---|---|---|
| 14 | 1:19.0–1:27.0 | 8.0s | `dna` | 14_dna.jpg | Glowing DNA double helix | 推近 1.06→1.30 · 旋转 3.0° | 实验室青白 | 叠化 | 光晕 |
| 15 | 1:26.0–1:33.0 | 7.0s | `editing` | 15_editing.jpg | Gene editing of a helix strand | 拉远 1.22→1.05 | 实验室青白 | 叠化 | — |
| 16 | 1:32.0–1:39.0 | 7.0s | `artlife` | 16_artlife.jpg | Artificial life forming in a vessel | 推近 1.05→1.22 · 上摇 | 实验室青白 | 叠化 | — |
| 17 | 1:38.0–1:45.6 | 7.6s | `nanobots` | 17_nanobots.jpg | Nanobots travelling through a blood vessel | 推近 1.00→1.35 | 科技冷蓝 | 径向光晕 | radial |
| 18 | 1:44.6–1:53.0 | 8.4s | `cellplanets` | 18_cellplanets.jpg | Cells orbiting like planets, micro meets cosmos | 推近 1.06→1.26 · 旋转 -2.5° | 深空黑蓝 | 径向光晕 | radial、星空视差 |
| 19 | 1:52.0–2:01.8 | 9.8s | `neurons` | 19_neurons.jpg | Neural network of light | 推近 1.04→1.24 · 右移 · 上摇 | 科技冷蓝 | 叠化 | 光晕 |
| 20 | 2:00.8–2:07.8 | 7.0s | `hands` | 20_hands.jpg | Human hand meeting a robotic hand | 推近 1.04→1.20 | 温柔蓝白 | 数字故障 | — |

## 第三章 · 人与机器融合（2:01.0–2:41.6）

| # | 时间 | 时长 | 镜头 | 素材 | 画面 | 运镜 | 色调 | 转场 | 特效 |
|---|---|---|---|---|---|---|---|---|---|
| 21 | 2:06.8–2:13.0 | 6.2s | `bci` | 21_bci.jpg | Brain-computer interface | 拉远 1.20→1.05 · 下摇 | 科技冷蓝 | 叠化 | — |
| 22 | 2:12.0–2:19.0 | 7.0s | `underground` | 24_underground.jpg | Giant Eastern underground city, Wandering-Earth scale | 右移 | 科技冷蓝 | 叠化 | — |
| 23 | 2:18.0–2:24.8 | 6.8s | `upload` | 25_upload.jpg | Consciousness dissolving into digital light | 推近 1.04→1.24 | 科技冷蓝 | 数字故障 | 数据流 |
| 24 | 2:23.8–2:30.0 | 6.2s | `ar` | 22_ar.jpg | Augmented-reality street | 拉远 1.16→1.04 | 科技冷蓝 | 叠化 | 招牌模糊 |
| 25 | 2:29.0–2:35.2 | 6.2s | `stationin` | 26_stationin.jpg | Space station interior | 推近 1.04→1.20 | 科技冷蓝 | 叠化 | — |
| 26 | 2:34.2–2:42.6 | 8.4s | `mirror` | 27_mirror.jpg | A person facing a digital reflection of themself | 推近 1.02→1.16 · 上摇 | 温柔蓝白 | 叠化 | 压暗 |

## 插入段 · 谁能共享这个未来？（v2 新增，片中不加章节标题）（2:41.6–3:25.6）

| # | 时间 | 时长 | 镜头 | 素材 | 画面 | 运镜 | 色调 | 转场 | 特效 |
|---|---|---|---|---|---|---|---|---|---|
| 27 | 2:41.6–2:49.2 | 7.6s | `clinic` 🆕 | 36_clinic.jpg | Life-upgrade clinic high above the city: a privileged client under a BCI halo | 拉远 1.22→1.04 · 左移 · 下摇 | 实验室青白 | 叠化 | — |
| 28 | 2:48.2–2:55.4 | 7.2s | `automation` 🆕 | 37_automation.jpg | Lights-out automated factory in the same city; one human watching from a catwalk | 推近 1.04→1.20 · 上摇 | 科技冷蓝 | 数字故障 | — |
| 29 | 2:54.4–3:01.4 | 7.0s | `worker` 🆕 | 38_worker.jpg | MCU: a middle-aged worker behind glass, watching robots do his former job | 推近 1.04→1.18 · 右移 · 上摇 | 温柔蓝白 | 叠化 | — |
| 30 | 3:00.4–3:08.6 | 8.2s | `faces` 🆕 | 39_faces.jpg | MCU: ordinary people - a delivery rider, an old man, a mother and child - looking up | 右移 · 上摇 | 温柔蓝白 | 叠化 | 招牌模糊 |
| 31 | 3:07.6–3:15.0 | 7.4s | `divide` 🆕 | 40_divide.jpg | Divided city: sky-towers in sunlight above, crowded streets in shadow below | 下摇 | 日出暖金 | 叠化 | — |
| 32 | 3:14.0–3:20.6 | 6.6s | `crowdwalk` 🆕 | 41_crowdwalk.jpg | MS tracking: ordinary people walking together toward the space port | 右移 · 上摇 | 东方琥珀金 | 叠化 | 招牌模糊 |
| 33 | 3:19.6–3:26.6 | 7.0s | `toport` 🆕 | 42_toport.jpg | The crowd streams through the great gate toward the rocket and the light | 推近 1.04→1.24 · 上摇 | 东方琥珀金 | 叠化 | 光晕 |

## 第四章 · 人类的新纪元（3:25.6–4:01.5）

| # | 时间 | 时长 | 镜头 | 素材 | 画面 | 运镜 | 色调 | 转场 | 特效 |
|---|---|---|---|---|---|---|---|---|---|
| 34 | 3:25.6–3:33.2 | 7.6s | `sunrise` | 28_sunrise.jpg | Sun rising over the curve of the Earth | 推近 1.04→1.22 | 日出暖金 | 叠化 | 光晕 |
| 35 | 3:32.2–3:39.2 | 7.0s | `futureearth` | 29_futureearth.jpg | Future Earth ringed with orbital structures | 推近 1.06→1.24 · 旋转 1.5° | 日出暖金 | 叠化 | — |
| 36 | 3:38.2–3:42.9 | 4.7s | `moonbase` | 30_moonbase.jpg | Permanent Moon base | 右移 | 科技冷蓝 | 叠化 | — |
| 37 | 3:41.9–3:47.7 | 5.8s | `marscity` | 31_marscity.jpg | Domed city on Mars | 推近 1.04→1.20 | 东方琥珀金 | 叠化 | — |
| 38 | 3:46.7–3:54.5 | 7.8s | `starship` | 32_starship.jpg | Starship leaving the solar system | 推近 1.04→1.30 | 深空黑蓝 | 叠化 | 震动 |
| 39 | 3:54.4–4:02.5 | 8.1s | `spaceport` | 33_spaceport.jpg | Crowds of humanity at an Eastern space port | 拉远 1.20→1.04 | 东方琥珀金 | 硬切 | 招牌模糊 |

## 尾声（4:01.5–4:30.7）

| # | 时间 | 时长 | 镜头 | 素材 | 画面 | 运镜 | 色调 | 转场 | 特效 |
|---|---|---|---|---|---|---|---|---|---|
| 40 | 4:01.5–4:18.7 | 17.2s | `child` | 34_child.jpg | A child in a space station looking at Earth | 推近 1.00→1.22 · 上摇 | 温柔蓝白 | 叠化 | — |
| 41 | 4:17.7–4:25.7 | 8.0s | `eye` | 35_eye.jpg | Earth's blue light reflected in the child's eye | 推近 1.00→1.30 | 温柔蓝白 | 叠化 | 光晕 |
| 42 | 4:23.3–4:30.7 | 7.4s | `end` | 01_cosmos.jpg | Back to the cosmos for the end card | 推近 1.10→1.20 · 旋转 0.5° | 深空黑蓝 | 叠化 | 星空视差、压暗 |

## 字幕时间轴（与 narration.srt 一致）

| # | 开始 | 结束 | 字幕 | 备注 |
|---|---|---|---|---|
| 1 | 0:02.6 | 0:06.6 | 过去，人类最大的梦想，是改变世界。 | 原稿 |
| 2 | 0:08.0 | 0:12.2 | 未来，人类可能开始改变自己。 | 原稿 |
| 3 | 0:36.8 | 0:40.6 | 人类第一次创造了一种新的智能。 | 原稿 |
| 4 | 0:42.0 | 0:45.6 | 它不需要生命，却能够学习。 | 原稿 |
| 5 | 0:47.6 | 0:51.6 | 智能，正在与意识分道扬镳。 | 补充旁白 ☆ |
| 6 | 0:53.0 | 0:57.0 | 算法，也许会比你自己更了解你。 | 补充旁白 ☆ |
| 7 | 1:02.8 | 1:08.8 | 当机器开始理解世界，人类的位置将发生什么变化？ | 原稿 |
| 8 | 1:18.0 | 1:21.8 | 过去，人类接受自然赋予的生命。 | 原稿 |
| 9 | 1:23.4 | 1:27.2 | 未来，人类可能开始设计生命。 | 原稿 |
| 10 | 1:28.8 | 1:33.0 | 四十亿年来，生命一直由自然选择塑造。 | 补充旁白 ☆ |
| 11 | 1:34.4 | 1:38.6 | 如今，智能设计开始取代自然选择。 | 补充旁白 ☆ |
| 12 | 1:46.0 | 1:52.6 | 疾病、衰老，甚至身体本身，都可能成为可以修改的对象。 | 原稿 |
| 13 | 1:54.2 | 1:59.2 | 新的人类议程：长生不死、幸福快乐、化身为神。 | 补充旁白 ☆ |
| 14 | 2:07.6 | 2:11.6 | 身体的边界，正在被重新定义。 | 补充旁白 ☆ |
| 15 | 2:20.0 | 2:23.8 | 如果意识可以被复制。 | 原稿 |
| 16 | 2:25.8 | 2:29.4 | 如果记忆可以被保存。 | 原稿 |
| 17 | 2:30.0 | 2:34.0 | 如果生命可以无限延续。 | 原稿 |
| 18 | 2:35.2 | 2:40.2 | 我们还是原来的自己吗？ | 原稿 |
| 19 | 2:42.4 | 2:47.0 | 但还有一个问题：这样的未来，会属于每个人吗？ | v2 新增 🆕 |
| 20 | 2:48.6 | 2:54.6 | 当算法承担越来越多工作，一些人可能难以在经济体系中重新找到位置。 | v2 新增 🆕 |
| 21 | 2:55.2 | 2:59.4 | 赫拉利将这种风险称为“无用阶级”。 | v2 新增 🆕 |
| 22 | 3:00.8 | 3:04.6 | 这里的“无用”，指劳动可能不再被需要， | v2 新增 🆕 |
| 23 | 3:04.9 | 3:08.0 | 绝不意味着人失去了价值。 | v2 新增 🆕 |
| 24 | 3:08.6 | 3:13.4 | 如果少数人获得升级生命的能力，更多人却被留在身后， | v2 新增 🆕 |
| 25 | 3:13.7 | 3:17.6 | 技术的进步，将把我们带向怎样的社会？ | v2 新增 🆕 |
| 26 | 3:18.4 | 3:21.2 | 当我们追问人类能成为什么， | v2 新增 🆕 |
| 27 | 3:21.5 | 3:25.2 | 也必须追问：谁能共享这个未来？ | v2 新增 🆕 |
| 28 | 3:32.6 | 3:36.2 | 未来最大的挑战。 | 原稿 |
| 29 | 3:37.6 | 3:41.6 | 不是机器是否会超越人类。 | 原稿 |
| 30 | 3:43.3 | 3:47.7 | 而是当我们拥有创造神的能力。 | 原稿 |
| 31 | 3:49.1 | 3:53.9 | 是否仍然知道如何成为人？ | 原稿 |
| 32 | 3:56.3 | 4:01.1 | 智人，也许正在走向“神人”。 | 补充旁白 ☆ |
| 33 | 4:12.9 | 4:17.3 | 下一章人类历史。 | 结尾字幕 |
| 34 | 4:17.7 | 4:22.3 | 正在等待我们书写。 | 结尾字幕 |

## 章节卡 / 画面标注 / 闪白

- 章节卡 `0:30.8–0:35.2` 第一章「智能革命」
- 章节卡 `1:12.4–1:16.8` 第二章「生命重塑」
- 章节卡 `2:01.4–2:06.0` 第三章「人与机器融合」
- 章节卡 `3:26.4–3:31.0` 第四章「人类的新纪元」
- 标注 `0:18.6–0:22.4` 近未来 · 太空电梯 · 连接地球与轨道
- 标注 `2:14.2–2:18.0` 未来 · 地下城
- 标注 `3:39.4–3:42.6` 未来 · 月球基地 · 永久前哨
- 标注 `3:43.4–3:47.0` 未来 · 火星城市 · 第二家园
- 片名卡 `0:22.6–0:27.6`，片尾卡 `4:24.1–4:30.1`
- 闪白 `0:13.0`、`0:30.4`、`1:12.0`、`2:01.0`、`3:26.1`、`3:54.5`

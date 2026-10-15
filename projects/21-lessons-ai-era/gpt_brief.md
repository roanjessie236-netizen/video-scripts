# 素材端任务书（可直接复制给 GPT）

---

你负责为 2K 纪录短片《今日简史：AI时代，人类如何重新定义自己》生成图片、搜集网络素材。完整需求在同目录的 `asset_requirements.md`，共 56 个镜头，编号 S001–S056。

## 1. 制作方式

- 按编号逐条制作。【生成】镜头：使用该镜头的“提示词”，并在末尾附上统一风格后缀
- 【网络】镜头：按“搜索”关键词寻找实拍视频或照片
- 【生成/网络】两者皆可，写在前面的优先
- 时间轴、片名、章节卡、字幕、光效、转场由剪辑端制作，不需要提供

统一风格后缀：

```
cinematic documentary still, photorealistic, shot on ARRI Alexa with anamorphic lens, 16:9, natural film grain, BBC documentary realism, volumetric light, epic civilisation scale, keep the bottom fifth of the frame dark and uncluttered, no text, no letters, no logos, no watermark
```

## 2. 规格

- 画幅 16:9；生成图片 ≥2560×1440，建议 3840×2160
- 网络视频 ≥1920×1080（建议 4K），长度 ≥ 镜头时长 + 2 秒，无水印
- 网络图片宽度 ≥2560
- 图片 JPG（质量 ≥90）或 PNG；视频 MP4
- 主体放在画面中部 80% 以内，四边各留约 10% 裁切余量

## 3. 字幕留白

- A：所有镜头画面下方 22% 保持较暗、干净，不放人脸、手、关键物体、强光源
- B（S007、S008、S018、S029、S041、S056）：画面中央留出暗部或负空间，用于片名和章节卡
- C（S008–S010）：画面下方 35% 干净，用于时间轴动画

## 4. 固定角色

- 劳动者（S023、S025、S026、S027）：约 50 岁东亚男性，花白短发，藏青色工装外套
- 画家（S037–S040）：约 40 岁东亚女性，齐耳短发，亚麻围裙
- 宇航员（S050、S052、S055）：白色舱外航天服，金色面罩，无任何标志或国旗
- 同一角色请保持脸型、发型、服装一致；所有人物均为成年人

## 5. 文件命名

- 图片：`S001.jpg`；视频：`S001.mp4`
- 同一镜头的多个备选：`S001_a.jpg`、`S001_b.jpg`
- 补单返修：`S001_r1.jpg`、`S001_r2.jpg`
- 不要改号、合并编号，也不要用其他编号的素材替代

## 6. 来源记录

网络素材请填写 `sources.csv`，每个文件一行：

```
编号,文件名,来源网站,原始链接,作者,授权协议,下载日期
```

推荐来源：Pexels、Pixabay、Wikimedia Commons（公有领域 / CC0 / CC BY）、NASA Image and Video Library（公有领域，使用时不得暗示 NASA 背书）。不要使用带水印、仅限编辑用途或授权不明的素材。

## 7. 交付前自检

- [ ] 16:9，分辨率达标
- [ ] 底部字幕区干净（以及需要的 B / C 区）
- [ ] 无可读文字、伪文字、Logo、水印、品牌、名人肖像
- [ ] 人物均为成年人，固定角色外观一致
- [ ] 手指、面部、建筑结构无畸形
- [ ] 网络素材已记录来源与授权

## 8. 交付方式

- 建议分四批打包为 zip：S001–S017、S018–S028、S029–S040、S041–S056
- 每批附上 `sources.csv` 和 `delivery_note.md`
- 发送到 Notion AI 对话，或提交到 GitHub `projects/21-lessons-ai-era/assets/`
- 做不了的镜头请在 `delivery_note.md` 写明“S0xx 缺失：原因”，剪辑端会列入补单并保留原编号

---

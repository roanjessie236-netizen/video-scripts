# 未来简史 v2 · 旁白配音

- lines.json：34 句旁白（对应 v2 字幕），每句带语速 rate、音高 pitch、音量 vol 和情绪提示 cue；‖ 表示戏剧性停顿。
- tts_edge.py：用 edge-tts 逐句合成男声旁白（默认 zh-CN-YunjianNeural），在 ‖ 处切开并插入停顿，输出 01.wav–34.wav。需要联网。
- 混音用 projects/sapiens-70000-years/voiceover/mix_voice.py。

```
pip install edge-tts
python3 tts_edge.py lines.json clips
python3 mix_voice.py homo_deus_future_v2.mp4 narration.srt clips homo_deus_future_v2_vo.mp4
```

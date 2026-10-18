import asyncio, json, sys, edge_tts
V = {
 'v0': '真正的问题，不是我们想成为什么，而是——我们究竟应该想要什么？',
 'v1': '真正的问题，不是我们想成为，什么，而是——我们究竟应该想要什么？',
 'v2': '真正的问题，不是我们想“成为”什么，而是——我们究竟应该想要什么？',
 'v3': '真正的问题，不是我们想成为 什么，而是——我们究竟应该想要什么？',
 'v4': '真正的问题，不是我们想成为、什么，而是——我们究竟应该想要什么？',
 'v5': '真正的问题，不是我们想成为——什么，而是——我们究竟应该想要什么？',
}
async def run(k, t):
    c = edge_tts.Communicate(t, 'zh-CN-YunjianNeural', rate='-5%', pitch='+0Hz', volume='+3%', boundary='WordBoundary')
    wb = []
    with open(k + '.mp3', 'wb') as f:
        async for ch in c.stream():
            if ch['type'] == 'audio': f.write(ch['data'])
            elif ch['type'] == 'WordBoundary': wb.append((round(ch['offset']/1e7, 3), round((ch['offset']+ch['duration'])/1e7, 3), ch['text']))
    json.dump(wb, open(k + '.wb.json', 'w'), ensure_ascii=False)
    return k, wb
async def main():
    for k, t in V.items():
        k, wb = await run(k, t)
        print(k, ' '.join('%s[%.2f-%.2f]' % (w, a, b) for a, b, w in wb[:9]))
asyncio.run(main())

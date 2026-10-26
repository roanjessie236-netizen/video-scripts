const { chromium } = require('playwright');
(async () => {
  const b = await chromium.connectOverCDP(process.env.AGENT_BROWSER_CDP);
  const ctx = b.contexts()[0] || await b.newContext();
  const out = {};
  for (const p of [1, 2]) {
    const page = await ctx.newPage();
    try {
      await page.goto(`https://www.bilibili.com/video/BV1kf4y1a7Hm?p=${p}`, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await page.waitForFunction(() => window.__playinfo__ && window.__playinfo__.data, null, { timeout: 30000 });
      out[p] = await page.evaluate(() => { const a = window.__playinfo__.data.dash.audio.sort((x, y) => y.bandwidth - x.bandwidth)[0]; return { url: a.baseUrl || a.base_url, bw: a.bandwidth, dur: window.__playinfo__.data.dash.duration }; });
    } catch (e) { out[p] = { err: String(e).slice(0, 200) }; }
    await page.close();
  }
  require('fs').writeFileSync('/tmp/vo/burls.json', JSON.stringify(out));
  console.log(JSON.stringify(Object.fromEntries(Object.entries(out).map(([k, v]) => [k, { bw: v.bw, dur: v.dur, err: v.err }]))));
  process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });

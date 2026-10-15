// Measure flyer layout for PPTX building; optionally screenshot the empty image slot.
// Usage: node tools/measure.js <url> <boxes.json> [placeholder.png] [preview.png]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [url, out, ph, preview] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 2200 }, deviceScaleFactor: 2 });
  await p.goto(url);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  const data = await p.evaluate(() => {
    const o = document.getElementById('poster').getBoundingClientRect();
    const r = el => { const b = el.getBoundingClientRect(); return { x: b.left - o.left, y: b.top - o.top, w: b.width, h: b.height }; };
    const q = s => [...document.querySelectorAll(s)].map(r);
    return {
      poster: { w: o.width, h: o.height },
      logo: q('.logo')[0], eyebrow: q('.eyebrow')[0],
      title: q('.title')[0], subtitle: q('.subtitle')[0], brand: q('.brand')[0], season: q('.season')[0],
      cards: q('.card'), media: q('.card .media'),
      imgs: [...document.querySelectorAll('.card img')].map(i => ({ ...r(i), src: i.getAttribute('src') })),
      feature: q('.feature')[0], fk: q('.feature .k')[0], fbig: q('.feature .big')[0], frame: q('.frame')[0],
      brandText: document.querySelector('.feature .k').textContent.trim(),
      bigText: document.querySelector('.feature .big').innerText.split('\n').slice(1).join(' ').trim(),
    };
  });
  fs.writeFileSync(out, JSON.stringify(data));
  if (ph) await p.locator('.card .placeholder').first().screenshot({ path: ph });
  if (preview) await p.locator('#poster').screenshot({ path: preview });
  await b.close();
})();

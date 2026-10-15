// Render the multi-page Instagram Story: page 1 = New Arrivals cover, then one outfit per page
// (every image in instagram/images, sorted by name). Writes story/_NN.png for flatten_story.py.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const dir = __dirname, out = path.join(dir, 'story');
fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out);
const images = fs.readdirSync(path.join(dir, 'images')).filter(f => /\.(png|jpe?g|webp)$/i.test(f)).sort();
const bgFile = path.join(dir, 'images', 'bg.json');
const bg = fs.existsSync(bgFile) ? JSON.parse(fs.readFileSync(bgFile)) : {};
const pages = [{ type: 'cover' }, ...images.map((f, i) => ({ type: 'look', src: 'images/' + f, n: i + 1, bg: bg[f] }))];
(async () => {
  const browser = await chromium.launch();
  for (const [i, pg] of pages.entries()) {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 2 });
    await page.addInitScript(p => { window.PAGE = p; }, pg);
    await page.goto('file://' + path.join(dir, 'story.html'));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForLoadState('networkidle');
    await page.locator('#story').screenshot({ path: path.join(out, `_${String(i + 1).padStart(2, '0')}.png`) });
    await page.close();
  }
  await browser.close();
  console.log(`rendered ${pages.length} page(s)`);
})();

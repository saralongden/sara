// Render the Instagram post to flat, single-layer high-res files for Canva.
// Usage: node instagram/build.js            (uses every image in instagram/images, sorted by name)
// Files named *-photo.* are treated as lifestyle shots (fill the tile); others as product shots.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const dir = __dirname, imgDir = path.join(dir, 'images');
const images = fs.readdirSync(imgDir).filter(f => /\.(png|jpe?g|webp)$/i.test(f)).sort()
  .map(f => ({ src: 'images/' + f, photo: /-photo\./i.test(f) }));
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  await page.addInitScript(i => { window.IMAGES = i; }, images);
  await page.goto('file://' + path.join(dir, 'post.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForLoadState('networkidle');
  await page.locator('#post').screenshot({ path: path.join(dir, '_raw.png') });
  await browser.close();
  console.log(`rendered ${images.length} image(s)`);
})();

// Measure every [data-x] element inside #post (text / rect / image) with its computed style,
// for tools/html_to_pptx.py. Usage: node tools/measure_html.js <page.html> <out.json>
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [src, out] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2000, height: 3000 } });
  await p.goto('file://' + path.resolve(src), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const data = await p.evaluate(() => {
    const post = document.querySelector('#post');
    const o = post.getBoundingClientRect();
    const els = [...post.querySelectorAll('[data-x]')].map(el => {
      const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
      const base = { kind: el.dataset.x, x: r.left - o.left, y: r.top - o.top, w: r.width, h: r.height };
      if (base.kind === 'text') {
        return { ...base, text: el.innerText, font: cs.fontFamily.split(',')[0].replace(/["']/g, ''),
          size: parseFloat(cs.fontSize), weight: parseInt(cs.fontWeight), italic: cs.fontStyle === 'italic',
          color: cs.color, spacing: parseFloat(cs.letterSpacing) || 0, align: cs.textAlign,
          lineHeight: parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2 };
      }
      if (base.kind === 'image') return { ...base, src: el.getAttribute('src'), fit: el.dataset.fit || 'cover', radius: parseFloat(cs.borderTopLeftRadius) || 0 };
      return { ...base, fill: cs.backgroundColor, radius: parseFloat(cs.borderTopLeftRadius) || 0,
        border: parseFloat(cs.borderTopWidth) ? { w: parseFloat(cs.borderTopWidth), c: cs.borderTopColor } : null };
    });
    return { w: o.width, h: o.height, bg: getComputedStyle(post).backgroundColor, els };
  });
  require('fs').writeFileSync(out, JSON.stringify(data, null, 1));
  await b.close();
})();

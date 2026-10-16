// Render print-ready PDFs of size-charts/womens-pant-size-chart.html at several trim sizes,
// each as a trim-size PDF and a PDF with 3 mm bleed on every side.
// Usage: node tools/print_size_chart.js <out_dir>
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BLEED = 3; // mm
const SIZES = [
  // name, trim w/h in mm, virtual layout width in mm (design is drawn at this width then scaled), compact layout
  { name: 'A4', w: 210, h: 297, v: 210 },
  { name: 'A5', w: 148, h: 210, v: 210 },
  { name: '5x7in', w: 127, h: 177.8, v: 210, css: '.page { padding-top:18mm; padding-bottom:21mm; } .rule { margin:11mm 0 6mm; }' },
  { name: '8x10cm', w: 80, h: 100, v: 150, compact: true },
];

const COMPACT = `
  .page { padding:9mm 8mm 7mm; }
  .page::before { inset:4mm; }
  .logo .word { font-size:30pt; }
  .logo .on { gap:3mm; margin:0.5mm 0 1mm; }
  .logo .on span { font-size:20pt; }
  .logo .small, .logo .since { font-size:7pt; letter-spacing:.3em; }
  .logo .since { margin-top:1mm; }
  .logo .course { padding-left:8mm; }
  .rule { margin:5mm 0 4mm; }
  h1 { font-size:13pt; letter-spacing:.25em; padding-left:.25em; }
  .sub { margin-top:2mm; font-size:7pt; letter-spacing:.3em; }
  table { margin-top:5mm; }
  thead th { font-size:7pt; letter-spacing:.12em; padding:2.8mm .3mm; }
  thead th.brand { font-size:6.5pt; letter-spacing:0; }
  thead tr.group th { font-size:6.5pt; letter-spacing:.25em; padding:0 0 1.5mm; }
  tbody td { font-size:14pt; padding:2.7mm .3mm; }
  .note { display:none; }
  .foot { padding-top:3mm; gap:2mm; }
  .foot .t { font-size:6.5pt; letter-spacing:.3em; }
`;

(async () => {
  const out = process.argv[2];
  fs.mkdirSync(out, { recursive: true });
  const src = 'file://' + path.resolve(__dirname, '../size-charts/womens-pant-size-chart.html');
  const b = await chromium.launch();
  for (const s of SIZES) {
    for (const bleed of [0, BLEED]) {
      const p = await b.newPage();
      await p.goto(src, { waitUntil: 'networkidle' });
      await p.evaluate(() => document.fonts.ready);
      const vh = s.v * s.h / s.w;
      await p.addStyleTag({ content: `
        @page { size: ${s.w + 2 * bleed}mm ${s.h + 2 * bleed}mm; margin: 0; }
        body { margin:0; }
        .sheet { width:${s.w + 2 * bleed}mm; height:${s.h + 2 * bleed}mm; padding:${bleed}mm; background:var(--pearl); overflow:hidden; }
        .page { width:${s.v}mm; height:${vh}mm; margin:0; zoom:${s.w / s.v}; }
        ${s.compact ? COMPACT : ''}
        ${s.css || ''}` });
      await p.evaluate(() => {
        const pg = document.querySelector('.page');
        const sheet = document.createElement('div'); sheet.className = 'sheet';
        pg.replaceWith(sheet); sheet.appendChild(pg);
      });
      const file = path.join(out, `womens-pant-size-chart-${s.name}${bleed ? '-3mm-bleed' : ''}.pdf`);
      await p.pdf({ path: file, width: `${s.w + 2 * bleed}mm`, height: `${s.h + 2 * bleed}mm`, printBackground: true, preferCSSPageSize: true });
      await p.close();
      console.log(file);
    }
  }
  await b.close();
})();

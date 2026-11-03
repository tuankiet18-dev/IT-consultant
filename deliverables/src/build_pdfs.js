// Renders journey.html and context.html to PDF (A4 landscape). Run: NODE_PATH=$(npm root -g) node build_pdfs.js
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  for (const [src, out] of [['journey.html', 'User Journey.pdf'], ['context.html', 'System Context Diagram.pdf']]) {
    await p.goto('file://' + path.resolve(__dirname, src)); await p.waitForLoadState('networkidle');
    await p.pdf({path: path.resolve(__dirname, '..', out), format: 'A4', landscape: true, printBackground: true, preferCSSPageSize: true});
    console.log('wrote', out);
  }
  await b.close();
})();

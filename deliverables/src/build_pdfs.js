// Renders journey.html and context.html to PDF (A4 landscape) and, with SHOTS=dir, page PNGs for visual checks.
// Run: NODE_PATH=<folder with playwright or playwright-core> node build_pdfs.js
// Set CHROME_PATH if Playwright's own Chromium is not installed.
const path = require('path');
const fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('playwright-core')); }
const chrome = process.env.CHROME_PATH
  || (process.env.USERPROFILE && path.join(process.env.USERPROFILE, 'AppData/Local/ms-playwright/chromium-1223/chrome-win64/chrome.exe'));
(async () => {
  const opts = chrome && fs.existsSync(chrome) ? { executablePath: chrome } : {};
  const b = await chromium.launch(opts);
  const p = await b.newPage({ viewport: { width: 1123, height: 794 } });
  const jobs = [['journey.html', 'User Journey.pdf'], ['context.html', 'System Context Diagram.pdf']];
  const only = process.env.ONLY;
  for (const [src, out] of jobs) {
    if (only && !src.startsWith(only)) continue;
    await p.goto('file://' + path.resolve(__dirname, src));
    await p.waitForLoadState('networkidle');
    await p.evaluate(() => document.fonts.ready);
    await p.pdf({ path: path.resolve(__dirname, '..', out), format: 'A4', landscape: true, printBackground: true, preferCSSPageSize: true });
    const pages = await p.evaluate(() => document.querySelectorAll('.page').length);
    console.log('wrote', out, 'pages in html:', pages);
    if (process.env.SHOTS) {
      fs.mkdirSync(process.env.SHOTS, { recursive: true });
      const els = await p.$$('.page');
      for (let i = 0; i < els.length; i++) await els[i].screenshot({ path: path.join(process.env.SHOTS, `${src.replace('.html', '')}-${i + 1}.png`) });
    }
  }
  await b.close();
})();

// node page/og.js -> docs/og.png, the picture shown when someone shares a link (needs Playwright)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 640 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'og.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(__dirname, '..', 'docs', 'og.png') }); await b.close(); console.log('built docs/og.png');
})();

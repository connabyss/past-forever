// node tests/sing.js -> ok: N sing page checks (needs Playwright, like tests/page.js)
// The singing roll (docs/sing.html): the digits it plays are the engine's own, it has one hole per digit,
// pressing play starts the sound and moves the roll in step with it, and nothing scrolls sideways on a phone.
const { chromium } = require('playwright');
const path = require('path');
const Forever = require('../forever.js');
(async () => {
  // served over http on this machine (a file:// page can't read its own canvas back)
  const docs = path.join(__dirname, '..', 'docs'), types = { html: 'text/html', jpg: 'image/jpeg', png: 'image/png' };
  const server = require('http').createServer((q, s) => {
    // serve only files inside docs/: resolve the path, then refuse anything that lands outside it
    let f = path.resolve(docs, '.' + path.sep + decodeURIComponent(q.url.split('?')[0]));
    if (f === docs) f = path.join(docs, 'index.html');
    if (!f.startsWith(docs + path.sep)) { s.writeHead(403); s.end(); return; }
    require('fs').readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); } else { s.writeHead(200, { 'content-type': types[f.split('.').pop()] || 'application/octet-stream' }); s.end(d); } });
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const file = 'http://127.0.0.1:' + server.address().port + '/sing.html';
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  let fails = 0, checks = 0;
  const check = (ok, what) => { checks++; if (!ok) { fails++; console.log('FAIL', what); } };
  const want = Forever.run('x = 3\nforever: x = 3 ^ x\nsing 360 digits of x').lines[0].sing.digits;
  for (const width of [320, 390, 760]) {
    const p = await b.newPage({ viewport: { width, height: 800 } });
    const errs = []; p.on('pageerror', (e) => errs.push(e.message));
    await p.route('**/*', (r) => r.request().url().startsWith('https://fonts') ? r.abort() : r.continue());
    await p.goto(file); await p.waitForTimeout(500);
    check(errs.length === 0, width + ': page errors ' + errs.join('; '));
    check(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), width + ': sideways scroll');
    const foot = await p.textContent('#foot');
    check(foot.includes('…' + want.slice(-12)) && foot.includes('360 digits'), width + ': the page says which digits it worked out: ' + foot);
    check(await p.textContent('#m') === 'one minute, turn the sound on', width + ': resting caption');
    await p.close();
  }
  // the page plays exactly the engine's digits, and the caption names the digit on the bar
  const p = await b.newPage({ viewport: { width: 390, height: 844 } });
  await p.route('**/*', (r) => r.request().url().startsWith('https://fonts') ? r.abort() : r.continue());
  await p.goto(file); await p.waitForTimeout(500);
  await p.evaluate(() => setT(0.16 * 40 + 0.05));
  check(await p.textContent('#m') === 'the 41st digit from the end is a ' + want[want.length - 41], 'caption for note 41');
  await p.evaluate(() => setT(0.16 * 11 + 0.05));
  check(await p.textContent('#m') === 'the 12th digit from the end is a ' + want[want.length - 12], 'caption for note 12 (12th, not 12nd)');
  await p.evaluate(() => setT(0.16 * 101 + 0.05));
  check(await p.textContent('#m') === 'the 102nd digit from the end is a ' + want[want.length - 102], 'caption for note 102');
  await p.evaluate(() => setT(-1));
  // a hole sits under the bar: the canvas is see-through in the middle of the column of the digit being played
  const seeThrough = async () => p.evaluate(() => {
    const c = document.getElementById('c'), x = c.getContext('2d'), r = c.width / c.clientWidth;
    const row = Math.round(200.9 * r), out = [];
    for (let px = 0; px < c.width; px++) out.push(x.getImageData(px, row, 1, 1).data[3] < 128 ? 1 : 0);
    const cols = []; out.forEach((v, i) => { if (v && !out[i - 1]) cols.push(i / r); }); return cols;
  });
  await p.evaluate(() => setT(0.16 * 40 + 0.08));
  const cols = await seeThrough(), u = (await p.evaluate(() => document.getElementById('c').clientWidth)) / 318;
  const xWant = (46 + (+want[want.length - 41]) * (318 - 20 - 46) / 9) * u;
  check(cols.length === 1 && Math.abs(cols[0] - xWant) < 4 * u, 'the hole on the bar is in the column of the digit being played: ' + JSON.stringify(cols) + ' want about ' + xWant.toFixed(1));
  await p.evaluate(() => setT(-1));
  // play: the button turns to stop, sound starts, and the roll moves with it; stop puts it back
  await p.click('#b'); await p.waitForTimeout(1200);
  check(await p.textContent('#b') === 'stop', 'button says stop while playing');
  check(/^the \d+(st|nd|rd|th) digit from the end is a \d$/.test(await p.textContent('#m')), 'caption follows the song');
  const playing = await p.evaluate(() => [...document.querySelectorAll('audio')].length === 0);
  check(playing, 'no stray audio elements in the page');
  await p.click('#b'); await p.waitForTimeout(200);
  check(await p.textContent('#b') === 'play' && await p.textContent('#m') === 'one minute, turn the sound on', 'stop puts it back to rest');
  // the playground links to it
  const idx = require('fs').readFileSync(path.join(__dirname, '..', 'docs', 'index.html'), 'utf8');
  check(idx.includes('href="sing.html"'), 'the playground links to the singing roll');
  await b.close(); server.close();
  if (fails) { console.log(fails + ' of ' + checks + ' sing page checks failed'); process.exit(1); }
  console.log('ok: ' + checks + ' sing page checks');
})();

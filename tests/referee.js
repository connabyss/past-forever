// The robot referee: random loops, every "settles" and "never settles" checked against plain arithmetic.
// Brute force works on the last D digits exactly; it is a check, not a proof.  Usage: node tests/referee.js [loops]
const F = require('../forever.js');
const LOOPS = Number(process.argv[2] || 3000);
let seed = 20261116; const rnd = (k) => { seed = (seed * 1103515245 + 12345) % 2147483648; return Math.floor(seed / 65536) % k; };
const lit = (v) => (v < 0n ? '(0 − ' + -v + ')' : String(v));
const pick = (xs) => xs[rnd(xs.length)];
const small = () => BigInt(rnd(21) - 10);
const coef = () => small() * pick([1n, 1n, 2n, 5n, 10n, 10n, 100n]);
const big = () => pick([1n, 1n, 1n, 10n ** BigInt(5 + rnd(30))]);

// each family gives: names, start values, update (a function on BigInt state, in loop order), and the source
const families = {
  square(){ const a = small() || 1n, b = coef(), c = small() * big(), x0 = small();
    return { vars: ['x'], start: { x: x0 }, src: 'x = ' + lit(x0) + '\nforever: x = ' + lit(a) + ' × x × x + ' + lit(b) + ' × x + ' + lit(c),
      step: (s, m) => { s.x = mod(a * s.x * s.x + b * s.x + c, m); } }; },
  liar(){ const c = BigInt(rnd(1000000)) * pick([1n, 1n, 10n]); return { vars: ['x'], start: { x: 0n }, src: 'x = 0\nforever: x = x × x + ' + c,
      step: (s, m) => { s.x = mod(s.x * s.x + c, m); } }; },
  linear(){ const a = coef(), b = small() * big(), x0 = small();
    return { vars: ['x'], start: { x: x0 }, src: 'x = ' + lit(x0) + '\nforever: x = ' + lit(a) + ' × x + ' + lit(b),
      step: (s, m) => { s.x = mod(a * s.x + b, m); } }; },
  pair(){ const [a, b, c, d] = [coef(), coef(), coef(), coef()], e = small(), f = small(), x0 = small(), y0 = small();
    return { vars: ['x', 'y'], start: { x: x0, y: y0 }, src: 'x = ' + lit(x0) + '\ny = ' + lit(y0) + '\nforever: x = ' + lit(a) + ' × x + ' + lit(b) + ' × y + ' + lit(e) + '   y = ' + lit(c) + ' × x + ' + lit(d) + ' × y + ' + lit(f),
      step: (s, m) => { s.x = mod(a * s.x + b * s.y + e, m); s.y = mod(c * s.x + d * s.y + f, m); } }; },
  relay(){ const k = pick([10n, 100n, 20n, 50n, 3n, 7n]), c = small(), x0 = small(), y0 = small();
    return { vars: ['x', 'y'], start: { x: x0, y: y0 }, src: 'x = ' + lit(x0) + '\ny = ' + lit(y0) + '\nforever: t = x   x = y   y = ' + k + ' × t + ' + lit(c),
      step: (s, m) => { const t = s.x; s.x = s.y; s.y = mod(k * t + c, m); } }; },
  sum(){ const p0 = small() || 1n, r = pick([10n, 100n, 20n, 50n, 2n, 3n, 5n]), x0 = small();
    return { vars: ['x', 'p'], start: { x: x0, p: p0 }, src: 'x = ' + lit(x0) + '\np = ' + lit(p0) + '\nforever: x = x + p   p = p × ' + r,
      step: (s, m) => { s.x = mod(s.x + s.p, m); s.p = mod(s.p * r, m); } }; },
  // towers: the loop's own number on top of a power.  The brute force only uses that B ^ λ = 1 for λ = λ(10^D)
  // (Carmichael's function), which divides 10^D; both facts are checked here for every loop, not assumed
  tower(){ const B = pick([3n, 7n, 9n, 11n, 13n, 17n, 21n, 3n, 7n, -3n]), a = pick([1n, 1n, 1n, 2n, 3n, -1n, 10n]), b = small(), c = pick([1n, 1n, 2n, 3n, -1n, 7n]), d = small(), x0 = small();
    const shape = rnd(3), top = shape === 0 ? 'x' : '(' + lit(a) + ' × x + ' + lit(b) + ')';
    const src = 'x = ' + lit(x0) + '\nforever: x = ' + lit(B) + ' ^ ' + top + (shape === 0 ? '' : ' × ' + lit(c) + ' + ' + lit(d)) + (shape === 2 ? ' + x' : '');
    return { vars: ['x'], start: { x: x0 }, src, tower: B,
      step: (s, m) => { const t = shape === 0 ? s.x : a * s.x + b; const p = powmodR(B, mod(t, m), m); s.x = shape === 0 ? p : mod(p * c + d + (shape === 2 ? s.x : 0n), m); } }; },
};
// towers whose bottom has a 2 or 5 in it (x = 2 ^ x, 10 ^ x …), run as extra loops on top of the families above.
// The numbers grow past any digit count after a few steps, and for a top t ≥ D, B ^ t has the same last D digits as
// B ^ (t mod λ + 10^D), with λ = λ(10^D) dividing 10^D.  That fact is checked for every loop here, not assumed.
const bigTower = () => { const B = pick([2n, 4n, 5n, 6n, 8n, 10n, 12n, 15n, 20n, 25n, 2n, 5n]), x0 = BigInt(rnd(11));
  return { vars: ['x'], start: { x: x0 }, src: 'x = ' + x0 + '\nforever: x = ' + B + ' ^ x', bigTower: B,
    step: (s, m) => { s.x = powmodR(B, s.x + m, m); } }; };
// loops that branch on their own last digits (is even, is odd, ends in …), run as extra loops too.  The brute force
// works on the last D digits only, which is exact here: each test reads at most its last 2 digits.
const branchy = () => {
  const d = pick(['0', '5', '1', '7', '25', '00', '36']);
  const [testSrc, test] = pick([['is even', (x) => x % 2n === 0n], ['is odd', (x) => x % 2n === 1n], ['ends in ' + d, (x) => x % 10n ** BigInt(d.length) === BigInt(d)]]);
  const rule = () => { const shape = rnd(3), a = coef(), b = small(), c = small();
    if (shape === 0) return { src: lit(a) + ' × x + ' + lit(b), f: (x) => a * x + b };
    if (shape === 1) return { src: 'x × x + ' + lit(c), f: (x) => x * x + c };
    return { src: lit(c || 1n) + ' × x × x + ' + lit(a) + ' × x', f: (x) => (c || 1n) * x * x + a * x }; };
  const r1 = rule(), r2 = rnd(4) ? rule() : null, x0 = small();
  return { vars: ['x'], start: { x: x0 }, src: 'x = ' + lit(x0) + '\nforever:\n  if x ' + testSrc + ': x = ' + r1.src + (r2 ? '\n  else: x = ' + r2.src : ''),
    step: (s, m) => { const x = mod(s.x, m); s.x = test(x) ? mod(r1.f(x), m) : r2 ? mod(r2.f(x), m) : x; } };
};
// y = k × y + (a settled endless number), k a multiple of 10: the brute force gets x's last D digits from its own loop
const tenMix = () => {
  const k = pick([10n, 20n, 100n, -10n, 30n]), a = small() || 1n, b = small(), y0 = small(), which = rnd(3);
  const xSrc = which === 0 ? 'x = 5\nforever: x = x × x' : which === 1 ? 'x = 6\nforever: x = x ^ 5' : 'x = 1 / 7';
  const xOf = (m) => { if (which === 2) return fracMod('1/7', m); let x = which ? 6n : 5n; for (let i = 0; i < 400; i++) x = which ? powmodR(x, 5n, m) : x * x % m; return x; };
  return { vars: ['y'], start: { y: y0 }, src: xSrc + '\ny = ' + lit(y0) + '\nforever: y = ' + lit(k) + ' × y + ' + lit(a) + ' × x + ' + lit(b), xOf,
    step: (s, m) => { s.xm = s.xm === undefined || s.mm !== m ? (s.mm = m, xOf(m)) : s.xm; s.y = mod(k * s.y + a * s.xm + b, m); } };
};
// a polynomial in y with an endless fixed number x in it (x from its own loop), and towers with 10 × x outside
const polyMix = () => {
  const [a, b, c, d] = [small(), coef(), small(), small() || 1n], y0 = small(), which = rnd(2);
  const xSrc = which === 0 ? 'x = 5\nforever: x = x × x' : 'x = 6\nforever: x = x ^ 5';
  const xOf = (m) => { let x = which ? 6n : 5n; for (let i = 0; i < 400; i++) x = which ? powmodR(x, 5n, m) : x * x % m; return x; };
  return { vars: ['y'], start: { y: y0 }, src: xSrc + '\ny = ' + lit(y0) + '\nforever: y = ' + lit(a) + ' + ' + lit(b) + ' × y + ' + lit(c) + ' × y × y + ' + lit(d) + ' × x',
    step: (s, m) => { if (s.mm !== m) { s.mm = m; s.xm = xOf(m); } s.y = mod(a + b * s.y + c * s.y * s.y + d * s.xm, m); } };
};
const towerTen = () => {
  const B = pick([3n, 7n, 9n, 11n, 13n]), k = pick([10n, -10n, 20n, 100n, 30n]), c = small(), x0 = small();
  return { vars: ['x'], start: { x: x0 }, src: 'x = ' + lit(x0) + '\nforever: x = ' + B + ' ^ x + ' + lit(k) + ' × x + ' + lit(c), tower: B,
    step: (s, m) => { s.x = mod(powmodR(B, mod(s.x, m), m) + k * s.x + c, m); } };
};
function powmodR(b, e, m) { let r = 1n; b = mod(b, m); while (e > 0n) { if (e & 1n) r = r * b % m; b = b * b % m; e >>= 1n; } return r; }
function carmichael10(D) { const two = D >= 3 ? 2n ** BigInt(D - 2) : D === 2 ? 2n : 1n, five = 4n * 5n ** BigInt(D - 1); const g = (x, y) => (y ? g(y, x % y) : x); return two * five / g(two, five); }
function mod(a, m) { const r = a % m; return r < 0n ? r + m : r; }
function fracMod(t, m) { const [p, q] = t.split('/').map(BigInt); if (!q) return mod(p, m); let inv = 1n, b = mod(q, m), e = m / 10n * 4n - 1n, base = b; while (e > 0n) { if (e & 1n) inv = inv * base % m; base = base * base % m; e >>= 1n; } return mod(p * inv, m); }

const tally = { settles: 0, 'never settles': 0, "can't see the end": 0, labels: 0 }, byFam = {};
let bad = 0;
const t0 = Date.now();
const names = Object.keys(families);
const EXTRA = Math.floor(LOOPS / 8), EXTRA2 = Math.floor(LOOPS / 8), EXTRA3 = Math.floor(LOOPS / 16), EXTRA4 = Math.floor(LOOPS / 16), EXTRA5 = Math.floor(LOOPS / 16);
const ALL = LOOPS + EXTRA + EXTRA2 + EXTRA3 + EXTRA4 + EXTRA5;
for (let i = 0; i < ALL; i++) {
  const c1 = LOOPS + EXTRA, c2 = c1 + EXTRA2, c3 = c2 + EXTRA3, c4 = c3 + EXTRA4;
  const fam = i < LOOPS ? names[i % names.length] : i < c1 ? 'bigtower' : i < c2 ? 'branch' : i < c3 ? 'tenmix' : i < c4 ? 'polymix' : 'towerten';
  const L = i < LOOPS ? families[fam]() : ({ bigtower: bigTower, branch: branchy, tenmix: tenMix, polymix: polyMix, towerten: towerTen })[fam]();
  const bigLen = Math.max(...(L.src.match(/\d+/g) || ['0']).map((d) => d.length));
  const D = 30 + bigLen, m = 10n ** BigInt(D);
  if (L.bigTower) { const lam = carmichael10(D); if (m % lam !== 0n || powmodR(L.bigTower, m + lam, m) !== powmodR(L.bigTower, m, m)) { bad++; console.log('LEMMA FAILS for ' + L.bigTower + ' at ' + D + ' digits'); continue; } }
  if (L.tower) { const lam = carmichael10(D); if (m % lam !== 0n || powmodR(L.tower, lam, m) !== 1n) { bad++; console.log('LEMMA FAILS for ' + L.tower + ' at ' + D + ' digits'); continue; } }
  const src = L.src + '\n' + L.vars.map((v) => 'show ' + v).join('\n');
  let lines; try { lines = F.run(src, { huntMs: 2000 }).lines; } catch (e) { bad++; console.log('CRASH ' + e.message + '\n' + src); continue; }
  // brute force: run long enough for digits that lock one per few steps, then see what the last D digits do
  const s = { ...L.start }; for (const v of L.vars) s[v] = mod(s[v], m);
  const steps = 8 * D + 400, tail = [];
  for (let j = 0; j < steps; j++) { L.step(s, m); if (j >= steps - 200) tail.push({ ...s }); }
  L.vars.forEach((v, vi) => {
    const got = lines[vi] && lines[vi].text || '';
    const still = tail.every((t) => t[v] === tail[0][v]);
    let verdict = got === 'never settles' ? 'never settles' : got === "can't see the end" ? "can't see the end" : 'settles';
    if (got.startsWith('stopped')) { bad++; console.log('STOPPED ' + got + '\n' + src); return; }
    tally[verdict]++; (byFam[fam] = byFam[fam] || { settles: 0, 'never settles': 0, "can't see the end": 0 })[verdict]++;
    if (verdict === 'never settles' && still) { bad++; console.log('WRONG: said never settles, but the last ' + D + ' digits of ' + v + ' stay put\n' + src); }
    if (verdict === 'settles') {
      if (!still) { bad++; console.log('WRONG: said settles, but ' + v + ' keeps changing in its last ' + D + ' digits\n' + src); return; }
      const digits = got.replace(/^…/, '').split(' ')[0];
      const shownLen = digits.length, mm = 10n ** BigInt(Math.min(shownLen, D));
      if (/^\d+$/.test(digits) && mod(BigInt(digits), mm) !== tail[0][v] % mm) { bad++; console.log('WRONG digits for ' + v + ': got ' + got + ', brute …' + String(tail[0][v]).slice(-shownLen) + '\n' + src); }
      const lab = got.match(/\(this is (-?\d+(?:\/\d+)?)\)/);
      if (lab) { tally.labels++; if (fracMod(lab[1], m) !== tail[0][v]) { bad++; console.log('WRONG label ' + lab[1] + ' for ' + v + '\n' + src); } }
      else if (!got.startsWith('…') && /^-?\d+$/.test(got) && mod(BigInt(got), m) !== tail[0][v]) { bad++; console.log('WRONG whole number ' + got + '\n' + src); }
    }
  });
}
const total = tally.settles + tally['never settles'] + tally["can't see the end"];
console.log('referee: ' + ALL + ' random loops, ' + total + ' answers: ' + tally.settles + ' settle, ' + tally['never settles'] + ' never settle, ' + tally["can't see the end"] + " can't see the end; " + tally.labels + ' exact fractions checked; ' + bad + ' wrong (' + ((Date.now() - t0) / 1000).toFixed(1) + ' s)');
for (const f of [...names, 'bigtower', 'branch', 'tenmix', 'polymix', 'towerten']) console.log('  ' + f.padEnd(7) + JSON.stringify(byFam[f]));
process.exit(bad ? 1 : 0);

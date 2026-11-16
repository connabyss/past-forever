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
};
function mod(a, m) { const r = a % m; return r < 0n ? r + m : r; }
function fracMod(t, m) { const [p, q] = t.split('/').map(BigInt); if (!q) return mod(p, m); let inv = 1n, b = mod(q, m), e = m / 10n * 4n - 1n, base = b; while (e > 0n) { if (e & 1n) inv = inv * base % m; base = base * base % m; e >>= 1n; } return mod(p * inv, m); }

const tally = { settles: 0, 'never settles': 0, "can't see the end": 0, labels: 0 }, byFam = {};
let bad = 0;
const t0 = Date.now();
const names = Object.keys(families);
for (let i = 0; i < LOOPS; i++) {
  const fam = names[i % names.length], L = families[fam]();
  const bigLen = Math.max(...(L.src.match(/\d+/g) || ['0']).map((d) => d.length));
  const D = 30 + bigLen, m = 10n ** BigInt(D);
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
console.log('referee: ' + LOOPS + ' random loops, ' + total + ' answers: ' + tally.settles + ' settle, ' + tally['never settles'] + ' never settle, ' + tally["can't see the end"] + " can't see the end; " + tally.labels + ' exact fractions checked; ' + bad + ' wrong (' + ((Date.now() - t0) / 1000).toFixed(1) + ' s)');
for (const f of names) console.log('  ' + f.padEnd(7) + JSON.stringify(byFam[f]));
process.exit(bad ? 1 : 0);

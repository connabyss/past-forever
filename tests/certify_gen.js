// Make N random one-number polynomial loops, run Past Forever on each, write JSON lines for tests/certify.py.
// Usage: node tests/certify_gen.js N seed | python3 tests/certify.py
// Each loop: x = p0/q0, forever: x = (c0 + c1 x + ... + cd x^d) / q   with q0, q not divisible by 2 or 5.
const F = require('../forever.js');
const N = Number(process.argv[2] || 1000); let seed = Number(process.argv[3] || 1);
const rnd = (k) => { seed = (seed * 1103515245 + 12345) % 2147483648; return Math.floor(seed / 65536) % k; };
const pick = (a) => a[rnd(a.length)], small = () => rnd(21) - 10;
const lit = (v) => (v < 0 ? '(0 − ' + -v + ')' : String(v));
const UNITS = [1, 1, 1, 1, 3, 7, 9, 11, 13, 21];
// a ring Past Forever says is proved ("And that is proved ... a ring of N endless numbers forever"), for certify.py to check
const provedRing = (r) => { const m = r.lines && r.lines[0] && /And that is proved.*a ring of (\d+) endless numbers forever/.exec(r.lines[0].why || ''); return m ? +m[1] : undefined; };
// node tests/certify_gen.js tests/certificates.jsonl: run the loops listed in that file instead of random ones
if (/\.jsonl$/.test(process.argv[2] || '')) {
  for (const line of require('fs').readFileSync(process.argv[2], 'utf8').split('\n').filter(Boolean)) {
    const L = JSON.parse(line); const r = F.run(L.src, { huntMs: 2000 });
    L.out = r.error ? 'stopped: ' + r.error : (r.lines[0] ? r.lines[0].text : ''); const ring = provedRing(r); if (ring) L.ring = ring; console.log(JSON.stringify(L));
  }
  process.exit(0);
}
// node tests/certify_gen.js towers: every tower x = b ^ x (b = 2..40, start 0..3) and every x = x ^ x (start 2..40)
if (process.argv[2] === 'towers') {
  const run = (L) => { const r = F.run(L.src, { huntMs: 2000 }); L.out = r.error ? 'stopped: ' + r.error : (r.lines[0] ? r.lines[0].text : ''); console.log(JSON.stringify(L)); };
  for (let b = 2; b <= 40; b++) for (let x0 = 0; x0 <= 3; x0++) run({ kind: 'tower', b, x0, src: `x = ${x0}\nforever: x = ${b} ^ x\nshow 60 digits of x\n` });
  for (let x0 = 2; x0 <= 40; x0++) run({ kind: 'selfpower', x0, src: `x = ${x0}\nforever: x = x ^ x\nshow 60 digits of x\n` });
  process.exit(0);
}
// node tests/certify_gen.js rings2: y leaning on a settled x. x settles (own square from 5, 1/7, 1/9 or −7/9); then
// y = y0, forever: y = (terms in x and y) / q, linear or square in y. Only loops Past Forever says never settle are
// written (that is what the checker certifies here: never settles, and any ring it calls proved).
if (process.argv[2] === 'rings2') {
  const XS = [{ cs: [0, 0, 1], q: 1, p0: 5, q0: 1, s: 'x = 5\nforever: x = x × x' }, { cs: [0, 2, -7], q: 1, p0: 3, q0: 1, s: 'x = 3\nforever: x = x × (2 − 7 × x)' },
    { cs: [-1, 10], q: 1, p0: 0, q0: 1, s: 'x = 0\nforever: x = 10 × x − 1' }, { cs: [7, 10], q: 1, p0: 0, q0: 1, s: 'x = 0\nforever: x = 10 × x + 7' }];
  const MON = [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2], [2, 1], [1, 2]];
  for (let i = 0; i < 400; i++) {
    const X = pick(XS), terms = [];
    for (const [a, b] of MON) { const c = pick([0, 0, 0, 1, -1, 2, -2, 3, 5, 10, small()]); if (c) terms.push([a, b, c]); }
    if (!terms.some(([, b]) => b)) terms.push([0, 1, -1]);
    const q = pick([1, 1, 1, 3, 7]), y0 = small();
    const body = terms.map(([a, b, c]) => lit(c) + ' × x'.repeat(a) + ' × y'.repeat(b)).join(' + ');
    const src = X.s + '\ny = ' + lit(y0) + '\nforever: y = ' + (q > 1 ? '(' + body + ') / ' + q : body) + '\nshow y\nwhy y\n';
    let r; try { r = F.run(src, { huntMs: 2000 }); } catch (e) { continue; }
    if (r.error || !r.lines[0] || r.lines[0].text !== 'never settles') continue;
    const ring = provedRing(r);
    console.log(JSON.stringify({ kind: 'ring2', xs: { cs: X.cs, q: X.q, p0: X.p0, q0: X.q0 }, ys: { terms, q, y0 }, src, out: r.lines[0].text, ...(ring ? { ring } : {}) }));
  }
  process.exit(0);
}
// node tests/certify_gen.js branch N: x = x0, forever: if TEST: x = f(x) [else: x = g(x)], TEST from ends in / is
// even / is odd, mixed with and, or, not (up to two levels).
if (process.argv[2] === 'branch') {
  const atom = () => { const d = pick(['0', '5', '1', '7', '25', '00', '36', '3', '9']); return rnd(3) ? { src: 'x ends in ' + d, t: ['ends', d] } : rnd(2) ? { src: 'x is even', t: ['mod2', 0] } : { src: 'x is odd', t: ['mod2', 1] }; };
  // written the way the language reads it: not binds tightest, then and, then or (no brackets needed)
  const lit1 = () => { const a = atom(); return rnd(3) ? a : { src: 'not ' + a.src, t: ['not', a.t] }; };
  const join = (op, parts) => parts.reduce((a, b) => ({ src: a.src + ' ' + op + ' ' + b.src, t: [op, a.t, b.t] }));
  const test = () => join('or', Array.from({ length: 1 + rnd(2) }, () => join('and', Array.from({ length: 1 + rnd(2) }, lit1))));
  const rule = () => { const s = rnd(3), a = pick([1, -1, 2, 3, 10, 11, -9, small()]), b = small(), c = small();
    const cs = s === 0 ? [b, a] : s === 1 ? [c, 0, 1] : [0, a, c || 1];
    return { cs, q: 1, src: cs.map((v, j) => lit(v) + ' × x'.repeat(j)).join(' + ') }; };
  const M = Number(process.argv[3] || 400);
  for (let i = 0; i < M; i++) {
    const T = test(), f = rule(), g = rnd(4) ? rule() : null, x0 = small();
    const src = 'x = ' + lit(x0) + '\nforever:\n  if ' + T.src + ': x = ' + f.src + (g ? '\n  else: x = ' + g.src : '') + '\nshow 60 digits of x\n';
    let out; try { const r = F.run(src, { huntMs: 2000 }); out = r.error ? 'stopped: ' + r.error : (r.lines[0] ? r.lines[0].text : ''); } catch (e) { out = 'crash: ' + e.message; }
    console.log(JSON.stringify({ kind: 'branch', test: T.t, then: { cs: f.cs, q: 1 }, ...(g ? { else: { cs: g.cs, q: 1 } } : {}), p0: x0, q0: 1, src, out }));
  }
  process.exit(0);
}
// node tests/certify_gen.js multi N: x = x0, y = y0, forever: x = f(x, y), then y = g(x, y); show x
if (process.argv[2] === 'multi') {
  const MON = [[0, 0], [1, 0], [0, 1], [1, 1], [2, 0], [0, 2]];
  const poly = () => { const t = []; for (const [i, j] of MON) { const c = pick([0, 0, 0, 1, -1, 2, 5, 10, -10, small()]); if (c) t.push([i, j, c]); } return t.length ? t : [[1, 0, 1]]; };
  const text = (t) => t.map(([i, j, c]) => lit(c) + ' × x'.repeat(i) + ' × y'.repeat(j)).join(' + ');
  const M = Number(process.argv[3] || 400);
  for (let i = 0; i < M; i++) {
    const f = poly(), g = poly(), x0 = small(), y0 = small();
    const src = 'x = ' + lit(x0) + '\ny = ' + lit(y0) + '\nforever:\n  x = ' + text(f) + '\n  y = ' + text(g) + '\nshow 60 digits of x\n';
    let out; try { const r = F.run(src, { huntMs: 2000 }); out = r.error ? 'stopped: ' + r.error : (r.lines[0] ? r.lines[0].text : ''); } catch (e) { out = 'crash: ' + e.message; }
    console.log(JSON.stringify({ kind: 'multi', f, g, x0, y0, src, out }));
  }
  process.exit(0);
}
for (let i = 0; i < N; i++) {
  const d = 1 + rnd(4), cs = [];
  for (let j = 0; j <= d; j++) cs.push(j === d ? (small() || 1) : pick([0, small(), small(), 10 * small(), 5 * small(), 2 * small()]));
  const q = pick(UNITS), p0 = small(), q0 = pick(UNITS);
  const terms = cs.map((c, j) => lit(c) + (j ? ' × ' + Array(j).fill('x').join(' × ') : '')).join(' + ');
  const src = 'x = ' + lit(p0) + (q0 > 1 ? ' / ' + q0 : '') + '\nforever: x = ' + (q > 1 ? '(' + terms + ') / ' + q : terms) + '\nshow 60 digits of x\n';
  let out, ring; try { const r = F.run(src, { huntMs: 2000 }); out = r.error ? 'stopped: ' + r.error : (r.lines[0] ? r.lines[0].text : ''); ring = provedRing(r); } catch (e) { out = 'crash: ' + e.message; }
  console.log(JSON.stringify({ cs, q, p0, q0, src, out, ...(ring ? { ring } : {}) }));
}

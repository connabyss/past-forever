// Make N random one-number polynomial loops, run Past Forever on each, write JSON lines for tests/certify.py.
// Usage: node tests/certify_gen.js N seed | python3 tests/certify.py
// Each loop: x = p0/q0, forever: x = (c0 + c1 x + ... + cd x^d) / q   with q0, q not divisible by 2 or 5.
const F = require('../forever.js');
const N = Number(process.argv[2] || 1000); let seed = Number(process.argv[3] || 1);
const rnd = (k) => { seed = (seed * 1103515245 + 12345) % 2147483648; return Math.floor(seed / 65536) % k; };
const pick = (a) => a[rnd(a.length)], small = () => rnd(21) - 10;
const lit = (v) => (v < 0 ? '(0 − ' + -v + ')' : String(v));
const UNITS = [1, 1, 1, 1, 3, 7, 9, 11, 13, 21];
for (let i = 0; i < N; i++) {
  const d = 1 + rnd(4), cs = [];
  for (let j = 0; j <= d; j++) cs.push(j === d ? (small() || 1) : pick([0, small(), small(), 10 * small(), 5 * small(), 2 * small()]));
  const q = pick(UNITS), p0 = small(), q0 = pick(UNITS);
  const terms = cs.map((c, j) => lit(c) + (j ? ' × ' + Array(j).fill('x').join(' × ') : '')).join(' + ');
  const src = 'x = ' + lit(p0) + (q0 > 1 ? ' / ' + q0 : '') + '\nforever: x = ' + (q > 1 ? '(' + terms + ') / ' + q : terms) + '\nshow 60 digits of x\n';
  let out; try { const r = F.run(src, { huntMs: 2000 }); out = r.error ? 'stopped: ' + r.error : (r.lines[0] ? r.lines[0].text : ''); } catch (e) { out = 'crash: ' + e.message; }
  console.log(JSON.stringify({ cs, q, p0, q0, src, out }));
}

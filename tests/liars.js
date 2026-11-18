// node tests/liars.js [depth] -> two checks of liars/records.txt that share no code with liars/search.py.
// 1. Brute force, base 10, no cleverness: every c from 1 to 10,000,000 ending in 2, 3, 7 or 8, how many digits it
//    stays calm for. The records found that way must be the first lines of the file, in order.
// 2. The same base-5 search, written again from scratch in JavaScript, down to `depth` digits (default 1000, the
//    whole file, about a minute; every build runs it). Every record it finds must match the file.
// 3. The last record, checked the plain way in base 10 at every depth from 1 to 1001 digits.
// Why the search skips nothing is written out in liars/WHY_SMALLEST.md.
const fs = require('fs'), path = require('path');
const DEPTH = Number(process.argv[2] || 1000);
const rows = fs.readFileSync(path.join(__dirname, '..', 'liars', 'records.txt'), 'utf8').split('\n')
  .filter((l) => l && !l.startsWith('#')).map((l) => l.split(' ')).map(([d, c]) => [Number(d), BigInt(c)]);
let bad = 0;
const fail = (msg) => { bad++; console.log('FAIL ' + msg); };

// steps for x -> x*x + c, from 0, to come round mod m (remember every value: plain and slow, on purpose)
function steps(c, m) { const seen = new Map(); let x = 0n, i = 0; while (!seen.has(x)) { seen.set(x, i++); x = (x * x + c) % m; } return i - seen.get(x); }

// 1. brute force in base 10
{
  const LIMIT = 10000000n, found = [];
  let best = 0;
  for (let c = 1n; c <= LIMIT; c++) {
    const last = c % 10n; if (last !== 2n && last !== 3n && last !== 7n && last !== 8n) continue;
    let calm = 0, m = 10n;
    while (steps(c, m) % 5 !== 0) { calm++; m *= 10n; }
    if (calm > best) { best = calm; found.push([calm, c]); }
  }
  const want = rows.filter(([, c]) => c <= LIMIT);
  if (JSON.stringify(found.map(String)) !== JSON.stringify(want.map(String))) fail('brute force below 10,000,000 found ' + found.join(' | ') + ', the file says ' + want.join(' | '));
  else console.log('brute force: every c up to 10,000,000, records ' + found.map(([, c]) => c).join(', ') + ': same as the file');
}

// 2. the base-5 search, written again: keep every remainder mod 5^k whose loop is calm for all of the last 1..k digits
{
  const period5 = (c, m) => { // Brent's cycle finder this time, a different method from the brute force above
    let power = 1, lam = 1, tort = 0n, hare = c % m;
    while (tort !== hare) { if (power === lam) { tort = hare; power *= 2; lam = 0; } hare = (hare * hare + c) % m; lam++; }
    return lam;
  };
  let calm = [2n, 3n], five = 5n, best = -1n;
  const mine = [];
  for (let k = 2; k <= DEPTH; k++) {
    const next = [];
    for (const r of calm) for (let d = 0n; d < 5n; d++) { const c = r + d * five; if (period5(c, five * 5n) % 5 !== 0) next.push(c); }
    five *= 5n; calm = next;
    const low = calm.reduce((a, b) => (b < a ? b : a));
    if (low !== best) { if (mine.length) mine[mine.length - 1][0] = k - 1; mine.push([k, low]); best = low; }
  }
  const want = rows.filter(([, c]) => mine.some(([, x]) => x === c));
  const upTo = mine.slice(0, -1);   // the last one's calm length is only known past DEPTH
  const fileUpTo = rows.slice(0, upTo.length);
  if (JSON.stringify(upTo.map(String)) !== JSON.stringify(fileUpTo.map(String))) fail('the JavaScript search disagrees with the file');
  else if (rows[upTo.length][1] !== mine[mine.length - 1][1]) fail('the JavaScript search ends on a different record');
  else console.log('base-5 search, written again in JavaScript: ' + mine.length + ' records down to ' + DEPTH + ' digits, all the same as the file (' + calm.length + ' calm remainders at the last depth)');
  void want;
}
// 3. the last record, checked the plain way in base 10 at EVERY depth from 1 to 1001 digits, then the break at 1002
{
  const [calmFor, c] = rows[rows.length - 1];
  let m = 10n, wrong = 0;
  const pers = [];
  for (let j = 1; j <= calmFor; j++) { const p = steps(c, m); if (j <= 3 || j > calmFor - 2) pers.push(j + ':' + p); if (p % 5 === 0) { wrong = j; break; } m *= 10n; }
  const broke = steps(c, m);
  if (wrong) fail('the last record goes wild at ' + wrong + ' digits, not after ' + calmFor);
  else if (broke % 5 !== 0) fail('the last record does not break at ' + (calmFor + 1) + ' digits (' + broke + ' steps)');
  else console.log('the last record (' + String(c).length + ' digits long): calm at every depth from 1 to ' + calmFor + ' digits, checked one by one in base 10 (' + pers.join(', ') + ' steps), then ' + broke + ' steps at ' + (calmFor + 1) + ': wild');
}
console.log(bad ? 'FAILED: ' + bad : 'ok: liars/records.txt checked three independent ways');
process.exit(bad ? 1 : 0);

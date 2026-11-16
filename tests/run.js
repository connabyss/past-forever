// node tests/run.js   ->  ok: N checks
const F = require('../forever.js'), fs = require('fs'), path = require('path');
let n = 0, bad = 0;
function is(got, want, label) { n++; if (got !== want) { bad++; console.log('FAIL ' + label + '\n   got : ' + JSON.stringify(got) + '\n   want: ' + JSON.stringify(want)); } }
function has(got, part, label) { n++; if (!String(got).includes(part)) { bad++; console.log('FAIL ' + label + '\n   got : ' + JSON.stringify(got) + '\n   want it to include: ' + part); } }
const out = (src) => F.text(src);
const ex = (f) => out(fs.readFileSync(path.join(__dirname, '..', 'examples', f), 'utf8'));

// ── the five programs CH was shown, word for word
is(ex('own_square.txt'), '…918212890625\nyes  (proved)', 'ex1');
is(ex('minus_one.txt'), '…999999999999  (this is -1)\n0', 'ex2');
is(ex('one_third.txt'), '…666666666667  (this is 1/3)\n1', 'ex3');
is(ex('past_forever.txt'), 'forever + 1\nforever × 2', 'ex4');
is(ex('search.txt'), "no  (proved)\ncan't see the end", 'ex5');

// ── digits checked against plain big-number arithmetic done a different way
function powmod(b, e, m) { let r = 1n; b %= m; while (e > 0n) { if (e & 1n) r = r * b % m; b = b * b % m; e >>= 1n; } return r; }
const pad = (x, k) => '…' + String(x).padStart(k, '0');
is(out('x = 5\nforever: x = x × x\nshow 80 digits of x'), pad(powmod(5n, 2n ** 400n, 10n ** 80n), 80), 'own square from 5, 80 digits');
is(out('x = 6\nforever: x = x × x\nshow x'), 'never settles', '6 squared forever does NOT settle (its last two digits go 36, 96, 16, 56)');
{ // the twin of the own-square number, reached by a better rule
  const m = 10n ** 60n, e = powmod(5n, 2n ** 400n, m), twin = ((1n - e) % m + m) % m;
  is(out('x = 6\nforever: x = 3 × x × x − 2 × x × x × x\nshow 60 digits of x\nshow x × x = x'), pad(twin, 60) + '\nyes  (proved)', 'the twin, from 6');
  is(out('x = 5\nforever: x = 3 × x × x − 2 × x × x × x\nshow 60 digits of x\nshow x × x = x'), pad(e, 60) + '\nyes  (proved)', 'the same rule from 5');
}
is(out('x = 25\nforever: x = x × x\nshow 30 digits of x'), pad(powmod(5n, 2n ** 400n, 10n ** 30n), 30), 'from 25 lands on the same number');
{ // 1/7 by a loop: x = x × (2 − 7x), start 3 (7×3 = 21)
  const m = 10n ** 50n; let inv = 1n; for (let i = 0n; i < m; i++) { if ((7n * i) % 10n === 1n) { inv = i; break; } }
  let x = 3n; for (let i = 0; i < 60; i++) x = ((x * (2n - 7n * x)) % m + m) % m;
  is((x * 7n) % m, 1n, 'self-check of the checker');
  is(out('x = 3\nforever: x = x × (2 − 7 × x)\nshow 50 digits of x'), pad(x, 50) + '  (this is 1/7)', '1/7 by a loop');
}
{ // sum of all factorials 1! + 2! + 3! + ...
  const m = 10n ** 40n; let s = 0n, f = 1n; for (let k = 1n; k <= 400n; k++) { f = f * k % m; s = (s + f) % m; }
  is(out('n = 0  f = 1  s = 0\nforever: n = n + 1   f = f × n   s = s + f\nshow f\nshow 40 digits of s'), '0\n' + pad(s, 40), 'factorials go to 0, their sum settles');
}
{ // two names feeding each other
  const e = powmod(5n, 2n ** 400n, 10n ** 30n);
  is(out('a = 5  b = 5\nforever: t = a   a = b × b   b = t × t\nshow 30 digits of a'), pad(e, 30), 'a pair that pull each other in');
}

// ── things that settle, exactly
is(out('x = 10\nforever: x = x × x\nshow x'), '0', '10 squared forever is 0');
is(out('x = 1\nforever: x = x × x\nshow x'), '1', '1 stays 1');
is(out('x = 0  p = 1\nforever: x = x + p   p = p × 10\nshow x\nshow x × 9 + 1'), '…111111111111  (this is -1/9)\n0', 'ones forever is -1/9');
is(out('x = 1  p = 1\nforever: p = p × 10   x = x + 3 × p × p\nshow x'), '…030303030301  (this is -67/33)', 'geometric with squares, later order');
is(out('x = 3\nforever: x = 10 × x + 3\nshow x\nshow x × 3'), '…333333333333  (this is -1/3)\n…999999999999  (this is -1)', 'threes forever');
is(out('x = 7\nforever: x = x mod 5\nshow x'), '2', 'settles by standing still');
is(out('x = 5\nforever: x = x × x\ny = x × 2\nshow y = x + x\nshow x × x × x = x\nshow x = 5\nshow (1 − x) × (1 − x) = 1 − x\nshow x × (1 − x)'), 'yes  (proved)\nyes  (proved)\nno  (proved)\nyes  (proved)\n0', 'algebra with the endless number');
is(out('x = 5  y = 0\nforever: x = x × x   y = x + 1\nshow y × y = 3 × y − 2'), 'yes  (proved)', 'a name remade from a settling one');

is(out('a = 5\nforever: a = a × a\nb = 6\nforever: b = 3 × b × b − 2 × b × b × b\nshow a + b\nshow a × b\nshow b = 1 − a'), '1\n0\nyes  (proved)', 'the twins add to 1 and multiply to 0');
is(out('a = 5\nforever: a = a × a\nb = 25\nforever: b = b × b\nshow a = b'), 'yes  (proved)', 'two loops landing on the same endless number');

// ── sums it works out exactly by finding what stays the same on every step
is(out('n = 0  f = 1  s = 0\nforever: n = n + 1   f = f × n   s = s + n × f\nshow s'), '…999999999999  (this is -1)', '1×1! + 2×2! + 3×3! + … = −1');
is(out('n = 0  f = 1  s = 0\nforever: s = s + (n × n + 1) × f   n = n + 1   f = f × n\nshow s'), '1', 'sum of (k²+1)×k! = 1');
is(out('n = 0  f = 1  s = 0\nforever: s = s + (n^3 − 4 × n + 1) × f   n = n + 1   f = f × n × n\nshow s'), '3', 'sum of (k³−4k+1)×(k!)² = 3');
is(out('n = 0  f = 1  s = 0\nforever: s = s + (n^4 + 10 × n − 3) × f   n = n + 1   f = f × n × n\nshow s'), '…999999999993  (this is -7)', 'sum of (k⁴+10k−3)×(k!)² = −7');
is(out('n = 0  f = 1  s = 0\nforever: s = s + (n^5 − 29 × n + 7) × f   n = n + 1   f = f × n × n\nshow s'), '18', 'sum of (k⁵−29k+7)×(k!)² = 18');
is(out('n = 0  f = 1  s = 0\nforever: s = s + (n^3 − 4 × n + 2) × f   n = n + 1   f = f × n × n\nshow s'), '…517069851821', 'one off, and it is no longer a whole number');
{ // the same three facts in plain whole numbers: the sum up to N is the answer plus a multiple of (N!)²
  const fact = (k) => { let r = 1n; for (let i = 2n; i <= k; i++) r *= i; return r; };
  for (const [P, val] of [[(k) => k ** 3n - 4n * k + 1n, 3n], [(k) => k ** 4n + 10n * k - 3n, -7n], [(k) => k ** 5n - 29n * k + 7n, 18n]]) {
    let s = 0n, good = true;
    for (let N = 1n; N <= 40n; N++) { s += P(N - 1n) * fact(N - 1n) ** 2n; if ((s - val) % (fact(N) ** 2n) !== 0n) good = false; }
    is(good, true, 'plain-number check of an exact sum');
  }
}
{ const m = 10n ** 40n; let p = 1n, f = 1n; for (let k = 1n; k <= 400n; k++) { f = f * k % m; p = p * (1n + f) % m; }
  is(out('n = 0  f = 1  p = 1\nforever: n = n + 1   f = f × n   p = p × (1 + f)\nshow 40 digits of p'), pad(p, 40), 'an endless product'); }
is(out('x = 2\nforever: x = x^5\nshow x^5 = x\ny = x^4\nshow y × y = y'), 'yes  (proved)\nyes  (proved)', 'fifth powers from 2');
is(out('x = 3\nforever: x = x^5\nshow x'), 'never settles', 'fifth powers from 3 only look settled for 4 digits');
has(F.text('x = 3\nforever: x = x^5\nshow x', { why: true }), 'the last 5 digits of x go round 85443, 35443', 'fifth powers from 3: the reason');
is(out('show 2^10\nshow (1 + 2)^3'), '1024\n27', 'powers');

// ── looking deeper at loops that go round: rings and liars
has(F.text('x = 0\nforever: x = x × x + 1\nwhy x'), 'going round a ring of 6 endless numbers', 'square and add 1: a ring of six');
has(F.text('x = 0\nforever: x = x × x + 6\nwhy x'), 'going round a ring of 3 endless numbers', 'square and add 6: a ring of three');
has(F.text('x = 0\nforever: x = x × x + 14557\nwhy x'), 'take 2, 2, 2, 2, 2, 2, 8, 8, 40, 200, 1000, 5000 steps', 'a liar: calm for 6 digits, then it breaks');
has(F.text('x = 0\nforever: x = x × x + 7\nwhy x'), 'take 2, 2, 8, 8, 40, 200, 1000, 5000 steps', 'square and add 7');
{ // brute force: steps for the last k digits of x = x² + c to come round, starting from 0
  const per = (c, k) => { const m = 10n ** BigInt(k); let x = 0n, i = 0; const seen = new Map(); while (!seen.has(x)) { seen.set(x, i++); x = (x * x + c) % m; } return i - seen.get(x); };
  is([1, 2, 3, 4, 5, 6, 7, 8, 9].map((k) => per(14557n, k)).join(', '), '2, 2, 2, 2, 2, 2, 8, 8, 40', 'brute-force check of the liar 14557');
  is([1, 2, 3, 4, 5, 6].map((k) => per(1n, k)).join(', '), '6, 6, 6, 6, 6, 6', 'brute-force check of the ring of six');
}

// ── things proved to never settle
is(out('x = 2\nforever: x = x × x\nshow x'), 'never settles', '2 squared forever');
has(F.text('x = 2\nforever: x = x × x\nshow x', { why: true }), 'the last 2 digits of x go round 16, 56, 36, 96 every 4 steps', '2 squared: the reason');
is(out('x = 3\nforever: x = x × x\nshow x'), 'never settles', '3 squared forever');
is(out('n = 0\nforever: n = n + 1\nshow n\nshow n + 1'), 'never settles\nnever settles', 'a plain counter never settles, and that spreads');
is(out('lamp = no\nforever: lamp = not lamp\nshow lamp'), 'never settles', "Thomson's lamp");
is(out('x = 27  found = no\nforever:\n    if x is even: x = x / 2\n    else: x = 3 × x + 1\n    if x = 1: found = yes\nshow found\nshow x'), 'yes  (proved)\nnever settles', 'Collatz from 27 reaches 1 and then goes round');
has(F.text('x = 27\nforever:\n    if x is even: x = x / 2\n    else: x = 3 × x + 1\nshow x', { why: true }), 'x goes round 4, 2, 1 without end', 'Collatz: the reason');
is(out('x = 0  s = 1\nforever: x = x + s   s = s × 3\nshow x'), 'never settles', 'adding powers of 3');

// ── counting past forever
is(out('show 1 + forever = forever\nshow forever + 1 = forever\nshow forever + 1 > forever\nshow 2 × forever = forever\nshow forever × 2 = forever'), 'yes\nno\nyes\nyes\nno', 'order of adding matters past forever');
is(out('count n = 0\nforever:\n    forever: n = n + 1\nshow n'), 'forever × forever', 'forever inside forever');
is(out('count n = 0\nforever:\n    forever: n = n + 1\n    n = n + 5\nshow n\nn = n + 3\nforever: n = n + 2\nshow n'), 'forever × forever\nforever × forever + forever', 'a finite step is swallowed');
is(out('count n = 7\nforever: n = n + 3\nshow n\nshow n × 2\nshow n × forever\nshow (n + 4) × 3'), 'forever\nforever × 2\nforever × forever\nforever × 3 + 4', 'count arithmetic');
is(out('count n = forever\nshow n − 1'), 'stopped: there is no step just before forever, so that cannot be taken away', 'no step before forever');
is(out('count hits = 0  n = 0\nforever: n = n + 1   if n × n ends in 9: hits = hits + 1\nshow hits'), 'forever', 'squares ending in 9: without end');
is(out('count hits = 0  n = 0\nforever: n = n + 1   if n × n ends in 7: hits = hits + 1\nshow hits'), '0', 'squares ending in 7: none');
is(out('count hits = 0  x = 3\nforever:\n    if x ends in 3: hits = hits + 1\n    x = x × 10\nshow hits\nshow x'), '1\n0', 'happens once, block form');

// ── searches that run forever
is(out('found = no  n = 0\nforever: n = n + 1   if n × n = 2: found = yes\nshow found'), 'no  (proved)', 'no whole number squares to 2');
is(out('found = no  n = 0\nforever: n = n + 1   if n × n = 49: found = yes\nshow found'), 'yes  (found at step 7)', 'found by looking');
is(out('found = no  p = 1\nforever: p = p × 2   if p ends in 3: found = yes\nshow found'), 'no  (proved)', 'no power of 2 ends in 3');
is(out('found = no  p = 1\nforever: p = p × 2   if p ends in 2024: found = yes\nshow found'), 'no  (proved)', 'no power of 2 ends in 2024');
is(out('found = no  p = 1\nforever: p = p × 2   if p ends in 736: found = yes\nshow found'), 'yes  (found at step 36)', 'a power of 2 ending in 736');
is(out('found = no  p = 1\nforever: p = p × 7   if p ends in 99999: found = yes\nshow found'), 'no  (proved)', 'powers of 7');
is(out('found = no  a = 1  b = 1\nforever: t = a + b   a = b   b = t   if b × b = 2 × a × a + 7: found = yes\nshow found'), 'yes  (found at step 3)', 'found among Fibonacci numbers');
is(out('found = no  n = 0\nforever: n = n + 1   if (n × n − 13) × (n × n − 17) × (n × n − 221) = 0: found = yes\nshow found'), "can't see the end", 'honest when it cannot tell (this one has a match on every clock but none in whole numbers)');

// ── after a loop it could not see through
is(out('x = 196\nforever: x = x + backwards(x)\nshow x\nshow x + 1\nshow x = 5'), "can't see the end\ncan't see the end\ncan't see the end", 'the unseen spreads');
is(out('x = 196\nforever: x = x + backwards(x)\ny = 0\nforever: y = y + x\nshow y'), "can't see the end", 'a loop leaning on the unseen');

// ── plain arithmetic
is(out('show 2 + 3 × 4\nshow (2 + 3) × 4\nshow 7 − 10\nshow 1 / 3\nshow 1 / 3 + 2 / 3\nshow 10 / 2\nshow 17 mod 5'), '14\n20\n…999999999997  (this is -3)\n…666666666667  (this is 1/3)\n1\n5\n2', 'sums');
is(out('show 1 / 2'), 'stopped: 2 does not go into 1. Here you can divide by anything except what has a 2 or a 5 left over underneath', '1/2 does not exist here');
is(out('x = 5\nforever: x = x × x\nshow x < 3'), 'stopped: endless numbers have no bigger or smaller, only the same or different', 'no order on endless numbers');
is(out('show y'), 'stopped: line 1: y has no value yet', 'unknown name');
is(out('x = 3\nrepeat 4: x = x × x\nshow x\nshow backwards(1230)\nshow 12321 is a palindrome'), '43046721\n321\nyes', 'repeat and helpers');
is(out('a = 4\nif a is even: show 1\nelse: show 2\nif a is odd: show 1 else: show 2'), '1\n2', 'if and else');
is(out('n = 0\nforever: n = n + 1   show n'), '1\n2\n3\n4\n… and so on, forever', 'show inside forever');

// ── random loops: every "settled" and every "never settles" is checked by brute force
{
  let seed = 12345; const rnd = (k) => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed % k; };
  let settled = 0, restless = 0, unseen = 0;
  for (let trial = 0; trial < 400; trial++) {
    const f = trial % 2 ? 1 : [5, 10, 2][rnd(3)];
    const a = (rnd(21) - 10) * f, b = (rnd(21) - 10) * f, c = rnd(21) - 10, x0 = rnd(40) - 10;
    const src = 'x = ' + (x0 < 0 ? '0 − ' + -x0 : x0) + '\nforever: x = ' + (a < 0 ? '0 − ' + -a : a) + ' × x × x + ' + (b < 0 ? '0 − ' + -b : b) + ' × x + ' + (c < 0 ? '0 − ' + -c : c) + '\nshow 25 digits of x';
    const got = out(src).split('  (')[0];
    const m = 10n ** 25n; let x = BigInt(x0); const tail = [];
    for (let i = 0; i < 700; i++) { x = (((BigInt(a) * x * x + BigInt(b) * x + BigInt(c)) % m) + m) % m; if (i >= 600) tail.push(x); }
    const still = tail.every((t) => t === tail[0]);
    if (got === 'never settles') { restless++; n++; if (still) { bad++; console.log('FAIL said never settles but brute force settles:\n' + src); } }
    else if (got === "can't see the end") unseen++;
    else {
      settled++; n++;
      const want = /^\d+$/.test(got) ? got : null;
      const brute = pad(tail[0], 25);
      if (!still || (want === null ? got !== brute : BigInt(want) % m !== tail[0])) { bad++; console.log('FAIL settled value wrong:\n' + src + '\n got ' + got + '\n brute ' + brute + ' still=' + still); }
    }
  }
  n++; if (settled < 40 || restless < 40) { bad++; console.log('FAIL random loops too one-sided: settled ' + settled + ', restless ' + restless + ', unseen ' + unseen); }
  console.log('random loops: ' + settled + ' settled, ' + restless + ' never settle, ' + unseen + " can't see the end (all settled / never-settles answers brute-force checked)");
}

// ── hunt: one line tries a whole range and sorts the answers
{
  const H = (body, lo = 0, hi = 99) => 'hunt c from ' + lo + ' to ' + hi + ':\n    ' + body.split('\n').join('\n    ');
  is(out(H('x = 0\nforever: x = x × x + c\nshow x')),
    'hunt c from 0 to 99: tried 100 numbers, 5 kinds of answer\n' +
    '  settles     10   0, 10, 20, 30, 40, 50, 60, 70, …\n' +
    '  ring of 6   10   1, 11, 21, 31, 41, 51, 61, 71, …\n' +
    '  goes wild   40   2, 3, 7, 8, 12, 13, 17, 18, …\n' +
    '  ring of 2   30   4, 5, 9, 14, 15, 19, 24, 25, …\n' +
    '  ring of 3   10   6, 16, 26, 36, 46, 56, 66, 76, …', 'hunt: liar loops sort by last digit');
  // every square checked one by one against the same program written without hunt
  const r = F.run(H('x = 0\nforever: x = x × x + c\nshow x', 0, 59)), items = r.lines[0].hunt.items;
  is(items.length, 60, 'hunt: one item per number');
  for (const it of items) {
    const single = F.run('x = 0\nforever: x = x × x + ' + it.c + '\nshow x').lines[0];
    const kind = single.text === 'never settles' ? (/ring of (\d+)/.test(single.why) ? 'ring of ' + single.why.match(/ring of (\d+)/)[1] : /take [\d, ]+ steps/.test(single.why) ? 'goes wild' : 'never settles') : "can't see the end" === single.text ? "can't see the end" : 'settles';
    is(it.group, kind, 'hunt agrees with the single loop for c = ' + it.c);
    if (it.value !== undefined) is(it.value, single.text, 'hunt value for c = ' + it.c);
  }
  // yes / no answers, and names from outside the hunt
  is(out('k = 3\nhunt c from 1 to 6:\n    show c × k ends in 2'), 'hunt c from 1 to 6: tried 6 numbers, 2 kinds of answer\n  no   5   1, 2, 3, 5, 6\n  yes  1   4', 'hunt: yes/no and an outside name');
  // the hunt leaves nothing behind
  is(out('x = 7\nhunt c from 0 to 3:\n    x = c\n    show x\nshow x'), 'hunt c from 0 to 3: tried 4 numbers, 1 kind of answer\n  settles  4   0, 1, 2, 3\n7', 'hunt: names inside do not leak out');
  has(out('hunt c from 0 to 3:\n    x = c'), 'a hunt needs a show line inside it', 'hunt: needs a show');
  has(out('hunt c from 5 to 3:\n    show c'), 'at least as big', 'hunt: backwards range');
  has(out('hunt c from 0 to 5000:\n    show c'), 'at most 2000', 'hunt: range cap');
  has(out('hunt c from 0 to 3:\n    show c +'), 'line 2', 'hunt: a typo is still a typo');
  has(F.text(H('x = c + 89\nforever: x = x + backwards(x)\nshow x', 0, 50), { huntMs: 300 }), 'ran out of time after c = ', 'hunt: time budget');
  is(out('hunt c from 1 to 3: show c × c'), 'hunt c from 1 to 3: tried 3 numbers, 1 kind of answer\n  settles  3   1, 2, 3', 'hunt on one line');
  // the dividing hunt: 1/3 when c ends in 7, and a half-and-third mix when c is even
  const t = F.run(H('x = c\nforever: x = x × (2 − 3 × x)\nshow x', 0, 99)).lines[0].hunt;
  is(t.items.filter((x) => x.group === 'settles').map((x) => Number(x.c) % 10).every((d) => d === 0 || d === 2 || d === 7), true, 'hunt thirds: settles only for c ending in 0, 2 or 7');
  is(t.items.find((x) => x.c === '7').value, '…666666666667  (this is 1/3)', 'hunt thirds: 7 lands on 1/3');
}

// ── hunt ... ends in: look only at numbers ending in some digits (the zoom)
{
  const r = F.run('hunt c from 0 to 9 ends in 57:\n    show c'), h = r.lines[0].hunt;
  is(h.items.map((x) => x.c).join(','), '57,157,257,357,457,557,657,757,857,957', 'ends in: the numbers tried');
  is(r.lines[0].text.split('\n')[0], 'hunt c from 0 to 9 ends in 57: tried 10 numbers, 1 kind of answer', 'ends in: head line');
  is(F.run('hunt c from 0 to 2 ends in 007:\n    show c').lines[0].hunt.items.map((x) => x.c).join(','), '7,1007,2007', 'ends in: leading zeros count');
  is(out('show 57 ends in 7'), 'yes', 'ends in still works as a test');
  const z = F.run('hunt c from 0 to 99 ends in 557:\n    x = 0\n    forever: x = x × x + c\n    show x').lines[0].hunt.items;
  const tame = (it) => { let t = 0; while (t < it.wild.length && it.wild[t] === it.wild[0]) t++; return t; };
  const best = z.filter((x) => x.wild).sort((a, b) => tame(b) - tame(a))[0];
  is(best.c + ':' + tame(best), '14557:6', 'zooming on ...557 finds the record liar 14557');
}

// ── looking deeper goes 40 digits, not 9: a 10-digit liar is not mistaken for a ring (CH found this by zooming)
{
  const w = F.run('x = 0\nforever: x = x × x + 406530182\nshow x').lines[0].why;
  has(w, 'take 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8, 8, 40', '406530182 keeps a ring for 10 digits, then goes wild');
  const h = F.run('hunt c from 0 to 99 ends in 6530182:\n    x = 0\n    forever: x = x × x + c\n    show x').lines[0].hunt;
  is(h.groups.map((g) => g.label + ' ' + g.count).join(', '), 'goes wild 100', 'the zoomed view ending in 6530182 has no fake rings');
  has(F.run('x = 0\nforever: x = x × x + 1\nshow x').lines[0].why, 'the last 1 to 40 digits all come round every 6 steps', 'a true ring is checked 40 digits deep');
}

// ── Break it #1 (Leo AI): a loop that starts on its own answer settles at once, proved by the rule, not digits
{
  const E = 'e = 5\nforever: e = e × e\nf = 1 - e\n';
  is(out(E + 'y = f\nforever: y = y × y\nshow y'), '…081787109376', "squaring the 6-twin forever settles (it is already its own square)");
  has(F.run(E + 'y = f\nforever: y = y × y\nshow y').lines[0].why, 'gives back exactly what it started with', 'and it says why');
  is(out(E + 'y = e\nforever: y = y × y\nshow y'), '…918212890625', 'same for the 5-twin');
  is(out(E + 'r = e - f\nforever: r = r × r × r\nshow r'), '…836425781249', 'the odd square root of 1 is still under cubing');
  is(out(E + 'r = e - f\nforever: r = r × r\nshow r'), '1', 'squaring the odd square root of 1 settles on 1 after one step');
  is(out(E + 'a = e\nb = f\nforever: t = a   a = b   b = t\nshow a'), 'never settles', 'swapping the twins forever never settles');
  is(out(E + 'y = e + 1\nforever: y = y × y\nshow y'), "can't see the end", 'a start that is not at rest is not claimed');
  is(out(E + 'y = e\nforever: show y   y = y × y').split('\n')[1], '… and so on, forever', 'a show inside still prints');
}

// ── Break it #2 (GPT Luna): a big number can hide what happens past 40 digits, so look as deep as the loop's own numbers
{
  const M = '1' + '0'.repeat(40);
  const r = F.run('M = ' + M + '\nx = 0\nforever: x = (M + 1) × x + M\nshow x').lines[0];
  is(r.text, 'never settles', "Luna's loop: the 41st digit goes round, so it never settles");
  has(r.why, 'the last 40 digits of x stay put, but the digit to their left goes round 0, 1, 2, 3, 4, 5, 6, 7, 8, 9', 'and it names the digit that moves');
  is(out('M = ' + M + '\nx = 1 + M\nforever: x = x × x\nshow x'), 'never settles', '1 + M squared forever: digit 41 goes 2, 4, 8, 6');
  is(out('M = ' + M + M + '\nx = 0\nforever: x = (M + 1) × x + M\nshow x'), 'never settles', 'the same trick 81 digits deep');
  is(out('M = ' + M + '\nx = 0\nforever: x = M × x + 1\nshow x').split('  ')[0], '…000000000001', 'a big multiplier that pulls digits together still settles');
}

console.log(bad ? 'FAILED: ' + bad + ' of ' + n + ' checks' : 'ok: ' + n + ' checks');
process.exit(bad ? 1 : 0);

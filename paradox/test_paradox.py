"""Checks for PARADOX. Run from the repo root: python3 paradox/test_paradox.py   (needs: pip install z3-solver)
Each example must give exactly the timelines below, and every answer is re-checked with plain arithmetic.
Add --slow to also rebuild the autogram (about 30 to 60 seconds) and re-count its letters.
"""
import subprocess, sys, re
ok = True
def run(args):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True, timeout=600).stdout
def expect(name, cond, detail):
    global ok
    print(('ok    ' if cond else 'FAIL  ') + name + ('' if cond else '   ' + detail)); ok &= bool(cond)

out = run(['paradox/paradox.py', 'paradox/examples/grandfather.px'])
expect('grandfather: no consistent timeline', 'PARADOX! No consistent timeline exists' in out, out)

out = run(['paradox/paradox.py', 'paradox/examples/factor.px'])
p, q = map(int, re.search(r'p = (\d+), q = (\d+)', out).groups())
expect('factor: exactly one timeline', 'Exactly 1 consistent timeline' in out, out)
expect('factor: p x q = 1071514531, both > 1', p * q == 1071514531 and 1 < p <= q, f'{p} {q}')

out = run(['paradox/paradox.py', 'paradox/examples/self_describing.px'])
d = re.search(r'd = (\d+)', out).group(1)
expect('self-describing: exactly one timeline', 'Exactly 1 consistent timeline' in out, out)
expect('self-describing: digit i counts the i\'s', len(d) == 10 and all(int(d[i]) == d.count(str(i)) for i in range(10)), d)

out = run(['paradox/paradox.py', 'paradox/examples/square_root.px'])
xs = [int(v) for v in re.findall(r'x = (\d+)', out)]
expect('square root: exactly 4 timelines', 'Exactly 4 consistent timelines' in out and len(xs) == 4, out)
expect('square root: 1234 is one of them', 1234 in xs, str(xs))
expect('square root: every one squares to 1522756 in 64-bit arithmetic', all(x * x % 2 ** 64 == 1522756 and x < 2 ** 63 for x in xs), str(xs))

if '--slow' in sys.argv:
    out = run(['paradox/autogram.py'])
    sent = re.search(r'(This sentence was sent back.*?\.)\n', out).group(1)
    ones = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
    tens = dict(twenty=20, thirty=30, forty=40, fifty=50)
    def num(w): return sum(ones.index(p) if p in ones else tens[p] for p in w.split('-'))
    claims = {c: num(w) for w, c in re.findall(r"([a-z-]+) ([a-z])(?:'s)?(?=,| and|\.)", sent.split('contains', 1)[1])}
    expect('autogram: 26 claims, each equal to the real letter count', len(claims) == 26 and all(sent.lower().count(c) == n for c, n in claims.items()), sent)

print('PARADOX checks: ' + ('all ok' if ok else 'FAILED'))
sys.exit(0 if ok else 1)

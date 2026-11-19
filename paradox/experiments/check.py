"""Checks for the PARADOX experiments. Run from the repo root:

    python3 paradox/experiments/check.py          # about 15 seconds
    python3 paradox/experiments/check.py --slow   # adds the two wide runs, about 2.5 minutes

Each experiment is run, then its answers are re-derived here with plain Python arithmetic and an
exhaustive search, so nothing below trusts z3. Needs z3-solver.
"""
import itertools, re, subprocess, sys

ok = True
def expect(name, cond, detail=''):
    global ok
    print(('ok    ' if cond else 'FAIL  ') + name + ('' if cond else '   ' + str(detail)))
    ok &= bool(cond)

def run(path):
    return subprocess.run([sys.executable, 'paradox/paradox.py', path],
                          capture_output=True, text=True, timeout=900).stdout

def timelines(out):
    """Every printed timeline, as a dict of show-string -> int (so negatives come back negative)."""
    rows = []
    for line in out.split('\n'):
        m = re.match(r'\s+timeline \d+: (.*)$', line)
        if m:
            rows.append({k.strip(): int(v) for k, v in re.findall(r'([\w\[\]]+) = (-?\d+)', m.group(1))})
    return rows

def srem(a, b):
    """C's %, which is what `%` means here: the remainder keeps the sign of the dividend."""
    return abs(a) % abs(b) * (1 if a >= 0 else -1)

def signed_w(v, W):
    v %= 2 ** W
    return v - 2 ** W if v >= 2 ** (W - 1) else v

def idempotents(m):
    return sorted(x for x in range(m) if x * x % m == x)

# ------------------------------------------------------------- a theorem, proved by paradox
out = run('paradox/experiments/prove_no_cube.px')
expect('prove: the claim has no counterexample, so there is no timeline',
       'PARADOX! No consistent timeline exists' in out, out)
expect('prove: and indeed no 8-bit cube is 2 (checked all 256)',
       [a for a in range(256) if a ** 3 % 256 == 2] == [], 'found one')

# ------------------------------------------------------------- the same lines, the claim false
out = run('paradox/experiments/witness_cube_of_five.px')
rows = timelines(out)
expect('witness: exactly one timeline', 'Exactly 1 consistent timeline' in out and len(rows) == 1, out)
expect('witness: it is a real cube root of 5 mod 256',
       rows and rows[0]['a'] ** 3 % 256 == 5, rows)
expect('witness: and the only one (checked all 256)',
       rows and rows[0]['a'] == [a for a in range(256) if a ** 3 % 256 == 5][0], rows)

# ------------------------------------------------------------- code from the future
M = 256
def execute(prog, a):
    """The instruction set exactly as synthesize_times_three.px defines it."""
    t = 0
    for op in prog:
        if op == 0:   t = (t + a) % M
        elif op == 1: t = (t << 1) % M
        elif op == 2: t = t ^ a
        elif op == 3: t = (t + 1) % M
        elif op == 4: t = (t - a) % M
        else:         return None          # not an instruction
    return t

out = run('paradox/experiments/synthesize_times_three.px')
rows = timelines(out)
progs = [tuple(r[f'prog[{k}]'] for k in range(3)) for r in rows]
expect('synthesize: every timeline is a program of valid instructions',
       progs and all(all(0 <= op <= 4 for op in p) for p in progs), progs)
expect('synthesize: each one computes 3*a for all 256 inputs',
       progs and all(all(execute(p, a) == 3 * a % M for a in range(256)) for p in progs), progs)
correct = [p for p in itertools.product(range(5), repeat=3)
           if all(execute(p, a) == 3 * a % M for a in range(256))]
expect('synthesize: and they are all of them (125 candidates checked by brute force)',
       sorted(set(progs)) == sorted(correct), f'engine {sorted(set(progs))} vs brute {sorted(correct)}')

# ------------------------------------------------------------- fixed points of squaring
expect('bridge: mod 10^6 has exactly four fixed points (checked 0..999999)',
       idempotents(10 ** 6) == [0, 1, 109376, 890625], idempotents(10 ** 6))
expect('bridge: past-forever\'s two hero numbers end in two of them',
       str(918212890625).endswith('890625') and str(81787109376).endswith('109376'), '')

# ------------------------------------------------------------- the same, far too narrow
out = run('paradox/experiments/fixed_points_too_narrow.px')
got = sorted(r['x'] for r in timelines(out))
true5 = idempotents(10 ** 5)
expect('too narrow: it drops a real answer', 90625 not in got and 90625 in true5, got)
expect('too narrow: and prints a negative value that is not one of the answers mod 10^5',
       90625 not in got and any(x < 0 for x in got), got)
expect('too narrow: the ghost is not a solver mistake - it solves the signed, wrapping equation '
       'the file actually wrote', any(srem(signed_w(x * x, 32), 10 ** 5) == x for x in got if x < 0), got)
expect('too narrow: while still reporting "Exactly 4"', 'Exactly 4 consistent timelines' in out, out)

# ------------------------------------------------------------- the same, one bit short
if '--slow' in sys.argv:
    out = run('paradox/experiments/fixed_points_of_squaring.px')
    got = sorted(r['x'] for r in timelines(out))
    expect('44 bits: the time machine returns all four, without iterating',
           got == [0, 1, 109376, 890625], got)

    out = run('paradox/experiments/fixed_points_one_bit_short.px')
    got = sorted(r['x'] for r in timelines(out))
    expect('40 bits: 890625 * 890625 does fit in 40 bits', 890625 ** 2 < 2 ** 40, '')
    expect('40 bits: but it is negative as a signed 40-bit number', signed_w(890625 ** 2, 40) < 0, '')
    expect('40 bits: so the signed remainder cannot equal 890625',
           srem(signed_w(890625 ** 2, 40), 10 ** 6) != 890625, '')
    expect('40 bits: and exactly that answer is the missing one', got == [0, 1, 109376], got)

print('PARADOX experiment checks: ' + ('all ok' if ok else 'FAILED'))
sys.exit(0 if ok else 1)

"""Checks for the PARADOX experiments. Run from the repo root:

    python3 paradox/experiments/check.py          # about 15 seconds
    python3 paradox/experiments/check.py --slow   # adds the 40- and 44-bit runs, several minutes

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

# ------------------------------------------------------------- the same, in only 32 bits
# These two used to go wrong (the arithmetic wrapped, so 90625 / 890625 vanished and a negative ghost appeared).
# PARADOX's arithmetic is now exact, like Python's, so the narrow widths must give the true answers too.
out = run('paradox/experiments/fixed_points_too_narrow.px')
got = sorted(r['x'] for r in timelines(out))
expect('32 bits: x*x % 10^5 == x gives exactly the true four, 0, 1, 9376, 90625',
       got == idempotents(10 ** 5) == [0, 1, 9376, 90625] and 'Exactly 4 consistent timelines' in out, got)
expect('32 bits: no negative ghost (-87231 was the old wrong answer)', -87231 not in got and all(x >= 0 for x in got), got)

# ------------------------------------------------------------- bugs found by the Arena agent, now fixed
def all_rows(path): o = run(path); return o, timelines(o)
o, rows = all_rows('paradox/experiments/bugs/range_step.px')
expect('bug fixed: range(0, 6, 2) runs i = 0, 2, 4, so y = 3 in every timeline', rows and all(r['y'] == 3 for r in rows), o)
o, rows = all_rows('paradox/experiments/bugs/range_down.px')
expect('bug fixed: range(6, 0, -1) runs six times, no crash', rows and all(r['y'] == 6 for r in rows) and 'Traceback' not in o, o)
o, rows = all_rows('paradox/experiments/bugs/branch_leak.px')
expect('bug fixed: a name set only inside a branch has no value outside it; reading it crashes that timeline, '
       'so only x = 3 survives', 'Exactly 1 consistent timeline' in o and rows == [{'x': 3}], o)
o, rows = all_rows('paradox/experiments/bugs/branch_leak_fixed.px')
expect('the declared version agrees: only x = 3', 'Exactly 1 consistent timeline' in o and rows == [{'x': 3}], o)
o = run('paradox/experiments/bugs/negative_index.px')
expect('bug fixed: d[-1] is the last item, no crash', 'Traceback' not in o and 'consistent timeline' in o, o)
o = run('paradox/experiments/bugs/list_paradox.px')
expect('bug fixed: a list paradox is explained, not a crash', 'PARADOX! No consistent timeline exists' in o and 'd = [1, 0]' in o and 'Traceback' not in o, o)

# ------------------------------------------------------------- the same, in 40 and 44 bits
if '--slow' in sys.argv:
    out = run('paradox/experiments/fixed_points_of_squaring.px')
    got = sorted(r['x'] for r in timelines(out))
    expect('44 bits: the time machine returns all four, without iterating', got == [0, 1, 109376, 890625], got)
    out = run('paradox/experiments/fixed_points_one_bit_short.px')
    got = sorted(r['x'] for r in timelines(out))
    expect('40 bits: all four as well (890625 used to vanish here)', got == [0, 1, 109376, 890625], got)

print('PARADOX experiment checks: ' + ('all ok' if ok else 'FAILED'))
sys.exit(0 if ok else 1)

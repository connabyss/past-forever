"""Check the liars of other powers (liars/powers.py) the slow, plain way: base 10, one c at a time.

    python3 tests/powers.py        # about a minute

1. The 4th-power record liars from liars/powers.py match a brute force over every c below 4,000,000, and every line
   of liars/records4.txt up to 150 digits of calm is right in base 10 (calm for exactly that many digits).
2. 6th powers: every c below 15,625 either goes wild by its 3rd digit or stays calm for all 7 digits we look at.
3. 10th powers: no c below 3,125 goes wild in 7 digits.
4. The table: which even powers up to 26 can lie, as README.md says.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'liars'))
import powers  # noqa: E402

bad = 0


def fail(*a):
    global bad
    bad += 1
    print('FAIL', *a)


def period(c, m, p):
    seen, x = {}, 0
    while x not in seen:
        seen[x] = len(seen)
        x = (pow(x, p, m) + c) % m
    return len(seen) - seen[x]


def calm_digits(c, p, most):
    """How many decimal digits x = x^p + c stays calm for (no factor 5 in the steps to come round), up to most."""
    for j in range(1, most + 1):
        if period(c, 10 ** j, p) % 5 == 0:
            return j - 1
    return most


# 1. 4th powers: brute force records below 4,000,000 (c ending in 0, 4, 5 or 9 can't go wild: from 0 their last digit's
#    ring passes through 0, where the slope 4x^3 is 0)
best, brute = 0, []
for c in range(1, 4000000):
    if c % 5 in (0, 4):
        continue
    k = calm_digits(c, 4, 12)
    if k > best:
        best = k
        brute.append((k, c))
fast = [r for r in powers.records(4, 12) if r[1] < 4000000]
# a brute-force record is calm for k digits; the fast list gives exact calm, so compare the c values and the depths
if [c for _, c in brute] != [c for _, c in fast] or [k for k, _ in brute] != [k for k, _ in fast]:
    fail('4th-power records below 4,000,000:', brute, 'vs', fast)
rows = [tuple(map(int, line.split())) for line in (ROOT / 'liars' / 'records4.txt').read_text(encoding='utf-8').splitlines()
        if line and not line.startswith('#')]
if rows[:len(fast)] != fast:
    fail('liars/records4.txt does not start with the brute-force records', rows[:len(fast)], fast)
for calm, c in rows:
    if calm > 150:
        break
    got = calm_digits(c, 4, calm + 1)
    if got != calm:
        fail('records4.txt:', c, 'is calm for', got, 'digits, not', calm)

# 2. 6th powers: wild by the 3rd digit, or calm all the way (7 digits)
for c in range(15625):
    k = calm_digits(c, 6, 7)
    if 2 < k < 7:
        fail('6th powers:', c, 'stays calm for', k, 'digits and then goes wild')
    if (k == 7) != (c % 5 in (0, 1, 4)):
        fail('6th powers:', c, 'calm for', k, 'digits, but its last digit says otherwise')

# 3. 10th powers: never wild
for c in range(3125):
    if calm_digits(c, 10, 7) != 7:
        fail('10th powers:', c, 'goes wild')

# 4. the table
want = {2: 'can lie', 4: 'can lie', 6: 'at most 2', 8: 'can lie', 10: 'never', 12: 'can lie', 14: 'can lie',
        16: 'at most 2', 18: 'can lie', 20: 'never', 22: 'can lie', 24: 'can lie', 26: 'at most 3'}
for p, w in want.items():
    counts = [len(c) for _, c in powers.calm_sets(p, 25)]
    got = 'never' if not powers.wild_starts(p) else 'at most %d' % (len(counts) - 1) if counts[-1] == 0 else 'can lie'
    if got != w:
        fail('power', p, 'is', got, 'not', w)

if bad:
    print(bad, 'wrong')
    sys.exit(1)
print('ok: 4th-power records match a brute force below 4,000,000, records4.txt checked to 150 digits, 6th and 10th powers as said, table of 13 powers')

"""Check record liars the slow, plain way: in base 10, digit by digit, no cleverness.

    python3 liars/check.py            # checks every record in liars/records.txt (about 8 minutes)
    python3 liars/check.py 40         # only the records with up to 40 digits of calm
"""
import sys
from pathlib import Path


def period(c, m):
    seen, x = {}, 0
    while x not in seen:
        seen[x] = len(seen)
        x = (x * x + c) % m
    return len(seen) - seen[x]


def calm_digits(c, most):
    for j in range(1, most + 1):
        if period(c, 10 ** j) % 5 == 0:
            return j - 1
    return most


limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 9
rows = [line.split() for line in Path(__file__).with_name('records.txt').read_text(encoding='utf-8').splitlines()
        if line and not line.startswith('#')]
bad = 0
for calm, c in rows:
    calm, c = int(calm), int(c)
    if calm > limit:
        break
    got = calm_digits(c, calm + 1)
    if got != calm:
        bad += 1
        print('WRONG', c, 'is calm for', got, 'digits, not', calm)
print('checked', sum(1 for r in rows if int(r[0]) <= limit), 'records,', bad, 'wrong')

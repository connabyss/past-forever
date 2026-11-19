"""The four magnets, made precise and tested.

Loop: x = x * x + c from 0. "Calm for k digits" means the last k digits come round in a number of steps with no
factor 5, at every depth up to k. Only the 5s side can lie, so calm for k digits depends only on c mod 5^k, and
only c that is 2 or 3 mod 5 can lie at all (see liars/WHY_SMALLEST.md and "Why they lie" in liars/README.md).

Precise words:
- "c shares d digits with a" means c and a have the same last d digits in base 5, that is, 5^d divides c - a.
- The four magnets are four 5-adic numbers: -2, the two square roots of -1 (one ends in 2, one in 3 in base 5),
  and M, the other solution of f^10(0) = f^2(0) that ends in 2 in base 5 (f(x) = x * x + c).

The claim this file tests, for every depth k from 3 to 1000:
  every c that stays calm for k digits shares at least k - 2 base-5 digits with one of the four magnets,
  and from depth 5 on, k - 2 can't be raised (some calm c shares exactly k - 2).

What is proved and what is only checked:
- For c that is 3 mod 5, the proof sketch in liars/README.md says calm for k digits means 5^k divides
  f^4(0) - f^2(0) = c^3 (c + 1)^2 (c + 2)(c^2 + 1). c and c + 1 have no factor 5 then, so that is
  "5^k divides (c + 2)(c^2 + 1)", and since -2 and the root of -1 ending in 3 share only 1 digit, c shares at
  least k - 1 digits with one of them. This file checks that formula against the plain ring count.
- For c that is 2 mod 5 (the magnets sqrt(-1) ending in 2, and M), the k - 2 bound is only checked, here, to
  depth 1000. Nobody outside this project has reviewed any of it.

Run: python3 tests/magnets.py   (about 20 seconds; exits 1 on any failure)
"""
import sys

K = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
TOP = K + 2  # magnets are worked out 2 digits deeper than the deepest check
fails = []


def orbit(c, n, m):
    x = 0
    for _ in range(n):
        x = (x * x + c) % m
    return x


def ring_length(c, m):  # plain count: steps for 0's path mod m to come round
    seen, x = {}, 0
    while x not in seen:
        seen[x] = len(seen)
        x = (x * x + c) % m
    return len(seen) - seen[x]


def calm_by_rings(c, k):
    return all(ring_length(c, 5 ** j) % 5 for j in range(1, k + 1))


def calm_by_formula(c, k):  # 5^k divides f^4(0) - f^2(0) (c = 3 mod 5) or f^10(0) - f^2(0) (c = 2 mod 5)
    m = 5 ** k
    return (orbit(c, 4 if c % 5 == 3 else 10, m) - orbit(c, 2, m)) % m == 0


def shares(a, b, cap):
    d, v = (a - b) % 5 ** cap, 0
    if d == 0:
        return cap
    while d % 5 == 0:
        d //= 5
        v += 1
    return v


# 1. the formula agrees with the plain ring count for every residue mod 5^k, k <= 6
for k in range(1, 7):
    for c in range(5 ** k):
        if c % 5 in (2, 3) and calm_by_rings(c, k) != calm_by_formula(c, k):
            fails.append(f'formula and ring count disagree for c = {c} mod 5^{k}')
# 1b. for c = 3 mod 5 the formula is (c + 2)(c^2 + 1), every residue mod 5^8
for c in range(3, 5 ** 8, 5):
    if calm_by_formula(c, 8) != (((c + 2) * (c * c + 1)) % 5 ** 8 == 0):
        fails.append(f'c = {c}: (c + 2)(c^2 + 1) does not match')
print('ok: calm-for-k-digits formula matches the plain ring count (all residues, depth 6; 3 mod 5: depth 8)'
      if not fails else '\n'.join(fails))

# 2. every calm residue, depth by depth, to TOP (one base-5 digit at a time, nothing skipped)
calm, levels = [2, 3], {1: [2, 3]}
for k in range(2, TOP + 1):
    p = 5 ** (k - 1)
    calm = [r + j * p for r in calm for j in range(5) if calm_by_formula(r + j * p, k)]
    levels[k] = calm

# 3. the magnets, worked out on their own
P = 5 ** TOP


def sqrt_minus_one(last):
    x = last
    for k in range(2, TOP + 1):
        x = next(x + j * 5 ** (k - 1) for j in range(5) if ((x + j * 5 ** (k - 1)) ** 2 + 1) % 5 ** k == 0)
    return x


i2, i3 = sqrt_minus_one(2), sqrt_minus_one(3)
assert (i2 * i2 + 1) % P == 0 and (i3 * i3 + 1) % P == 0
# M: the calm residues at the deepest level that end in 2 and are not near i2 all share their digits; check it
far = [r for r in levels[TOP] if r % 5 == 2 and shares(r, i2, TOP) < TOP // 2]
M = far[0]
spread = min(shares(a, M, TOP) for a in far)
if spread < TOP - 2:
    fails.append(f'the residues near M only share {spread} digits: M is not pinned down')
assert calm_by_formula(M, TOP)
magnets = {'-2': (-2) % P, 'sqrt(-1) ending in 2': i2, 'sqrt(-1) ending in 3': i3, 'M': M}

# 4. the claim
for k in range(3, K + 1):
    worst = min(max(shares(r, a, k) for a in magnets.values()) for r in levels[k])
    if worst < k - 2 or (k >= 5 and worst != k - 2):  # from depth 5 on, k - 2 is exactly the worst case
        fails.append(f'depth {k}: closest calm residue shares {worst} digits, expected {k - 2}')
    for r in levels[k]:
        if r % 5 == 3 and max(shares(r, magnets['-2'], k), shares(r, i3, k)) < k - 1:
            fails.append(f'depth {k}: {r} (3 mod 5) is not within k - 1 digits of -2 or sqrt(-1)')
counts = {name: sum(1 for r in levels[K] if shares(r, a, K) >= K - 2) for name, a in magnets.items()}
if sum(counts.values()) != len(levels[K]):
    fails.append(f'at depth {K} some calm residue is near no magnet, or near two: {counts}')
print(f'calm residues at depth {K}: {len(levels[K])}, near each magnet: {counts}')
digits = lambda a, n: ''.join(str(a // 5 ** j % 5) for j in range(n - 1, -1, -1))
print('M, last 40 digits in base 5: …' + digits(M, 40))
if fails:
    print('FAILED:', len(fails))
    for f in fails[:10]:
        print('  ', f)
    sys.exit(1)
print(f'ok: at every depth 3..{K}, every calm c shares at least k - 2 base-5 digits with one of the four magnets,'
      ' and k - 2 is tight from depth 5')

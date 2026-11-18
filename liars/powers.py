"""Liars for other even powers: x = x^p + c, starting from x = 0.

Same idea as liars/search.py, for any power p. Calm for k digits means the steps the last j digits take to come
round have no factor 5, for every j <= k. As with squares, that only depends on c's remainder after dividing by
5^k (for an even p the 2s side never lies), so we keep every remainder that is still calm, among the c whose loop
goes wild, and grow it one base-5 digit at a time. The smallest kept remainder at depth k is the smallest positive
c calm for k digits.

    python3 liars/powers.py 4 60          # the record liars of x = x^4 + c, to 60 digits of calm
    python3 liars/powers.py table         # for each even power up to 26: can it lie, and how many calm remainders
"""
import sys


def period(c, m, p):
    """Steps the loop x -> x^p + c takes to come round, mod m (Brent's cycle finder)."""
    power = lam = 1
    t, h = 0, c % m
    while t != h:
        if power == lam:
            t, power, lam = h, power * 2, 0
        h = (pow(h, p, m) + c) % m
        lam += 1
    return lam


def wild_starts(p):
    """Last base-5 digits r (0 to 4) whose own loop, c = r, goes wild within 6 digits."""
    return [r for r in range(5) if period(r, 5 ** 6, p) % 5 == 0]


def calm_sets(p, K):
    """Yield (k, the calm remainders mod 5^k) for k = 1..K."""
    calm = [r for r in wild_starts(p) if period(r, 5, p) % 5]
    yield 1, calm
    for k in range(2, K + 1):
        m, step = 5 ** k, 5 ** (k - 1)
        calm = [r + d * step for r in calm for d in range(5) if period(r + d * step, m, p) % 5]
        yield k, calm
        if not calm:
            return


def records(p, K):
    """(digits of calm, c) for each record liar, calm for exactly that many digits, up to K digits of calm."""
    out, prev = [], None
    for k, calm in calm_sets(p, K + 1):
        best = min(calm) if calm else None
        if prev is not None and best != prev[1]:
            out.append((k - 1, prev[1]))
        prev = (k, best)
        if best is None:
            break
    return [r for r in out if r[0] <= K]


def table(top=26, depth=25):
    for p in range(2, top + 1, 2):
        counts = [len(c) for _, c in calm_sets(p, depth)]
        if not wild_starts(p):
            print(p, 'never goes wild')
        elif counts[-1] == 0:
            print(p, 'can lie for at most', len(counts) - 1, 'digits')
        else:
            print(p, 'can lie:', counts[-1], 'calm remainders at every depth from', counts.index(counts[-1]) + 1, 'to', depth)


if __name__ == '__main__':
    if sys.argv[1:2] == ['table']:
        table()
    else:
        p, K = int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 60
        for calm, c in records(p, K):
            print(calm, c)

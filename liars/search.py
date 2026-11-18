"""Find the record liars of x = x*x + c (start x = 0), with nothing skipped.

A liar is calm for k digits when, for every j <= k, the steps its last j digits take to come round
have no factor 5. That only depends on c's remainder after dividing by 5^k (the 2s side never lies),
so we keep every remainder that is still calm and grow it one base-5 digit at a time. The smallest
kept remainder at depth k is the smallest positive c calm for k digits.

    python3 liars/search.py 80      # well under a second
    python3 liars/search.py 1000    # about a minute and a half
"""
import sys


def period(c, m):
    """Steps the loop x -> x*x + c takes to come round, mod m (Brent's cycle finder)."""
    power = lam = 1
    t, h = 0, c % m
    while t != h:
        if power == lam:
            t, power, lam = h, power * 2, 0
        h = (h * h + c) % m
        lam += 1
    return lam


def main(K):
    calm = [2, 3]  # c ending in 2, 3, 7 or 8: the only ones that can go wild
    best = None
    for k in range(2, K + 1):
        m, step = 5 ** k, 5 ** (k - 1)
        calm = [r + d * step for r in calm for d in range(5) if period(r + d * step, m) % 5]
        if min(calm) != best:
            best = min(calm)
            print(k, best, flush=True)  # from depth k on, this is the smallest c calm for k digits


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 80)

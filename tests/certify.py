"""Independent certificate checker for Past Forever's answers on one-number polynomial loops, power towers
x = b ^ x (b a whole number from 2 up, started at a whole number) and x = x ^ x (started at a whole number >= 2).

Towers: SETTLES (Euler) b ^ e mod m only depends on e mod lambda(m) once e is past the biggest power of 2 or 5 in m,
and the chain m, lambda(m), lambda(lambda(m)), ... reaches 1. For each loop it finds the step n0 from which x is
big enough, so the last 60 digits must freeze by step n0 + (chain length); it then runs that loop on every level of
the chain and checks each level freezes on time, and compares the 60 digits with what Past Forever printed.
x = x ^ x: NEVER (ring) once x >= k, x ^ x mod 10^k only depends on x mod 10^k, so a ring of length > 1 in the last
k digits means it never settles. SETTLES (zeros) a start ending in 0: x ^ x is a multiple of 10 ^ x, limit 0.

Polynomial loops:

Shares no code with the engine (different language, own arithmetic). For each loop x -> f(x) = (sum c_j x^j)/q,
with q and the start's denominator free of 2 and 5 (so every value is a 10-adic integer), it tries to PROVE an
answer from textbook facts, and writes the proof down:

  NEVER   (ring lemma)   The last k digits of x_n are eventually periodic with period p > 1. Then x_n cannot
                         converge 10-adically (convergence would freeze the last k digits). Sound because f has
                         10-adic integer coefficients, so x mod 10^k determines f(x) mod 10^k.
  SETTLES (contraction)  x_N = r (mod 10), f(r) = r (mod 10) and f'(r) = 0 (mod 10). Then f maps r + 10Z_10 into
                         itself and f(a) - f(b) = (a - b)(f'(b) + (a - b) g(a, b)), so each step gains a digit and
                         x_n converges to the unique fixed point of f ending in r. If a rational L with f(L) = L and
                         L = r (mod 10) exists (rational root theorem), the limit is exactly L.
  EXACT                  x_n lands exactly on a fixed point (f(x_N) = x_N as fractions).
Otherwise UNPROVED: an honest "no certificate", not a disagreement.
Then it compares with what Past Forever said. It exits with 1 if they disagree anywhere, or if any answer Past
Forever gave is left without a certificate (inconclusive), and it prints how many answers it proved again.

    node tests/certify_gen.js 300 2027 | python3 tests/certify.py            # the CI-sized run, about a minute
    node tests/certify_gen.js towers | python3 tests/certify.py              # towers and x ^ x, a few seconds
    node tests/certify_gen.js 5000 2027 | python3 tests/certify.py report.json   # the full run, about 20 minutes

Written by an explorer agent in a GitHub Codespace, November 2026, as a second opinion that doesn't trust the engine.
"""
import sys, json
from fractions import Fraction as Fr


def f_exact(cs, q, x):
    return sum(Fr(c) * x ** j for j, c in enumerate(cs)) / q


def res(x, m):  # residue mod m of a rational whose denominator is prime to 10
    return x.numerator * pow(x.denominator, -1, m) % m


def f_mod(cs, q, r, m):
    s = 0
    for c in reversed(cs):
        s = (s * r + c) % m
    return s * pow(q, -1, m) % m


def df_mod(cs, q, r, m):
    s = 0
    for j in range(len(cs) - 1, 0, -1):
        s = (s * r + j * cs[j]) % m
    return s * pow(q, -1, m) % m


def orbit(cs, q, r0, m, cap=200000):
    seen, r, n = {}, r0, 0
    while r not in seen and n < cap:
        seen[r] = n
        r = f_mod(cs, q, r, m)
        n += 1
    return (seen[r], n - seen[r]) if r in seen else None


def rational_fixed_points(cs, q):  # rational roots of (sum c_j x^j) - q x
    P = list(cs) + [0] * (2 - len(cs))
    P[1] -= q
    while len(P) > 1 and P[-1] == 0:
        P.pop()
    if all(c == 0 for c in P):
        return set()
    low = next(i for i, c in enumerate(P) if c)
    roots = {Fr(0)} if low > 0 else set()
    divs = lambda n: [d for d in range(1, abs(n) + 1) if n % d == 0]
    for a in divs(P[low]):
        for b in divs(P[-1]):
            for s in (1, -1):
                x = Fr(s * a, b)
                if sum(Fr(c) * x ** j for j, c in enumerate(P)) == 0:
                    roots.add(x)
    return roots


def carmichael(m):  # lambda(m) for m = 2^a 5^b (every modulus here is one)
    a = b = 0
    while m % 2 == 0:
        m //= 2; a += 1
    while m % 5 == 0:
        m //= 5; b += 1
    assert m == 1
    la = 1 if a <= 1 else 2 if a == 2 else 2 ** (a - 2)
    lb = 1 if b == 0 else 4 * 5 ** (b - 1)
    return la * lb // __import__('math').gcd(la, lb)


def tower_mod(b, m):  # last digits of b ^ b ^ b ^ ... (tall enough), mod m
    if m == 1:
        return 0
    lam = carmichael(m)
    # b ^ e mod m depends only on e mod lam once e is at least the biggest power of 2 or 5 in m (< m.bit_length())
    e = tower_mod(b, lam) + lam * m.bit_length()
    return pow(b, e, m)


def certify_tower(L, K=60):  # x = b ^ x from a whole number x0 >= 0, b >= 2: a certificate for this one loop
    b, x0 = L['b'], L['x0']
    M = 10 ** K
    chain = [M]  # 10^K, lambda(10^K), lambda(lambda(10^K)), ... down to 1
    while chain[-1] > 1:
        chain.append(carmichael(chain[-1]))
    big = M.bit_length()  # past this, b ^ e mod any modulus in the chain only depends on e mod its lambda
    x, n0 = x0, 0
    while x < big:  # exact steps; b ^ x > x for b >= 2, so x only grows
        x, n0 = b ** x, n0 + 1
    # From step n0 every top is >= big. Then x_(n+1) mod chain[i] is a function of x_n mod chain[i + 1], so x mod
    # chain[-1] = 1 is frozen at once, x mod chain[-2] one step later, ..., and x mod 10^K from step n0 + len(chain).
    freeze = n0 + len(chain)
    # run the loop on all levels of the chain at once, step by step, for this b and x0
    r, hist = [x % m for m in chain], []
    for n in range(n0, freeze + 3):
        hist.append(r)
        r = [pow(b, r[i + 1] + chain[i + 1] * big, chain[i]) for i in range(len(chain) - 1)] + [0]
    # level i (counted from the bottom, 1 is level 0) must be frozen from step n0 + level, as the induction says
    L = len(chain)
    for i in range(L):
        start = (L - 1 - i)  # steps after n0
        if len({h[i] for h in hist[start:]}) != 1:
            return 'UNPROVED', None, f'level {i} of the chain was still moving after step {n0 + start}'
    if hist[-1][0] != tower_mod(b, M):
        return 'UNPROVED', None, 'the frozen digits differ from the tower formula'
    return 'SETTLES', None, (f'TOWER: the chain 10^{K} -> lambda -> ... reaches 1 in {len(chain) - 1} steps; x is at least '
                             f'{big} from step {n0}, so its last {K} digits are frozen from step {freeze} (Euler, one '
                             f'level of the chain per step)')


def certify_selfpower(L):  # x = x ^ x from a whole number x0 >= 2
    x = L['x0']
    if x % 10 == 0:
        return 'SETTLES', Fr(0), 'ZEROS: x ends in 0, so x ^ x is a multiple of 10 ^ x, and x grows: every digit becomes 0; limit = 0 exactly'
    while x < 1000:  # a few real steps first, so x is bigger than every k below
        x = x ** x
    for k in range(2, 9):
        m = 10 ** k
        # once x >= k, x ^ x mod 10^k only depends on x mod 10^k (lambda(10^k) divides 10^k for k >= 2)
        seen, r, n = {}, x % m, 0
        while r not in seen and n < 200000:
            seen[r] = n
            r = pow(r, r + m, m)
            n += 1
        if r not in seen:
            return 'UNPROVED', None, 'orbit too long'
        if n - seen[r] > 1:
            return 'NEVER', None, f'RING: once x is big, the last {k} digits repeat every {n - seen[r]} steps'
    return 'UNPROVED', None, 'no ring in 8 digits'


def certify(L):
    if L.get('kind') == 'tower':
        return certify_tower(L)
    if L.get('kind') == 'selfpower':
        return certify_selfpower(L)
    cs, q = L['cs'], L['q']
    x0 = Fr(L['p0'], L['q0'])
    x = x0
    for n in range(6):
        y = f_exact(cs, q, x)
        if y == x:
            return 'SETTLES', x, f'EXACT: after step {n} it sits on a fixed point, f({x}) = {x}'
        if abs(y.numerator) > 10 ** 200:
            break
        x = y
    for k in range(1, 9):
        o = orbit(cs, q, res(x0, 10 ** k), 10 ** k)
        if o is None:
            return 'UNPROVED', None, 'orbit too long'
        pre, per = o
        if per > 1:
            return 'NEVER', None, f'RING: the last {k} digits repeat every {per} steps from step {pre}'
    pre, _ = orbit(cs, q, res(x0, 10), 10)
    r = res(x0, 10)
    for _ in range(pre):
        r = f_mod(cs, q, r, 10)
    if df_mod(cs, q, r, 10) != 0:
        return 'UNPROVED', None, f"last digit settles on {r}, but f'({r}) is not 0 mod 10"
    Ls = [z for z in rational_fixed_points(cs, q) if z.denominator % 2 and z.denominator % 5 and res(z, 10) == r]
    proof = f"CONTRACTION: from step {pre} the last digit is {r}, f({r}) = {r} and f'({r}) = 0 mod 10"
    return 'SETTLES', (Ls[0] if Ls else None), proof + (f'; limit = {Ls[0]} exactly' if Ls else '; no rational fixed point ends in that digit, so the limit is irrational')


def limit_digits(L, k):  # last k digits of the limit (valid once SETTLES is certified)
    if L.get('kind') == 'tower':
        return tower_mod(L['b'], 10 ** k)
    if L.get('kind') == 'selfpower':
        return 0
    cs, q = L['cs'], L['q']
    m = 10 ** k
    r = res(Fr(L['p0'], L['q0']), m)
    for _ in range(3 * k + 60):
        r = f_mod(cs, q, r, m)
    return r


def main():
    tally, problems, examples = {}, [], {}
    for line in sys.stdin:
        L = json.loads(line)
        out = L['out']
        pf = 'never' if out == 'never settles' else 'cant' if out == "can't see the end" else 'other' if out.startswith(('stopped', 'crash')) else 'settles'
        verdict, val, proof = certify(L)
        key = f'{pf:8s}/ {verdict}'
        tally[key] = tally.get(key, 0) + 1
        examples.setdefault(key, (L['src'], out[:90], proof))
        if (pf == 'never' and verdict == 'SETTLES') or (pf == 'settles' and verdict == 'NEVER'):
            problems.append((L['src'], out, proof))
        if pf == 'settles' and verdict == 'SETTLES':
            digits = out.lstrip('…').split()[0]
            if digits.isdigit():
                k = min(len(digits), 60)
                if int(digits) % 10 ** k != limit_digits(L, k):
                    problems.append((L['src'], out, 'DIGITS DIFFER'))
            if '(this is' in out:
                lab = Fr(out.split('(this is ')[-1].rstrip(')'))
                if val is not None and lab != val:
                    problems.append((L['src'], out, f'LABEL differs from certified limit {val}'))
                if val is None and 'irrational' in proof:
                    problems.append((L['src'], out, 'LABEL given, but certificate says irrational'))
    print('Past Forever said  /  independent certificate:')
    for k in sorted(tally):
        print(f'  {k:22s} {tally[k]}')
    # an answer counts as independently proved only when the checker found its own certificate for the same answer
    proved = sum(v for k, v in tally.items() if k.startswith(('never   / NEVER', 'settles / SETTLES')))
    pf_answers = sum(v for k, v in tally.items() if k.startswith(('never', 'settles')))
    unproved = sum(v for k, v in tally.items() if k.endswith('UNPROVED') and k.startswith(('never', 'settles')))
    engine_open = sum(v for k, v in tally.items() if k.startswith(('cant', 'other')))
    total = sum(tally.values())
    print('loops:', total)
    print("Past Forever's answers proved again by the checker:", proved, 'of', pf_answers)
    print('answers the checker could not decide (UNPROVED):', unproved)
    print("loops where Past Forever gave no answer (can't see the end, stopped):", engine_open)
    print('disagreements:', len(problems))
    for p in problems[:5]:
        print('  ', p)
    if not problems and unproved:
        print('INCONCLUSIVE: no disagreement, but', unproved, 'answers have no independent certificate')
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'w', encoding='utf-8') as fh:
            json.dump({'tally': tally, 'problems': problems, 'examples': examples}, fh, indent=1)
    sys.exit(1 if problems or unproved else 0)   # CI fails on a disagreement or on any answer left without a certificate


if __name__ == '__main__':
    main()

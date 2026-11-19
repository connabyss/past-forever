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
  RING    (proved ring)  When Past Forever says a ring of n is proved: the last digit of x_n goes round n values
                         r_1..r_n and f'(r_1)...f'(r_n) = 0 (mod 10). Then g = f done n times maps r_1 + 10Z_10
                         into itself and pulls any two of its numbers a digit closer, so it has one fixed point z,
                         z's f-ring is exactly n long at every depth, and x_n falls into it. No certificate for a
                         ring Past Forever calls proved counts as a disagreement.
Two loops, y leaning on a settled x (kind 'ring2'): x = x0, forever: x = f(x) settles (certified as above, limit
x*), then y = y0, forever: y = g(x, y), a polynomial in x and y. y's last k digits depend only on y's and x*'s.
  NEVER   (ring lemma)   y's last k digits, run with x*'s last k digits, go round with period > 1.
  RING    (slopes)       y's last digit goes round n values and dg/dy multiplies to 0 mod 10 round them (x* frozen):
                         the RING argument above, for the one-name step y -> g(x*, y).
  RING    (exact return) g done n times is y itself, as algebra in x and y (fractions, no digits involved), and y's
                         last digit needs all n steps: every depth comes round every n steps, and not sooner.
Branch loops (kind 'branch'): x = x0 (a whole number), forever: if TEST: x = f(x), else: x = g(x) (or nothing),
f and g polynomials with whole coefficients, TEST built from "x ends in D", "x is even", "x is odd" with and, or,
not. TEST reads only the last d digits, and f, g need only the last k digits of x for their own last k digits, so
x mod 10^k (k >= d) runs on a finite machine.
  NEVER   (ring lemma)   that machine goes round with period > 1 at some k >= d.
  then a plain loop      the machine at k = d sits still from step N: from then on TEST always gives the same answer,
                         so the loop is x = f(x) (or g) from the exact x_N, certified as a one-name loop above.
Two names in one loop (kind 'multi'): x = x0, y = y0, forever: x = f(x, y), then y = g(x, y) (with the new x),
f and g polynomials with whole coefficients. The answer checked is x's.
  one-name               if f never reads y, x is a one-name loop, certified as above.
  EXACT                  the whole state comes back exactly (whole numbers) within 8 steps.
  NEVER   (ring lemma)   the state's last k digits come round, and x's last k digits take more than one value round it.
  SETTLES (contraction)  the state's last digit sits still from step N at (r, s), and the step's Jacobian J there
                         (chain rule through the two lines) has J^2 = 0 mod 10 (nilpotent: mod 2 and mod 5 are
                         fields). Two steps then have a Jacobian that is 0 mod 10 on all states ending in (r, s), so
                         they pull any two such states a digit closer: the state converges, so x settles.
Otherwise UNPROVED: an honest "no certificate", not a disagreement.
Then it compares with what Past Forever said. It exits with 1 if they disagree anywhere, or if any answer Past
Forever gave is left without a certificate (inconclusive), and it prints how many answers it proved again.

    node tests/certify_gen.js 300 2027 | python3 tests/certify.py            # the CI-sized run, about a minute
    node tests/certify_gen.js towers | python3 tests/certify.py              # towers and x ^ x, a few seconds
    node tests/certify_gen.js rings2 | python3 tests/certify.py              # y leaning on a settled x, rings
    node tests/certify_gen.js branch 400 | python3 tests/certify.py         # loops that branch on last digits
    node tests/certify_gen.js multi 400 | python3 tests/certify.py          # two names in one loop
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


def certify_ring(L):  # Past Forever says x goes round a ring of L['ring'] endless numbers, proved
    cs, q, n = L['cs'], L['q'], L['ring']
    pre, per = orbit(cs, q, res(Fr(L['p0'], L['q0']), 10), 10)
    r = res(Fr(L['p0'], L['q0']), 10)
    for _ in range(pre):
        r = f_mod(cs, q, r, 10)
    ring, slope = [], 1
    for _ in range(per):
        ring.append(r)
        slope = slope * df_mod(cs, q, r, 10) % 10
        r = f_mod(cs, q, r, 10)
    if per != n:
        return False, f'the last digit goes round {per} values, not {n}'
    if slope:
        return False, f"f' at {ring} multiplies to {slope} mod 10, not 0"
    # g = f done n times maps r + 10Z into itself with g' = 0 mod 10 there, so it pulls any two such numbers a digit
    # closer each time: one fixed point z, whose f-ring is exactly n long (it is n long on the last digit) at every depth
    return True, f"RING-CONTRACTION: last digits {ring}, f' multiplies to 0 mod 10 round them"


# polynomials in x and y: {(i, j): Fraction} for c x^i y^j
def p_add(a, b):
    r = dict(a)
    for k, c in b.items():
        r[k] = r.get(k, 0) + c
        if r[k] == 0:
            del r[k]
    return r


def p_mul(a, b):
    r = {}
    for (i, j), c in a.items():
        for (k, l), d in b.items():
            key = (i + k, j + l)
            r[key] = r.get(key, 0) + c * d
            if r[key] == 0:
                del r[key]
    return r


def p_sub_y(g, h):  # g with y replaced by the polynomial h
    out, powers = {}, {0: {(0, 0): Fr(1)}}
    for (i, j), c in g.items():
        while j not in powers:
            powers[len(powers)] = p_mul(powers[len(powers) - 1], h)
        out = p_add(out, p_mul({(i, 0): Fr(c)}, powers[j]))
    return out


def g_mod(terms, q, x, y, m):
    return sum(c * pow(x, i, m) * pow(y, j, m) for i, j, c in terms) * pow(q, -1, m) % m


def certify_ring2(L):
    X = dict(L['xs'], kind=None)
    verdict, _, proof = certify(X)
    if verdict != 'SETTLES':
        return 'UNPROVED', None, 'x is not certified to settle: ' + proof, None
    terms, q, y0 = L['ys']['terms'], L['ys']['q'], L['ys']['y0']
    ring_ok = None
    for k in range(1, 13):
        m, xk = 10 ** k, limit_digits(X, k)
        seen, y, n = {}, y0 % m, 0
        while y not in seen and n < 200000:
            seen[y] = n
            y = g_mod(terms, q, xk, y, m)
            n += 1
        if y not in seen:
            return 'UNPROVED', None, 'orbit too long', None
        pre, per = seen[y], n - seen[y]
        if k == 1:
            ring = [r for r, s in sorted(seen.items(), key=lambda t: t[1]) if s >= pre]
            if 'ring' in L:
                N = L['ring']
                if per != N:
                    ring_ok = (False, f'the last digit goes round {per} values, not {N}')
                else:
                    slope = 1
                    for r in ring:
                        slope = slope * sum(j * c * pow(xk, i, 10) * pow(r, j - 1, 10) for i, j, c in terms if j) * pow(q, -1, 10) % 10
                    if slope == 0:
                        ring_ok = (True, f"RING-CONTRACTION: y's last digits {ring} with x* ending in {xk}, dg/dy multiplies to 0 mod 10")
                    else:
                        g = {}
                        for i, j, c in terms:
                            g = p_add(g, {(i, j): Fr(c, q)})
                        h = {(0, 1): Fr(1)}
                        for _ in range(N):
                            h = p_sub_y(g, h)
                        ring_ok = (True, f'RING-EXACT: g done {N} times is y itself') if h == {(0, 1): Fr(1)} else (False, f"dg/dy multiplies to {slope} mod 10 and g done {N} times is not y")
        if per > 1:
            return 'NEVER', None, f'RING: with x* frozen, the last {k} digits of y repeat every {per} steps', ring_ok
    return 'UNPROVED', None, 'no ring in 12 digits', ring_ok


def t_digits(t):
    return len(t[1]) if t[0] == 'ends' else 1 if t[0] == 'mod2' else max(t_digits(u) for u in t[1:])


def t_ev(t, x):
    if t[0] == 'ends':
        return x % 10 ** len(t[1]) == int(t[1])
    if t[0] == 'mod2':
        return x % 2 == t[1]
    if t[0] == 'not':
        return not t_ev(t[1], x)
    a, b = t_ev(t[1], x), t_ev(t[2], x)
    return (a and b) if t[0] == 'and' else (a or b)


def certify_branch(L):
    t, then, other = L['test'], L['then'], L.get('else')
    d = t_digits(t)
    def step(x, m):
        f = then if t_ev(t, x % 10 ** d) else other
        return f_mod(f['cs'], f['q'], x, m) if f else x % m
    for k in range(d, d + 9):
        m = 10 ** k
        seen, x, n = {}, L['p0'] % m, 0
        while x not in seen and n < 200000:
            seen[x] = n
            x = step(x, m)
            n += 1
        if x not in seen:
            return 'UNPROVED', None, 'machine too long'
        pre, per = seen[x], n - seen[x]
        if per > 1:
            return 'NEVER', None, f'RING: TEST reads {d} digits; the last {k} digits of x repeat every {per} steps from step {pre}'
        if k == d:
            N, fixed = pre, x
    f = then if t_ev(t, fixed % 10 ** d) else other
    if f is None:
        f = {'cs': [0, 1], 'q': 1}
    xn = L['p0']
    for _ in range(N):
        g = then if t_ev(t, xn % 10 ** d) else other
        if g:
            xn = sum(c * xn ** j for j, c in enumerate(g['cs'])) // g['q'] if g['q'] == 1 else None
        if xn is None or abs(xn) > 10 ** 400:
            return 'UNPROVED', None, 'x_N too big to run exactly'
    plain = {'cs': f['cs'], 'q': f['q'], 'p0': xn, 'q0': 1}
    L['_plain'] = plain
    verdict, val, proof = certify(plain)
    return verdict, val, f'from step {N} TEST always says {t_ev(t, fixed % 10 ** d)}, so it is the plain loop from x_{N}: ' + proof


def m_eval(terms, x, y, m):
    return sum(c * pow(x, i, m) * pow(y, j, m) for i, j, c in terms) % m


def m_d(terms, x, y, m, wrt):
    if wrt == 'x':
        return sum(i * c * pow(x, i - 1, m) * pow(y, j, m) for i, j, c in terms if i) % m
    return sum(j * c * pow(x, i, m) * pow(y, j - 1, m) for i, j, c in terms if j) % m


def m_step(L, st, m):
    x, y = st
    x = m_eval(L['f'], x, y, m)
    return (x, m_eval(L['g'], x, y, m))


def certify_multi(L):
    if not any(j for _, j, _ in L['f']):  # x never reads y: it is a one-name loop
        cs = [0] * (1 + max(i for i, _, _ in L['f']))
        for i, _, c in L['f']:
            cs[i] += c
        L['_plain'] = {'cs': cs, 'q': 1, 'p0': L['x0'], 'q0': 1}
        verdict, val, proof = certify(L['_plain'])
        return verdict, val, 'x never reads y, so it is a one-name loop: ' + proof
    st, seen = (L['x0'], L['y0']), {}
    for n in range(8):  # EXACT: the whole state comes back exactly
        if st in seen:
            xs = {h[0] for h, t in seen.items() if t >= seen[st]}
            if len(xs) == 1:
                return 'SETTLES', Fr(st[0]), f'EXACT: from step {seen[st]} the state comes back every {n - seen[st]} steps and x stays {st[0]}'
            return 'NEVER', None, f'EXACT: from step {seen[st]} the state comes back every {n - seen[st]} steps and x takes {len(xs)} values'
        seen[st] = n
        if max(abs(v) for v in st) > 10 ** 100:
            break
        x = sum(c * st[0] ** i * st[1] ** j for i, j, c in L['f'])
        st = (x, sum(c * x ** i * st[1] ** j for i, j, c in L['g']))
    for k in range(1, 9):
        m = 10 ** k
        seen, st, n, hist = {}, (L['x0'] % m, L['y0'] % m), 0, []
        while st not in seen and n < 200000:
            seen[st] = n
            hist.append(st)
            st = m_step(L, st, m)
            n += 1
        if st not in seen:
            return 'UNPROVED', None, 'orbit too long'
        pre, per = seen[st], n - seen[st]
        if len({s[0] for s in hist[pre:]}) > 1:
            return 'NEVER', None, f'RING: the state comes round every {per} steps on its last {k} digits, and x takes more than one value'
        if k == 1:
            N, (r, s), per1 = pre, st, per
    if per1 != 1:
        return 'UNPROVED', None, "the state's last digit goes round, x's last 8 digits stay: no rule here"
    x2 = m_eval(L['f'], r, s, 10)
    J1 = [[m_d(L['f'], r, s, 10, 'x'), m_d(L['f'], r, s, 10, 'y')], [0, 1]]
    J2 = [[1, 0], [m_d(L['g'], x2, s, 10, 'x'), m_d(L['g'], x2, s, 10, 'y')]]
    mul = lambda A, B: [[sum(A[i][t] * B[t][j] for t in range(2)) % 10 for j in range(2)] for i in range(2)]
    J = mul(J2, J1)
    if any(v for row in mul(J, J) for v in row):
        return 'UNPROVED', None, f'state frozen at {(r, s)} on the last digit, but J^2 = {mul(J, J)} is not 0 mod 10'
    return 'SETTLES', None, f'CONTRACTION: from step {N} the state ends in {(r, s)}, J = {J}, J^2 = 0 mod 10'


def limit_digits(L, k):  # last k digits of the limit (valid once SETTLES is certified)
    if L.get('kind') == 'multi' and '_plain' in L:
        return limit_digits(L['_plain'], k)
    if L.get('kind') == 'multi':
        m, st = 10 ** k, (L['x0'] % 10 ** k, L['y0'] % 10 ** k)
        for _ in range(4 * k + 400):
            st = m_step(L, st, m)
        return st[0]
    if L.get('kind') == 'branch':
        return limit_digits(L['_plain'], k)
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
    tally, problems, examples, rings = {}, [], {}, {True: 0, False: 0}
    for line in sys.stdin:
        L = json.loads(line)
        out = L['out']
        pf = 'never' if out == 'never settles' else 'cant' if out == "can't see the end" else 'other' if out.startswith(('stopped', 'crash')) else 'settles'
        ring2 = None
        if L.get('kind') == 'ring2':
            verdict, val, proof, ring2 = certify_ring2(L)
        elif L.get('kind') == 'branch':
            verdict, val, proof = certify_branch(L)
        elif L.get('kind') == 'multi':
            verdict, val, proof = certify_multi(L)
        else:
            verdict, val, proof = certify(L)
        key = f'{pf:8s}/ {verdict}'
        tally[key] = tally.get(key, 0) + 1
        examples.setdefault(key, (L['src'], out[:90], proof))
        if (pf == 'never' and verdict == 'SETTLES') or (pf == 'settles' and verdict == 'NEVER'):
            problems.append((L['src'], out, proof))
        if 'ring' in L:
            ok, why = (ring2 or (False, 'no ring found')) if L.get('kind') == 'ring2' else certify_ring(L)
            rings[ok] += 1
            if not ok:
                problems.append((L['src'], out, 'PROVED RING without a certificate: ' + why))
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
    print('rings Past Forever called proved, proved again by the checker:', rings[True], 'of', rings[True] + rings[False])
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

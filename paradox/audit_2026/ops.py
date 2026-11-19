#!/usr/bin/env python3
"""Every operator on every pair of small values, against plain Python. Run from the repo root:

    python3 paradox/audit_2026/ops.py paradox

For 3-, 4- and 5-bit messages a and b, each expression below is built once by PARADOX and then evaluated for all
pairs. Its value must equal Python's, and it must crash (dividing by 0) exactly when Python does.
"""
import ast, sys
import z3

sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else 'paradox')
import paradox as P  # noqa: E402

EXPRS = ['a // b', 'a % b', 'a + b', 'a - b', 'a * b', 'a & b', 'a | b', 'a ^ b', '-a', '~a', 'abs(a)', 'min(a, b)',
         'max(a, b)', 'a * a', 'a // 3', 'a % 3', 'a // -3', 'a % -3', 'a // 4', 'a % 4', 'a // -4', 'a % -4',
         '(a * b) // (b - a)', '(a - b) % (a + b)', 'a << 2', 'a >> 1', '(a if a < b else b) // 2']
bad = 0
for W in (3, 4, 5):
    P.W = W; R = range(-(1 << (W - 1)), 1 << (W - 1))
    for ex in EXPRS:
        pr = P.Prog(); env = {n: (P.V(z3.BitVec(n, W), R.start, R.stop - 1), z3.BoolVal(True)) for n in 'ab'}
        v = pr.val(ast.parse(ex, mode='eval').body, env)
        for a in R:
            for b in R:
                try: want = eval(ex)
                except ZeroDivisionError: want = None
                sub = [(z3.BitVec('a', W), z3.BitVecVal(a, W)), (z3.BitVec('b', W), z3.BitVecVal(b, W))]
                alive = all(z3.is_true(z3.simplify(z3.substitute(g, *sub))) for g in pr.guards)
                got = z3.simplify(z3.substitute(v.e, *sub)).as_signed_long() if alive else None
                if want != got:
                    bad += 1
                    if bad <= 5: print(f'{W} bits: {ex} with a={a}, b={b}: python {want}, paradox {got}')
print('bad', bad)
sys.exit(1 if bad else 0)

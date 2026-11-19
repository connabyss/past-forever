#!/usr/bin/env python3
"""Brute-force sweep: random small PARADOX programs against plain Python. Run from the repo root.

    python3 paradox/audit_2026/fuzz.py [count] [seed]      (default 400 programs, seed 1)

Each program gets x from the future (bits 4, so x is -8..7). For every one of the 16 messages, plain Python runs the
program; a crash (dividing by 0, an index off the end, a name with no value yet) means that timeline can't happen.
The consistent timelines are the messages whose program ends with x equal to what was sent. PARADOX must find
exactly the same set. The programs mix the things that only run sometimes: if/else, for loops inside branches,
`a if c else b`, `and`/`or` and chains like a < b < c that stop early, and functions that return early.
"""
import ast, random, sys
from pathlib import Path
import z3

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paradox  # noqa: E402

W = 4
VARS = ['x', 'i', 'y']


def expr(r, d=0):
    k = r.randrange(9 if d < 2 else 3)
    if k == 0: return str(r.randrange(-3, 4))
    if k in (1, 2): return r.choice(VARS)
    if k == 3: return f'({expr(r, d+1)} {r.choice("+-*")} {expr(r, d+1)})'
    if k == 4: return f'({expr(r, d+1)} {r.choice(["//", "%"])} {expr(r, d+1)})'
    if k == 5: return f'({expr(r, d+1)} if {cond(r, d+1)} else {expr(r, d+1)})'
    if k == 6: return f'd[{r.randrange(-3, 3)}]'
    if k == 7: return f'f({expr(r, d+1)})'
    return f'({expr(r, d+1)} {r.choice(["&", "|"])} {expr(r, d+1)})'


def cond(r, d=0):
    a = f'{expr(r, d+1)} {r.choice(["==", "!=", "<", ">="])} {expr(r, d+1)}'
    if r.random() < 0.3: a += f' {r.choice(["<", "<=", "!="])} {expr(r, d+1)}'      # a chain: a < b < c
    if r.random() < 0.35: a = f'({a} {r.choice(["and", "or"])} {expr(r, d+1)} {r.choice(["==", "<"])} {expr(r, d+1)})'
    return a


def stmts(r, ind, d=0, n=None):
    out = []
    for _ in range(n or r.randrange(1, 4)):
        k = r.randrange(6 if d < 2 else 2)
        p = '    ' * ind
        if k == 0: out.append(f'{p}{r.choice(VARS)} = {expr(r)}')
        elif k == 1: out.append(f'{p}{r.choice(VARS)} {r.choice(["+=", "-="])} {expr(r)}')
        elif k in (2, 3):
            out.append(f'{p}if {cond(r)}:'); out += stmts(r, ind + 1, d + 1)
            if r.random() < 0.5: out.append(f'{p}else:'); out += stmts(r, ind + 1, d + 1)
        elif k == 4:
            a = r.randrange(-1, 3); b = r.randrange(-1, 4)
            out.append(f'{p}for {r.choice(VARS[1:])} in range({a}, {b}):'); out += stmts(r, ind + 1, d + 1)
        else: out.append(f'{p}d[{r.randrange(-3, 3)}] = {expr(r)}')
    return out


def program(r):
    f = ['def f(n):', '    i = 2', '    if n < 0:', '        return n * 2', '    for i in range(3):',
         f'        if i == n {r.choice(["+", "-"])} 1:', '            return i', '    return i']
    body = ['x = future(x)', f'y = {r.randrange(-2, 3)}', 'd = [1, 0]'] + (['i = 1'] if r.random() < 0.7 else []) + stmts(r, 0, n=r.randrange(2, 5))
    if r.random() < 0.4: body.append(f'x = {expr(r)}')
    return '\n'.join(f + body)


def python_fixed(src):
    good = []
    for sent in range(-(1 << (W - 1)), 1 << (W - 1)):
        g = {'future': lambda name, *a: sent}
        try:
            exec(src.replace('x = future(x)', f'x = {sent}', 1), g)
        except (ZeroDivisionError, IndexError, NameError, UnboundLocalError):
            continue
        if g['x'] == sent: good.append(sent)
    return good


def paradox_fixed(src):
    paradox.W = W
    P = paradox.Prog(); env = {}; st = {'live': z3.BoolVal(True), 'done': z3.BoolVal(False), 'ret': paradox.C(0)}
    main = []
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef): P.fns[node.name] = node
        else: main.append(node)
    P.block(main, env, st)
    fx = P.futures['x']
    s = z3.Solver(); s.add(paradox.cmp(ast.Eq, P.read(env, 'x'), fx), *P.guards)
    good = []
    for sent in range(-(1 << (W - 1)), 1 << (W - 1)):
        if s.check(fx.e == z3.BitVecVal(sent, W)) == z3.sat: good.append(sent)
    return good


if __name__ == '__main__':
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    r = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    bad = 0; tried = 0; alive = 0
    while tried < count:
        src = program(r)
        try:
            want = python_fixed(src)
        except Exception:
            continue          # the program itself is not plain Python we can judge (e.g. a type error): skip it
        tried += 1
        try:
            got = paradox_fixed(src)
        except (NameError, IndexError) as e:
            got = [] if not want else f'{type(e).__name__}: {e}'   # crashing in every timeline: a plain error is fine
        except Exception as e:
            got = f'{type(e).__name__}: {e}'
        if want: alive += 1
        if got != want:
            bad += 1
            if bad <= 3: print(f'--- MISMATCH\n{src}\npython: {want}\nparadox: {got}\n')
    print(f'fuzz: {tried} programs ({alive} with at least one consistent timeline), {bad} disagree with plain Python')
    sys.exit(1 if bad else 0)

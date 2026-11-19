"""PARADOX: a language with time travel.

    x = future(x)      # x starts as the value x will have when the program ends: a message from the future

Plain Python-style code otherwise: exact integers (like Python's, they never wrap), if/else, for loops over
range(...) with fixed bounds, functions, lists. PARADOX runs the program once for every possible message from the
future, all at once, and keeps only the CONSISTENT TIMELINES: the ones where what the future sends back is exactly
what the program ends with. Then:
  - one timeline: that's the answer (it was "received from the future")
  - several: it lists them and says exactly how many there are
  - none: a PARADOX, and it shows why (every message the future could send changes itself)
    show x             prints x in every consistent timeline
    prefer smallest x  picks the timeline where x is smallest
    bits N             messages from the future are N-bit signed numbers (default 64)
A timeline that crashes (divides by zero, reads a name that has no value yet, indexes past the end of a list) is not
consistent. Usage: python3 paradox.py file.px
"""
import ast, re, sys, time
import z3

W = 64              # width of the messages from the future; the arithmetic itself is exact
MAXW = 4096         # bits any in-between value may need before PARADOX refuses (instead of wrapping)


def need(lo, hi):   # fewest two's-complement bits that hold every integer in [lo, hi]
    w = 2
    while lo < -(1 << (w - 1)) or hi > (1 << (w - 1)) - 1: w += 1
    if w > MAXW: raise OverflowError(f'a value needs more than {MAXW} bits; PARADOX refuses rather than wrap')
    return w


class V:
    """An exact integer for every timeline at once: a bit-vector always wide enough for its known range [lo, hi]."""
    def __init__(self, e, lo, hi):
        self.lo, self.hi = lo, hi
        w = need(lo, hi)
        # always exactly w bits: widen, or drop high bits that the range proves are only sign copies
        self.e = z3.SignExt(w - e.size(), e) if e.size() < w else z3.Extract(w - 1, 0, e) if e.size() > w else e
    def at(self, w): return z3.SignExt(w - self.e.size(), self.e) if w > self.e.size() else self.e

def C(n): return V(z3.BitVecVal(n, need(n, n)), n, n)
def const(v):       # the Python int if v is the same in every timeline, else None
    if v.lo == v.hi: return v.lo
    s = z3.simplify(v.e)
    return s.as_signed_long() if z3.is_bv_value(s) else None
def pair(a, b, lo, hi):
    w = need(min(lo, a.lo, b.lo), max(hi, a.hi, b.hi)); return a.at(w), b.at(w), w
def ite(c, a, b):
    if isinstance(a, list): return [ite(c, x, y) for x, y in zip(a, b)]
    if isinstance(a, z3.BoolRef) or isinstance(b, z3.BoolRef): return z3.If(c, a, b)
    x, y, w = pair(a, b, min(a.lo, b.lo), max(a.hi, b.hi))
    return V(z3.If(c, x, y), min(a.lo, b.lo), max(a.hi, b.hi))
def truth(v): return v if isinstance(v, z3.BoolRef) else v.e != 0
def cmp(op, a, b):
    x, y, _ = pair(a, b, 0, 0)
    return {ast.Eq: x == y, ast.NotEq: x != y, ast.Lt: x < y, ast.Gt: x > y, ast.LtE: x <= y, ast.GtE: x >= y}[op]

def add(a, b):
    lo, hi = a.lo + b.lo, a.hi + b.hi; x, y, _ = pair(a, b, lo, hi); return V(x + y, lo, hi)
def sub(a, b):
    lo, hi = a.lo - b.hi, a.hi - b.lo; x, y, _ = pair(a, b, lo, hi); return V(x - y, lo, hi)
def neg(a): return sub(C(0), a)
def mul(a, b, same=False):
    ps = [a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi]
    lo, hi = min(ps), max(ps)
    if same and a.lo < 0 < a.hi: lo = 0                     # x * x is never negative
    x, y, _ = pair(a, b, lo, hi); return V(x * y, lo, hi)
def mod(a, b):                                              # Python's %: the sign follows b
    c = const(b)
    if c is not None and c > 0 and c & (c - 1) == 0:      # % 2^k is just the last k bits (true for negatives too)
        k = c.bit_length() - 1
        if k == 0: return C(0)
        e = a.at(max(k, a.e.size()))                        # sign-extend first if it is narrower than k bits
        return V(z3.ZeroExt(1, z3.Extract(k - 1, 0, e)), 0, c - 1)
    if c is not None and c > 0:
        lo, hi = (a.lo % c, a.hi % c) if a.hi - a.lo < c and a.lo % c <= a.hi % c else (0, c - 1)
        if a.lo >= 0:                                       # both sides non-negative: plain unsigned remainder
            x, y, w = pair(a, b, 0, 0); return V(z3.URem(x, y), lo, hi)
        x, y, w = pair(a, b, 0, 0); return V(x % y, lo, hi)  # z3's % on bit-vectors is signed modulo, like Python
    m = max(abs(b.lo), abs(b.hi))
    x, y, _ = pair(a, b, -m, m); return V(x % y, -m, m)
def floordiv(a, b):                                         # Python's //: rounds down
    c = const(b)
    if c is not None and c > 0 and c & (c - 1) == 0:      # // 2^k is an arithmetic shift right (rounds down, like Python)
        return shift(a, C(c.bit_length() - 1), False)
    if c is not None and c > 0:
        lo, hi = a.lo // c, a.hi // c
        if a.lo >= 0: x, y, _ = pair(a, b, 0, 0); return V(z3.UDiv(x, y), lo, hi)
    else:
        m = max(abs(a.lo), abs(a.hi)); lo, hi = -m, m
    x, y, _ = pair(a, b, lo, hi)
    return V((x - x % y) / y, lo, hi)                       # exact division of a multiple: Python's floor
def bitop(op, a, b):
    if a.lo >= 0 and b.lo >= 0:
        top = (1 << max(a.hi, b.hi).bit_length()) - 1
        lo, hi = 0, (min(a.hi, b.hi) if op is ast.BitAnd else top)
    else:
        k = max(need(a.lo, a.hi), need(b.lo, b.hi)) - 1; lo, hi = -(1 << k), (1 << k) - 1
    x, y, _ = pair(a, b, lo, hi)
    return V({ast.BitAnd: x & y, ast.BitOr: x | y, ast.BitXor: x ^ y}[op], lo, hi)
def shift(a, b, left):
    k = const(b)
    if k is None: raise SyntaxError('PARADOX can only shift by a fixed amount')
    if k < 0: raise SyntaxError('negative shift count')
    if left:
        lo, hi = a.lo << k, a.hi << k; w = need(lo, hi); return V(a.at(w) << k, lo, hi)
    return V(a.e >> k, a.lo >> k, a.hi >> k)


class Prog:
    def __init__(self):
        self.fns = {}; self.futures = {}; self.shows = []; self.prefer = None
        self.guards = []; self.live = z3.BoolVal(True)
    def crash_unless(self, cond): self.guards.append(z3.Implies(self.live, cond))
    def read(self, env, name):
        if name not in env: raise NameError(f'{name} is used before it ever gets a value')
        v, defined = env[name]
        if not z3.is_true(defined): self.crash_unless(defined)   # read where it may have no value yet: that timeline crashes
        return v
    def val(self, e, env):
        if isinstance(e, ast.Constant):
            return z3.BoolVal(e.value) if isinstance(e.value, bool) else C(e.value)
        if isinstance(e, ast.Name): return self.read(env, e.id)
        if isinstance(e, ast.List): return [self.val(x, env) for x in e.elts]
        if isinstance(e, ast.Subscript):
            lst = self.val(e.value, env); i = self.idx(e.slice, env)
            if not -len(lst) <= i < len(lst): raise IndexError(f'index {i} is outside a list of {len(lst)}')
            return lst[i]
        if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Mult) and isinstance(e.left, ast.List):
            return [self.val(x, env) for x in e.left.elts] * self.idx(e.right, env)
        if isinstance(e, ast.UnaryOp):
            a = self.val(e.operand, env)
            if isinstance(e.op, ast.Not): return z3.Not(truth(a))
            if isinstance(e.op, ast.USub): return neg(a)
            if isinstance(e.op, ast.Invert): return V(~a.e, -a.hi - 1, -a.lo - 1)
            if isinstance(e.op, ast.UAdd): return a
        if isinstance(e, ast.BinOp):
            a, b = self.val(e.left, env), self.val(e.right, env); t = type(e.op)
            if t in (ast.FloorDiv, ast.Mod): self.crash_unless(b.e != 0)     # dividing by 0 crashes that timeline
            if t is ast.Add: return add(a, b)
            if t is ast.Sub: return sub(a, b)
            if t is ast.Mult: return mul(a, b, same=ast.dump(e.left) == ast.dump(e.right))
            if t is ast.FloorDiv: return floordiv(a, b)
            if t is ast.Mod: return mod(a, b)
            if t in (ast.BitAnd, ast.BitOr, ast.BitXor): return bitop(t, a, b)
            if t in (ast.LShift, ast.RShift): return shift(a, b, t is ast.LShift)
        if isinstance(e, ast.Compare):
            a = self.val(e.left, env); out = []
            for op, rt in zip(e.ops, e.comparators):
                b = self.val(rt, env); out.append(cmp(type(op), a, b)); a = b
            return z3.And(*out) if len(out) > 1 else out[0]
        if isinstance(e, ast.BoolOp):
            vs = [truth(self.val(v, env)) for v in e.values]
            return z3.And(*vs) if isinstance(e.op, ast.And) else z3.Or(*vs)
        if isinstance(e, ast.IfExp):
            return ite(truth(self.val(e.test, env)), self.val(e.body, env), self.val(e.orelse, env))
        if isinstance(e, ast.Call):
            f = e.func.id
            if f == 'future':
                name = e.args[0].id
                if name not in self.futures:
                    k = self.idx(e.args[1], env) if len(e.args) > 1 else None
                    mk = lambda tag: V(z3.BitVec(tag, W), -(1 << (W - 1)), (1 << (W - 1)) - 1)
                    self.futures[name] = mk('future_' + name) if k is None else [mk(f'future_{name}{i}') for i in range(k)]
                fv = self.futures[name]; return list(fv) if isinstance(fv, list) else fv
            if f == 'abs': a = self.val(e.args[0], env); return ite(cmp(ast.Lt, a, C(0)), neg(a), a)
            if f in ('min', 'max'):
                a, b = self.val(e.args[0], env), self.val(e.args[1], env); c = cmp(ast.Lt, a, b)
                return ite(c, a, b) if f == 'min' else ite(c, b, a)
            if f == 'len': return C(len(self.val(e.args[0], env)))
            fn = self.fns[f]
            local = {a.arg: (self.val(x, env), z3.BoolVal(True)) for a, x in zip(fn.args.args, e.args)}
            st = {'live': self.live, 'done': z3.BoolVal(False), 'ret': C(0)}
            outer = self.live; self.block(fn.body, local, st); self.live = outer
            return st['ret']
        raise SyntaxError('PARADOX cannot read: ' + ast.dump(e)[:80])
    def idx(self, e, env):
        k = const(self.val(e, env))
        if k is None: raise SyntaxError('a list index, list size or range bound must be the same in every timeline')
        return k
    def assign(self, env, name, v, live):
        if name in env:
            old, d = env[name]; v = ite(live, v, old); d = z3.simplify(z3.Or(d, live))
        else: d = live
        if isinstance(v, V): v = V(z3.simplify(v.e), v.lo, v.hi)      # fold what is already known (keeps formulas small)
        env[name] = (v, d)
    def block(self, stmts, env, st):
        for s in stmts:
            live = z3.simplify(z3.And(st['live'], z3.Not(st['done']))); self.live = live
            if isinstance(s, ast.Return):
                st['ret'] = ite(live, self.val(s.value, env), st['ret']); st['done'] = z3.Or(st['done'], live)
            elif isinstance(s, (ast.Assign, ast.AugAssign)):
                t = s.targets[0] if isinstance(s, ast.Assign) else s.target
                v = self.val(s.value if isinstance(s, ast.Assign) else ast.BinOp(t, s.op, s.value), env)
                if isinstance(t, ast.Subscript):
                    lst = list(self.read(env, t.value.id)); i = self.idx(t.slice, env)
                    if not -len(lst) <= i < len(lst): raise IndexError(f'index {i} is outside a list of {len(lst)}')
                    lst[i] = ite(live, v, lst[i]); env[t.value.id] = (lst, env[t.value.id][1])
                else: self.assign(env, t.id, v, live)
            elif isinstance(s, ast.If):
                c = truth(self.val(s.test, env)); outer = st['live']
                st['live'] = z3.And(outer, c); self.block(s.body, env, st)
                st['live'] = z3.And(outer, z3.Not(c)); self.block(s.orelse, env, st)
                st['live'] = outer
            elif isinstance(s, ast.For):
                if not (isinstance(s.iter, ast.Call) and s.iter.func.id == 'range'):
                    raise SyntaxError('for loops must be over range(...) with fixed bounds')
                for i in range(*[self.idx(a, env) for a in s.iter.args]):   # start, stop and step, exactly as Python
                    env[s.target.id] = (C(i), z3.BoolVal(True)); self.block(s.body, env, st)
            elif isinstance(s, (ast.Expr, ast.Pass)): pass
            else: raise SyntaxError('PARADOX cannot run: ' + type(s).__name__)


def num(m, v): return m.eval(v.e, True).as_signed_long()
def text(m, v): return ''.join(str(num(m, x)) for x in v) if isinstance(v, list) else str(num(m, v))

def run(path):
    global W
    src = open(path).read()
    m = re.search(r'^bits\s+(\d+)\s*$', src, re.M)
    if m: W = int(m.group(1)); src = src.replace(m.group(0), '')
    P = Prog(); body = []
    for l in src.split('\n'):
        m = re.match(r'^show\s+(.+)$', l); p = re.match(r'^prefer\s+(smallest|largest)\s+(\w+)\s*$', l)
        if m: P.shows.append(m.group(1).strip())
        elif p: P.prefer = (p.group(1), p.group(2))
        else: body.append(l)
    env = {}; st = {'live': z3.BoolVal(True), 'done': z3.BoolVal(False), 'ret': C(0)}; main = []
    for node in ast.parse('\n'.join(body)).body:
        if isinstance(node, ast.FunctionDef): P.fns[node.name] = node
        else: main.append(node)
    t0 = time.time()
    P.block(main, env, st)
    names = list(P.futures)
    pairs = []
    for n, fv in P.futures.items():
        end = P.read(env, n) if n in env else fv
        pairs += list(zip(end, fv)) if isinstance(fv, list) else [(end, fv)]
    flat = [f for _, f in pairs]
    consistent = [cmp(ast.Eq, a, b) for a, b in pairs] + P.guards
    s = z3.SolverFor('QF_BV'); s.add(*consistent)          # the bit-vector solver: much faster at listing every timeline
    total = f'{2 ** (W * len(flat)):,}' if W * len(flat) <= 192 else f'2^{W * len(flat)}'
    print('PARADOX: ' + ', '.join(names) + (' arrives' if len(names) == 1 else ' arrive') + f' from the future. Searching every possible message at once ({total} of them) for consistent timelines...')
    timelines = []
    while len(timelines) < 6 and s.check() == z3.sat:
        mdl = s.model(); timelines.append(mdl)
        s.add(z3.Or(*[f.e != mdl.eval(f.e, True) for f in flat]))
    more = len(timelines) == 6 and s.check() == z3.sat
    dt = time.time() - t0
    if not timelines:
        print(f'\nPARADOX! No consistent timeline exists ({dt:.2f} s). Every message the future could send would change itself (or crash).')
        for guess in (0, 1, 7):
            sub = [(f.e, z3.BitVecVal(guess, W)) for f in flat]
            def after(v):
                if isinstance(v, list): return '[' + ', '.join(after(x) for x in v) + ']'
                r = z3.simplify(z3.substitute(v.e, *sub)); return str(r.as_signed_long()) if z3.is_bv_value(r) else '?'
            outs = [after(P.read(env, n) if n in env else P.futures[n]) for n in names]
            print(f'   if the future sent {guess} everywhere, the program would end with ' + ', '.join(f'{n} = {o}' for n, o in zip(names, outs)) + ': not what was sent')
        return
    if P.prefer:
        kind, nm = P.prefer; o = z3.Optimize(); o.add(*consistent)
        v = P.read(env, nm).e; key = v ^ z3.BitVecVal(1 << (v.size() - 1), v.size())   # signed order as unsigned
        (o.minimize if kind == 'smallest' else o.maximize)(key); o.check(); timelines = [o.model()]
        print(f'\nChose the timeline with the {kind} {nm} ({dt:.2f} s):')
    else:
        print(f'\n{"Exactly " + str(len(timelines)) if not more else "More than " + str(len(timelines) - 1)} consistent timeline{"s" if len(timelines) != 1 else ""} ({dt:.2f} s):')
    for i, mdl in enumerate(timelines[:5], 1):
        vals = [f'{e} = ' + text(mdl, P.val(ast.parse(e, mode='eval').body, env)) for e in (P.shows or names)]
        print(f'   timeline {i}: ' + ', '.join(vals))

if __name__ == '__main__':
    run(sys.argv[1])

"""PARADOX: a language with time travel.

    x = future(x)      # x starts as the value x will have when the program ends: a message from the future

Plain Python-style code otherwise (fixed-width integers that wrap like C, if/else, for i in range(K), functions).
PARADOX runs the program once for every possible message from the future, all at once, and keeps only the
CONSISTENT TIMELINES: the ones where what the future sends back is exactly what the program ends with. Then:
  - one timeline: that's the answer (it was "received from the future")
  - several: it lists them and says exactly how many there are
  - none: a PARADOX, and it shows why (every message the future could send changes itself)
    show x            prints x in every consistent timeline
    prefer smallest x  picks the timeline where x is smallest
Usage: python3 paradox.py file.px
"""
import ast, re, sys, time
import z3

W = 64
def C(n): return z3.BitVecVal(n % 2 ** W, W)
def B(e): return e if isinstance(e, z3.BoolRef) else e != C(0)
def signed(v): return v - 2 ** W if v >> (W - 1) else v

class Prog:
    def __init__(self, src):
        self.src = src; self.fns = {}; self.futures = {}; self.shows = []; self.prefer = None
    def val(self, e, env):
        if isinstance(e, ast.Constant):
            return z3.BoolVal(e.value) if isinstance(e.value, bool) else C(e.value)
        if isinstance(e, ast.Name): return env[e.id]
        if isinstance(e, ast.Subscript):
            return self.val(e.value, env)[self.idx(e.slice, env)]
        if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Mult) and isinstance(e.left, ast.List):
            return [self.val(e.left.elts[0], env)] * e.right.value
        if isinstance(e, ast.UnaryOp):
            a = self.val(e.operand, env)
            return {ast.USub: lambda: -a, ast.Invert: lambda: ~a, ast.Not: lambda: z3.Not(B(a))}[type(e.op)]()
        if isinstance(e, ast.BinOp):
            a, b = self.val(e.left, env), self.val(e.right, env)
            return {ast.Add: lambda: a + b, ast.Sub: lambda: a - b, ast.Mult: lambda: a * b,
                    ast.FloorDiv: lambda: z3.If(b == 0, C(0), a / b), ast.Mod: lambda: z3.If(b == 0, a, z3.SRem(a, b)),
                    ast.BitAnd: lambda: a & b, ast.BitOr: lambda: a | b, ast.BitXor: lambda: a ^ b,
                    ast.LShift: lambda: a << b, ast.RShift: lambda: a >> b}[type(e.op)]()
        if isinstance(e, ast.Compare):
            a = self.val(e.left, env); out = []
            for op, rt in zip(e.ops, e.comparators):
                b = self.val(rt, env)
                out.append({ast.Eq: lambda: a == b, ast.NotEq: lambda: a != b, ast.Lt: lambda: a < b, ast.Gt: lambda: a > b,
                            ast.LtE: lambda: a <= b, ast.GtE: lambda: a >= b}[type(op)]()); a = b
            return z3.And(*out) if len(out) > 1 else out[0]
        if isinstance(e, ast.BoolOp):
            vs = [B(self.val(v, env)) for v in e.values]
            return z3.And(*vs) if isinstance(e.op, ast.And) else z3.Or(*vs)
        if isinstance(e, ast.IfExp):
            return z3.If(B(self.val(e.test, env)), self.val(e.body, env), self.val(e.orelse, env))
        if isinstance(e, ast.Call):
            f = e.func.id
            if f == 'future':
                name = e.args[0].id
                if name not in self.futures:
                    k = e.args[1].value if len(e.args) > 1 else None
                    self.futures[name] = z3.BitVec('future_' + name, W) if k is None else [z3.BitVec(f'future_{name}{i}', W) for i in range(k)]
                return list(self.futures[name]) if isinstance(self.futures[name], list) else self.futures[name]
            if f == 'abs': a = self.val(e.args[0], env); return z3.If(a < 0, -a, a)
            if f in ('min', 'max'):
                a, b = self.val(e.args[0], env), self.val(e.args[1], env)
                return z3.If(a < b, a, b) if f == 'min' else z3.If(a < b, b, a)
            fn = self.fns[f]; local = dict(zip([a.arg for a in fn.args.args], [self.val(a, env) for a in e.args]))
            st = {'live': z3.BoolVal(True), 'done': z3.BoolVal(False), 'ret': C(0)}
            self.block(fn.body, local, st)
            return st['ret']
        raise SyntaxError('PARADOX cannot read: ' + ast.dump(e)[:80])
    def idx(self, e, env):
        return z3.simplify(self.val(e, env)).as_long()
    def block(self, stmts, env, st):
        for s in stmts:
            live = z3.And(st['live'], z3.Not(st['done']))
            if isinstance(s, ast.Return):
                st['ret'] = z3.If(live, self.val(s.value, env), st['ret']); st['done'] = z3.Or(st['done'], live)
            elif isinstance(s, ast.Assign) and isinstance(s.targets[0], ast.Subscript):
                t = s.targets[0]; lst = env[t.value.id]; i = self.idx(t.slice, env)
                lst = list(lst); lst[i] = z3.If(live, self.val(s.value, env), lst[i]); env[t.value.id] = lst
            elif isinstance(s, ast.AugAssign) and isinstance(s.target, ast.Subscript):
                t = s.target; lst = list(env[t.value.id]); i = self.idx(t.slice, env)
                lst[i] = z3.If(live, self.val(ast.BinOp(t, s.op, s.value), env), lst[i]); env[t.value.id] = lst
            elif isinstance(s, ast.Assign):
                n = s.targets[0].id; v = self.val(s.value, env)
                if isinstance(v, list):
                    env[n] = [z3.If(live, a, b) for a, b in zip(v, env[n])] if n in env else v; continue
                env[n] = z3.If(live, v, env[n]) if n in env else v
            elif isinstance(s, ast.AugAssign):
                n = s.target.id; v = self.val(ast.BinOp(ast.Name(n), s.op, s.value), env)
                env[n] = z3.If(live, v, env[n])
            elif isinstance(s, ast.If):
                c = B(self.val(s.test, env)); outer = st['live']
                st['live'] = z3.And(outer, c); self.block(s.body, env, st)
                st['live'] = z3.And(outer, z3.Not(c)); self.block(s.orelse, env, st)
                st['live'] = outer
            elif isinstance(s, ast.For):
                K = s.iter.args[-1].value; lo = s.iter.args[0].value if len(s.iter.args) > 1 else 0
                for i in range(lo, K): env[s.target.id] = C(i); self.block(s.body, env, st)
            elif isinstance(s, (ast.Expr, ast.Pass)): pass
            else: raise SyntaxError('PARADOX cannot run: ' + type(s).__name__)

def run(path):
    global W
    src = open(path).read()
    m = re.search(r'^bits\s+(\d+)\s*$', src, re.M)
    if m: W = int(m.group(1)); src = src.replace(m.group(0), '')
    P = Prog(src)
    lines = src.split('\n'); body = []
    for l in lines:
        m = re.match(r'^show\s+(.+)$', l); p = re.match(r'^prefer\s+(smallest|largest)\s+(\w+)\s*$', l)
        if m: P.shows.append(m.group(1).strip())
        elif p: P.prefer = (p.group(1), p.group(2))
        else: body.append(l)
    tree = ast.parse('\n'.join(body))
    env = {}; st = {'live': z3.BoolVal(True), 'done': z3.BoolVal(False), 'ret': C(0)}
    main = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            P.fns[node.name] = node
        else: main.append(node)
    t0 = time.time()
    # functions: Return inside functions handled by guarded "live"; patch Return to stop later statements
    P.block(main, env, st)
    consistent = []
    for n, fv in P.futures.items():
        consistent += [a == b for a, b in zip(env[n], fv)] if isinstance(fv, list) else [env[n] == fv]
    flat = [x for fv in P.futures.values() for x in (fv if isinstance(fv, list) else [fv])]
    s = z3.Solver(); s.add(*consistent)
    names = list(P.futures)
    print('PARADOX: ' + ', '.join(names) + ' arrive' + ('s' if len(names) == 1 else '') + ' from the future. Searching every possible message at once ('
          + f'{2 ** (W * len(flat)):,} of them) for consistent timelines...' if len(flat) < 4 else f'2^{W * len(flat)} of them) for consistent timelines...')
    timelines = []
    while len(timelines) < 6 and s.check() == z3.sat:
        mdl = s.model(); timelines.append(mdl)
        s.add(z3.Or(*[fv != mdl.eval(fv, True) for fv in flat]))
    more = len(timelines) == 6 and s.check() == z3.sat
    dt = time.time() - t0
    if not timelines:
        print(f'\nPARADOX! No consistent timeline exists ({dt:.2f} s). Every message the future could send would change itself.')
        # show what happens to a few messages
        for guess in (0, 1, 7):
            sub = [(fv, C(guess)) for fv in P.futures.values()]
            outs = [signed(z3.simplify(z3.substitute(env[n], *sub)).as_long()) for n in names]
            print(f'   if the future sent {guess}, the program would end with ' + ', '.join(f'{n} = {o}' for n, o in zip(names, outs)) + ': not what was sent')
        return
    if P.prefer:
        kind, nm = P.prefer; o = z3.Optimize(); o.add(*consistent)
        (o.minimize if kind == 'smallest' else o.maximize)(env[nm]); o.check(); timelines = [o.model()]
        print(f'\nChose the timeline with the {kind} {nm} ({dt:.2f} s):')
    else:
        print(f'\n{"Exactly " + str(len(timelines)) if not more else "More than " + str(len(timelines) - 1)} consistent timeline{"s" if len(timelines) != 1 else ""} ({dt:.2f} s):')
    for i, mdl in enumerate(timelines[:5], 1):
        vals = []
        for e in P.shows or names:
            v = P.val(ast.parse(e, mode='eval').body, env)
            ev = lambda x: (lambda y: signed(y.as_long()) if z3.is_bv_value(y) else y)(mdl.eval(x, True))
            vals.append(f'{e} = ' + (''.join(str(ev(x)) for x in v) if isinstance(v, list) else str(ev(v))))
        print(f'   timeline {i}: ' + ', '.join(vals))

if __name__ == '__main__':
    run(sys.argv[1])

"""Write tests/certificates.md: a few loops, what Past Forever printed, and the proof the independent checker wrote,
with the small facts it rests on spelled out so a reader can check them by hand. Run from the repo root:
    python3 wild/cert/showcase.py
"""
import json, os, subprocess, sys
from fractions import Fraction as Fr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from certify import certify, f_mod, df_mod, res, orbit, f_exact, limit_digits

# (coefficients c0..cd, divisor q, start p0/q0): x -> (c0 + c1 x + ... + cd x^d) / q
LOOPS = [
    ([0, 0, 1], 1, 5, 1),          # x = x * x from 5: the number that is its own square
    ([7, 0, 3], 11, 1, 1),         # x = (3x^2 + 7) / 11
    ([-49, 1, 0, 7], 1, 3, 1),     # x = x + 7(x^3 - 7) = 7x^3 + x - 49: the cube root of 7
    ([1, 10], 1, 0, 1),            # x = 10x + 1: settles on -1/9
    ([2, 0, 1], 1, 0, 1),          # x = x^2 + 2: wild
    ([4, 0, 1], 1, 0, 1),          # x = x^2 + 4: a ring of 2
    ([1, 0, 1], 1, 0, 1),          # x = x^2 + 1: a ring of 6
    ([3, 5, 0, 0, 2], 7, 2, 3),    # x = (2x^4 + 5x + 3) / 7 from 2/3
    ([-3, 0, 0, 1], 1, 1, 1),      # x = x^3 - 3
    ([6, 20, 0, -5], 9, -4, 13),   # x = (-5x^3 + 20x + 6) / 9 from -4/13
]


def lit(v): return f'(0 − {-v})' if v < 0 else str(v)


def source(cs, q, p0, q0):
    xs = lambda j: ' × '.join(['x'] * j)
    terms = ' + '.join((xs(j) if c == 1 and j else lit(c) + (' × ' + xs(j) if j else '')) for j, c in enumerate(cs) if c or j == len(cs) - 1)
    rule = f'({terms}) / {q}' if q > 1 else terms
    return f'x = {lit(p0)}' + (f' / {q0}' if q0 > 1 else '') + f'\nforever: x = {rule}\nshow 30 digits of x\n'


def poly_text(cs, q):
    parts = []
    for j, c in enumerate(cs):
        if c == 0: continue
        x = '' if j == 0 else 'x' if j == 1 else f'x^{j}'
        parts.append(f'{c}{x}' if j == 0 or abs(c) != 1 else ('-' if c < 0 else '') + x)
    t = ' + '.join(parts).replace('+ -', '− ')
    return f'({t}) / {q}' if q > 1 else t


out = ['# Certificates: proofs you can check by hand', '',
       'Each loop below was run by Past Forever, and then proved again from scratch by [certify.py](../wild/cert/certify.py),',
       'a separate checker in Python that never calls the engine. It only uses two textbook facts about numbers that run',
       'off to the left (10-adic integers), stated here once:', '',
       '- **Ring lemma.** The rule only uses +, −, × and division by numbers with no 2 or 5 in them, so the last k digits',
       '  after a step depend only on the last k digits before it. If those last k digits go round a ring longer than 1,',
       '  they never freeze, so the loop **never settles**.',
       "- **Contraction.** If the last digit stops at r, the rule sends r to r (mod 10), and its slope f'(r) is 0 (mod 10),",
       '  then f(a) − f(b) = (a − b)(f\'(b) + (a − b)·g(a, b)) gains a factor of 10 every step: one more digit freezes each',
       '  step and the loop **settles** on the one fixed point ending in r. If a fraction L with f(L) = L ends in r, the',
       '  answer is exactly L (the rational root theorem finds every such L).', '',
       'Regenerate this file with `python3 wild/cert/showcase.py` from the repo root.', '']
for n, (cs, q, p0, q0) in enumerate(LOOPS, 1):
    src = source(cs, q, p0, q0)
    open('/tmp/cert_loop.txt', 'w').write(src)
    pf = subprocess.run(['node', 'cli.js', '/tmp/cert_loop.txt'], capture_output=True, text=True).stdout.strip().split('\n')[0]
    L = {'cs': cs, 'q': q, 'p0': p0, 'q0': q0}
    verdict, val, proof = certify(L)
    out += [f'## {n}. x = {Fr(p0, q0)}, then forever x = {poly_text(cs, q)}', '', '```', src.strip(), '```', '',
            f'Past Forever printed: `{pf}`', '', f'**Certificate: {verdict}.** {proof}.', '']
    x0 = Fr(p0, q0)
    if verdict == 'NEVER':
        w = proof.split('last ')[1].split(' ')[0]; k = 1 if w == 'digit' else int(w); m = 10 ** k
        pre, per = orbit(cs, q, res(x0, m), m)
        r = res(x0, m)
        for _ in range(pre): r = f_mod(cs, q, r, m)
        ring = []
        for _ in range(min(per, 12)): ring.append(str(r).zfill(k)); r = f_mod(cs, q, r, m)
        out += [(f'Check it: work with the last {k} digits only. From step {pre} they go ' if k > 1 else f'Check it: work with the last digit only. From step {pre} it goes ')
                + ', '.join(ring) + (', …' if per > 12 else '') + f', and then back to {ring[0]}: a ring of {per}.', '']
    elif 'CONTRACTION' in proof:
        r = int(proof.split('last digit is ')[1].split(',')[0])
        out += [f"Check it: f({r}) ends in {f_mod(cs, q, r, 10)}, and the slope f'(x) at {r} ends in {df_mod(cs, q, r, 10)}."
                + (f' And f({val}) = {f_exact(cs, q, val)} exactly.' if val is not None else ''),
                f'The checker also rebuilt the last 30 digits on its own: `…{str(limit_digits(L, 30)).zfill(30)}`.', '']
    out.append('')
target = 'tests/certificates.md'
os.makedirs('tests', exist_ok=True)
open(target, 'w').write('\n'.join(out).rstrip() + '\n')
print('wrote', target, len(LOOPS), 'loops')

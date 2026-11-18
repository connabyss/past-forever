"""Copilot's three probes (November 2026), each widened into a family and checked against a plain modular simulation.

1. Towers on any base, x = b ^ x, including bases with 2 or 5 in them (bigTowerLoop): 100 digits vs certify.tower_mod.
2. Towers mixed with x, x = B ^ x - c * x, from 10-adic starts like -1 (towerLoop's gain rule): the map on the last
   k digits is iterated directly (B ^ x mod 10^k only needs x mod lambda(10^k), which divides 10^k).
3. Polynomials with a settled endless number, y = y * y + s * y + t * a after a = a * a forever (fixedPartsMap).
A "can't see the end" is allowed (it is honest); a wrong "settles", "never settles" or digit is a failure.

This is a FINITE check, not a proof. "Settles" here means the simulation's path came to rest at the depths it looked
at (10^3 or 10^2 up to 10^110), and liars show that a loop can look calm for many digits and change later. It
catches wrong answers in the families below; it says nothing about loop shapes it doesn't try.

    python3 tests/probes.py
"""
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tests')); from certify import tower_mod
K=100; M=10**K
def lit(v): return f"(0 − {-v})" if v<0 else str(v)
progs=[]
# 1 towers with any base, 100 digits
for b in [2,4,5,6,8,10,12,15,20,25,50,7,3]:
    for x0 in [0,1,2,5]:
        progs.append(('tower',dict(b=b),f"x = {x0}\nforever: x = {b} ^ x\nshow 100 digits of x\n"))
# 2 x = 3^x - c x  (also base 7, 13) from various starts
for base in [3,7,13]:
  for c in range(-30,31,5):
    for x0 in [-1,0,2]:
        progs.append(('mix',dict(base=base,c=c,x0=x0),f"x = {lit(x0)}\nforever: x = {base} ^ x − {lit(c)} × x\nshow 100 digits of x\n"))
# 3 fixed parts: a = automorphic 5 or 6; y = y*y + t*a (+ s*y)
for a0 in [5,6]:
  for t in [10,20,30,-10,5,1]:
    for s in [0,10,1]:
      progs.append(('fixed',dict(a0=a0,t=t,s=s),f"a = {a0}\nforever: a = a × a\ny = 0\nforever: y = y × y + {lit(s)} × y + {lit(t)} × a\nshow 100 digits of y\n"))
js="const F=require(process.argv[1]);const P=JSON.parse(require('fs').readFileSync(0,'utf8'));console.log(JSON.stringify(P.map(s=>{try{const r=F.run(s,{huntMs:2000});return r.error?'stopped: '+r.error:r.lines[0].text}catch(e){return 'crash '+e.message}})))"
outs=json.loads(subprocess.run(['node','-e',js,str(ROOT / 'forever.js')],input=json.dumps([p[2] for p in progs]),capture_output=True,text=True).stdout)
def lam(m):
    a=b=0
    while m%2==0: m//=2;a+=1
    while m%5==0: m//=5;b+=1
    la=1 if a<=1 else 2 if a==2 else 2**(a-2); lb=1 if b==0 else 4*5**(b-1)
    from math import gcd; return la*lb//gcd(la,lb)
def truth_orbit(g, r0, mods=(10**2,10**5,10**20,10**60,10**110)):
    # iterate a residue map at each depth; return ('never',k) if ring >1 at some depth, else ('settles', fixed residue mod 10^110)
    res=None
    for m in mods:
        seen={}; r=r0(m); n=0
        while r not in seen and n<300000: seen[r]=n; r=g(r,m); n+=1
        if r not in seen: return ('unknown',m)
        if n-seen[r]>1: return ('never',m)
        res=r
    return ('settles',res)
bad=0; tally={}
for (kind,p,src),out in zip(progs,outs):
    if kind=='tower':
        t=('settles',tower_mod(p['b'],10**110))
    elif kind=='mix':
        B,c=p['base'],p['c']
        # 10-adic x: B^x mod m depends on x mod lam(m), and lam(10^k) | 10^k for k>=3
        t=truth_orbit(lambda r,m:(pow(B,r%lam(m),m)-c*r)%m, lambda m:p['x0']%m, mods=(10**3,10**5,10**20,10**60,10**110))
    else:
        A=lambda m: (lambda x:[x:=x*x%m for _ in range(400)][-1])(p['a0']%m)
        cache={}
        def g(r,m):
            if m not in cache: cache[m]=A(m)
            return (r*r+p['s']*r+p['t']*cache[m])%m
        t=truth_orbit(g, lambda m:0)
    pf='never' if out=='never settles' else 'cant' if out.startswith("can't") else 'settles' if out[0]=='…' or out.lstrip('-').split()[0].isdigit() else out
    ok = (pf==t[0]) or pf=='cant'
    if ok and pf=='settles':
        d=int(out.lstrip('…').split()[0]) if out[0]=='…' else None
        if d is not None and d % M != t[1] % M: ok=False
        if d is None:  # exact small number
            from fractions import Fraction
            q=Fraction(out.split()[0]); v=q.numerator*pow(q.denominator,-1,M)%M
            if v!=t[1]%M: ok=False
    key=(kind,pf,t[0]); tally[key]=tally.get(key,0)+1
    if not ok:
        bad+=1
        if bad<8: print('MISMATCH',src.replace('\n',' | '),'->',out[:60],'truth',t[0])
for k, v in sorted(tally.items()):
    print('  ', k, v)
if bad:
    print('FAILED:', bad, 'of', len(progs), 'answers differ from the modular simulation'); sys.exit(1)
print(f'ok: {len(progs)} probe loops (Copilot\'s three: towers on any base, towers mixed with x, polynomials with a settled'
      ' endless number), every answer matches an independent modular simulation at depths up to 110 digits (a finite check, not a proof)')

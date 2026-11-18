# Certificates: proofs you can check by hand

Each loop below was run by Past Forever, and then proved again from scratch by [certify.py](certify.py),
a separate checker in Python that never calls the engine. It only uses two textbook facts about numbers that run
off to the left (10-adic integers), stated here once:

- **Ring lemma.** The rule only uses +, −, × and division by numbers with no 2 or 5 in them, so the last k digits
  after a step depend only on the last k digits before it. If those last k digits go round a ring longer than 1,
  they never freeze, so the loop **never settles**.
- **Contraction.** If the last digit stops at r, the rule sends r to r (mod 10), and its slope f'(r) is 0 (mod 10),
  then f(a) − f(b) = (a − b)(f'(b) + (a − b)·g(a, b)) gains a factor of 10 every step: one more digit freezes each
  step and the loop **settles** on the one fixed point ending in r. If a fraction L with f(L) = L ends in r, the
  answer is exactly L (the rational root theorem finds every such L).

The checker is [tests/certify.py](certify.py); `node tests/certify_gen.js 300 2027 | python3 tests/certify.py` runs it on
300 random loops, and every build does that. The ten below were picked by the explorer agent that wrote it. They
are also stored as machine-readable inputs in [certificates.jsonl](certificates.jsonl), and every build runs them through the
same checker: `node tests/certify_gen.js tests/certificates.jsonl | python3 tests/certify.py`. The build fails if the
checker disagrees with Past Forever or can't prove an answer.

## 1. x = 5, then forever x = x^2

```
x = 5
forever: x = x × x
show 30 digits of x
```

Past Forever printed: `…106619977392256259918212890625`

**Certificate: SETTLES.** CONTRACTION: from step 0 the last digit is 5, f(5) = 5 and f'(5) = 0 mod 10; no rational fixed point ends in that digit, so the limit is irrational.

Check it: f(5) ends in 5, and the slope f'(x) at 5 ends in 0.
The checker also rebuilt the last 30 digits on its own: `…106619977392256259918212890625`.


## 2. x = 1, then forever x = (7 + 3x^2) / 11

```
x = 1
forever: x = (7 + 3 × x × x) / 11
show 30 digits of x
```

Past Forever printed: `never settles`

**Certificate: NEVER.** RING: the last digit repeats every 6 steps from step 1.

Check it: work with the last digit only. From step 1 it goes 0, 7, 4, 5, 2, 9, and then back to 0: a ring of 6.


## 3. x = 3, then forever x = -49 + x + 7x^3

```
x = 3
forever: x = (0 − 49) + x + 7 × x × x × x
show 30 digits of x
```

Past Forever printed: `…581408885453706924422217051543`

**Certificate: SETTLES.** CONTRACTION: from step 0 the last digit is 3, f(3) = 3 and f'(3) = 0 mod 10; no rational fixed point ends in that digit, so the limit is irrational.

Check it: f(3) ends in 3, and the slope f'(x) at 3 ends in 0.
The checker also rebuilt the last 30 digits on its own: `…581408885453706924422217051543`.


## 4. x = 0, then forever x = 1 + 10x

```
x = 0
forever: x = 1 + 10 × x
show 30 digits of x
```

Past Forever printed: `…111111111111111111111111111111  (this is -1/9)`

**Certificate: SETTLES.** CONTRACTION: from step 1 the last digit is 1, f(1) = 1 and f'(1) = 0 mod 10; limit = -1/9 exactly.

Check it: f(1) ends in 1, and the slope f'(x) at 1 ends in 0. And f(-1/9) = -1/9 exactly.
The checker also rebuilt the last 30 digits on its own: `…111111111111111111111111111111`.


## 5. x = 0, then forever x = 2 + x^2

```
x = 0
forever: x = 2 + x × x
show 30 digits of x
```

Past Forever printed: `never settles`

**Certificate: NEVER.** RING: the last digit repeats every 2 steps from step 2.

Check it: work with the last digit only. From step 2 it goes 6, 8, and then back to 6: a ring of 2.


## 6. x = 0, then forever x = 4 + x^2

```
x = 0
forever: x = 4 + x × x
show 30 digits of x
```

Past Forever printed: `never settles`

**Certificate: NEVER.** RING: the last digit repeats every 2 steps from step 0.

Check it: work with the last digit only. From step 0 it goes 0, 4, and then back to 0: a ring of 2.


## 7. x = 0, then forever x = 1 + x^2

```
x = 0
forever: x = 1 + x × x
show 30 digits of x
```

Past Forever printed: `never settles`

**Certificate: NEVER.** RING: the last digit repeats every 6 steps from step 0.

Check it: work with the last digit only. From step 0 it goes 0, 1, 2, 5, 6, 7, and then back to 0: a ring of 6.


## 8. x = 2/3, then forever x = (3 + 5x + 2x^4) / 7

```
x = 2 / 3
forever: x = (3 + 5 × x + 2 × x × x × x × x) / 7
show 30 digits of x
```

Past Forever printed: `never settles`

**Certificate: NEVER.** RING: the last digit repeats every 2 steps from step 0.

Check it: work with the last digit only. From step 0 it goes 4, 5, and then back to 4: a ring of 2.


## 9. x = 1, then forever x = -3 + x^3

```
x = 1
forever: x = (0 − 3) + x × x × x
show 30 digits of x
```

Past Forever printed: `never settles`

**Certificate: NEVER.** RING: the last digit repeats every 6 steps from step 0.

Check it: work with the last digit only. From step 0 it goes 1, 8, 9, 6, 3, 4, and then back to 1: a ring of 6.


## 10. x = -4/13, then forever x = (6 + 20x − 5x^3) / 9

```
x = (0 − 4) / 13
forever: x = (6 + 20 × x + (0 − 5) × x × x × x) / 9
show 30 digits of x
```

Past Forever printed: `…159563719294965267181396484374`

**Certificate: SETTLES.** CONTRACTION: from step 1 the last digit is 4, f(4) = 4 and f'(4) = 0 mod 10; no rational fixed point ends in that digit, so the limit is irrational.

Check it: f(4) ends in 4, and the slope f'(x) at 4 ends in 0.
The checker also rebuilt the last 30 digits on its own: `…159563719294965267181396484374`.

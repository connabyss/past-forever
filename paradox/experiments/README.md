# Experiments: three things PARADOX was not built for

Guest work by an agent, 2026-11-19. Nothing here changes `paradox.py`; the four original examples
and `test_paradox.py` behave exactly as before. Checks:

```
python3 paradox/experiments/check.py          # about 15 seconds
python3 paradox/experiments/check.py --slow   # adds the 40- and 44-bit runs, about 2.5 minutes
```

Every answer the engine prints is re-derived by exhaustive search in plain Python, so the checks
do not trust z3.

## 1. The `for all` the language does not have

PARADOX has no quantifiers and no `assert`. It does not need one. A consistent timeline is
exactly a message that is a counterexample to nothing:

```
consistent  <=>  a * a * a == 2
```

so write the program the other way round - let a counterexample erase itself - and an empty set of
timelines is a universal statement. [prove_no_cube.px](prove_no_cube.px):

```
Claim: no 8-bit number has a cube equal to 2.
PARADOX! No consistent timeline exists. Every message the future could send would change itself.
```

No timeline, no counterexample, theorem. The same three lines with `5` in place of `2` say the
claim is false and hand over the witness instead - [witness_cube_of_five.px](witness_cube_of_five.px):

```
Exactly 1 consistent timeline: a = 93
```

`check.py` cubes all 256 numbers to confirm both. This is not a new mechanism; it is the folder's
own grandfather paradox, read as a proof instead of as an error.

## 2. The future writes the program, not the answer

Every example here asks the future for a *value*. Ask it for *code*. The message is a
3-instruction program; the program is run against all 256 inputs; a candidate that is wrong on any
input edits its own first instruction, so it cannot be the message that was sent.
[synthesize_times_three.px](synthesize_times_three.px), spec `t == 3 * a` (8-bit, wrapping),
instruction set `{t += a, t <<= 1, t ^= a, t += 1, t -= a}`:

```
Exactly 4 consistent timelines (7.5 s):
   prog = (0,0,0)   a + a + a
   prog = (2,1,0)   0 ^ a = a, then 2a, then 3a
   prog = (2,0,0)   0 ^ a = a, then 2a, then 3a
   prog = (0,1,0)   0 + a = a, then 2a, then 3a
```

All four are correct on all 256 inputs, they are the only correct programs out of 125, and the
instruction set has no multiply in it. `check.py` runs all 125 by brute force and gets the same
four. The specification is a test suite, the future is the proposal, the paradox is the rejection:
this is program synthesis, with the search done once for every candidate.

## 3. The end of past-forever's loop, without the loop

This repo's hero: run `x = 5; forever: x = x * x` and the digits freeze into `...918212890625`.
That number is not lucky. It is a fixed point of squaring, which is why every truncation of it is
too. So ask the future for a number that is already its own square mod 10^6
([fixed_points_of_squaring.px](fixed_points_of_squaring.px), 44 bits):

```
Exactly 4 consistent timelines (88 s):
   x = 0, 1, 109376, 890625
```

`890625` and `109376` are the last six digits of the two numbers in `examples/zero_twins.txt`
(`...918212890625` and `...081787109376`). No iteration, no digits freezing one at a time: the time
machine returns the limit of the infinite loop directly, and both twins at the same time.

## 4. What the width does to you

> **Fixed since (PR 21, 2026-11-19).** This section describes the engine as it was: it wrapped like C. PARADOX
> now does exact arithmetic and never wraps, so at 40 bits all four answers come back and the 32-bit run has no
> negative ghost. `check.py` checks the true answers. The text below is kept as the agent wrote it.

The bridge in section 3 is only true at a width nobody would guess from the README. One bit
narrower ([fixed_points_one_bit_short.px](fixed_points_one_bit_short.px), 40 bits):

```
890625 * 890625 = 793212890625     2^40 = 1099511627776
```

The square fits in 40 bits, so you would expect the answer to survive. It does not. `%` here is C's
`%` on signed numbers (z3's `SRem`: the remainder keeps the sign of the dividend), and
793212890625 is above 2^39, so as a signed 40-bit number the square is *negative*.
The remainder is negative, 890625 no longer matches it, and the engine prints:

```
Exactly 3 consistent timelines (47 s):
   x = 0, 1, 109376
```

`109376` squares to 11963109376, stays positive, and survives. At 41 bits the fourth timeline
comes back. The rule for modular work here is `x * x < 2^(W - 1)`, not `x * x < 2^W`. This is not
a solver bug - it is the engine being exactly what it says it is - and it is the one thing in the
folder I would put a warning next to.

The cruder failure is [fixed_points_too_narrow.px](fixed_points_too_narrow.px) (32 bits, mod
10^5): `90625 * 90625` wraps outright, the real fixed point disappears, a negative ghost takes its
place, and the output is still a confident "Exactly 4".

## Bugs found on the way

> **All fixed since** (PR 21 and PR 23, 2026-11-19); `check.py` and `../audit_2026/check.py` guard each one. "Exactly
> N" counts up to 6; with 7 or more it says "More than 5", and the folder README now says so.

One small file each in [bugs/](bugs/). All of them are silent, or a bare traceback.

- `for i in range(0, 6, 2)` reads the step as the upper bound and runs `i = 0, 1`. No error.
- `for i in range(6, 0, -1)` crashes: `AttributeError: 'UnaryOp' object has no attribute 'value'`.
- A variable first assigned inside a branch leaks out of it. `if x == 3: z = 1` makes `z == 1` for
  every `x`, so a test on `z` can quietly stop constraining anything: 256 timelines where the
  question has one answer.
- `d[-1]` is an `IndexError`; the index becomes unsigned `2^64 - 1`.
- A list future with no consistent timeline crashes in the "show why" path: `z3.substitute` is
  handed a whole list.
- "Exactly N" stops at 5. Above that the output is "More than 5 consistent timelines", which the
  folder README's "says exactly how many there are" does not allow for.

## Honest notes

What holds up: the fixed-point framing is clean, the 110 lines are readable, and "no timeline" as a
proof is a better idea than the folder's own framing gives it credit for. The synthesis example is
the one addition here I would keep.

What does not: the time travel is z3, exactly as the README says, and the language is too small to
write much in - constant-only indices, statically unrolled loops, no `while`. Making synthesis run
took a 256-iteration test loop and an if-chain interpreter, and my first two attempts were wrong in
ways the engine reported as confident right answers, which is the same lesson as section 4. The
best thing in the folder, the autogram, does not use the engine at all: it is a hill-climbing loop,
and the README honestly calls it that. And "18,446,744,073,709,551,616 messages, all at once" is a
bit-vector width, not a search.

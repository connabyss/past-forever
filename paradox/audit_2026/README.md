# PARADOX adversarial audit (2026-11-19)

The Arena agent wrote this audit to break PARADOX after the first round of fixes. It has small repros and an
independent checker. Every expected answer comes from plain Python running the program for every possible
message, never from z3 or from PARADOX.

Run with Python that has `z3-solver` installed (about 10 seconds):

```sh
python3 paradox/audit_2026/check.py
```

- `check.py` runs every `.px` file here and compares PARADOX's timelines with the brute-force answer.
- `ops.py` builds every operator once and checks it on every pair of 3-, 4- and 5-bit values (value, and crash on
  dividing by 0) against Python.
- `fuzz.py [count] [seed]` writes random small programs (if/else, loops inside branches, `a if c else b`,
  `and`/`or`, functions that return early, lists) and checks that PARADOX finds exactly the timelines Python finds.

## What Arena found, and what was true

Arena ran its audit against `main`, which still had the old wrapping engine. The first round of fixes (exact
arithmetic, `d[-1]`, the list show-why) was in a separate, unmerged pull request, so three of its findings were
about code that had already been fixed. All of this was rechecked by hand.

- **Arithmetic, range, branches:** these held. Arena's remainder check expected C's `%`; PARADOX now follows
  Python, so `x % -3` has the fixed points -2, -1, 0 (the sign follows the divisor).
- **`d[-1]` and the list show-why:** both already fixed by the exact-arithmetic change. `negative_index.px` gives
  all 256 timelines with `x` equal to the last element; `vector_show_why.px` prints its explanation.
- **A skipped loop changed its name: real.** In `inactive_loop_target.px` the loop sits in a branch only `x == 0`
  takes, yet PARADOX set `i` to 1 in every timeline and answered `x = 1`. The only right answer is `x = 7`.

## The same bug, everywhere it lived

Arena's bug is one case of a wider one: code that only some timelines reach changed, or crashed, all of them.
Sweeping that class with `fuzz.py` found 42 wrong answers in 126 programs that had a consistent timeline. The
causes, each with a repro here:

| repro | what went wrong | right answer |
|---|---|---|
| `inactive_loop_target.px` | a loop in a skipped branch still set its loop name | `x = 7` |
| `dead_arm.px` | `12 // x if x != 0 else 0`: the unchosen arm's divide-by-0 killed the `x = 0` timeline | `x = 0` |
| `short_circuit.px` | `x == 0 or 12 // x == 99`: `or` didn't stop early, so `x = 0` crashed | `x = 0` |
| `dead_branch_index.px` | `d[5]` in a branch only `x == 0` takes stopped the whole program | `x = 3` |
| `dead_branch_name.px` | a name with no value, read in a branch only `x == 0` takes, stopped the whole program | `x = 2` |
| `floor_division_edge.px` | `-8 // 3` gave 2: working it out needs -9, one more than 4 bits, and it wrapped | `x = -8` |

The last one isn't about branches; `fuzz.py` found it, and `ops.py` now checks every operator for it. After the
fixes, `fuzz.py` agrees with Python on 3,000 random programs (seeds 2 and 3) and `ops.py` finds 0 wrong values.

## Arena's surprise, checked

Arena claimed `x = 5 * x + 12` has four 8-bit timelines: -67, -3, 61, 125. That is true for C-style wrapping
bytes, because 4x = -12 (mod 256) has four solutions (4 isn't invertible mod 256). Python agrees on all 256 bytes.
It is a textbook linear congruence, though, not a new find. And PARADOX no longer wraps: written plainly, the
only answer is the integer one, `x = -3` (`modular_fixed_points.px`); with `% 256` written out, the answers are
61 and 125, the two that fit in a message from -128 to 127 (`modular_wrap.px`).

## Verdict

Arena's own verdict was "partly impressed". Its one new bug was real and serious (a wrong answer, with a
complete brute-force proof), and sweeping its family turned up five more (four in the family, plus a division slip). Its two "still crashes" findings and its
surprise were about the old engine.

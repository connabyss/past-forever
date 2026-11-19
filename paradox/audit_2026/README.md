# PARADOX adversarial audit (2026-11-19)

This folder contains small black-box repros and an independent exhaustive checker.
It does not modify `paradox.py` or any other engine file.

Run with Python that has `z3-solver` installed:

```sh
python3 paradox/audit_2026/check.py
```

The checker enumerates every 4-bit signed future value (or every pair of 4-bit
vector messages), evaluates the expected transformation with plain Python, and
compares it with PARADOX's reported fixed points. For large-literal wrapping it
enumerates the entire 8-bit domain. It exits zero when all checks match the
observed audit, including known failures reproduced below; `PASS` means the
repro/check behaved as expected, not that every engine behavior is correct.

## Results

### Prior repro categories rechecked

- **Arithmetic exactness:** passed. Exhaustive 4-bit checks confirmed the five
  fixed points of signed C-style `x % -3` (`-2` through `2`) and the sole fixed
  point of `x // -3` (`0`).
- **Range boundaries:** passed. `range(3, 3)` is empty; brute force confirms the
  one consistent value is 6.
- **Branch scoping:** passed for the branch-swap repro; brute force confirms
  there are no consistent values.
- **`d[-1]`: not fixed.** `negative_index.px` has 256 valid unchanged two-element
  messages, with `d[-1]` equal to the second element in every case. Instead,
  PARADOX raises `IndexError: list index out of range` while compiling it.
- **Vector `show-why`: not fixed.** In `vector_show_why.px`, every one of 256
  possible messages changes its first element, so the independent answer is no
  consistent timeline. PARADOX detects that paradox, then raises a Z3
  `Z3 expression expected` exception while trying to explain it.

### New wrong-answer finding

`inactive_loop_target.px` is a genuine unsound answer, not a timeout or a
crash. In 4-bit signed arithmetic, enumerate `x` from -8 through 7:

- for `x == 0`, the loop runs and leaves `i = 1`;
- otherwise, the branch is skipped and the pre-existing `i = 7` must survive;
- therefore the only fixed point is `x = 7`.

The engine returns **exactly one timeline, `x = 1`**. Its loop unrolling writes
the loop target on each syntactic iteration even when the containing branch is
inactive. The independent reference in `check.py` enumerates the full domain and
asserts the discrepancy.

### Other edge checks

- A 128-bit-sized literal reduces exactly to 255 modulo 256; `x -> x - 1` has
  no fixed point, and PARADOX reports none.
- For `x = x | 1` there are exactly eight 4-bit fixed points. PARADOX reports
  “More than 5” and displays five valid samples.
- Five nested conditions are checked against the 15 expected fixed points;
  displayed samples are valid.
- A program without future variables yields one ordinary timeline.

### Independently verified surprise

`modular_fixed_points.px` asks for a fixed point of `x -> 5*x + 12` in 8-bit
wrapping arithmetic. Although the update looks like it should run away, the
congruence is `4*x = -12 (mod 256)`, which has four solutions because 4 is not
invertible modulo 256. PARADOX finds `61, 125, -3, -67`. A separate Python loop
enumerating all 256 bit patterns confirms this exact set.

## Verdict

**Partly impressed.** The exact arithmetic, tested range boundary, branch
selection, large-integer wrapping, nesting, and bounded timeline reporting
survived exhaustive small-domain checks. However, two prior issues (`d[-1]` and
vector `show-why`) still crash, and the inactive-loop-target repro demonstrates
a wrong answer with a complete brute-force proof. The wrong-answer finding is
the most serious result.

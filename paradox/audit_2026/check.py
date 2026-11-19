#!/usr/bin/env python3
"""Independent small-domain audit of PARADOX. Run from the repo root.

Requires z3-solver, as does paradox.py. This is deliberately a black-box checker:
all expected answers below come from ordinary Python enumeration, not Z3 or the
PARADOX implementation. Exit 0 means the observed behavior matches this audit,
including the two captured, still-reproducible crashes and the wrong timeline.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "paradox" / "paradox.py"
HERE = Path(__file__).resolve().parent


def run(case):
    return subprocess.run(
        [sys.executable, str(ENGINE), str(HERE / case)], cwd=ROOT,
        capture_output=True, text=True, timeout=30,
    )


def check(name, condition, detail=""):
    print(("PASS " if condition else "FAIL ") + name + (" — " + detail if detail else ""))
    return bool(condition)


def signed(v, width):
    v %= 1 << width
    return v - (1 << width) if v & (1 << (width - 1)) else v


def timeline_values(out, name="x"):
    return [int(v) for v in re.findall(rf"timeline \d+: {re.escape(name)} = (-?\d+)", out)]


ok = True

# Old arithmetic repro family: exhaustively compute all 16 signed inputs.
def c_rem(a, b):
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return a - q * b

rem_expected = sorted(x for x in range(-8, 8) if c_rem(x, -3) == x)
r = run("arithmetic_remainder.px")
rem_actual = timeline_values(r.stdout)
ok &= check("old arithmetic: exact signed remainder", r.returncode == 0 and sorted(rem_actual) == rem_expected == [-2, -1, 0, 1, 2], f"brute force={rem_expected}; solver={sorted(rem_actual)}")

def c_div(a, b):
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q

div_expected = sorted(x for x in range(-8, 8) if c_div(x, -3) == x)
r = run("arithmetic_division.px")
ok &= check("old arithmetic: exact signed division", r.returncode == 0 and sorted(timeline_values(r.stdout)) == div_expected == [0], f"brute force={div_expected}; solver={timeline_values(r.stdout)}")

# range(3,3) is empty; across all 16 future messages the output is always 6.
range_expected = [x for x in range(-8, 8) if x == 6]
r = run("range_empty.px")
ok &= check("old range repro: empty range leaves state unchanged", r.returncode == 0 and timeline_values(r.stdout) == range_expected == [6], f"brute force fixed points={range_expected}; solver={timeline_values(r.stdout)}")

# Branch swap: F(0)=1, F(1)=0, and F(other)=0. No x in [-8,7] is fixed.
branch_map = {x: (1 if x == 0 else 0) for x in range(-8, 8)}
branch_expected = [x for x in branch_map if branch_map[x] == x]
r = run("branch_scoping.px")
ok &= check("old branch repro: both arms are properly scoped", r.returncode == 0 and "PARADOX! No consistent timeline exists" in r.stdout and not branch_expected, f"brute force fixed points={branch_expected}")

# For any pair of 4-bit messages, d[-1] selects the second element and the
# untouched future vector is its own output: exactly 16*16 consistent messages.
vector_messages = [(a, b) for a in range(16) for b in range(16)]
negative_index_expected = []
for a, b in vector_messages:
    received = [a, b]
    program_output = [a, received[-1]]  # d itself is unchanged; x reads d[-1].
    if received == [a, b] and program_output[1] == b:
        negative_index_expected.append((a, b))
r = run("negative_index.px")
negative_index_still_fails = r.returncode != 0 and "IndexError" in r.stderr
ok &= check("old d[-1] repro: expected all 256 messages, but interpreter still crashes", negative_index_still_fails and len(negative_index_expected) == 256, f"independent brute-force count={len(negative_index_expected)}; stderr={r.stderr.strip().splitlines()[-1] if r.stderr.strip() else '(none)'}")

# Every one of the 256 two-element messages changes its first element, so the
# vector program has no fixed point. The solver detects that, then crashes while
# constructing its show-why substitution (the explanation path is the defect).
showwhy_fixed = [(a, b) for a, b in vector_messages if ((a + 1) % 16, b) == (a, b)]
r = run("vector_show_why.px")
showwhy_still_fails = r.returncode != 0 and "PARADOX! No consistent timeline exists" in r.stdout and "Z3 expression expected" in r.stderr
ok &= check("old show-why repro: no fixed points, explanation still crashes", showwhy_still_fails and len(showwhy_fixed) == 0, f"brute force fixed points={len(showwhy_fixed)}; stdout has paradox={('PARADOX! No consistent timeline exists' in r.stdout)}")

# New wrong-answer bug: under ordinary branch/loop semantics, x=0 runs the
# loop and maps to 1; all nonzero x skip it and retain i=7, so the only fixed
# point is 7. The engine unconditionally unrolls the skipped loop and returns 1.
def reference_loop(x):
    i = 7
    if x == 0:
        for i in range(2):
            pass
    return i
loop_expected = [x for x in range(-8, 8) if reference_loop(x) == x]
r = run("inactive_loop_target.px")
loop_actual = timeline_values(r.stdout)
ok &= check("NEW WRONG ANSWER: inactive branch leaks unrolled loop target", r.returncode == 0 and loop_expected == [7] and loop_actual == [1] and loop_actual != loop_expected, f"brute force fixed points={loop_expected}; solver claims={loop_actual}")

# Huge literal: modulo 256 it is 255, so translation by -1 has no fixed point.
huge_expected = [x for x in range(-128, 128) if signed(x + 340282366920938463463374607431768211455, 8) == x]
r = run("huge_wrap.px")
ok &= check("huge integer wraps exactly; no fixed point", r.returncode == 0 and not huge_expected and "PARADOX! No consistent timeline exists" in r.stdout, f"brute force fixed points={huge_expected}")

# x|1 has precisely the eight odd 4-bit signed fixed points; the CLI intentionally
# lists five and reports that there are more than five.
many_expected = sorted(x for x in range(-8, 8) if (x | 1) == x)
r = run("many_timelines.px")
many_shown = timeline_values(r.stdout)
ok &= check("many timelines: reports truncation without claiming an exact count", r.returncode == 0 and len(many_expected) == 8 and "More than 5 consistent timelines" in r.stdout and len(many_shown) == 5 and all(x in many_expected for x in many_shown), f"brute force count={len(many_expected)}; shown={many_shown}")

# Nested condition maps zero to one and leaves all other values alone: 15 fixed points.
deep_expected = [x for x in range(-8, 8) if (1 if x == 0 else x) == x]
r = run("deep_nesting.px")
deep_shown = timeline_values(r.stdout)
ok &= check("deep nested branches: all sampled timelines are valid", r.returncode == 0 and len(deep_expected) == 15 and "More than 5 consistent timelines" in r.stdout and len(deep_shown) == 5 and all(x in deep_expected for x in deep_shown), f"brute force count={len(deep_expected)}; shown={deep_shown}")

# Surprise: x -> 5x+12 appears to amplify values, but in Z/256Z it has
# four fixed points because 4x = -12 has four solutions modulo 256.
modular_expected = sorted(signed(x, 8) for x in range(256) if (5 * x + 12) % 256 == x)
r = run("modular_fixed_points.px")
modular_actual = timeline_values(r.stdout)
ok &= check("surprise: independently enumerate four modular fixed points", r.returncode == 0 and modular_expected == [-67, -3, 61, 125] and sorted(modular_actual) == modular_expected, f"brute force={modular_expected}; solver={sorted(modular_actual)}")

# A program with no future inputs has one ordinary empty-message execution.
r = run("no_future.px")
no_future_ok = (r.returncode == 0 and "Exactly 1 consistent timeline" in r.stdout and "timeline 1: x = 3" in r.stdout)
ok &= check("no future variables: one ordinary timeline", no_future_ok, f"rc={r.returncode}; contains count={'Exactly 1 consistent timeline' in r.stdout}; contains value={'timeline 1: x = 3' in r.stdout}")

print("\nAudit result: " + ("findings reproduced; all control checks matched" if ok else "unexpected behavior; see FAIL lines"))
sys.exit(0 if ok else 1)

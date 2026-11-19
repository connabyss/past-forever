#!/usr/bin/env python3
"""Independent small-domain audit of PARADOX. Run from the repo root.

Requires z3-solver, as does paradox.py. This is deliberately a black-box checker:
all expected answers below come from ordinary Python enumeration, not Z3 or the
PARADOX implementation. Exit 0 means the observed behavior matches this audit,
that PARADOX gave the right answer on every repro (the arithmetic is exact, as in Python: nothing wraps).
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

# Old arithmetic repro family: exhaustively compute all 16 signed inputs. PARADOX follows Python's % and //
# (the sign of % follows the divisor; // rounds down), not C's.
rem_expected = sorted(x for x in range(-8, 8) if x % -3 == x)
r = run("arithmetic_remainder.px")
rem_actual = timeline_values(r.stdout)
ok &= check("old arithmetic: Python remainder", r.returncode == 0 and sorted(rem_actual) == rem_expected == [-2, -1, 0], f"brute force={rem_expected}; solver={sorted(rem_actual)}")

div_expected = sorted(x for x in range(-8, 8) if x // -3 == x)
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
shown = re.findall(r"timeline \d+: d = (-?\d)(-?\d), x = (-?\d+)", r.stdout)
ok &= check("old d[-1] repro: all 256 messages work and x is always the last element", r.returncode == 0 and len(negative_index_expected) == 256 and "More than 5 consistent timelines" in r.stdout and len(shown) == 5 and all(b == x for a, b, x in shown), f"independent brute-force count={len(negative_index_expected)}; shown={shown}; stderr={r.stderr.strip()[-200:]}")

# Every one of the 256 two-element messages changes its first element, so the
# vector program has no fixed point. The solver detects that, then crashes while
# constructing its show-why substitution (the explanation path is the defect).
showwhy_fixed = [(a, b) for a, b in vector_messages if ((a + 1) % 16, b) == (a, b)]
r = run("vector_show_why.px")
explained = all(f"if the future sent {g} everywhere, the program would end with d = [{g + 1}, {g}]" in r.stdout for g in (0, 1, 7))
ok &= check("old show-why repro: no fixed points, and the explanation prints", r.returncode == 0 and "PARADOX! No consistent timeline exists" in r.stdout and explained and len(showwhy_fixed) == 0, f"brute force fixed points={len(showwhy_fixed)}; out={r.stdout[-300:]} err={r.stderr[-200:]}")

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
ok &= check("Arena's wrong answer, fixed: a skipped loop leaves its name alone", r.returncode == 0 and loop_expected == [7] and loop_actual == loop_expected, f"brute force fixed points={loop_expected}; solver claims={loop_actual}")

# The same bug class: code that only some timelines reach must only change (or crash) those timelines.
def plain(prog):
    """The consistent x for a 4-bit one-name program, by running it in Python for all 16 messages."""
    good = []
    for sent in range(-8, 8):
        g = {}
        try: exec(prog.replace("future(x)", str(sent)), g)
        except (ZeroDivisionError, IndexError, NameError): continue
        if g["x"] == sent: good.append(sent)
    return good

for case, want in [("dead_arm.px", [0]), ("short_circuit.px", [0]), ("dead_branch_index.px", [3]),
                   ("dead_branch_name.px", [2]), ("floor_division_edge.px", [-8])]:
    src = "\n".join(l for l in (HERE / case).read_text().splitlines() if not l.startswith(("bits", "show", "#")))
    r = run(case); got = timeline_values(r.stdout)
    ok &= check(f"same class: {case}", r.returncode == 0 and plain(src) == want and sorted(got) == want, f"brute force={plain(src)}; solver={got}; err={r.stderr[-200:]}")

# An outside review (2026-11-19). Each of these was wrong before its fix.
r = run("name_clash.px")
ok &= check("future(x, 2) and future(x1) are separate messages", r.returncode == 0 and "Exactly 1 consistent timeline" in r.stdout and "timeline 1: x = 01, x1 = 2" in r.stdout, r.stdout[-300:] + r.stderr[-300:])
r = run("list_length.px")
ok &= check("a list that ends shorter than it was sent is never consistent", r.returncode == 0 and "PARADOX! No consistent timeline exists" in r.stdout, r.stdout[-300:] + r.stderr[-300:])
r = run("shape_branch.px")
ok &= check("a list that changes length in only some timelines is refused, not cut short", r.returncode != 0 and "same shape in every timeline" in r.stderr, r.stdout[-300:] + r.stderr[-300:])
chain_src = "\n".join(l for l in (HERE / "chained_compare.px").read_text().splitlines() if not l.startswith(("bits", "show", "#")))
r = run("chained_compare.px")
ok &= check("a < b < c stops at the first false, like Python", r.returncode == 0 and plain(chain_src) == [0] and timeline_values(r.stdout) == [0], f"brute force={plain(chain_src)}; solver={timeline_values(r.stdout)}")
six = [x for x in range(-4, 4) if (x + 1 if x in (0, 1) else x) == x]
r = run("exactly_six.px")
ok &= check("Exactly 6 lists all 6", r.returncode == 0 and len(six) == 6 and "Exactly 6 consistent timelines" in r.stdout and sorted(timeline_values(r.stdout)) == six, f"brute force={six}; shown={timeline_values(r.stdout)}")

# Huge literal: added exactly, so x + huge is never x.
huge_expected = [x for x in range(-128, 128) if x + 340282366920938463463374607431768211455 == x]
r = run("huge_wrap.px")
ok &= check("huge integer is added exactly; no fixed point", r.returncode == 0 and not huge_expected and "PARADOX! No consistent timeline exists" in r.stdout, f"brute force fixed points={huge_expected}")

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

# Arena's surprise: x -> 5x+12 has four fixed points in C-style 8-bit wraparound, because 4x = -12 has four
# solutions modulo 256 (-67, -3, 61, 125 as signed bytes). PARADOX no longer wraps: written plainly there is one
# integer answer, and written with % 256 the answers are the ones a message (-128..127) can carry.
assert sorted(signed(x, 8) for x in range(256) if (5 * x + 12) % 256 == x) == [-67, -3, 61, 125]
modular_expected = [x for x in range(-128, 128) if 5 * x + 12 == x]
r = run("modular_fixed_points.px")
modular_actual = timeline_values(r.stdout)
ok &= check("surprise, exact: 5x + 12 = x only at -3", r.returncode == 0 and modular_expected == [-3] and sorted(modular_actual) == modular_expected, f"brute force={modular_expected}; solver={sorted(modular_actual)}")
wrap_expected = [x for x in range(-128, 128) if (5 * x + 12) % 256 == x]
r = run("modular_wrap.px")
ok &= check("surprise, with % 256: 61 and 125", r.returncode == 0 and wrap_expected == [61, 125] and sorted(timeline_values(r.stdout)) == wrap_expected, f"brute force={wrap_expected}; solver={timeline_values(r.stdout)}")

# A program with no future inputs has one ordinary empty-message execution.
r = run("no_future.px")
no_future_ok = (r.returncode == 0 and "Exactly 1 consistent timeline" in r.stdout and "timeline 1: x = 3" in r.stdout)
ok &= check("no future variables: one ordinary timeline", no_future_ok, f"rc={r.returncode}; contains count={'Exactly 1 consistent timeline' in r.stdout}; contains value={'timeline 1: x = 3' in r.stdout}")

# Every operator on every pair of 3-, 4- and 5-bit values, and random programs with branches, loops,
# `a if c else b`, and/or and early returns, against plain Python.
for script, args in [("ops.py", [str(ROOT / "paradox")]), ("fuzz.py", ["200", "1"])]:
    r = subprocess.run([sys.executable, str(HERE / script)] + args, cwd=ROOT, capture_output=True, text=True, timeout=900)
    ok &= check(f"brute force: {script}", r.returncode == 0 and ("bad 0" in r.stdout or "0 disagree" in r.stdout), r.stdout[-400:] + r.stderr[-300:])

print("\nAudit result: " + ("every repro gave the right answer" if ok else "wrong answers; see FAIL lines"))
sys.exit(0 if ok else 1)

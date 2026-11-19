# PARADOX: a language with time travel

**Read a variable before it is written. The language finds a timeline where that makes sense.**

```
x = future(x)      # x starts as the value x will have when the program ends
```

Everything else is plain Python-style code with exact integers, like Python's. The messages from the future are
64-bit numbers unless you write `bits 32` or `bits 8`. PARADOX runs the program for every message the future could send, all at once, and keeps only the
**consistent timelines**: the ones where the program ends with exactly what the future sent back.

- one timeline: that is the answer, "received from the future"
- several: it lists them and says exactly how many there are, up to 6 (with 7 or more it shows 5 and says "More than 5")
- none: a **paradox**, and it shows why

```
pip install z3-solver
python3 paradox/paradox.py paradox/examples/factor.px
```

## Four programs

**The grandfather paradox** ([grandfather.px](examples/grandfather.px)): `x = future(x)` then `x = x + 1`. Whatever
the future sends, the program ends with one more, so no timeline is consistent. PARADOX says so.

**Factoring by time travel** ([factor.px](examples/factor.px)): the future sends p and q. If they aren't a real
factor pair of 1,071,514,531, the program changes p, so that timeline can't exist. The only one left:
`p = 32719, q = 32749`, in about a second and a half. Check it: `32719 × 32749 = 1071514531`.

**A number that describes itself** ([self_describing.px](examples/self_describing.px)): the future sends 10 digits;
the program counts how many 0s, 1s, … 9s they contain and ends with those counts. Out of 2^80 possible messages,
exactly one survives: `6210001000` (six 0s, two 1s, one 2, one 6). The program never says how to find it.

**Exact arithmetic, so nothing is lost or made up** ([square_root.px](examples/square_root.px)): numbers never
wrap around. Every value in between is as wide as it needs to be, like a Python int; only the messages from the
future are limited to 64 bits (or `bits N`). So `x × x = 1522756` gives exactly one timeline, 1234. (An earlier
version wrapped like C: it found three fake answers here, lost real ones and invented negative ghosts elsewhere. An
AI agent in the Arena proved it; see [experiments/](experiments/), whose checks now guard it.) A timeline that crashes,
by dividing by zero, reading a name that has no value yet or indexing past the end of a list, is not consistent.
Only the timelines that actually get there crash: a branch, loop, `a if c else b` or the far side of `and`/`or`
that a timeline skips can't change or crash it, just as in Python. (Arena's second audit caught a skipped loop that
still changed its name; see [audit_2026/](audit_2026/).)

## A sentence from the future that counts its own letters

[autogram.py](autogram.py) builds a sentence whose 26 numbers are sent from the future, counts its letters, and nudges
the numbers until the sentence is true:

> This sentence was sent back from the future and contains six a's, two b's, four c's, three d's, twenty-nine e's,
> ten f's, one g, six h's, twelve i's, one j, two k's, two l's, two m's, twenty-three n's, fifteen o's, one p, one q,
> nine r's, thirty s's, twenty-five t's, six u's, four v's, ten w's, four x's, five y's and one z.

Count any letter yourself. Sentences like this are called autograms; Lee Sallows made them famous in the 1980s.
This one is new because of its wording; the idea is his.

## Honest notes

- "All messages at once" is a SAT solver ([z3](https://github.com/Z3Prover/z3)) underneath. PARADOX turns the
  program into one big logic formula and asks for every fixed point. Exact arithmetic costs speed on big numbers:
  `x × x % 10^6 == x` takes about 2 minutes with `bits 40`, and the 64-bit version with `% 10^18` did not finish in
  10 minutes. Slow, but never wrong: it no longer wraps.
- The autogram search is a plain nudge-toward-the-count loop, not the solver, and it is not guaranteed to finish for
  every wording.
- Checks: `python3 paradox/test_paradox.py` (add `--slow` to rebuild the autogram and re-count its letters), and
  `python3 paradox/experiments/check.py` (add `--slow` for the 40- and 44-bit runs), and
  `python3 paradox/audit_2026/check.py` (every repro, every operator on small values, and 200 random programs, all
  against plain Python).

Built live in a GitHub Codespace by an explorer agent.

Guest additions that go past these four: [experiments/](experiments/) - a proof by having no
timeline, a program the future writes, and the fixed points of squaring (which are the ends of
`past-forever`'s two hero numbers). Plus the width trap that used to eat one of them, now fixed.

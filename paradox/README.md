# PARADOX: a language with time travel

**Read a variable before it is written. The language finds a timeline where that makes sense.**

```
x = future(x)      # x starts as the value x will have when the program ends
```

Everything else is plain Python-style code on fixed-width integers (64-bit unless you write `bits 32` or `bits 8`),
wrapping like C. PARADOX runs the program for every message the future could send, all at once, and keeps only the
**consistent timelines**: the ones where the program ends with exactly what the future sent back.

- one timeline: that is the answer, "received from the future"
- several: it lists them and says exactly how many there are
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

**Time travel finds your overflow bug** ([square_root.px](examples/square_root.px)): ask for x with
`x × x = 1522756`. You expect 1234. PARADOX finds 4 timelines: 1234, and three huge numbers whose 64-bit square wraps
around to 1522756.

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
  program into one big logic formula and asks for every fixed point. Big multiplications and divisions on 64-bit
  numbers can be slow (factoring a 40-bit number with `%` did not finish in two minutes).
- The autogram search is a plain nudge-toward-the-count loop, not the solver, and it is not guaranteed to finish for
  every wording.
- Checks: `python3 paradox/test_paradox.py` (add `--slow` to rebuild the autogram and re-count its letters).

Built live in a GitHub Codespace by an explorer agent.

Guest additions that go past these four: [experiments/](experiments/) - a proof by having no
timeline, a program the future writes, and the fixed points of squaring (which are the ends of
`past-forever`'s two hero numbers). Plus the width trap that silently eats one of them.

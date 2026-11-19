# Liars

Back to the [README](../README.md). A **liar** is a loop like `x = x × x + c` whose last digits look settled into a ring for many digits, and then go wild.

## The records

**A loop that lies for 1000 digits.** Run `x = x × x + c` from 0. For a wild c, the steps its last 1, 2, 3… digits
take to come round grow ×5 per digit (10, 50, 250…). A liar stays calm first: digit after digit the count stays at
1, 2 or 8, like a loop that has settled, and only then it goes wild. The record liars, each calm for more digits
than every smaller c, go 2, 7, 57, 182, 1068, 14557, 30982, 265357, 6139557, 8077857, … and the list now runs
to 1000 digits of calm. The smallest c that stays calm for 1000 digits is 698 digits long, and it holds out for 1001
before it breaks. Check it yourself in plain Python, from a clone of this repo (it takes a blink):

```python
c = int(open("liars/records.txt").read().split()[-1])   # the last record in the list
for k in (1000, 1001, 1002):                             # look at the last k digits
    m, x, seen = 10**k, 0, {}
    while x not in seen:
        seen[x] = len(seen); x = (x * x + c) % m
    print(k, "digits come round every", len(seen) - seen[x], "steps")
# 1000: 2,  1001: 2,  then 1002: 10, and ×5 for every digit after that
```

A short one to check without cloning: c = `38533618339183472936432`, calm for 35 digits.

```python
c = 38533618339183472936432
for k in (34, 35, 36, 37):                    # look at the last k digits
    m, x, seen = 10**k, 0, {}
    while x not in seen:
        seen[x] = len(seen); x = (x * x + c) % m
    print(k, "digits come round every", len(seen) - seen[x], "steps")
# 34: 8,  35: 8,  then 36: 40,  37: 200, and ×5 for every digit after that
```

## Why they lie

**Why they lie.** Two fresh AI agents worked this out on their own ([Hall of Fame](../BREAK_IT.md#hall-of-fame) #5), and it
matches what turned up while hunting. The last k digits run two clocks at once, one for the 2s in 10^k and one for
the 5s. The 2s clock never lies (proved: there the slope 2x is even, so the ring is 1 or 2 long). The 5s clock does
all of it. Every long liar sits close, in base 5, to one of four special values of c, the **magnets**: −2, the two
5-adic square roots of −1, and M, the other c ending in 2 (base 5) with x·x + c from 0 landing back on its own
second step after 10 steps (…1001440314111230040323412323104031442412 in base 5). "Close" means exactly this: **a c
that stays calm for k digits has the same last k − 2 base-5 digits as one of the four magnets**, and from 5 digits
on, k − 2 can't be raised. For c ending in 3 (base 5) that follows from a short formula, calm for k digits means 5^k
divides (c + 2)(c·c + 1), inside a proof sketch nobody outside this project has checked. For c ending in 2 it is
**checked, not proved**: [tests/magnets.py](../tests/magnets.py) builds every calm c, digit by digit, and tests the
statement at every depth from 3 to 1000, on every build. Making liars on purpose is checked, not proved: c = 5^k − 2 stayed calm for
exactly k + 1 digits for every k we tried (k up to 40).

## Other powers

**Odd powers can't lie (proved, short).** From 0, `x = x × x × x + c` (or the 5th or 7th power) settles into a
ring whose length never changes with depth: however many digits you watch, it comes round in the same number of
steps as its last digit does. For example `x = x × x × x + 1` goes 0, 1, 2, 9, 0 on the last digit, and on the last
30 digits it still comes round every 4 steps. The proof, for f(x) = x^p + c with p = 3, 5 or 7:
1. On one digit, f shuffles 0 to 9 without losing any (x^p mod 2 is x, and x^p mod 5 is a shuffle because p shares
   no factor with 4). So 0's last digit comes back to 0, after r steps, and r is the ring's length on one digit.
2. Let g be f done r times. Its slope at 0 is a product of f's slopes round the ring, and one of them is f'(0) =
   p × 0^(p−1) = 0. So for any two numbers ending in 0, g(x) − g(y) = (x − y) × (a multiple of 10): if they share
   k digits, g of them share k + 1.
3. So g, started at 0, freezes one more digit every round and has one limit z ending in 0, with g(z) = z. f's ring
   through z is r long on every depth (it can't be shorter, because on the last digit it is r long), and 0's path
   falls into it. Squares are different: the same step only works when the ring's slopes multiply to a multiple
   of 10, and for most c they don't. (Also checked by machine: every c below 200 with powers 3, 5 and 7, on 1 digit and on 30, comes round in the same
   number of steps.)

**Even powers: some lie, some can't.** Squares aren't the only liars. `x = x ^ 4 + c`, from 0, lies too, and its
record liars are a different list: 1, 7, 11, 61, 211, 836, 1061, 5348, 366461, 3110436, … ([liars/records4.txt](records4.txt),
to 1000 digits of calm). Check one in plain Python:

```python
c = 366461
for k in (10, 11, 12, 13):                    # look at the last k digits
    m, x, seen = 10**k, 0, {}
    while x not in seen:
        seen[x] = len(seen); x = (x**4 + c) % m
    print(k, "digits come round every", len(seen) - seen[x], "steps")
# 10: 4,  11: 4,  then 12: 20,  13: 100, and ×5 for every digit after that
```

Going up the even powers, they split three ways ([liars/powers.py](powers.py) `table`):

| power | what its loops do |
|---|---|
| 2, 4, 8, 12, 14, 18, 22, 24 | can lie: calm for 25 digits and more before going wild (squares and 4th powers: 1000) |
| 6 and 16 | go wild by their 3rd digit or never (26: by the 4th) |
| 10 and 20 | never go wild |

- **10 and 20 (proved, short).** The slope of x^10 is 10 × x^9, a multiple of 5 and of 2 for every x, so every
  ring pulls digits together the way 0 does in "Odd powers can't lie": however deep you look, it comes round in
  the same number of steps.
- **6, 16 and 26 (proved, by a finite check).** For an even power the 2s clock never lies (the slope p × x^(p−1)
  is even), and whether c stays calm for k digits depends only on c's remainder after dividing by 5^k. A c that
  leaves 0, 1 or 4 after dividing by 5 (for the 16th power, 0 or 4) can never go wild, because then, on the last
  base-5 digit, the loop comes back round to 0 itself, where the slope is 0. So it is enough to try the 125
  remainders (625 for the 26th) of the others, and none stays calm. [tests/powers.py](../tests/powers.py) also
  checks every c below 15,625 the slow way in base 10.
- **The loner.** 4th powers keep 61 calm remainders, not 60, and the extra one has no family: it is the only
  calm remainder that shares its last k − 2 base-5 digits with no other. It is the 5-adic c with c × c × c = i − 1
  (i is the square root of −1 ending in 3, base 5). Its loop doesn't lie, it settles, after exactly two steps:
  x goes 0, c, then c^4 + c = c × i, and (c × i)^4 + c is c × i again, because i^4 = 1 (proved, three lines of
  algebra). Every c near it is a liar. 8th powers have a loner too, with c^7 = −2. That each loner stands alone is
  checked at every depth from 5 to 60, not proved.
- **The liars.** That 2, 4, 8… can lie is shown by the liars themselves. How many calm remainders each keeps
  (deep down, 60 for squares, 61 for 4th powers, 21 for 8th powers) is checked to 25 digits, not proved, and so
  is that they can lie for as long as you like.
  Nobody outside this project has checked any of this, and we haven't been able to search the
  [OEIS](https://oeis.org) for the 4th-power list yet.

## How we searched

**How we searched.** The first ten records came from trying every c up to 40 million, one by one, in two separate
programs. Past that, whether c stays calm for k digits depends only on c's remainder after dividing by 5^k, so the
calm remainders can be built one base-5 digit at a time, with nothing skipped (there are exactly 60 at every depth
from 5 on). The smallest one is the record, and each record was re-checked by brute force. Rebuild the list yourself with
[liars/search.py](search.py) (`python3 liars/search.py 1000`, about a minute and a half) and re-check it the
slow way, digit by digit in base 10, with [liars/check.py](check.py) (all 785 records, about 8 minutes, 0 wrong). Why each one is the
smallest, in four steps you can check by reading, and how a second program and a brute force below 10 million confirm
it on every build: [liars/WHY_SMALLEST.md](WHY_SMALLEST.md). "Nothing skipped" rests
on our reasoning and the agents', not on anyone's review. We searched the [OEIS](https://oeis.org) for the record
list in November 2026 and didn't find it, but many of its terms are close cousins of lists that are there: the
5-adic square roots of −1 ([A048898](https://oeis.org/A048898), [A048899](https://oeis.org/A048899)).

**Don't believe it? Good.** Pick the claim you trust least and check it with your own arithmetic. Then try to
[break it](../BREAK_IT.md): a wrong `proved` gets your name in the Hall of Fame. Coding agents: [AGENTS.md](../AGENTS.md)
has a dare for you.

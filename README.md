# Past Forever

**Write a loop that never ends. Get its answer anyway, exactly.** This loop never stops, and the program runs on past it:

```
x = 5
forever: x = x × x
show x
```

```
…918212890625
```

5, 25, 625, 390625… squared forever, and the digits on the right freeze. **Check it on any calculator:**
`90625 × 90625 = 8212890625`, which ends in `90625` again. Every digit you keep does the same. It is its own square.

Same trick, other answers: `1 ÷ 7 = …142857143` (check: `142857143 × 7 = 1000000001`, and the more 142857s you
add, the more zeros), and the last digits of [Graham's number](#the-last-digits-of-grahams-number).

**Two numbers, neither one zero, that multiply to exactly 0.** Run a second loop, `y = 6` then
`forever: y = y ^ 5`, and it settles to `…081787109376`. Now `show x × y` prints `0`, and `show x + y` prints
`1`. Check the last 4 digits by hand: `0625 × 9376 = 5860000` (four zeros) and `0625 + 9376 = 10001`. Take more
digits and you get more zeros. In these numbers, 0 has two non-zero factors (`node cli.js examples/zero_twins.txt`).

**What it can and can't do.** Past Forever answers loops of plain arithmetic on one or a few numbers: adding,
multiplying, fractions, powers, tests like `is even`. For each it either proves the answer, proves the loop never
settles, or says `can't see the end`. It does not solve any infinite program you could write, and it tells you
when it can't.

**Try it in 10 seconds** (Node 18+, no dependencies):

```
git clone https://github.com/connabyss/past-forever && cd past-forever
node cli.js examples/graham.txt     # …262464195387, the end of Graham's number
```

**Found with it: a loop that lies for 1000 digits.** Run `x = x × x + c` from 0. For a wild c, the steps its last 1, 2, 3… digits
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

**Why they lie.** Two fresh AI agents worked this out on their own ([Hall of Fame](#hall-of-fame) #5), and it
matches what turned up while hunting. The last k digits run two clocks at once, one for the 2s in 10^k and one for
the 5s. The 2s clock never lies (proved: there the slope 2x is even, so the ring is 1 or 2 long). The 5s clock does
all of it. Every long liar sits close, in base 5, to one of four special values of c, the **magnets**: −2, the two
5-adic square roots of −1, and M, the other c ending in 2 (base 5) with x·x + c from 0 landing back on its own
second step after 10 steps (…1001440314111230040323412323104031442412 in base 5). "Close" means exactly this: **a c
that stays calm for k digits has the same last k − 2 base-5 digits as one of the four magnets**, and from 5 digits
on, k − 2 can't be raised. For c ending in 3 (base 5) that follows from a short formula, calm for k digits means 5^k
divides (c + 2)(c·c + 1), inside a proof sketch nobody outside this project has checked. For c ending in 2 it is
**checked, not proved**: [tests/magnets.py](tests/magnets.py) builds every calm c, digit by digit, and tests the
statement at every depth from 3 to 1000, on every build. Making liars on purpose is checked, not proved: c = 5^k − 2 stayed calm for
exactly k + 1 digits for every k we tried (k up to 40).

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

**How we searched.** The first ten records came from trying every c up to 40 million, one by one, in two separate
programs. Past that, whether c stays calm for k digits depends only on c's remainder after dividing by 5^k, so the
calm remainders can be built one base-5 digit at a time, with nothing skipped (there are exactly 60 at every depth
from 5 on). The smallest one is the record, and each record was re-checked by brute force. Rebuild the list yourself with
[liars/search.py](liars/search.py) (`python3 liars/search.py 1000`, about a minute and a half) and re-check it the
slow way, digit by digit in base 10, with [liars/check.py](liars/check.py) (all 785 records, about 8 minutes, 0 wrong). Why each one is the
smallest, in four steps you can check by reading, and how a second program and a brute force below 10 million confirm
it on every build: [liars/WHY_SMALLEST.md](liars/WHY_SMALLEST.md). "Nothing skipped" rests
on our reasoning and the agents', not on anyone's review. We searched the [OEIS](https://oeis.org) for the record
list in November 2026 and didn't find it, but many of its terms are close cousins of lists that are there: the
5-adic square roots of −1 ([A048898](https://oeis.org/A048898), [A048899](https://oeis.org/A048899)).

**Don't believe it? Good.** Pick the claim you trust least and check it with your own arithmetic. Then try to
[break it](#break-it): a wrong `proved` gets your name in the Hall of Fame. Coding agents: [AGENTS.md](AGENTS.md)
has a dare for you.

**A word on `proved`.** It means proved by the engine's own hand-written rules, listed in
[How it knows](#how-it-knows). No mathematician has reviewed them and no proof assistant has checked them. Some kinds
of answer also get a **second opinion**: a separate checker, [tests/certify.py](tests/certify.py), shares no code with
the engine, writes its own proof, and fails the build if it can't prove an answer or disagrees. It covers one-name
polynomial loops like `x = (3 × x × x + 7) / 11`, power towers like `x = 3 ^ x` (any whole number from 2 up), and
`x = x ^ x`. Every other `proved` (pairs of names, loops with `if`, endless sums, counts past forever, polynomials
with an endless number in them) rests on the engine's rules alone, plus the robot referee, which tries thousands of
random loops on every build: a strong check, not a proof. [How it knows](#how-it-knows) marks which is which.

<p align="center"><a href="https://connabyss.github.io/past-forever/"><img src="media/try-it-now.svg" width="300" alt="Try it now: open the playground in your browser"></a></p>

<p align="center">or take the <a href="https://connabyss.github.io/past-forever/#wonders">Wonders tour</a>: 7 surprises, one tap each</p>

## First, try this on a calculator

Any calculator works (turn your phone sideways if an answer gets cut off). Copy each sum exactly: the number of zeros matters, and one zero more or less spoils the trick. Do one step at a time, then open the answer.

**1.** Work out `90625 × 90625`. Look at the last five digits.

<details><summary>Answer</summary>

`8212890625`. It ends in **90625**, the number you started with.

</details>

**2.** Work out `9376 × 9376`. Look at the end.

<details><summary>Answer</summary>

`87909376`. It ends in **9376** again.

</details>

**3.** Add the two numbers: `90625 + 9376`.

<details><summary>Answer</summary>

`100001`. A 1, a row of zeros, and a 1.

</details>

**4.** Work out `66666667 × 3`. Look at the zeros.

<details><summary>Answer</summary>

`200000001`. Everything after the 2 is zeros and a final 1. So 66666667 acts a lot like a third.

</details>

**5.** Work out `1 ÷ 7`.

<details><summary>Answer</summary>

`0.142857142857…`. The digits **142857** repeat to the right, forever.

</details>

**6.** Now divide these by 7, one at a time, and compare them with step 5:

```
1001 ÷ 7
1000000001 ÷ 7
1000000000000001 ÷ 7
```

<details><summary>Answer</summary>

`143`, then `142857143`, then `142857142857143`.

<img src="media/seventh.png" width="520" alt="1 ÷ 7 = 0.142857142857... and 1000000000000001 ÷ 7 = 142857142857143: the same digits, one running right and one growing left">

</details>

**7.** Your turn. Try these, and compare them with `1 ÷ 11` and `1 ÷ 13`:

```
1001 ÷ 11
100001 ÷ 11
1000000001 ÷ 13
```

<details><summary>Answer</summary>

`91` and `9091`, while 1 ÷ 11 = `0.090909…`. And `76923077`, while 1 ÷ 13 = `0.076923076923…`.
The same digits again, growing to the left.

</details>

## How this ties to Past Forever

This is real, old maths with one different rule: digits go left forever, and two numbers count as close when their
endings match. Mathematicians call these 10-adic numbers, the base-10 cousin of
[p-adic numbers](https://en.wikipedia.org/wiki/P-adic_number) (Hensel, 1897). In that world …142857142857143 times 7
is exactly 1, and it counts as a whole number there (a 10-adic integer). It is not one of the ordinary whole numbers
you count with.

A calculator only ever sees the last few digits. Past Forever works with the whole endless left side. You write the
loop that never ends, like "square 5 forever" or "1 ÷ 7, the left way", and it tells you the endless answer, and
whether it ever settles at all.

```
x = 1 / 7
show x
show x × 7
```

```
…857142857143  (this is 1/7)
1
```

**Your calculator rounds. Past Forever doesn't.** Work out `1 ÷ 7` on a calculator and the last digit it shows is
rounded, like `0.1428571429` or `0.142857142857143`, because the real digits `142857` never stop. Past Forever
never holds all the digits. It finds the repeating pattern, so the answer is exact, and when it can't be sure it
says `can't see the end` instead of guessing.

Here it squares 5 forever. The gold digits are the ones that never change again:

<p align="center"><img src="media/hero.gif" width="520" alt="5 squared again and again: 25, 625, 390625... the digits on the right freeze one or more at a time, and Past Forever gives the final ending ...918212890625"></p>

If the digits settle, the program gets the finished number and carries on. If they never settle, it proves that
instead. If it can't tell, it says so.

**Try it in your browser:** [connabyss.github.io/past-forever](https://connabyss.github.io/past-forever/). No install, works on a phone.
New here? Take the [Wonders tour](https://connabyss.github.io/past-forever/#wonders): 7 surprises, one tap each.

## Four lines

```
x = 5
forever: x = x × x
show x
show x × x = x
```

```
…918212890625
yes  (proved)
```

5, 25, 625, 390625… Squaring forever never stops, but the digits on the right freeze, one or more at a time.
So after forever, `x` is an endless number that runs off to the left, and it is its own square. Ask `why x`
and it tells you how it knows.

It isn't the only one. 0 and 1 are their own squares, and so is its twin, `…081787109376` (start at 6 and take the
fifth power forever). Add the twins and you get `…000000000001`, which is 1. That's the `90625 + 9376 = 100001` from
the calculator steps above. The `why` for `…918212890625` says it is the one ending in 5, not the only one.

## The last digits of Graham's number

[Graham's number](https://en.wikipedia.org/wiki/Graham%27s_number) is defined with Knuth's up-arrows, 64 layers of
them. Unfold the last layer and it is a tower of 3s, `3 ^ 3 ^ … ^ 3`, so tall that the universe is too small to hold its digits. The tower does end somewhere, but nobody knows its first
digit. Past Forever can show you its last ones, by building the tower forever:

```
x = 3
forever: x = 3 ^ x
show x
show 3 ^ x = x
```

```
…262464195387
yes  (proved)
```

<p align="center"><img src="media/tower.gif" width="520" alt="A tower of 3s, one floor at a time: 3, 27, 7625597484987, and then numbers too long to write down. The digits on the right freeze in gold, one more each floor, and after forever the ending is ...262464195387"></p>

Once the tower is a few floors tall, every new floor freezes one more digit on the right. Why, in one line: two
powers 3^a and 3^b share their last k + 1 digits whenever a and b share their last k digits (for k ≥ 2), because 3
to the power 10^k ends in …0001 on its last k + 1 digits (Euler's theorem: λ(10^(k+1)) divides 10^k). So once two
floors in a row share their last 2 digits, each floor after that shares one more, and the last k digits stop
changing for good. Graham's number is a finite tower of 3s, far taller than any number of digits you
could ask for, so its last k digits are the endless tower's last k digits, for every k you can write down. Ask for `show 105 digits of x` and all 105 match the digits listed in the
[OEIS (A133613)](https://oeis.org/A133613). The tests check them on every build.

**Hear it.** `sing` plays any answer's digits as music, one note per digit, right to left: the order the digits
freeze in. Each digit picks a note from a five-note scale (0 lowest, 9 highest), so no order of digits can clash,
with a bass note every 4th digit and a bell every 10th. In the [playground](https://connabyss.github.io/past-forever/)
pick **Sing it** and press play. On your own computer, save a minute of Graham's number as a sound file:

```
node cli.js examples/sing.txt --wav graham.wav     # its last 360 digits, about a minute
```

The tune came from an explorer agent in a GitHub Codespace ([Hall of Fame](#hall-of-fame) #7).

## Three honest answers

Every value that comes out of a forever loop is one of three things:

| answer | example | what it printed |
|---|---|---|
| a number, with proof | add 9, 90, 900, … forever | `…999999999999  (this is -1)` |
| **never settles**, with proof | `x = 6`, square forever | `never settles` (the last two digits go 36, 96, 16, 56 forever) |
| **can't see the end** | 196, reverse and add forever | `can't see the end` |

Searches work the same way. "Does some square end in 7?" answers `no  (proved)` after looking at infinitely many
squares. Counts can go past forever too: count to forever, add one, and you get `forever + 1`.

## Hunt: try a whole range at once

```
hunt c from 0 to 99:
    x = 0
    forever: x = x × x + c
    show x
```

```
hunt c from 0 to 99: tried 100 numbers, 5 kinds of answer
  settles     10   0, 10, 20, 30, 40, 50, 60, 70, …
  ring of 6   10   1, 11, 21, 31, 41, 51, 61, 71, …
  goes wild   40   2, 3, 7, 8, 12, 13, 17, 18, …
  ring of 2   30   4, 5, 9, 14, 15, 19, 24, 25, …
  ring of 3   10   6, 16, 26, 36, 46, 56, 66, 76, …
```

<p align="center"><img src="media/zoom.gif" width="420" alt="The hunt map in the playground, zooming in on liars"></p>

`ring of N` in a hunt means every digit Past Forever looked at, 40 deep, came round every N steps. It is what it
saw, not a proof, and a liar calmer than that fools it: c = 5^45 − 2 shows `ring of 2` but goes wild at digit 47.

In the playground every number becomes a coloured square. Some wild loops are **liars**: their last digits
go round a ring of 2 for a while, then the next digit breaks it. Brighter means it lied for longer.
Tap the brightest square and **Zoom in** (`ends in 123`) to see only numbers ending in those digits.
Following the brightest one goes 123 → 78123 → 5078123 → 205078123 → 85205078123, and that last one lies for 13 digits.

## Break it

Find one of these and your name goes in the Hall of Fame below:

- **A wrong answer.** A loop where Past Forever says `proved` and is wrong. This is the big one.
- **A loop it can't see the end of, but you can.** It says `can't see the end`, and you can show the real answer.
- **The 10,000-digit liar.** [liars/records.txt](liars/records.txt) stops at 1000 digits of calm, and
  [liars/search.py](liars/search.py) takes about a minute and a half to get there. Find the smallest c that stays calm
  for 10,000 digits, show how you got it, and make it checkable. A faster way to build the same list counts too.
- **Why only four magnets?** Every c that stays calm for k digits shares its last k − 2 base-5 digits with one of
  the four magnets in "Why they lie" (checked to 1000 digits by [tests/magnets.py](tests/magnets.py)). Write a real
  proof for every k, or show a c that stays calm for k digits while sharing fewer than k − 2 with all four.

To enter, open a [Break it issue](https://github.com/connabyss/past-forever/issues/new?template=break-it.yml)
with the code and what it printed.

### Hall of Fame

1. **Leo AI in Brave (Qwen).** Its "numbers that are their own square" challenge turned up a loop that starts
   on its own answer, …081787109376 squared forever, where Past Forever said `can't see the end`. It settles,
   and now Past Forever proves it. (November 2026)
2. **GPT Luna in Brave.** `x = (M + 1) × x + M` with M = 1 and 40 zeros: the last 40 digits never move, but the
   41st goes round 0 to 9 forever. Past Forever only looked 9 digits in and said `can't see the end`. Now it looks
   as deep as the biggest number in the loop, and proves `never settles`. (November 2026)
3. **GitHub Copilot.** `repeat 10 ^ 64: x = x + 1` had no time limit, so it froze the playground. Not a wrong answer,
   but a real hang. Now `repeat` stops with a clear message after 15 seconds (8 in the playground). (November 2026)
4. **A fresh Claude Opus agent, and GitHub Copilot.** Asked only to take a look, Opus tried a tower of 2s,
   `x = 2 ^ x`, where Past Forever said `can't see the end`. It settles, on …075353432948736. Copilot found the same
   gap with `x = 10 ^ x`, which settles on 0. Now every tower on a whole number from 2 up settles by its own rule.
   (November 2026)
5. **Two fresh Claude Opus agents, separately.** Asked to "use this language like a researcher", both worked out
   why liars exist (the 5s clock and the four special values of c), found the 34-digit record
   `8616755347677791280982`, and showed c = 5^k − 2 is a liar as long as you like. One of those, 5^45 − 2, fooled the
   hunt into saying `ring of 2`, so the hunt's why now says that rings are what it saw, not proofs. (November 2026)
6. **The Liar Race: Claude Haiku, Sonnet and Opus.** Three fresh agents raced to find the smallest c that stays calm
   for 35 digits. All three found `38533618339183472936432`, each by building the calm remainders in base 5. Sonnet
   got there first: "go count to 3.85e22 by hand." (November 2026)
7. **An explorer agent in a GitHub Codespace.** Found two loops it could answer by hand where Past Forever said
   `can't see the end`: `if x is even: x = x + 1, else: x = x + 3` (its last digit goes round all ten digits forever),
   and `y = 10 × y + x` with x the endless …918212890625 (it settles on −x ÷ 9). Both are now proved, with two new
   rules below and two new families of loops for the robot referee. It also turned the last 360 digits of Graham's
   number into a song, which became `sing`, found counts that climb, like `f = f × f`, that it couldn't finish, and `x = x ^ x`, which provably never settles
   (from 7 it's a liar: its last 2 to 4 digits flip between two values, then the 5th goes wild).
   (November 2026)

## How it knows

There is no magic, only a few rules in [forever.js](forever.js), and each answer says which one it used. **(2nd)**
marks the rules whose answers the separate checker, [tests/certify.py](tests/certify.py), proves again on every build;
the rest are checked by the robot referee only.

- The whole state comes back: from then on it repeats forever. **(2nd)** for one-name polynomial loops.
- A digit stops changing, and the rule pulls nearby numbers together: one more digit locks in every step. **(2nd)** for one-name
  polynomial loops.
- A sum whose pieces end in more and more zeros settles.
- A power tower like `x = 3 ^ x`: when two tops share their last k digits, the powers share k + 1 (the bottom
  number must have no 2 or 5 in it). So once the last 2 digits stop changing, it settles. **(2nd)**
- A tower on 2, 5, 10 or any other whole number from 2 up, like `x = 2 ^ x` from an ordinary whole number: every
  step is a whole number and they grow, so soon every top is bigger than any number of digits you ask for. Then the
  same lock-one-more rule holds, and it settles. **(2nd)**
- A loop whose `if`s only test its last digits (`is even`, `is odd`, `ends in …`): the last few digits of every name
  then only depend on their last few digits, so they must come round. If a name's digits keep going round, it never
  settles. If the digits the tests read freeze, every test gives the same answer forever, and the loop is a plain one.
- `y = 10 × y + x` (or 20, 100, any multiple of 10) with x settling: each step locks one more digit, and the answer
  is exactly x ÷ (1 − 10), so −x ÷ 9.
- A count that only climbs ends at the top of its climb: `count f = 2` then `forever: f = f × f` ends at `forever`,
  and adding a count made by an earlier loop works like adding a number. (`d = d × forever` climbs to forever ^
  forever, which the language can't write yet, so it says `can't see the end` and tells you why.)
- `x = x ^ x` from a whole number of 2 or more: the numbers grow, and once x is big, the last k digits of x ^ x only
  depend on the last k digits of x. So if those go round a ring, it never settles. If x ends in 0, x ^ x ends in at
  least x zeros, so it settles on exactly 0. **(2nd)**
- Any polynomial rule whose other names are fixed endless numbers, like `y = 70 × y − 8 × y × y − 3 × x − 7`: if the
  last digit freezes where the rule's slope ends in 0, one more digit locks every step. Towers work the same way with
  extra parts times a number ending in 0, like `x = 3 ^ x − 10 × x`.
- The last digits go round a ring that never stops: proved never to settle. **(2nd)** for one-name polynomial loops
  and `x = x ^ x`.
- None of these fit: `can't see the end`.

## Honest notes

- **The maths is old.** Numbers that run off to the left are the 10-adic numbers named above. Counting past forever
  is Cantor's ordinals. The …212890625 number is an automorphic number. The frozen last digits of towers of 3s have been known for a long time too. What is new here, as far as we found,
  is a language you can actually run where code keeps going after a forever loop. Closest cousins: the
  Zeno esolang (an imaginary machine) and infinite time Turing machines
  (theory, not a language). Not finding one is not proof there isn't one.
- **The referee and the tests are strong checks, not proofs.** Everything below that says "checked" or "tested"
  means tried, not proved.
- **"proved" means proved by the rules above**, as written in forever.js. No mathematician has reviewed them and
  no proof assistant has checked them. For one-name polynomial loops, power towers and `x = x ^ x`, an independent
  checker writes its own proof of each answer (below), and the build fails if it can't prove one.
- **A robot referee checks them on every build.** [tests/referee.js](tests/referee.js) makes 4,311 random loops
  (squares, liars, straight-line rules, pairs, numbers passed back and forth, endless sums, power towers, towers on
  2, 5 and 10, loops that branch on their last digits, and y = 10 × y + an endless number, polynomials with an endless number in them, towers plus 10 × x) and checks
  every `settles`, `never settles` and exact fraction against plain arithmetic on the last 30 or more digits. Last
  run: 5,596 answers, 0 wrong, 0 `can't see the end`. That is a strong check, not a proof.
- **You don't have to trust us: a second opinion.** [tests/certify.py](tests/certify.py) is a separate checker in
  Python, about 150 lines, that shares no code with the engine. For loops like `x = (3 × x × x + 7) / 11` it writes
  down its own proof of each answer, using textbook facts only: last digits going round a ring means never settles;
  a last digit that the rule fixes and pulls in means settles, and the rational root theorem names the exact answer.
  It prints how many of Past Forever's answers it proved again, how many it couldn't decide, and how many loops
  Past Forever gave no answer for. The build fails on any disagreement and on any answer it couldn't prove. On
  5,000 random loops it proved all 5,000 answers again, 0 undecided, 0 disagreements, all 60 digits matching. Every
  build re-runs 300 of them, every tower `x = b ^ x` for b from 2 to 40 and every `x = x ^ x` from 2 to 40 (all 60
  digits compared), plus the ten loops in [tests/certificates.jsonl](tests/certificates.jsonl), whose
  proofs are written out by hand in [tests/certificates.md](tests/certificates.md). (Written by an explorer agent in a GitHub Codespace.)
- Rings and liars are checked 40 digits deep. A liar that lies for more than 40 digits would look like a ring.
- `can't see the end` comes up a lot. That's the language being honest, not a bug.

## Run it

You need Node.js 18 or newer. There are no dependencies.

```
git clone https://github.com/connabyss/past-forever && cd past-forever
node cli.js examples/own_square.txt --why
node tests/run.js        # ok: 665 checks
node tests/referee.js    # the robot referee, about 5 minutes
node tests/certify_gen.js 300 2027 | python3 tests/certify.py   # the second opinion, about a minute
```

The playground is one file, [docs/index.html](docs/index.html). Rebuild it with `python3 page/build.py`.

## Where it came from

connabyss asked Claude (an AI) for a strange new language that would grow out of playing with numbers.
One idea from that play was a loop that finishes forever, and connabyss picked it. The language was built in a day
with Claude Code, and the liar loops turned up while hunting with it.

MIT licence.

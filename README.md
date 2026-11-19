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
add, the more zeros), and the last digits of [Graham's number](GUIDE.md#the-last-digits-of-grahams-number), which you can
[hear played on a paper piano roll](https://connabyss.github.io/past-forever/sing.html).

**Two numbers, neither one zero, that multiply to exactly 0.** Run a second loop, `y = 6` then
`forever: y = y ^ 5`, and it settles to `…081787109376`. Now `show x × y` prints `0`, and `show x + y` prints
`1`. Check the last 4 digits by hand: `0625 × 9376 = 5860000` (four zeros) and `0625 + 9376 = 10001`. Take more
digits and you get more zeros. In these numbers, 0 has two non-zero factors (`node cli.js examples/zero_twins.txt`, or tap Wonder 2 in
the [playground](https://connabyss.github.io/past-forever/)).

**What it can and can't do.** Past Forever answers loops of plain arithmetic on one or a few numbers: adding,
multiplying, fractions, powers, tests like `is even`. For each it either proves the answer, proves the loop never
settles, or says `can't see the end`. It does not solve any infinite program you could write, and it tells you
when it can't.

**Try it in 10 seconds** (Node 18+, no dependencies):

```
git clone https://github.com/connabyss/past-forever && cd past-forever
node cli.js examples/graham.txt     # …262464195387, the end of Graham's number
```

**Found with it: loops that lie.** Run `x = x × x + c` from 0. Most choices of c either settle or go wild fast. A
**liar** looks settled for a while: its last digits keep coming round in a small ring, digit after digit, and then
one more digit breaks the pattern and it goes wild. The record liars, each calm for more digits than every smaller
c, go 2, 7, 57, 182, 1068, 14557, … and the list runs to 1000 digits of calm.

Check one yourself, in plain Python: c = `38533618339183472936432` stays calm for 35 digits.

```python
c = 38533618339183472936432
for k in (34, 35, 36, 37):                    # look at the last k digits
    m, x, seen = 10**k, 0, {}
    while x not in seen:
        seen[x] = len(seen); x = (x * x + c) % m
    print(k, "digits come round every", len(seen) - seen[x], "steps")
# 34: 8,  35: 8,  then 36: 40,  37: 200, and ×5 for every digit after that
```

Why they lie, the four "magnets" every liar hugs, liars of other powers, and how the records were found:
[liars/README.md](liars/README.md).

<p align="center"><a href="https://connabyss.github.io/past-forever/"><img src="media/try-it-now.svg" width="300" alt="Try it now: open the playground in your browser"></a></p>

<p align="center">or take the <a href="https://connabyss.github.io/past-forever/#wonders">Wonders tour</a>: 7 surprises, one tap each</p>

## Three honest answers

Every value that comes out of a forever loop is one of three things:

| answer | example | what it printed |
|---|---|---|
| a number, with proof | add 9, 90, 900, … forever | `…999999999999  (this is -1)` |
| **never settles**, with proof | `x = 6`, square forever | `never settles` (the last two digits go 36, 96, 16, 56 forever) |
| **can't see the end** | 196, reverse and add forever | `can't see the end` |

Searches work the same way. "Does some square end in 7?" answers `no  (proved)` after looking at infinitely many
squares. Counts can go past forever too: count to forever, add one, and you get `forever + 1`.

**Words you'll see.**
- **settles**: the digits on the right freeze, one more after another, so the loop has a finished endless answer.
- **ring of N**: the last digits keep coming round the same N values forever, so it never settles.
- **goes wild**: each extra digit you look at takes 5 times as long to come round, so it never settles.
- **liar**: looks like a ring for many digits, then goes wild.

**A word on `proved`.** It means proved by the engine's own hand-written rules, listed in
[HOW_IT_KNOWS.md](HOW_IT_KNOWS.md). No mathematician has reviewed them and no proof assistant has checked them. A
separate checker that shares no code with the engine proves many answers a second time on every build, and a robot
referee tries thousands of random loops: strong checks, not proofs. HOW_IT_KNOWS.md marks which answers get which.

## Break it

Find one of these and your name goes in the Hall of Fame below:

- **A wrong answer.** A loop where Past Forever says `proved` and is wrong. This is the big one.
- **A loop it can't see the end of, but you can.** It says `can't see the end`, and you can show the real answer.
- **The 10,000-digit liar.** [liars/records.txt](liars/records.txt) stops at 1000 digits of calm, and
  [liars/search.py](liars/search.py) takes about a minute and a half to get there. Find the smallest c that stays calm
  for 10,000 digits, show how you got it, and make it checkable. A faster way to build the same list counts too.
- **Why 60, 61, 21?** Deep down, squares keep exactly 60 calm remainders at every depth, 4th powers 61,
  8th powers 21, 14th powers 20 ([liars/powers.py](liars/powers.py) `table`, checked to 25 digits). The loners
  explain the odd 1s (61 = 60 + 1, 21 = 20 + 1). Explain the 60s and 20s, or show a count that changes further down.
- **Why only four magnets?** Every c that stays calm for k digits shares its last k − 2 base-5 digits with one of
  the four magnets in [liars/README.md](liars/README.md#why-they-lie) (checked to 1000 digits by [tests/magnets.py](tests/magnets.py)). Write a real
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
   rules in [HOW_IT_KNOWS.md](HOW_IT_KNOWS.md) and two new families of loops for the robot referee. It also turned the last 360 digits of Graham's
   number into a song, which became `sing`, found counts that climb, like `f = f × f`, that it couldn't finish, and `x = x ^ x`, which provably never settles
   (from 7 it's a liar: its last 2 to 4 digits flip between two values, then the 5th goes wild).
   (November 2026)

## More

- [Try this on a calculator first](CALCULATOR.md): seven steps, two minutes, no maths needed.
- [A tour of the language](GUIDE.md): four lines that square forever, the last digits of Graham's number (and a
  song made of them), and `hunt`, which tries a whole range of loops at once.
- [Liars](liars/README.md): why they lie, the records, and which powers can lie.
- [How it knows](HOW_IT_KNOWS.md): every rule behind a `proved`, and honest notes on what is and isn't checked.

## Run it

You need Node.js 18 or newer. There are no dependencies.

```
git clone https://github.com/connabyss/past-forever && cd past-forever
node cli.js examples/own_square.txt --why
node tests/run.js        # ok: 665 checks
node tests/referee.js    # the robot referee, about 5 minutes
node tests/certify_gen.js 300 2027 | python3 tests/certify.py   # the second opinion, about a minute
```

The playground is one file, [docs/index.html](docs/index.html), and the piano roll is [docs/sing.html](docs/sing.html). Rebuild both
with `python3 page/build.py`. `node tests/sing.js` checks the piano roll in a browser (it needs Playwright).

## Where it came from

connabyss asked Claude (an AI) for a strange new language that would grow out of playing with numbers.
One idea from that play was a loop that finishes forever, and connabyss picked it. The language was built in a day
with Claude Code, and the liar loops turned up while hunting with it.

MIT licence. The piano roll's paper is Paper 001 from [ambientCG](https://ambientcg.com/view?id=Paper001), CC0.

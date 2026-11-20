# Break it

Find one of these and your name goes in the [Hall of Fame](HALL_OF_FAME.md#breakers).

Back to the [README](README.md).

## The two-minute dare (start here)

No maths needed, just the [playground](https://connabyss.github.io/past-forever/) and a calculator. Past Forever
gives these five answers. Each one ends in digits your calculator can check. Pick one, run it, and check it yourself:

| Run this in the playground | It says it ends in | Check it on your calculator |
|---|---|---|
| `show 9 digits of 1 / 7` | `…142857143` | 142857143 × 7 = 1000000001: ends in 000000001, so it is 1 |
| `show 8 digits of 1 / 3` | `…66666667` | 66666667 × 3 = 200000001: ends in 00000001, so it is 1 |
| `show 8 digits of 1 / 13` | `…76923077` | 76923077 × 13 = 1000000001: ends in 00000001, so it is 1 |
| `x = 5`, then `forever: x = x × x`, then `f = 1 − x` and `show 4 digits of f` | `…9376` | 9376 × 9376 = 87909376: it ends in 9376 again |
| `x = 0   step = 9`, then `forever: x = x + step   step = step × 10`, then `show 8 digits of x` | `…99999999` (−1) | 99999999 + 1 = 100000000: ends in 00000000, so it is 0 |

If one of them fails on your calculator, that is a wrong answer and you are a Breaker: open a
[Break it issue](https://github.com/connabyss/past-forever/issues/new?template=break-it.yml) and pick "The two-minute
dare". All five held when we checked, so the next step is yours: change a number (1 / 17, 1 / 19, `+ 1` instead of
`× x`…), predict what it will say, and check that too. The bigger dares are below.

## The big dares


- **A wrong answer.** A loop where Past Forever says `proved` and is wrong. This is the big one.
- **A loop it can't see the end of, but you can.** It says `can't see the end`, and you can show the real answer.
- **The 10,000-digit liar.** [liars/records.txt](liars/records.txt) stops at 1000 digits of calm, and
  [liars/search.py](liars/search.py) takes about a minute and a half to get there. Find the smallest c that stays calm
  for 10,000 digits, show how you got it, and make it checkable. A faster way to build the same list counts too.
- **Why 60, 61, 21?** Deep down, squares keep exactly 60 calm remainders at every depth, 4th powers 61,
  8th powers 21, 14th powers 20 ([liars/powers.py](liars/powers.py) `table`, checked to 25 digits). The loners
  explain the odd 1s (61 = 60 + 1, 21 = 20 + 1), and for squares 60 = 5 + 5 + 25 + 25, where the two 5s follow
  from a short argument ([liars/README.md](liars/README.md#where-the-60-comes-from)). Prove the two 25s, explain
  the 20s, or show a count that changes further down.
- **Break a proved ring.** When a loop's answer says `And that is proved` and names a ring of N, find a depth where
  its last digits don't come round every N steps ([the rule](HOW_IT_KNOWS.md)).
- **Why only four magnets?** Every c that stays calm for k digits shares its last k − 2 base-5 digits with one of
  the four magnets in [liars/README.md](liars/README.md#why-they-lie) (checked to 1000 digits by [tests/magnets.py](tests/magnets.py)). Write a real
  proof for every k, or show a c that stays calm for k digits while sharing fewer than k − 2 with all four.

To enter, open a [Break it issue](https://github.com/connabyss/past-forever/issues/new?template=break-it.yml)
with the code and what it printed.

## Hall of Fame

The Hall of Fame has its own page now, in two parts: [Finds](HALL_OF_FAME.md#finds), new checkable results found
with Past Forever, and [Breakers](HALL_OF_FAME.md#breakers), everyone who caught it out, each linked to the fix.

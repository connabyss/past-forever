# Break it

Find one of these and your name goes in the Hall of Fame below.

Back to the [README](README.md).


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

## Hall of Fame

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


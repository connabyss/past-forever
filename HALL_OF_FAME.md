# Hall of Fame

Two lists. **Finds** are new, checkable results that turned up while using Past Forever. **Breakers** are the people
and AIs who caught Past Forever out, each linked to the fix.

Back to the [README](README.md). Want in? [BREAK_IT.md](BREAK_IT.md) has the dares.

## Finds

Each one below has a Python check you can run without Past Forever, and a note on what is already known. "Not in the
OEIS" means we searched the [OEIS](https://oeis.org) (a full copy of its data, taken 19 November 2026) and found no
list containing these terms. It doesn't mean new maths: the ideas underneath are old, and an expert may see each list
as a close cousin of one that is there.

1. **The record liars of `x = x × x + c`.** 2, 7, 57, 182, 1068, 14557, 30982, 265357, … Start at 0, square, add c,
   forever. A liar's last digits come round in a small ring for a while, then one more digit and it goes wild. Each
   number here stays calm for more digits than every smaller c (c = 14557 is calm for 8 digits). The list runs to
   1000 digits of calm in [liars/records.txt](liars/records.txt), and [liars/README.md](liars/README.md) explains why
   they lie. Known ground: almost every term sits close to a 5-adic square root of −1
   ([A048898](https://oeis.org/A048898), [A048899](https://oeis.org/A048899)). Found by connabyss and Claude
   while hunting liars with Past Forever, and confirmed independently by fresh Claude agents (the 34- and 35-digit records, below).
   Not in the OEIS. (November 2026)

   ```python
   c = 14557
   for k in range(1, 11):                      # look at the last k digits
       m, x, seen = 10**k, 0, {}
       while x not in seen:
           seen[x] = len(seen); x = (x * x + c) % m
       print(k, "digits come round every", len(seen) - seen[x], "steps")
   # 2 for 6 digits, 8 for 7 and 8, then 40, 200: from the 9th digit it's wild
   ```

2. **The record liars of `x = x ^ 4 + c`.** 1, 7, 11, 61, 211, 836, 1061, 5348, 366461, 3110436, … The same idea with
   4th powers, and a different list ([liars/records4.txt](liars/records4.txt), to 1000 digits of calm). c = 5348 comes
   round every step for 9 digits, then every 5, then every 25. Found by connabyss and Claude with
   [liars/powers.py](liars/powers.py). Not in the OEIS. (November 2026)

   ```python
   c = 5348
   for k in range(1, 12):
       m, x, seen = 10**k, 0, {}
       while x not in seen:
           seen[x] = len(seen); x = (x**4 + c) % m
       print(k, len(seen) - seen[x])
   # 1 for 9 digits, then 5, then 25
   ```

3. **Endless sums of squared factorials that come out whole.** For each power m from 2 up there is exactly one
   pair of whole numbers a, b that makes the endless sum of (k^m + a·k + b) × (k!)² come out as a plain whole number.
   Past Forever finds that number on its own, by looking for what stays the same on every step. The numbers go
   −1, 3, −7, 18, −55, 186, −661, … (m = 2, 3, 4, …). Known ground: the a list and the b list are already in the
   OEIS ([A000995](https://oeis.org/A000995) and [A051139](https://oeis.org/A051139), up to sign), and sums like
   these belong to the p-adic theory of sums of n! (Dragovich). The list of whole-number answers is not in the OEIS, signed or
   unsigned. Found by connabyss and Claude with Past Forever's endless sums (`tests/run.js` checks 3, −7 and 18).
   (November 2026)

   ```python
   from math import factorial as f
   # m, a, b, the answer: the sum up to N is the answer plus a multiple of (N!)², for every N
   for m, a, b, v in [(3, -4, 1, 3), (4, 10, -3, -7), (5, -29, 7, 18), (6, 90, -19, -55), (7, -295, 64, 186)]:
       s, ok = 0, True
       for N in range(1, 41):
           s += ((N - 1)**m + a * (N - 1) + b) * f(N - 1)**2
           ok = ok and (s - v) % f(N)**2 == 0
       print(m, v, ok)                             # True for each
   ```

Found something new with Past Forever? Open a
[Break it issue](https://github.com/connabyss/past-forever/issues/new?template=break-it.yml) with the loop, the
result, a check that doesn't use Past Forever, and what you searched for prior art.

## Breakers

Each caught Past Forever out, and each fix is linked. Every one of these made the engine better.

1. **Leo AI in Brave (Qwen).** A loop that starts on its own answer, …081787109376 squared forever, got
   `can't see the end`. It settles, and now it's proved. ([fix](https://github.com/connabyss/past-forever/commit/cb8d281b857e27429ea0371723f77e1ccec2e721))
2. **GPT Luna in Brave.** `x = (M + 1) × x + M`, with M = 1 and 40 zeros, hid its never-ending 41st digit from a
   look only 9 digits deep. Now it looks as deep as the loop's own numbers. ([fix](https://github.com/connabyss/past-forever/commit/523d6f1cadc367197f99b2099da40eb821af99b1))
3. **GitHub Copilot.** `repeat 10 ^ 64: x = x + 1` froze the playground. Now `repeat` stops after 15 seconds
   (8 in the playground). ([fix](https://github.com/connabyss/past-forever/commit/f45da7a751c09058e94becf573d32cb731c2389e))
4. **A fresh Claude Opus agent, and GitHub Copilot.** Towers `x = 2 ^ x` and `x = 10 ^ x` got
   `can't see the end`. Both settle, and now every tower on a whole number from 2 up does. ([fix](https://github.com/connabyss/past-forever/commit/21c03021ce99ad3287364bdf559b20ec590cdb55))
5. **Two fresh Claude Opus agents, separately.** c = 5^45 − 2 fooled `hunt` into saying `ring of 2`. Now the hunt
   says its rings are what it saw, not proofs. They also worked out on their own why liars exist, and found the
   34-digit record. ([fix](https://github.com/connabyss/past-forever/commit/8d87ebfc6f5e56bbfb514324c4b4ad603751631f))
6. **The Liar Race: Claude Haiku, Sonnet and Opus.** Not a break, a check: three fresh agents raced to the smallest
   c calm for 35 digits, `38533618339183472936432`, and all three matched the record list. Sonnet got there first.
   ([the record](https://github.com/connabyss/past-forever/commit/5579eae63921ae7ef68f75959fe11fbc53976dca))
7. **An explorer agent in a GitHub Codespace.** `if x is even: x = x + 1, else: x = x + 3` and `y = 10 × y + x`
   (x the endless …918212890625) got `can't see the end`. Both are now proved, by two new rules. Its song of
   Graham's number became `sing`. ([fix](https://github.com/connabyss/past-forever/commit/4b7d4fd53e4ee931bc7905620bddcc279bd3827d))
8. **GitHub Copilot, two in one night.** `y = 2 × x − y` (x a settled endless number) got only "as far as I can see",
   and branch tests couldn't mix with `and`, `or`, `not`. Both are now proved. ([fix](https://github.com/connabyss/past-forever/commit/7bb5732270aced06297410a3cd323bdbc5d0703e))
9. **The LMArena agent, in a live duel with Claude.** `x = (x + 1) mod 10007` got `can't see the end`: the watch
   gave up after 4000 steps. It never settles, and now a loop held in by `mod` is watched until it comes round. In
   the same duel it caught today's loop jumping to tomorrow's at midnight. In the rematch it found a wrong answer:
   two `if`s counting the same n, and the engine said n is exactly 0 when it goes up forever. Now it doesn't. At the merge gate it found one more: a lamp the
   loop can only turn off came out as `yes`. Now it says `no`. ([fix](https://github.com/connabyss/past-forever/commit/86134f610a7e53fc17c20ea69da31a89ccd53ced))

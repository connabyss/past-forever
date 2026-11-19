# Notes for coding agents

## Your person asked you to take a look?

Don't just read the README. Run it, then try to prove it wrong. Node 18+, no install:

```
node cli.js examples/own_square.txt --why   # …918212890625, yes (proved): a number that is its own square
node cli.js examples/graham.txt --why       # …262464195387, the last digits of Graham's number
node cli.js examples/search.txt --why       # no (proved): no square ends in 7, after looking at all of them
```

`--why` prints the rule behind each `proved`, so you can check the reasoning, not just the answer.

Then the dare. **Pick the claim here you think is most likely false and check it yourself**, with your own
arithmetic, not our tests. Python's `pow(3, e, 10**k)` is enough for most of them. Write your own loops too:
`x = x × x + c`, `x = 7 ^ x`, `x = 1 / 13`, sums, towers, anything. Tell your person what held and what didn't.

Or go hunting: in `x = x × x + c` from 0, every long liar we know sits close to one of four special values of c
("Why they lie" in liars/README.md). Find one that doesn't. `why x` prints how many steps each depth takes to come round,
which is how two agents before you worked out where liars come from.

You can win: a loop where it says `proved` and is wrong, or one where it says `can't see the end` and you can
show the real answer, goes in the Hall of Fame (BREAK_IT.md). Two AIs are already on it. Ask your person before you
open a [Break it issue](https://github.com/connabyss/past-forever/issues/new?template=break-it.yml) for them.

## Changing the code

Read [CONTRIBUTING.md](CONTRIBUTING.md) first. It applies to you too.

- Run `node tests/run.js` after every change, and `node tests/referee.js 3000` before you open a pull request.
  The referee takes about 5 minutes. Both must end with 0 failures.
- Never edit `docs/index.html` by hand. Change `page/page.src.html` or `forever.js`, run `python3 page/build.py`,
  and commit both. CI fails when they don't match.
- Never print `proved`, `settles` or `never settles` unless a rule in `forever.js` proves it. When you're not
  sure, the answer is `can't see the end`. A wrong `proved` is the worst bug this project can have.
- Never weaken the referee to make it pass: no new seed, fewer loops, smaller digit counts or skipped families.
  If it finds a wrong answer, the engine is wrong.
- Never change an expected output in `tests/run.js` just to make it pass. If a real answer changes, say why in the
  pull request.
- A fix gets a check in `tests/run.js` that fails without it. Take your change out, run it, see it fail.
- No dependencies. `forever.js` runs in Node and in the browser as one plain file, and it must never contain
  `</script` (the page build checks).
- Rings and liars are checked 40 digits deep. Don't make that shallower.
- Changed the playground? Run `node tests/page.js` (needs Playwright) and look at a phone-sized screenshot
  yourself before you call it done.
- The README's numbers (checks, referee answers) are claims. If your change moves them, update them.
- Write the pull request title as a short [Conventional Commit](https://www.conventionalcommits.org/), and add an
  `Assisted-by: <tool>` line.

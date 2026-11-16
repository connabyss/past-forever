# Notes for coding agents

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

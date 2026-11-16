# Contributing to Past Forever

Thanks for wanting to help. Past Forever is small on purpose, so the best changes are small and careful too.

## Ways to help

- **Break it.** This helps most. Open a [Break it issue](https://github.com/connabyss/past-forever/issues/new?template=break-it.yml)
  if you find a wrong answer (it says `proved` and is wrong), a loop it can't see the end of but you can, or a
  longer liar. Your name goes in the Hall of Fame in the README.
- **Fixes.** A crash, a confusing message, a playground bug, something broken on a phone.
- **A new rule** that turns a `can't see the end` into a real answer. Please open an issue first so we can talk
  about it before you build it.

## Set up

You need Node.js 18 or newer. There are no dependencies. Python 3 is only for rebuilding the playground.

```
git clone https://github.com/connabyss/past-forever && cd past-forever
node tests/run.js           # ok: N checks, a few seconds
node tests/referee.js 3000  # the robot referee, about 5 minutes
python3 page/build.py       # rebuild the playground: docs/index.html
```

CI runs all three on every pull request, and it fails if `docs/index.html` is out of date.

`node tests/page.js` clicks through the playground on a phone-sized screen. It needs Playwright
(`npm i -D playwright && npx playwright install chromium`) and doesn't run in CI, so run it when you change the page.

## Where things are

| | |
|---|---|
| `forever.js` | the whole language: reading a program, running it, and the rules that prove answers |
| `cli.js` | `node cli.js program.txt --why` |
| `page/page.src.html` | the playground's source. `page/build.py` puts it and `forever.js` into `docs/index.html` |
| `docs/` | what GitHub Pages serves. Never edit `docs/index.html` by hand |
| `examples/` | example programs |
| `tests/run.js` | the main checks |
| `tests/referee.js` | random loops, every answer checked against plain arithmetic |
| `tests/page.js` | the playground, clicked through in a browser |

## The rules that keep it honest

- **`proved` means a rule in `forever.js` proved it.** Never print `proved`, `settles` or `never settles` on a
  guess. When no rule fits, the answer is `can't see the end`.
- **Every answer can say how it knows.** A new rule needs a `why` line in plain words.
- **The referee is the judge.** If it finds a wrong answer, the rule is wrong. Never change its seed, lower its
  number of loops or skip a case to make it pass.
- **A fix comes with a check in `tests/run.js` that fails without it.**
- **Old outputs stay the same.** The example programs at the top of `tests/run.js` must print exactly what they
  print now. If an answer has to change, say why in the pull request.

## Pull requests

- One change per pull request. A short title in the [Conventional Commit](https://www.conventionalcommits.org/)
  style, like `fix(engine): see the ring when the loop starts on its answer`.
- Say what was wrong, what you changed and how you checked it.
- Changed the engine or the page? Run `python3 page/build.py` and commit `docs/index.html` with it.
- Changed how the playground looks? A phone screenshot helps.
- AI helped? Welcome. Add an `Assisted-by: <tool>` line to the commit or the pull request, and make sure you've
  read and run the change yourself. Coding agents: read [AGENTS.md](AGENTS.md) too.

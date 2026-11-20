<!-- Thanks for the PR! Check what applies, or write n/a on a line that doesn't. -->

## What this changes

<!-- One or two sentences. Link the issue it fixes. -->

## How it was checked

<!-- The commands you ran and what they printed. -->

## Checklist

- [ ] The title is a short Conventional Commit, for example `fix(engine): see the ring when the loop starts on its answer`.
- [ ] A fix has a check in `tests/run.js` that fails when the change is taken out.
- [ ] `node tests/run.js` and `node tests/referee.js 3000` both end with 0 failures.
- [ ] Changed the engine or the page: I ran `python3 page/build.py` and committed `docs/index.html`.
- [ ] No answer says `proved` unless a rule in `forever.js` proves it.

Nice to have: a phone screenshot if the playground looks different, and an `Assisted-by: <tool>` line if an AI helped.

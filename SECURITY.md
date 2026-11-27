# Security

Past Forever runs loops people write, in Node and in the playground at connabyss.github.io/past-forever. A wrong
`proved` is the worst bug this project can have, but that's a [Break it issue](BREAK_IT.md), not a security report.
This page is for real security holes. Please tell us about one privately first, not in a public issue.

## How to report one

- Best: the **Report a vulnerability** button on the
  [Security tab](https://github.com/connabyss/past-forever/security/advisories/new). Only the maintainer sees it.
- Or email connabyss.code@proton.me with "Past Forever security" in the subject.

Say what you ran, what happened, and which commit you're on. A small program that shows it helps most. You'll
get an answer within a week, and credit if you'd like it.

## Which versions get fixes

Only the newest code on `main` and the live playground.

## What counts

- A program or shared playground link that runs script in the page (cross-site scripting) or reads something it
  shouldn't.
- `cli.js` reading or writing files other than the program you gave it and an output file you asked for.
- A workflow in this repo leaking a secret or running untrusted pull request code with write access.

Not a security hole: a loop that is slow or uses a lot of memory, or an answer you think is wrong. Those go in a
normal or Break it issue.

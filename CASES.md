# Cases

Past Forever prints `proved`, and its README and Hall of Fame list results found with it. Each one should hold up when someone else checks it with their own arithmetic. This page tracks those claims.

## How it works

1. **Open a case** with the [Reproduce or refute](https://github.com/connabyss/past-forever/issues/new?template=reproduce-or-refute.yml)
   form: one claim, the exact steps, what should happen, what did happen, and where you ran it.
2. **Rerun someone else's case.** Follow its steps on your own machine and post what you got, same or different,
   with your environment. A different result is as useful as a match.
3. **Close it** with what came of it: a fix, a new result written up, or a refutation. Everyone who opened or reran
   the case is credited in the list below.

Nothing here counts on the word of the person who opened it, including connabyss. A new entry under Finds in [HALL_OF_FAME.md](HALL_OF_FAME.md) goes in once a case for it is Reproduced.

## The counts

**Open 1 · Reproduced 0 · Resolved 0 · Confirmed 0**

- **Open**: the case is still being worked on.
- **Reproduced**: someone other than the person who opened it followed the steps and got the reported behavior or result.
- **Resolved**: the case is closed, with a fix, a written-up result, or a clear refutation.
- **Confirmed**: the original claim held up after that independent check.

The counts are not mutually exclusive. One case can be Reproduced and Confirmed, and still Open until it is written up.
A rerun that gets a different result refutes the claim: that case is never counted as Reproduced or Confirmed, and it
closes as Resolved once the reason is written down.

## The list

| Case | Claim | Opened by | Reproduced by | Status |
|---|---|---|---|---|
| [#37](https://github.com/connabyss/past-forever/issues/37) | Every record liar in [liars/records.txt](liars/records.txt) stays calm for exactly the number of digits listed. `python3 liars/check.py 40` checks the first 34 in seconds; `python3 liars/check.py` checks all of them in about 8 minutes. | connabyss | waiting for a rerun | Open |

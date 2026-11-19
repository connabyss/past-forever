# How it knows

Back to the [README](README.md).

**A word on `proved`.** It means proved by the engine's own hand-written rules, listed below. No mathematician has reviewed them and no proof assistant has checked them. Some kinds
of answer also get a **second opinion**: a separate checker, [tests/certify.py](tests/certify.py), shares no code with
the engine, writes its own proof, and fails the build if it can't prove an answer or disagrees. It covers one-name
polynomial loops like `x = (3 × x × x + 7) / 11`, power towers like `x = 3 ^ x` (any whole number from 2 up), and
`x = x ^ x`. Every other `proved` (pairs of names, loops with `if`, endless sums, counts past forever, polynomials
with an endless number in them) rests on the engine's rules alone, plus the robot referee, which tries thousands of
random loops on every build: a strong check, not a proof. The list below marks which is which.

There is no magic, only a few rules in [forever.js](forever.js), and each answer says which one it used. **(2nd)**
marks the rules whose answers the separate checker, [tests/certify.py](tests/certify.py), proves again on every build;
the rest are checked by the robot referee only.

- The whole state comes back: from then on it repeats forever. **(2nd)** for one-name polynomial loops.
- A digit stops changing, and the rule pulls nearby numbers together: one more digit locks in every step. **(2nd)** for one-name
  polynomial loops.
- A sum whose pieces end in more and more zeros settles.
- A power tower like `x = 3 ^ x`: when two tops share their last k digits, the powers share k + 1 (the bottom
  number must have no 2 or 5 in it). So once the last 2 digits stop changing, it settles. **(2nd)**
- A tower on 2, 5, 10 or any other whole number from 2 up, like `x = 2 ^ x` from an ordinary whole number: every
  step is a whole number and they grow, so soon every top is bigger than any number of digits you ask for. Then the
  same lock-one-more rule holds, and it settles. **(2nd)**
- A loop whose `if`s only test its last digits (`is even`, `is odd`, `ends in …`): the last few digits of every name
  then only depend on their last few digits, so they must come round. If a name's digits keep going round, it never
  settles. If the digits the tests read freeze, every test gives the same answer forever, and the loop is a plain one.
- `y = 10 × y + x` (or 20, 100, any multiple of 10) with x settling: each step locks one more digit, and the answer
  is exactly x ÷ (1 − 10), so −x ÷ 9.
- A count that only climbs ends at the top of its climb: `count f = 2` then `forever: f = f × f` ends at `forever`,
  and adding a count made by an earlier loop works like adding a number. (`d = d × forever` climbs to forever ^
  forever, which the language can't write yet, so it says `can't see the end` and tells you why.)
- `x = x ^ x` from a whole number of 2 or more: the numbers grow, and once x is big, the last k digits of x ^ x only
  depend on the last k digits of x. So if those go round a ring, it never settles. If x ends in 0, x ^ x ends in at
  least x zeros, so it settles on exactly 0. **(2nd)**
- Any polynomial rule whose other names are fixed endless numbers, like `y = 70 × y − 8 × y × y − 3 × x − 7`: if the
  last digit freezes where the rule's slope ends in 0, one more digit locks every step. Towers work the same way with
  extra parts times a number ending in 0, like `x = 3 ^ x − 10 × x`.
- The last digits go round a ring that never stops: proved never to settle. **(2nd)** for one-name polynomial loops
  and `x = x ^ x`.
- The ring's length, for a one-name polynomial loop like `x = x × x + 1`: if the rule's slopes at the ring's last
  digits multiply to a number ending in 0, the answer says `And that is proved` and names the ring. Doing the rule
  once round the ring is then a step whose slope ends in 0, so, as in the rule above, it locks one more digit every
  round: there is exactly one ring of that length, at every depth, and x falls into it. Otherwise the answer says
  `As far as I can see`, because a liar can keep a ring for 46 digits and then go wild. The separate checker doesn't check
  this rule yet; [tests/run.js](tests/run.js) checks every ring it proves for `x^p + c` (p 2 to 5, c from −20 to 60)
  against plain arithmetic on the last 60 digits.
- None of these fit: `can't see the end`.

## Honest notes

- **The maths is old.** Numbers that run off to the left are the 10-adic numbers (see [the tour](GUIDE.md#how-this-ties-to-past-forever)). Counting past forever
  is Cantor's ordinals. The …212890625 number is an automorphic number. The frozen last digits of towers of 3s have been known for a long time too. What is new here, as far as we found,
  is a language you can actually run where code keeps going after a forever loop. Closest cousins: the
  Zeno esolang (an imaginary machine) and infinite time Turing machines
  (theory, not a language). Not finding one is not proof there isn't one.
- **The referee and the tests are strong checks, not proofs.** Everything below that says "checked" or "tested"
  means tried, not proved.
- **"proved" means proved by the rules above**, as written in forever.js. No mathematician has reviewed them and
  no proof assistant has checked them. For one-name polynomial loops, power towers and `x = x ^ x`, an independent
  checker writes its own proof of each answer (below), and the build fails if it can't prove one.
- **A robot referee checks them on every build.** [tests/referee.js](tests/referee.js) makes 4,311 random loops
  (squares, liars, straight-line rules, pairs, numbers passed back and forth, endless sums, power towers, towers on
  2, 5 and 10, loops that branch on their last digits, and y = 10 × y + an endless number, polynomials with an endless number in them, towers plus 10 × x) and checks
  every `settles`, `never settles` and exact fraction against plain arithmetic on the last 30 or more digits. Last
  run: 5,596 answers, 0 wrong, 0 `can't see the end`. That is a strong check, not a proof.
- **You don't have to trust us: a second opinion.** [tests/certify.py](tests/certify.py) is a separate checker in
  Python, about 150 lines, that shares no code with the engine. For loops like `x = (3 × x × x + 7) / 11` it writes
  down its own proof of each answer, using textbook facts only: last digits going round a ring means never settles;
  a last digit that the rule fixes and pulls in means settles, and the rational root theorem names the exact answer.
  It prints how many of Past Forever's answers it proved again, how many it couldn't decide, and how many loops
  Past Forever gave no answer for. The build fails on any disagreement and on any answer it couldn't prove. On
  5,000 random loops it proved all 5,000 answers again, 0 undecided, 0 disagreements, all 60 digits matching. Every
  build re-runs 300 of them, every tower `x = b ^ x` for b from 2 to 40 (starts 0 to 3) and every `x = x ^ x` from 2
  to 40, plus the ten loops in [tests/certificates.jsonl](tests/certificates.jsonl), whose
  proofs are written out by hand in [tests/certificates.md](tests/certificates.md). (Written by an explorer agent in a GitHub Codespace.)
  For each tower it writes a certificate for that one loop: the step from which x is big enough, the length of the
  chain 10^60, λ(10^60), …, 1, and so the step by which all 60 digits must be frozen. Then it runs that loop on every
  level of the chain, checks each level freezes on time, and compares the 60 digits. Its coverage is narrow on
  purpose (those loop families only): a different loop shape gets no second opinion.
- **Copilot's three probes.** GitHub Copilot picked the three rules it trusted least: towers on bases with 2 or 5 in
  them, towers mixed with x (like `x = 3 ^ x − 20 × x` from −1), and polynomials that use an endless number
  settled by an earlier loop. [tests/probes.py](tests/probes.py) widens each into a family, 205 loops, and checks
  every answer against a plain modular simulation, up to 110 digits deep, on every build. 0 wrong; 18 of the third
  kind say `can't see the end` (honest, but a gap). That is a finite check, not a proof: it looks at a fixed set of
  depths and loop families, and a loop shape it doesn't try could still hide a bug.
- Rings and liars are checked 40 digits deep. A liar that lies for more than 40 digits would look like a ring, unless
  its answer says `And that is proved` (no liar can: its ring never passes a slope ending in 0).
- `can't see the end` comes up a lot. That's the language being honest, not a bug.

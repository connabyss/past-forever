# Why each record is the smallest

[records.txt](records.txt) says each c is the **smallest** positive c that stays calm that long. Checking that a c
stays calm is easy ([check.py](check.py) does it digit by digit). Checking that nothing smaller does is the hard
part, because you can't try every number below a 698-digit one. Here is the whole argument, in four steps you can
check by reading, then what the computer does with it, and how it is checked twice.

The loop is `x = x × x + c` from `x = 0`. "Calm for k digits" means: for every j from 1 to k, the steps the last j
digits take to come round have no factor 5. A record only counts c ending in 2, 3, 7 or 8 (the others can never
go wild, so they are not liars).

1. **Only the 5s matter.** The last j digits come round when both their 2s part (the remainder after dividing by
   2^j) and their 5s part (the remainder after dividing by 5^j) come round. On the 2s side the rule's slope, 2x, is
   always even, so that part settles into a ring of 1 or 2 steps: no factor 5 ever comes from there. So c is calm for
   k digits exactly when, for every j up to k, the 5s part's steps have no factor 5.
2. **Only c's remainder matters.** The 5s part of x after each step only depends on the 5s part of x and of c
   before it (adding and multiplying respect remainders). So whether c is calm for k digits only depends on c's
   remainder after dividing by 5^k.
3. **Calm for k means calm for k − 1.** That is just the definition. So every calm remainder at depth k comes from
   a calm remainder at depth k − 1 with one more base-5 digit in front (5 choices). Building them one depth at a time,
   trying all 5 choices each time, finds every calm remainder and skips none.
4. **The smallest remainder is the record.** Every whole number from 0 up to 5^k − 1 is its own remainder. So the
   smallest positive c that is calm for k digits is the smallest calm remainder at depth k.

What the computer does: start with the remainders 2 and 3 at depth 1, and keep the calm ones as above. At every depth
from 5 to 1000 there are exactly 60 of them, so the work stays small. The smallest is the record.

How it is checked, by two programs that share no code:

- [search.py](search.py) (Python) builds the list.
- [tests/liars.js](../tests/liars.js) (JavaScript, written separately, a different cycle finder) builds it again down
  to 1000 digits and compares every line. It also tries every c from 1 to 10,000,000 the slow way, in base 10 with no
  base-5 step at all, and gets the first ten records. Every build on GitHub runs it.
- The same program checks the last record, the 698-digit one, the plain way in base 10 at every depth from 1 to
  1001 digits, one at a time, and sees it go wild at 1002.
- [check.py](check.py) re-checks every record's calm length digit by digit in base 10 (about 8 minutes).

What this does not give you: a proof checked by a proof assistant, or a mathematician's review. Steps 1 to 4 are
ordinary reasoning that nobody outside this project has reviewed yet.

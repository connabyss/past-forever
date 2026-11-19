"""AUTOGRAM: a sentence, sent back from the future, that counts every one of its own letters.

Each text is a template with holes; each hole is a number the future sends. The text is built, its letters are
counted, and the timeline survives only if every hole matches the real count. Search: start anywhere, build,
count, and nudge the numbers toward what was counted (with some randomness, so it doesn't loop forever).
That's the method Lee Sallows and Rudy Kousbroek used by hand and with a home-built machine in the 1980s.
Usage: python3 autogram.py [total]
Every result is re-counted from the printed text at the end, so you can trust what's on screen.
"""
import random, re, sys, time
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = {2: 'twenty', 3: 'thirty', 4: 'forty', 5: 'fifty', 6: 'sixty', 7: 'seventy', 8: 'eighty', 9: 'ninety'}
def word(n): return ONES[n] if n < 20 else TENS[n // 10] + ('-' + ONES[n % 10] if n % 10 else '') if n < 100 else word(n // 100) + ' hundred' + (' and ' + word(n % 100) if n % 100 else '')
AZ = 'abcdefghijklmnopqrstuvwxyz'
def counts(s):
    s = s.lower(); return [s.count(c) for c in AZ]

def inventory(prefix, v, letters=AZ):
    parts = [f"{word(v[AZ.index(c)])} {c}" + ("'s" if v[AZ.index(c)] != 1 else '') for c in letters]
    return prefix + ' ' + ', '.join(parts[:-1]) + ' and ' + parts[-1] + '.'

def solve(texts, describes, letters_of, seed=1, limit=3_000_000, show_every=200000):
    """texts[i](v) renders text i from number list v; text i describes the letter counts of text describes[i]."""
    rnd = random.Random(seed); n = len(texts)
    vs = [[rnd.randint(1, 12) for _ in AZ] for _ in range(n)]
    t0 = time.time()
    for it in range(limit):
        rendered = [texts[i](vs[i]) for i in range(n)]
        actual = [counts(r) for r in rendered]
        bad = 0
        for i in range(n):
            tgt = actual[describes[i]]
            for c in letters_of[i]:
                k = AZ.index(c)
                if vs[i][k] != tgt[k]:
                    bad += 1
                    if rnd.random() < 0.5: vs[i][k] = tgt[k] if rnd.random() < 0.7 else max(1, (vs[i][k] + tgt[k]) // 2 + rnd.randint(-1, 1))
        if bad == 0: return rendered, it, time.time() - t0
        if it % show_every == 0: print(f'   ...timeline {it:>8,}: {bad} counts still wrong', flush=True)
    return None, limit, time.time() - t0

def verify(texts, describes, letters_of):
    ok = True
    for i, t in enumerate(texts):
        tgt = counts(texts[describes[i]])
        for c in letters_of[i]:
            k = AZ.index(c); claim = word(tgt[k]) + ' ' + c + ("'s" if tgt[k] != 1 else '')
            if not re.search(r'(?<![\w-])' + re.escape(claim) + r'(?![\w])', t): ok = False; print(f'   MISMATCH in text {i + 1}: expected "{claim}"')
    return ok

demo = sys.argv[1] if len(sys.argv) > 1 else 'autogram'
if demo == 'total':
    for n in range(1, 200):
        s = f'this sentence has {word(n)} letters'
        if sum(ch.isalpha() for ch in s) == n: print(f'   timeline: "{s}"   (count them: {n})')
    sys.exit()
T = [lambda v: inventory('This sentence was sent back from the future and contains', v)]; D = [0]; Ls = [AZ]
print(f'AUTOGRAM: {len(T)} text(s), each one\'s 26 numbers sent from the future. Searching timelines...\n', flush=True)
for seed in range(1, 40):
    res, it, dt = solve(T, D, Ls, seed=seed)
    if res: break
    print(f'   seed {seed} gave up after {it:,} timelines, trying another', flush=True)
print(f'\nConsistent timeline found after {it:,} tries ({dt:.1f} s):\n')
for r in res: print('   ' + r + '\n')
print('Re-counting every letter of the printed text(s):', 'ALL CORRECT' if verify(res, D, Ls) else 'something is wrong')

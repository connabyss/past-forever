"""Keeps tests/certificates.md in step with tests/certificates.jsonl and with what the code really says.

    node tests/certify_gen.js tests/certificates.jsonl | python3 tests/certificates_sync.py

For each of the ten loops it checks that the page shows the same program as the .jsonl file, the same answer that
Past Forever prints today, and the same certificate line that certify.py writes today, word for word; and that a
"ring of N" in the hand check names the ring certify.py found. Exits 1 on any difference.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from certify import certify  # noqa: E402

md = (Path(__file__).parent / 'certificates.md').read_text(encoding='utf-8')
sections = {int(m.group(1)): m.group(2) for m in re.finditer(r'^## (\d+)\. .*?\n(.*?)(?=^## |\Z)', md, re.S | re.M)}
loops = [json.loads(line) for line in sys.stdin if line.strip()]
fails = []
if sorted(sections) != sorted(L['n'] for L in loops):
    fails.append(f'the page has loops {sorted(sections)}, the .jsonl file has {sorted(L["n"] for L in loops)}')
for L in loops:
    text = sections.get(L['n'], '')
    code = re.search(r'```\n(.*?)```', text, re.S)
    if not code or code.group(1).strip() != L['src'].strip():
        fails.append(f'#{L["n"]}: the program on the page is not the one in the .jsonl file')
    printed = re.search(r'^Past Forever printed: `(.*)`$', text, re.M)
    if not printed or printed.group(1) != L['out']:
        fails.append(f'#{L["n"]}: page says Past Forever printed {printed and printed.group(1)!r}, today it prints {L["out"]!r}')
    verdict, _, proof = certify(L)
    line = f'**Certificate: {verdict}.** ' + proof.replace('the last 1 digits repeat', 'the last digit repeats') + '.'
    shown = re.search(r'^\*\*Certificate: .*$', text, re.M)
    if not shown or shown.group(0).strip() != line:
        fails.append(f'#{L["n"]}: page certificate {shown and shown.group(0)!r} differs from certify.py: {line!r}')
    ring = re.search(r'a ring of (\d+)', text)
    every = re.search(r'repeats? every (\d+) steps', proof)
    if ring and (not every or ring.group(1) != every.group(1)):
        fails.append(f'#{L["n"]}: the hand check says a ring of {ring.group(1)}, certify.py found {every and every.group(1)}')
if fails:
    print('FAILED:', len(fails))
    for f in fails:
        print('  ', f)
    sys.exit(1)
print(f'ok: tests/certificates.md matches tests/certificates.jsonl, Past Forever and certify.py on all {len(loops)} loops')

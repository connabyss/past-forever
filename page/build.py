# Builds the playground: page/page.src.html + forever.js -> docs/index.html (served by GitHub Pages)
import os
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'page.src.html'), encoding='utf8').read()
eng = open(os.path.join(here, '..', 'forever.js'), encoding='utf8').read()
assert '</script' not in eng
head = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body style="margin:0">\n'
open(os.path.join(here, '..', 'docs', 'index.html'), 'w', encoding='utf8').write(head + src.replace('/*ENGINE*/', eng) + '\n</body></html>\n')
print('built docs/index.html')

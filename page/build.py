# Builds the playground: page/page.src.html + forever.js -> docs/index.html (served by GitHub Pages)
import os
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'page.src.html'), encoding='utf8').read()
eng = open(os.path.join(here, '..', 'forever.js'), encoding='utf8').read()
assert '</script' not in eng
site = 'https://connabyss.github.io/past-forever/'
title = 'Past Forever'
desc = 'Infinite loops that finish with an answer. 1 ÷ 7 = …142857143, a whole number. Try it in your browser.'
meta = ''.join([
  '<title>%s</title>' % title,
  '<meta name="description" content="%s">' % desc,
  '<link rel="canonical" href="%s">' % site,
  '<meta property="og:type" content="website">',
  '<meta property="og:site_name" content="%s">' % title,
  '<meta property="og:title" content="%s">' % title,
  '<meta property="og:description" content="%s">' % desc,
  '<meta property="og:url" content="%s">' % site,
  '<meta property="og:image" content="%sog.png">' % site,
  '<meta property="og:image:width" content="1280"><meta property="og:image:height" content="640">',
  '<meta property="og:image:alt" content="1 ÷ 7 = …142857143 in gold digits, with the words: Past Forever, infinite loops that finish with an answer">',
  '<meta name="twitter:card" content="summary_large_image">',
])
head = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' + meta + '</head><body style="margin:0">\n'
open(os.path.join(here, '..', 'docs', 'index.html'), 'w', encoding='utf8').write(head + src.replace('/*ENGINE*/', eng) + '\n</body></html>\n')
print('built docs/index.html')

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
def page(src_name, out_name, title, desc, url, image_alt):
  src = open(os.path.join(here, src_name), encoding='utf8').read()
  meta = ''.join([
    '<title>%s</title>' % title,
    '<meta name="description" content="%s">' % desc,
    '<link rel="canonical" href="%s">' % url,
    '<meta property="og:type" content="website">',
    '<meta property="og:site_name" content="Past Forever">',
    '<meta property="og:title" content="%s">' % title,
    '<meta property="og:description" content="%s">' % desc,
    '<meta property="og:url" content="%s">' % url,
    '<meta property="og:image" content="%s%s">' % (site, image_alt[0]),
    '<meta property="og:image:alt" content="%s">' % image_alt[1],
    '<meta name="twitter:card" content="summary_large_image">',
  ])
  head = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' + meta + '</head><body style="margin:0">\n'
  open(os.path.join(here, '..', 'docs', out_name), 'w', encoding='utf8').write(head + src.replace('/*ENGINE*/', eng) + '\n</body></html>\n')
  print('built docs/' + out_name)
head = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' + meta + '</head><body style="margin:0">\n'
open(os.path.join(here, '..', 'docs', 'index.html'), 'w', encoding='utf8').write(head + src.replace('/*ENGINE*/', eng) + '\n</body></html>\n')
print('built docs/index.html')
# the singing roll: Graham's number's last 360 digits, worked out in the page and played on a paper piano roll
page('sing.src.html', 'sing.html', "Graham's number, as music", "The last 360 digits of Graham's number, worked out by a loop in your browser and played on a paper piano roll.",
     site + 'sing.html', ('sing.png', "A paper piano roll with punched holes running over a brass bar, under the title: The last 360 digits of Graham's number, as music"))

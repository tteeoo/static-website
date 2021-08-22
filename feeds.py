#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime
from feedgen.feed import FeedGenerator

fg = FeedGenerator()
fg.id('https://theohenson.com/blog.html')
fg.title('Theo Henson\'s blog')
fg.subtitle('I write about whatever I’m interested in')
fg.author(name='Theo Henson', email='theodorehenson@protonmail.com')
fg.link(href='https://theohenson.com/rss.xml', rel='self')
fg.language('en')

for post in [i for i in os.listdir('./src/') if 'blog-' in i]:
    html = post[:len(post)-2] + 'html'
    fe = fg.add_entry()
    fe.guid('https://theohenson.com/'+html, permalink=True)
    fe.link(href='https://theohenson.com/'+html)
    fe.author(name='Theo Henson', email='theodorehenson@protonmail.com')
    with open('./src/'+post, 'r') as f:
        fe.title(f.readline().strip()[2:])
        fe.description(f.read(), isSummary=False)
    fe.updated(subprocess.check_output(['git', 'log', '-1', '--pretty=%cI', './src/'+post]).decode('utf-8').strip())
    fe.published(subprocess.check_output(['git', 'log', '-1', '--pretty=%cI', './src/'+post]).decode('utf-8').strip())

with open('./dst/rss.xml', 'wb') as f:
    f.write(fg.rss_str(pretty=True))
with open('./dst/atom.xml', 'wb') as f:
    f.write(fg.atom_str(pretty=True))

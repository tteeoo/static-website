#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup
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
    soup = None
    with open('./dst/'+html, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    fe.title(soup.find_all('h1')[0].string)
    fe.content(
        ''.join([str(i) for i in soup.find(id='content').contents]),
        type='CDATA'
    )
    fe.updated(subprocess.check_output(['git', 'log', '-1', '--pretty=%cI', './src/'+post]).decode('utf-8').strip())
    fe.published(subprocess.check_output(['git', 'log', '-1', '--pretty=%cI', './src/'+post]).decode('utf-8').strip())

with open('./dst/rss.xml', 'wb') as f:
    f.write(fg.rss_str(pretty=True))
with open('./dst/atom.xml', 'wb') as f:
    f.write(fg.atom_str(pretty=True))

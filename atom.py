#!/usr/bin/env python3

import os
import pytz
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator

fg = FeedGenerator()
fg.id('https://theohenson.com/blog.html')
fg.title('Theo Henson\'s blog')
fg.subtitle('I write about whatever I’m interested in')
fg.author({'name': 'Theo Henson', 'email': 'theodorehenson@protonmail.com'})
fg.link(href='https://theohenson.com/feed.atom', rel='self')
fg.language('en')

for post in [i for i in os.listdir('./src/') if 'blog-' in i]:
    html = post[:len(post)-2] + 'html'
    fe = fg.add_entry()
    fe.id('https://theohenson.com/' + html)
    fe.link(href='https://theohenson.com/' + html)
    with open('./src/' + post, 'r') as f:
        fe.title(f.readline().strip()[2:])

fg.atom_file('./dst/feed.atom')

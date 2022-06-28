#!/usr/bin/env python3

import os
import subprocess
from copy import copy
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

fg = FeedGenerator()
fg.id("https://theohenson.com/")
fg.title("Theo Henson's blog and poems")
fg.subtitle("Miscellaneous writings.")
fg.author(name="Theo Henson", email="theodorehenson@protonmail.com")
fg.language("en")

for post in [i for i in os.listdir("./src/") if "blog-" in i]:
    html = post[:len(post)-2] + "html"
    fe = fg.add_entry()
    fe.guid("https://theohenson.com/"+html, permalink=True)
    fe.link(href="https://theohenson.com/"+html)
    fe.author(name="Theo Henson", email="theodorehenson@protonmail.com")
    soup = None
    with open("./dst/"+html, "r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    fe.title(soup.find_all("h1")[0].string)
    fe.content(
        "".join([str(i) for i in soup.find(id="content").contents]),
        type="CDATA"
    )
    fe.updated(subprocess.check_output(["git", "log", "-1", "--pretty=%cI", "./src/"+post]).decode("utf-8").strip())
    fe.published(subprocess.check_output(["git", "log", "-1", "--pretty=%cI", "./src/"+post]).decode("utf-8").strip())

fga = copy(fg)
with open("./dst/atom.xml", "wb") as f:
    fga.link(href="https://theohenson.com/atom.xml", rel="self")
    f.write(fga.atom_str(pretty=True))

fg.link(href="https://theohenson.com/rss.xml", rel="self")
with open("./dst/rss.xml", "wb") as f:
    f.write(fg.rss_str(pretty=True))

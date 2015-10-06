#!/usr/bin/env python

import copy, os, re, sqlite3, string, urllib
from bs4 import BeautifulSoup, NavigableString, Tag

DOCUMENTS_DIR = os.path.join('PHP-FIG.docset', 'Contents', 'Resources', 'Documents')
PHP_FIG_DIR = os.path.join('www.php-fig.org')

db = sqlite3.connect('PHP-FIG.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

page = open(os.path.join(DOCUMENTS_DIR, PHP_FIG_DIR, "index.html")).read()
soup = BeautifulSoup(page, "html5lib")
sidebar = soup.find("aside")

# remember pages to add sections later
pages = [os.path.join(DOCUMENTS_DIR, PHP_FIG_DIR, "index.html")]

type = "Guide"

# search for all possible guides
for link in sidebar.find_all("a"):
    path = os.path.join(PHP_FIG_DIR, link.attrs["href"])

    # add only PSR links
    if not re.search("psr", path):
        continue

    name = link.contents[2].strip() + " - " + link.contents[1].text.strip()

    cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)", (name, type, path))

    print "name: %s, type: %s, path: %s" % (name, type, path)

    if re.search("index.html", path):
        subpath = os.path.join(DOCUMENTS_DIR, path)
    else:
        subpath = os.path.join(DOCUMENTS_DIR, path, "index.html")

    pages.append(subpath)

# adding sections for all pages
for page in pages:
    content = open(page).read()
    soup = BeautifulSoup(content, "html5lib")
    section = soup.find("section")

    # strip unecessary tags
    [t.extract() for t in soup("script")]

    for headline in section.find_all(["h1", "h2", "h3", "h4", "h5"]):
        dashAnchor = headline.find("a", class_="dashAnchor")

        if dashAnchor:
            continue

        headline_name = headline.text.strip()

        print "adding toc tag for section: %s" % headline_name
        headline_name = "//apple_ref/cpp/Section/" + urllib.quote(headline_name, "")
        dashAnchor = BeautifulSoup('<a name="%s" class="dashAnchor"></a>' % headline_name).a
        headline.insert(0, dashAnchor)

    fp = open(page, "w")
    fp.write(str(soup))
    fp.close()

db.commit()
db.close()

# Usage:
# python pdp.py 'A' 1 will start scraping from A letter's first page
# python pdp.py 'B' 2 ...
# See http://public-domain-poetry.com/listpoetry.php
# a folder called html is created with html pages in the same order

from bs4 import BeautifulSoup as bs
import os
import sys
import re
from codecs import open
import string
from datetime import datetime
import time
import requests

ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36"

headers = {
    'User-Agent': ua,
}

html_dir = "html/"

def write_file(name, text, directory=None):
    if directory and not os.path.exists(html_dir + directory):
        os.makedirs(html_dir + directory)
    filehandle = open(name, 'w', "utf-8")
    filehandle.write(text)
    filehandle.close()


def read_page_listing(name):
    filehandle = open(name, 'r', "utf-8")
    text = filehandle.read()
    filehandle.close()
    return text

def generateazlink(letter, page):
    return 'http://public-domain-poetry.com/listpoetry.php?letter=' + letter + "&page=" + str(page)

def save_link(link, char, pageno):
    ro = re.search(r'href="(.+?)"', link)
    link = "http://public-domain-poetry.com/" + ro.group(1)
    r = requests.get(link, headers=headers)
    if r.status_code == 404:
        print "FAILED AT " + link + " --- " + char + " --- " + str(pageno)
    r.encoding = 'utf-8'
    filename = html_dir + char + "/" + str(pageno) + "/" + link.rsplit('/',1)[-1] + " - " + str(datetime.now())
    write_file(filename, r.text)
    time.sleep(3)

def get_page(char, pageno):
    link = generateazlink(char,pageno)
    r = requests.get(link, headers=headers)
    if r.status_code == 404:
        print "FAILED AT " + link + " --- " + char + " --- " + str(pageno)
    r.encoding = 'utf-8'
    filename = html_dir + char + "/" + str(pageno) + ".html"
    dirforpoems = char + "/" + str(pageno)
    write_file(filename, r.text, dirforpoems)
    bso = bs(r.text, "html5lib")
    return bso

def get_pages(char, pageno):
    current_page = get_page(char, pageno)
    required_links = current_page.find_all('table')[10].find_all('a')
    lastpage_link = required_links[-1]
    ro = re.search(r'(\d+)"><', str(lastpage_link))
    if ro is None:
        lastpage_no = 1
    else:
        lastpage_no =  ro.group(1)
    index = pageno
    while index <= int(lastpage_no):
        i = 0
        iindex = 1
        while iindex <= 50:
            try:
                link = required_links[i]
            except IndexError:
                break

            save_link(str(link), char, index)
            i += 3
            iindex += 1
        index = index + 1
        if lastpage_no != 1:
            current_page = get_page(char, index)
            required_links = current_page.find_all('table')[10].find_all('a')
            lastpage_link = required_links[-1]

skip_alpha = sys.argv[1]
pageno = sys.argv[2]

for char in string.ascii_uppercase:
    if ord(char) < ord(skip_alpha):
        continue
#    import pdb; pdb.set_trace()
    get_pages(char, int(pageno))
    pageno = 1

get_pages('Other', 1)


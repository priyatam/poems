from bs4 import BeautifulSoup as bs
import os
import sys
import re
from codecs import open
import string
from glob import glob
from pipes import quote

html_dir = "html/"
poems_dir = "poems/"
errors_dir = "errors/"
log = open("except.log", "a")

names = []

def write_file(name, text):
    output_file = poems_dir + name + ".txt"
    filehandle = open(output_file, 'w', "utf-8")
    filehandle.write(text)
    filehandle.close()


def get_first_line(poem):
    lines = poem.split('\n')
    for line in lines:
        if not re.match(r'^\s*$', line):
            title = line
            break
    title = u" ".join(re.split(r'\s*', title)[0:6])
    return title


def clean_name(name):
    punctuation_rx = re.compile('[%s]' % re.escape(string.punctuation))
    name = re.sub(punctuation_rx," ", name) # substiture punctuation with " "
    name = re.sub(" ", "-", name) # substitute spaces with
    name = re.sub("-+", "-", name) # replace multiple hyphens with single
    name = re.sub("-$", "", name) # remove ending hyphen
    return name

def generate_name(title,author,poem):
    first_line = get_first_line(poem)
    name= author + " " + title
    if len(name) <= 255: # some titles are huge
        if name not in names:
            return clean_name(name)
        else:
            name = author + " " + title + " " + first_line
            if name not in names:
                return clean_name(name)
            else:
                return -1
    else:
        title = u" ".join(re.split(r'\s*', title)[0:6])
        name = author + " " + title + " " + first_line
        if name not in names:
            return clean_name(name)
        else:
            return -1


def read_file(name):
    filehandle = open(name, 'r', "utf-8")
    text = filehandle.read()
    filehandle.close()
    bso = bs(text, "html5lib")
    return bso

def clean_html(matter):
    matter = re.sub(r'<.+?>', "", unicode(matter))
    matter = matter.replace(u'\xa0',u"")
    matter = matter.replace(u'\ufffd',u"")
    return matter


def add_front_matter(author, title, text):
    return u"""---
author: %s
title: %s
---

%s
""" % (author, title, text)

def parse_poem(path):
    bso = read_file(path)
    try:
        title = clean_html(bso.find_all("font", class_="t0")[1])
        author = clean_html(bso.find_all("font", class_="t1")[0].a)
        text = clean_html(bso.find_all("font", class_="t3a")[0])
        if not text:
            text = clean_html(bso.find_all("font", class_="t4")[0])
            if not text:
                raise Exception("Not Supposed to Happen")
    except:
        log.write("## ERROR: " + path + "\n")
        errors_path = errors_dir + os.path.basename(path)
        os.system("mv %s %s" % (quote(path), quote(errors_path)))
        return

    name = generate_name(title, author, text)
    if name == -1:
        log.write("## DUP: " + path + "\n")
        return
    else:
        names.append(name)
        write_file(name, add_front_matter(author, title, text))


def parse_poems(char, pageno):
    char_dir = html_dir + char
    files_in_char = os.listdir(char_dir)
    final_dir = len(files_in_char) / 2 # 1 1.html ...
    index = pageno

    while index <= final_dir:
        required_dir = char_dir + "/" + str(index) + "/"
        for html_poem_file in glob(required_dir + "*"):
            log.write("## PROCESS: " + html_poem_file + "\n")
            parse_poem(html_poem_file)
        index += 1


skip_alpha = sys.argv[1]
pageno = sys.argv[2]

for char in string.ascii_uppercase:
    if ord(char) < ord(skip_alpha):
        continue
    parse_poems(char, int(pageno))

parse_poems('Other',1)
log.close()


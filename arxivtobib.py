#!/usr/bin/python
# -*- coding: utf-8 -*-
# CC0, dedicated to public domain by Akihiro Uchida
from html.parser import HTMLParser
import argparse
import urllib.request as request
import os
import re
import calendar
ARXIV_ID_RE = re.compile(r'arXiv:((\d\d)(\d\d)\.\d+)')

class bibitem(object):
    def __init__(self, bibtype):
        assert isinstance(bibtype, str)
        self.bibtype = bibtype
        self.field = dict()
        return

    def add(self, dic):
        assert isinstance(dic, dict)
        for k, v in dic.items():
            self.field[k] = self.field.get(k, '') + v
        return

    def gen_key(self):
        key = ''
        if 'year' in self.field:
            key += self.field['year']
        if 'author' in self.field:
            authors = self.field['author'].split('and')
            for author in authors:
                cnt = 0
                for w in author.split():
                    if cnt < len(w):
                        (cnt, name) = (len(w), w.strip(',.'))
                        key += name
        if 'title' in self.field:
            for w in self.field['title'].split():
                key += w.title()
                if len(w) > 4:
                    break
        return key

    def dump(self):
        d = '@{}{{{}'.format(self.bibtype, self.gen_key())
        for k, v in self.field.items():
            if v not in ['', None]:
                d += ',\n{}={{{}}}'.format(k, v)
        d += '}\n'
        return d

class AbstParser(object):
    def __init__(self):
        self.parse = self.parse_main
        self.text = ''
        return

    def feed(self, text):
        i = 0
        while i < len(text):
            (self.parse, i) = self.parse(text, i)
        return

    def parse_main(self, text, i):
        c = text[i]
        if c == '"':
            self.text += '``'
            return (self.parse_quote, i+1)
        if c == '-':
            return (self.parse_hyphen, i+1)
        else:
            if c == '\n':
                self.text += ' '
            else:
                self.text += c
            return (self.parse_main, i+1)

    def parse_quote(self, text, i):
        c = text[i]
        if c == '"':
            self.text += '\'\''
            return (self.parse_main, i+1)
        else:
            if c == '\n':
                self.text += ' '
            else:
                self.text += c
            return (self.parse_quote, i+1)

    def parse_hyphen(self, text, i):
        c = text[i]
        if c not in (' ', '\n'):
            self.text += '-'
        return (self.parse_main, i+1)

def normalize(cls, dic):
    assert cls in dic
    value = dic[cls]
    result = dict()
    if cls == 'title mathjax':
        result['title'] = value.strip('\n')
    elif cls == 'authors':
        result['author'] = ''
        for c in value.strip('\n'):
            if c == ',':
                result['author'] += ' and '
            else:
                result['author'] += c
    elif cls == 'abstract mathjax':
        parser = AbstParser()
        parser.feed(value.strip())
        result['abstract'] = parser.text
    if cls.startswith('tablecell '):
        c = cls.partition('tablecell ')[-1]
        if c == 'arxivid':
            result['eprint'] = value
            m = ARXIV_ID_RE.match(value)
            result['url'] = 'http://arxiv.org/abs/{}'.format(m.group(1))
            result['year'] = '20{}'.format(m.group(2))
            result['month'] = calendar.month_abbr[int(m.group(3))]
        elif c == 'doi':
            result[c] = value
            result['doi-url'] = 'http://dx.doi.org/{}'.format(value)
        else:
            result[c] = dic[cls]
    return result

some_classes = ('title mathjax', 'authors', 'abstract mathjax',
                'tablecell comments', 'tablecell arxivid', 'tablecell subjects',
                'tablecell jref', 'tablecell doi', 'tablecell report-number',
                'tablecell msc-classes', 'tablecell acm-classes')

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.item = bibitem('misc')
        self.stack = []
        self.in_descriptor = False
        self.tmp = dict()
        return

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[1] in some_classes:
                self.stack.append({'tag': tag, 'class': attr[1]})
            if attr[1] == "descriptor":
                self.in_descriptor = True
        return

    def handle_endtag(self, tag):
        if self.in_descriptor and tag == "span":
            self.in_descriptor = False
        if self.stack != [] and tag == self.stack[-1]['tag']:
            s = self.stack.pop()
            self.item.add(normalize(s['class'], self.tmp))
        return

    def handle_data(self, data):
        for c in some_classes:
            if self.in_descriptor:
                continue
            if self.stack != [] and self.stack[-1]['class'] == c:
                self.tmp[c] = self.tmp.get(c, '') + data
        return

if __name__ == '__main__':
    try:
        proxy = {'http': os.environ['http_proxy']}
    except KeyError as e:
        proxy = {}
    handler = request.ProxyHandler(proxy)
    opener = request.build_opener(handler)
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('url', type=str)
    arg_parser.add_argument('-f', '--file', type=str,
                            required=True)
    args = arg_parser.parse_args()
    parser = MyHTMLParser()
    response = opener.open(args.url)
    parser.feed(response.read().decode('utf-8'))
    response.close()
    fpath = os.path.abspath(args.file)
    fflag = 'a' if os.path.exists(fpath) else 'w'
    with open(fpath, fflag, encoding="utf8") as f:
        f.write(parser.item.dump())
    parser.close()

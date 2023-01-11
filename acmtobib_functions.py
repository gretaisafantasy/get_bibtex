# !/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This script collects all DBLP citation keys from all .tex files in a given
# directory and downloads missing BibTeX records from DBLP to a given BibTeX
# file. Tested with Python 3.10.
#
# Copyright (c) 2014 Sebastian Abshoff <sebastian@abshoff.it>
#           (c) 2016 Akihiro Uchida
#           (c) 2022 Greta Tanudjaja
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pathlib import Path
from html.parser import HTMLParser
import urllib.request as req
import os
import os.path
import re
import argparse
import configparser
import calendar

ACM_ID_RE = re.compile(r'ACM:((\d\d)(\d\d)\.\d+)')
ARXIV_ID_RE = re.compile(r'arXiv:((\d\d)(\d\d)\.\d+)')
TEX_FILES_DIRECTORY = './'  # (sub)directory containing the .tex files
ignore_tex_files = set()  # files within the directory that should be ignored

known_keys = set([])
unused_keys = set([])

acm_keys = set([])
fetched_acm_keys = set([])

arxiv_keys = set([])
fetched_arxiv_keys = set([])

cogprints_keys = set([])
fetched_cogprints_keys = set([])

dblp_keys = set([])
fetched_dblp_keys = set([])

microsoft_keys = set([])
fetched_microsoft_keys = set([])

springer_keys = set([])
fetched_springer_keys = set([])

class BibItem():
    """Represents BibTeX items"""
    def __init__(self, bibtype):
        assert isinstance(bibtype, str)
        self.bibtype = bibtype
        self.field = {}

    def add(self, dic):
        """Adds BibTeX keys"""
        assert isinstance(dic, dict)
        for key, val in dic.items():
            self.field[key] = self.field.get(key, '') + val

    def gen_key(self):
        """Generates and returns the BibTeX keys"""
        key = ''
        if 'year' in self.field:
            key += self.field['year']
        if 'author' in self.field:
            authors = self.field['author'].split('and')
            for author in authors:
                cnt = 0
                for words in author.split():
                    if cnt < len(words):
                        (cnt, name) = (len(words), words.strip(',.'))
                        key += name
        if 'title' in self.field:
            for words in self.field['title'].split():
                key += words.title()
                if len(words) > 4:
                    break
        return key

    def dump(self):
        """Dumps BibTeX items and keys to the dictionary and returns it"""
        dic = f'@{self.bibtype}{{{self.gen_key()}'
        for key, val in self.field.items():
            if val not in ['', None]:
                dic += f',\n{key}={{{val}}}'
        dic += '}\n'
        return dic

class AbstParser():
    """Abstract basis for parsing texts"""
    def __init__(self):
        self.parse = self.parse_main
        self.text = ''

    def feed(self, text):
        """Receives data from the texts"""
        i = 0
        while i < len(text):
            (self.parse, i) = self.parse(text, i)

    def parse_main(self, text, i):
        """Parses the main texts"""
        char = text[i]
        if char == '"':
            self.text += '``'
            return (self.parse_quote, i+1)
        if char == '-':
            return (self.parse_hyphen, i+1)
        else:
            if char == '\n':
                self.text += ' '
            else:
                self.text += char
            return (self.parse_main, i+1)

    def parse_quote(self, text, i):
        """Parses the quote symbols in the texts"""
        char = text[i]
        if char == '"':
            self.text += '\'\''
            return (self.parse_main, i+1)
        else:
            if char == '\n':
                self.text += ' '
            else:
                self.text += char
            return (self.parse_quote, i+1)

    def parse_hyphen(self, text, i):
        """Parses the hyphen symbols in the texts"""
        char = text[i]
        if char not in (' ', '\n'):
            self.text += '-'
        return (self.parse_main, i+1)

def normalize(cls, dic):
    """Normalizes and returns the results of the text"""
    assert cls in dic
    val = dic[cls]
    result = {}
    if cls == 'title mathjax':
        result['title'] = val.strip('\n')
    elif cls == 'authors':
        result['author'] = ''
        for char in val.strip('\n'):
            if char == ',':
                result['author'] += ' and '
            else:
                result['author'] += char
    elif cls == 'abstract mathjax':
        parser = AbstParser()
        parser.feed(val.strip())
        result['abstract'] = parser.text
    if cls.startswith('tablecell '):
        char = cls.partition('tablecell ')[-1]
        if char == 'arxivid':
            result['eprint'] = val
            matches = ARXIV_ID_RE.match(val)
            result['url'] = f'http://arxiv.org/abs/{(matches.group(1))}'
            result['year'] = f'20{(matches.group(2))}'
            result['month'] = calendar.month_abbr[int(matches.group(3))]
        elif char == 'doi':
            result[char] = val
            result['doi-url'] = f'http://dx.doi.org/{val}'
        else:
            result[char] = dic[cls]
    return result

some_classes = ('title mathjax', 'authors', 'abstract mathjax',
                'tablecell comments', 'tablecell arxivid', 'tablecell subjects',
                'tablecell jref', 'tablecell doi', 'tablecell report-number',
                'tablecell msc-classes', 'tablecell acm-classes')

class MyHTMLParser(HTMLParser):
    """Basis for parsing text files formatted in HTML"""
    def __init__(self):
        HTMLParser.__init__(self)
        self.item = BibItem('misc')
        self.stack = []
        self.in_descriptor = False
        self.tmp = {}

    def handle_starttag(self, tag, attrs):
        """Handles the start of a tag"""
        for attr in attrs:
            if attr[1] in some_classes:
                self.stack.append({'tag': tag, 'class': attr[1]})
            if attr[1] == "descriptor":
                self.in_descriptor = True

    def handle_endtag(self, tag):
        """Handles the end of a tag"""
        if self.in_descriptor and tag == "span":
            self.in_descriptor = False
        if self.stack and tag == self.stack[-1]['tag']:
            stack = self.stack.pop()
            self.item.add(normalize(stack['class'], self.tmp))

    def handle_data(self, data):
        """Handles the text contents of the tags"""
        for char in some_classes:
            if self.in_descriptor:
                continue
            if self.stack and self.stack[-1]['class'] == char:
                self.tmp[char] = self.tmp.get(char, '') + data

def return_bibtex():
    """Compiles and returns the BibTeX file citations"""
    re_bibtex_citations = re.compile(r'@.*\{([^,]*),')
    return re_bibtex_citations

def read_existing_file(name_bibtex_file):
    """Reads the existing BibTeX file or create a new one if it is not found"""
    if os.path.isfile(name_bibtex_file):
        print(f'\nReading existing BibTeX file {name_bibtex_file}')
        with (open(name_bibtex_file, encoding="utf-8")) as file:
            for _, line in enumerate(file):
                for match in re.finditer(return_bibtex(), line):
                    for key in match.groups():
                        known_keys.add(key)

    else:
        print(f'\nBibTeX file {name_bibtex_file} not found, will try to create it.')

def read_all_existing_files():
    """Compiles and reads all of the existing bibliography BibTex files"""
    read_existing_file(acm_bibtex_file)
    read_existing_file(arxiv_bibtex_file)
    read_existing_file(cogprints_bibtex_file)
    read_existing_file(dblp_bibtex_file)
    read_existing_file(microsoft_bibtex_file)
    read_existing_file(springer_bibtex_file)

    print('\nThe following keys have been found in your BibTeX files:')
    for key in known_keys:
        print (f'{key}')

def return_tex_citation():
    """Compiles and returns the LateX citations"""
    re_tex_citation = re.compile(r'(?:cite|citep|citet|fullciteown|autocite|textcite)\{([^}]+)}')
    return re_tex_citation

def find_keys(name, name_keys):
    """Finds the bibliography keys in the LaTeX files"""
    print(f'\nThe following {name} keys have been found in your LaTeX files:')
    for key in name_keys:
        print (f'{key}')

def find_all_keys():
    """Calls on the previous functions of finding the keys of all the bibliographies"""
    find_keys('ACM Digital Library', acm_keys)
    find_keys('arXiv', arxiv_keys)
    find_keys('Cogprints', cogprints_keys)
    find_keys('DBLP', dblp_keys)
    find_keys('Microsoft Research', microsoft_keys)
    find_keys('SpringerLink', springer_keys)
    find_keys('unused', unused_keys)

def read_latex():
    """Reads the LateX documents and adds the corresponding keys"""
    print('\nReading your LaTeX documents:')

    return_tex_citation()

    for dirpath, dirnames, filenames in os.walk(TEX_FILES_DIRECTORY):
        exclude = set([])
        list(set(dirnames) - exclude)

        for filename in [f for f in filenames if f.endswith('.tex') and
                         f not in ignore_tex_files]:
            print (f'{filename}')
            with open(Path(dirpath) / filename, encoding="utf-8") as file:
                for _, line in enumerate(file):
                    for match in re.finditer(return_tex_citation(), line):
                        for group in match.groups():
                            for key in group.split(','):
                                if key.strip().startswith('ACM:'):
                                    acm_keys.add(key.strip())
                                elif key.strip().startswith('Arxiv:'):
                                    arxiv_keys.add(key.strip())
                                elif key.strip().startswith('Cogprints:'):
                                    cogprints_keys.add(key.strip())
                                elif key.strip().startswith('DBLP:'):
                                    dblp_keys.add(key.strip())
                                elif key.strip().startswith('Microsoft:'):
                                    microsoft_keys.add(key.strip())
                                elif key.strip().startswith('Springer:'):
                                    springer_keys.add(key.strip())
                                else:
                                    unused_keys.add(key.strip())

    find_all_keys()

def compile_bibtex_items():
    """Compiles the BibTeX items"""
    re_bibtex_items = re.compile(r'(@[a-zA-Z]+\{[^@]*\n})', re.DOTALL)
    return re_bibtex_items

def compile_bibtex_item_key():
    """Compiles the BibTeX item key"""
    re_bibtex_item_key = re.compile(r'@[a-zA-Z]+\{([^,]+),\s*', re.DOTALL)
    return re_bibtex_item_key

def find_missing_keys(name):
    """Finds the missing keys from the bibliography"""
    print(f'\nFetching BibTeX records for missing keys from {name}:')
    compile_bibtex_items()
    compile_bibtex_item_key()

def check_missing_keys(name_bibtex_file, name_keys, name):
    """Checks for missing keys in the BibTeX file"""
    if not os.path.isfile(name_bibtex_file) and name_keys == set():
        print (f'\nYou do not have a {name} BibTeX file, nothing needs to be fetched. :-)')
    elif name_keys == set():
        print(f'\nYour {name} BibTeX file is up to date, nothing needs to be fetched. :-)')
    else:
        find_missing_keys(name)
    return name_keys

def open_bibtex_file(name_bibtex_file, name_bibtex_file_content, fetched_name_keys, name):
    """Opens the BibTeX file for the bibliography and writes it to our BibTeX file if it is not already there"""
    with open(name_bibtex_file, 'a', encoding="utf8") as file:
        for match in re.finditer(compile_bibtex_items(), name_bibtex_file_content):
            for bibtex_item in match.groups():
                key = re.match(compile_bibtex_item_key(), bibtex_item).group(1)
                if key not in fetched_name_keys | known_keys:
                    file.write(bibtex_item)
                    file.write('\n\n')
                    fetched_name_keys.add(key)
                else:
                    print(f'(not adding {key} to {name} BibTeX file, it is already there.)')

def open_acm_url():
    """Opens ACM BibTeX file from its website"""
    for unknown_acm_key in check_missing_keys(acm_bibtex_file, acm_keys, 'ACM'):
        print (f'{unknown_acm_key}')

        acm_url = f'https://dl.acm.org/doi/10.1145/{unknown_acm_key[20:]}'

        with req.urlopen(acm_url) as res:
            acm_bibtex_file_content = MyHTMLParser()
            acm_bibtex_file_content.feed(res.read().decode('utf-8'))
            res.close()

            with open(acm_bibtex_file, 'a', encoding="utf8") as file:
                file.write(acm_bibtex_file_content.item.dump())
                file.write('\n')
            with open(acm_bibtex_file, 'r', encoding="utf8") as file:
                lines = dict.fromkeys(file.readlines())
            with open(acm_bibtex_file, 'w', encoding="utf8") as file:
                file.writelines(lines)
            acm_bibtex_file_content.close()

    print ('(Duplicate keys are not added to ACM BibTeX file.)')

def open_arxiv_url():
    """Opens arXiv BibTeX file from its website"""
    for unknown_arxiv_key in check_missing_keys(arxiv_bibtex_file, arxiv_keys, 'arXiv'):
        print (f'{unknown_arxiv_key}')

        arxiv_url = f'https://arxiv.org/abs/{unknown_arxiv_key[6:]}'

        with req.urlopen(arxiv_url) as res:
            arxiv_bibtex_file_content = MyHTMLParser()
            arxiv_bibtex_file_content.feed(res.read().decode('utf-8'))
            res.close()

            with open(arxiv_bibtex_file, 'a', encoding="utf8") as file:
                file.write(arxiv_bibtex_file_content.item.dump())
                file.write('\n')
            with open(arxiv_bibtex_file, 'r', encoding="utf8") as file:
                lines = dict.fromkeys(file.readlines())
            with open(arxiv_bibtex_file, 'w', encoding="utf8") as file:
                file.writelines(lines)
            arxiv_bibtex_file_content.close()

    print ('(Duplicate keys are not added to arXiV BibTeX file.)')

def open_cogprints_url():
    """Opens Cogprints BibTeX file from its website"""
    for unknown_cogprints_key in check_missing_keys(cogprints_bibtex_file, cogprints_keys, 'Cogprints'):
        print (f'{unknown_cogprints_key}')

        cogprints_url = f'https://web-archive.southampton.ac.uk/cogprints.org/{unknown_cogprints_key[10:]}.bib.html'

        with req.urlopen(cogprints_url) as res:
            cogprints_bibtex_file_content = res.read().decode('utf-8')
            open_bibtex_file(cogprints_bibtex_file, cogprints_bibtex_file_content, fetched_cogprints_keys, 'Cogprints')

def open_dblp_url():
    """Opens DBLP BibTeX file from its website"""
    for unknown_dblp_key in check_missing_keys(dblp_bibtex_file, dblp_keys, 'DBLP'):
        print (f'{unknown_dblp_key}')

        dblp_url = f'https://dblp.org/rec/{unknown_dblp_key[5:]}.bib'

        with req.urlopen(dblp_url) as res:
            dblp_bibtex_file_content = res.read().decode('utf-8')
            open_bibtex_file(dblp_bibtex_file, dblp_bibtex_file_content, fetched_dblp_keys, 'DBLP')

def open_microsoft_url():
    """Opens Microsoft Research BibTeX file from its website"""
    for unknown_microsoft_key in check_missing_keys(microsoft_bibtex_file, microsoft_keys, 'Microsoft Research'):
        print (f'{unknown_microsoft_key}')

        microsoft_url = f'https://www.microsoft.com/en-us/research/publication/{unknown_microsoft_key[10:]}/bibtex/'

        with req.urlopen(microsoft_url) as res:
            microsoft_bibtex_file_content = res.read().decode('utf-8')
            open_bibtex_file(microsoft_bibtex_file, microsoft_bibtex_file_content, fetched_microsoft_keys, 'Microsoft Research')

def open_springer_url():
    """Opens SpringerLink BibTeX file from its website"""
    for unknown_springer_key in check_missing_keys(springer_bibtex_file, springer_keys, 'SpringerLink'):
        print (f'{unknown_springer_key}')

        springer_url = f'https://citation-needed.springer.com/v2/references/10.1007/{unknown_springer_key[9:]}'

        with req.urlopen(springer_url) as res:
            springer_bibtex_file_content = res.read().decode('utf-8')
            open_bibtex_file(springer_bibtex_file, springer_bibtex_file_content, fetched_springer_keys, 'SpringerLink')

def open_url():
    """Calls on the previous functions of opening the BibTeX files from their website"""
    open_acm_url()
    open_arxiv_url()
    open_cogprints_url()
    open_dblp_url()
    open_microsoft_url()
    open_springer_url()

if __name__ == '__main__':
    try:
        proxy = {'http': os.environ['http_proxy']}
    except KeyError as e:
        proxy = {}
    handler = req.ProxyHandler(proxy)
    opener = req.build_opener(handler)

    arg_parser = argparse.ArgumentParser(description='Create BibTeX input and output files.')
    arg_parser.add_argument('--config',                         help='Configuration file; file header always starts with "[Defaults]".')
    arg_parser.add_argument('--ac',    default='acm.bib',       help='ACM BibTeX input and output file; argument always ends in .bib.')
    arg_parser.add_argument('--a',     default='arxiv.bib',     help='ArXiV BibTeX input and output file; argument always ends in .bib.')
    arg_parser.add_argument('--c',     default='cogprints.bib', help='Cogprints BibTeX input and output file; argument always ends in .bib.')
    arg_parser.add_argument('--d',     default='dblp.bib',      help='DBLP BibTeX input and output file; argument always ends in .bib.')
    arg_parser.add_argument('--m',     default='microsoft.bib', help='Microsoft Research BibTeX input and output file; argument always ends in .bib.')
    arg_parser.add_argument('--s',     default='springer.bib',  help='SpringerLink BibTeX input and output file; argument always ends in .bib.')
    args = arg_parser.parse_args()

    acm_bibtex_file = args.ac
    arxiv_bibtex_file = args.a
    cogprints_bibtex_file = args.c
    dblp_bibtex_file = args.d
    microsoft_bibtex_file = args.m
    springer_bibtex_file = args.s

    if args.config:
        config = configparser.ConfigParser()
        config.read(args.config)
        defaults = {}
        defaults.update(dict(config.items("Defaults")))
        arg_parser.set_defaults(**defaults)
        args = arg_parser.parse_args()

        acm_bibtex_file = args.ac
        arxiv_bibtex_file = args.a
        cogprints_bibtex_file = args.c
        dblp_bibtex_file = args.d
        microsoft_bibtex_file = args.m
        springer_bibtex_file = args.s

    read_all_existing_files()
    read_latex()
    open_url()

    print('\nAll done. :-)')

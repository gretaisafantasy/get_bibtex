#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This script collects all DBLP citation keys from all .tex files in a given 
# directory and downloads missing BibTeX records from DBLP to a given BibTeX 
# file. Tested with Python 2.7.
#
# Copyright (c) 2014 Sebastian Abshoff <sebastian@abshoff.it>
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

bibtex_file = 'dblp.bib'  # BibTeX input and output file
tex_files_directory = './'  # (sub)directory containing the .tex files
ignore_tex_files = set()  # files within the directory that should be ignored

import os, os.path
import re
import sys
import time
import urllib2

re_bibtex_dblp_citations = re.compile(r'@.*\{(DBLP:[^,]*),')

known_keys = set([])

if os.path.isfile(bibtex_file):
    print('Reading existing BibTeX file "%s"' % bibtex_file)
    for i,line in enumerate(open(bibtex_file)):
        for match in re.finditer(re_bibtex_dblp_citations,line):
            for key in match.groups():
                known_keys.add(key)
    
    print('The following DBLP keys have been found in your BibTeX file:')
    for key in known_keys:
        print(' * %s' % key)
else:
    print('BibTeX file "%s" not found, will try to create it.' % bibtex_file)

print('\nReading your LaTeX documents:')

re_tex_citation = re.compile(r'(?:cite|fullciteown)\{([^\}]+)\}')

nondblp_keys = set([])
dblp_keys = set([])

for dirpath,dirnames,filenames in os.walk(tex_files_directory):
    for filename in [f for f in filenames if f.endswith('.tex') and 
                                             not f in ignore_tex_files]:
        print(' * %s' % filename)
        for i,line in enumerate(open(os.path.join(dirpath,filename))):
            for match in re.finditer(re_tex_citation,line):
                for group in match.groups():
                    for key in group.split(','):
                        if key.strip().startswith('DBLP:'):
                            dblp_keys.add(key.strip())
                        else:
                            nondblp_keys.add(key.strip())

print('\nThe following non-DBLP keys have been found in your LaTeX files:')
for key in nondblp_keys:
    print(' * %s' % key)

print('\nThe following DBLP keys have been found in your LaTeX files:')
for key in dblp_keys:
    print(' * %s' % key)

unknown_keys = dblp_keys-known_keys

if unknown_keys == set():
    print('\nYour BibTeX file is up to date, nothing needs to be fetched. :-)')
    sys.exit(0)

print('\nFetching BibTeX records for missing keys from DBLP:')

re_bibtex_items = re.compile(r'(@[a-zA-Z]+\{[^@]*\n\})',re.DOTALL)
re_bibtex_item_key = re.compile(r'@[a-zA-Z]+\{(DBLP\:[^,]+),\s*',re.DOTALL)

fetched_keys = set([])

for unknown_key in unknown_keys:
    print(' * %s' % unknown_key)
    
    dblp_url = 'http://dblp.uni-trier.de/rec/bib2/%s.bib' % unknown_key[5:]
    dblp_bibtex_file_content = urllib2.urlopen(dblp_url).read()
    
    f = open(bibtex_file, 'a')
    for match in re.finditer(re_bibtex_items,dblp_bibtex_file_content):
        for dblp_bibtex_item in match.groups():
            key = re.match(re_bibtex_item_key,dblp_bibtex_item).group(1)
            if not key in fetched_keys|known_keys:
                f.write(dblp_bibtex_item)
                f.write('\n\n')
                fetched_keys.add(key)
            else:
                print('   (not adding %s to BibTeX file, it is already there)'
                      % key)
    f.close()
    
    time.sleep(1)

print('\nAll done. :-)')

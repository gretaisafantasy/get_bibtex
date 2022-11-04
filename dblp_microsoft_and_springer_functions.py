# !/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This script collects all DBLP citation keys from all .tex files in a given
# directory and downloads missing BibTeX records from DBLP to a given BibTeX
# file. Tested with Python 3.10.
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

from pathlib import Path
import urllib.request as req
import sys
import os
import os.path
import re
import argparse

TEX_FILES_DIRECTORY = './'  # (sub)directory containing the .tex files
ignore_tex_files = set()  # files within the directory that should be ignored

known_keys = set([])

known_dblp_keys = set([])
dblp_keys = set([])
nondblp_keys = set([])

known_microsoft_keys = set([])
microsoft_keys = set([])
nonmicrosoft_keys = set([])

known_springer_keys = set([])
springer_keys = set([])
nonspringer_keys = set([])

parser = argparse.ArgumentParser(description='Create BibTeX input and output files.')
parser.add_argument('--d', default='dblp.bib', type=str, help='DBLP BibTeX input and output file; always ends in .bib')
parser.add_argument('--m', default='microsoft.bib', type=str, help='Microsoft BibTeX input and output file; always ends in .bib')
parser.add_argument('--s', default='springer.bib', type=str, help='Springer BibTeX input and output file; always ends in .bib')
args = parser.parse_args()
dblp_bibtex_file = args.d
microsoft_bibtex_file = args.m
springer_bibtex_file = args.s
print("DBLP BibTeX file:", dblp_bibtex_file)
print("Microsoft BibTeX file:", microsoft_bibtex_file)
print("Springer BibTeX file:", springer_bibtex_file)

def return_bibtex():
    """This function compiles and returns the BibTeX file citations"""
    re_bibtex_citations = re.compile(r'@.*\{([^,]*),')
    return re_bibtex_citations


def find_known_keys(name, bibliography):
    """This function finds the known bibliography keys in the existing BibTeX file"""
    print(f'\nThe following {name} keys have been found in your BibTeX file:')
    for key in bibliography:
        print (f' {key}')


def read_existing_file(bibtex_file):
    """This function reads the existing BibTeX file or create a new one if it is not found"""
    if os.path.isfile(bibtex_file):
        print('\nReading existing BibTeX file "%s"' % bibtex_file)
        for i, line in enumerate(open(bibtex_file)):
            for match in re.finditer(return_bibtex(), line):
                for key in match.groups():
                    known_dblp_keys.add(key)
                    known_microsoft_keys.add(key)
                    known_springer_keys.add(key)
        find_known_keys('DBLP', known_dblp_keys) and find_known_keys('Microsoft', known_microsoft_keys) and find_known_keys('Springer', known_springer_keys)

    else:
        print('\nBibTeX file "%s" not found, will try to create it.' % bibtex_file)


def read_all_existing_files():
    """This function compiles and reads all of the existing bibliography BibTex files"""
    read_existing_file(dblp_bibtex_file)
    read_existing_file(microsoft_bibtex_file)
    read_existing_file(springer_bibtex_file)


read_all_existing_files()


def return_tex_citation():
    """This function compiles and returns the LateX citations"""
    re_tex_citation = re.compile(r'(?:cite|citep|citet|fullciteown|autocite|textcite)\{([^}]+)}')
    return re_tex_citation


def find_keys(name, bibliography_keys):
    """This function finds the bibliography keys in the LaTeX files"""
    print(f"\nThe following {name} keys have been found in your LaTeX files:")
    for key in bibliography_keys:
        print (f' {key}')


def find_all_keys():
    """This function calls on the previous functions of finding the keys of all the bibliographies"""
    find_keys('non-DBLP', nondblp_keys)
    find_keys('DBLP', dblp_keys)
    find_keys('non-Microsoft', nonmicrosoft_keys)
    find_keys('Microsoft', microsoft_keys)
    find_keys('non-Springer', nonspringer_keys)
    find_keys('Springer', springer_keys)


def read_latex():
    """This function reads the LateX documents and adds the corresponding keys"""
    print('\nReading your LaTeX documents:')

    return_tex_citation()

    for dirpath, dirnames, filenames in os.walk(TEX_FILES_DIRECTORY):
        exclude = set([])
        dirnames[:] = [d for d in set(dirnames)-exclude]

        for filename in [f for f in filenames if f.endswith('.tex') and
                         f not in ignore_tex_files]:
            print (f' {filename}')
            for i, line in enumerate(open(Path(dirpath) / filename, encoding="utf-8")):
                for match in re.finditer(return_tex_citation(), line):
                    for group in match.groups():
                        for key in group.split(','):
                            if key.strip().startswith('DBLP:'):
                                dblp_keys.add(key.strip())
                            else:
                                nondblp_keys.add(key.strip())
                            if key.strip().startswith('Microsoft:'):
                                microsoft_keys.add(key.strip())
                            else:
                                nonmicrosoft_keys.add(key.strip())
                            if key.strip().startswith('Springer:'):
                                springer_keys.add(key.strip())
                            else:
                                nonspringer_keys.add(key.strip())


    find_all_keys()


read_latex()


def compile_bibtex_items():
    """This function compiles the BibTeX items"""
    re_bibtex_items = re.compile(r'(@[a-zA-Z]+\{[^@]*\n})', re.DOTALL)
    return re_bibtex_items


def compile_bibtex_item_key():
    """This function compiles the BibTeX item key"""
    re_bibtex_item_key = re.compile(r'@[a-zA-Z]+\{([^,]+),\s*', re.DOTALL)
    return re_bibtex_item_key


def find_missing_keys(name):
    """This function finds the missing keys from the bibliography"""
    print(f'\nFetching BibTeX records for missing keys from {name}:')
    compile_bibtex_items()
    compile_bibtex_item_key()


def find_unknown_dblp_keys():
    """This function finds the unknown DBLP keys"""
    unknown_dblp_keys = dblp_keys - known_dblp_keys - known_springer_keys - known_microsoft_keys
    if unknown_dblp_keys == set():
        print('\nYour DBLP BibTeX file is up to date, nothing needs to be fetched. :-)')
    else:
        find_missing_keys('DBLP')
    return unknown_dblp_keys


def find_unknown_microsoft_keys():
    """This function finds the unknown Microsoft Research keys"""
    unknown_microsoft_keys = microsoft_keys - known_microsoft_keys
    if unknown_microsoft_keys == set():
        print('\nYour Microsoft Research BibTeX file is up to date, nothing needs to be fetched. :-)')
    else:
        find_missing_keys('Microsoft')
    return unknown_microsoft_keys


def find_unknown_springer_keys():
    """This function finds the unknown Springer keys"""
    unknown_springer_keys = springer_keys - known_springer_keys - known_microsoft_keys
    if unknown_springer_keys == set():
        print('\nYour Springer BibTeX file is up to date, nothing needs to be fetched. :-)')
    else:
        find_missing_keys('Springer')
    return unknown_springer_keys


def open_dblp_file():
    """This function opens the DBLP BibTeX file and writes it to our BibTeX file if it is not already there"""
    fetched_dblp_keys = set([])

    for unknown_dblp_key in find_unknown_dblp_keys():
        print (f' {unknown_dblp_key}')

        dblp_url = 'https://dblp.org/rec/%s.bib' % unknown_dblp_key[5:]
        dblp_bibtex_file_content = req.urlopen(dblp_url).read().decode('utf-8')

        f = open(dblp_bibtex_file, 'a')
        for match in re.finditer(compile_bibtex_items(), dblp_bibtex_file_content):
            for dblp_bibtex_item in match.groups():
                key = re.match(compile_bibtex_item_key(), dblp_bibtex_item).group(1)
                if key not in fetched_dblp_keys | known_dblp_keys:
                    f.write(dblp_bibtex_item)
                    f.write('\n\n')
                    fetched_dblp_keys.add(key)
                else:
                    print('   (not adding %s to DBLP BibTeX file, it is already there)'
                          % key)
        f.close()


def open_microsoft_file():
    """This function opens the Microsoft Research BibTeX file and writes it to our BibTeX file if it is not already there"""
    fetched_microsoft_keys = set([])

    for unknown_microsoft_key in find_unknown_microsoft_keys():
        print (f' {unknown_microsoft_key}')

        microsoft_url = 'https://www.microsoft.com/en-us/research/publication/%s/bibtex/' % unknown_microsoft_key[10:]
        microsoft_bibtex_file_content = req.urlopen(microsoft_url).read().decode('utf-8')

        f = open(microsoft_bibtex_file, 'a')
        for match in re.finditer(compile_bibtex_items(), microsoft_bibtex_file_content):
            for microsoft_bibtex_item in match.groups():
                key = re.match(compile_bibtex_item_key(), microsoft_bibtex_item).group(1)
                if key not in fetched_microsoft_keys | known_microsoft_keys:
                    f.write(microsoft_bibtex_item)
                    f.write('\n\n')
                    fetched_microsoft_keys.add(key)
                else:
                    print('   (not adding %s to Microsoft Research BibTeX file, it is already there)'
                          % key)
        f.close()


def open_springer_file():
    """This function opens the Springer BibTeX file and writes it to our BibTeX file if it is not already there"""
    fetched_springer_keys = set([])

    for unknown_springer_key in find_unknown_springer_keys():
        print (f' {unknown_springer_key}')

        springer_url = 'https://citation-needed.springer.com/v2/references/10.1007/%s' % unknown_springer_key[9:]
        springer_bibtex_file_content = req.urlopen(springer_url).read().decode('utf-8')

        f = open(springer_bibtex_file, 'a')
        for match in re.finditer(compile_bibtex_items(), springer_bibtex_file_content):
            for springer_bibtex_item in match.groups():
                key = re.match(compile_bibtex_item_key(), springer_bibtex_item).group(1)
                if key not in fetched_springer_keys | known_springer_keys:
                    f.write(springer_bibtex_item)
                    f.write('\n\n')
                    fetched_springer_keys.add(key)
                else:
                    print('   (not adding %s to Springer BibTeX file, it is already there)'
                          % key)
        f.close()


def open_file():
    """This function calls on the previous functions of opening the BibTeX file and writing it to our BibTeX file"""
    open_dblp_file()
    open_microsoft_file()
    open_springer_file()


open_file()


print('\nAll done. :-)')

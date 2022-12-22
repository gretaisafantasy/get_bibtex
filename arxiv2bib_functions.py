#! /usr/bin/env python
#
# Copyright (c) 2012, Nathan Grigg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of this package nor the
#   names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# This software is provided by the copyright holders and contributors "as
# is" and any express or implied warranties, including, but not limited
# to, the implied warranties of merchantability and fitness for a
# particular purpose are disclaimed. In no event shall Nathan Grigg be
# liable for any direct, indirect, incidental, special, exemplary, or
# consequential damages (including, but not limited to, procurement of
# substitute goods or services; loss of use, data, or profits; or business
# interruption) however caused and on any theory of liability, whether in
# contract, strict liability, or tort (including negligence or otherwise)
# arising in any way out of the use of this software, even if advised of
# the possibility of such damage.
#
# (also known as the New BSD License)
#
# Indiscriminate automated downloads from arXiv.org are not permitted.
# For more information, see http://arxiv.org/help/robots
#
# This script usually makes only one call to arxiv.org per run.
# No caching of any kind is performed.


from __future__ import print_function
from xml.etree import ElementTree
from pathlib import Path
import urllib.request as req
import os
import os.path
import re
import argparse
import configparser
import sys

TEX_FILES_DIRECTORY = './'  # (sub)directory containing the .tex files
ignore_tex_files = set()  # files within the directory that should be ignored

known_keys = set([])
unused_keys = set([])

cogprints_keys = set([])
fetched_cogprints_keys = set([])

dblp_keys = set([])
fetched_dblp_keys = set([])

microsoft_keys = set([])
fetched_microsoft_keys = set([])

springer_keys = set([])
fetched_springer_keys = set([])

arxiv = 'arxiv.bib'

if sys.version_info < (2, 6):
    raise Exception("Python 2.6 or higher required")

# Python 2 compatibility code
PY2 = sys.version_info[0] == 2
if not PY2:
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.error import HTTPError
    print_bytes = lambda s: sys.stdout.buffer.write(s)
else:
    import urllib.parse
    import urllib.request as req
    print_bytes = lambda s: sys.stdout.write(s)


# Namespaces
ATOM = '{http://www.w3.org/2005/Atom}'
ARXIV = '{http://arxiv.org/schemas/atom}'

# regular expressions to check if arxiv id is valid
NEW_STYLE = re.compile(r'^\d{4}\.\d{4,}(v\d+)?$')
OLD_STYLE = re.compile(r"""(?x)
^(
   math-ph
  |hep-ph
  |nucl-ex
  |nucl-th
  |gr-qc
  |astro-ph
  |hep-lat
  |quant-ph
  |hep-ex
  |hep-th
  |stat
    (\.(AP|CO|ML|ME|TH))?
  |q-bio
    (\.(BM|CB|GN|MN|NC|OT|PE|QM|SC|TO))?
  |cond-mat
    (\.(dis-nn|mes-hall|mtrl-sci|other|soft|stat-mech|str-el|supr-con))?
  |cs
    (\.(AR|AI|CL|CC|CE|CG|GT|CV|CY|CR|DS|DB|DL|DM|DC|GL|GR|HC|IR|IT|LG|LO|
      MS|MA|MM|NI|NE|NA|OS|OH|PF|PL|RO|SE|SD|SC))?
  |nlin
    (\.(AO|CG|CD|SI|PS))?
  |physics
    (\.(acc-ph|ao-ph|atom-ph|atm-clus|bio-ph|chem-ph|class-ph|comp-ph|
      data-an|flu-dyn|gen-ph|geo-ph|hist-ph|ins-det|med-ph|optics|ed-ph|
      soc-ph|plasm-ph|pop-ph|space-ph))?
  |math
      (\.(AG|AT|AP|CT|CA|CO|AC|CV|DG|DS|FA|GM|GN|GT|GR|HO|IT|KT|LO|MP|MG
      |NT|NA|OA|OC|PR|QA|RT|RA|SP|ST|SG))?
)/\d{7}(v\d+)?$""")


def is_valid(arxiv_id):
    """Checks if id resembles a valid arxiv identifier."""
    return bool(NEW_STYLE.match(arxiv_id)) or bool(OLD_STYLE.match(arxiv_id))


class FatalError(Exception):
    """Error that prevents us from continuing"""


class NotFoundError(Exception):
    """Reference not found by the arxiv API"""


class Reference(object):
    """Represents a single reference.

    Instantiate using Reference(entry_xml). Note entry_xml should be
    an ElementTree.Element object.
    """
    def __init__(self, entry_xml):
        self.xml = entry_xml
        self.url = self._field_text('id')
        self.id = self._id()
        self.authors = self._authors()
        self.title = self._field_text('title')
        if len(self.id) == 0 or len(self.authors) == 0 or len(self.title) == 0:
            raise NotFoundError("No such publication", self.id)
        self.summary = self._field_text('summary')
        self.category = self._category()
        self.year, self.month = self._published()
        self.updated = self._field_text('updated')
        self.bare_id = self.id[:self.id.rfind('v')]
        self.note = self._field_text('journal_ref', namespace=ARXIV)
        self.doi = self._field_text('doi', namespace=ARXIV)

    def _authors(self):
        """Extracts author names from xml."""
        xml_list = self.xml.findall(ATOM + 'author/' + ATOM + 'name')
        return [field.text for field in xml_list]

    def _field_text(self, id, namespace=ATOM):
        """Extracts text from arbitrary xml field"""
        try:
            return self.xml.find(namespace + id).text.strip()
        except:
            return ""

    def _category(self):
        """Get category"""
        try:
            return self.xml.find(ARXIV + 'primary_category').attrib['term']
        except:
            return ""

    def _id(self):
        """Get arxiv id"""
        try:
            id_url = self._field_text('id')
            return id_url[id_url.find('/abs/') + 5:]
        except:
            return ""

    def _published(self):
        """Get published date"""
        published = self._field_text('published')
        if len(published) < 7:
            return "", ""
        y, m = published[:4], published[5:7]
        try:
            m = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
                 "Aug", "Sep", "Oct", "Nov", "Dec"][int(m) - 1]
        except:
            pass
        return y, m

    def bibtex(self):
        """BibTex string of the reference."""

        lines = ["@article{" + self.id]
        for k, v in [("Author", " and ".join(self.authors)),
                    ("Title", self.title),
                    ("Eprint", self.id),
                    ("DOI", self.doi),
                    ("ArchivePrefix", "arXiv"),
                    ("PrimaryClass", self.category),
                    ("Abstract", self.summary),
                    ("Year", self.year),
                    ("Month", self.month),
                    ("Note", self.note),
                    ("Url", self.url),
                    ("File", self.id + ".pdf"),
                    ]:
            if len(v):
                lines.append("%-13s = {%s}" % (k, v))

        return ("," + os.linesep).join(lines) + os.linesep + "}"


class ReferenceErrorInfo(object):
    """Contains information about a reference error"""
    def __init__(self, message, id):
        self.message = message
        self.id = id
        self.bare_id = id[:id.rfind('v')]
        # mark it as really old, so it gets superseded if possible
        self.updated = '0'

    def bibtex(self):
        """BibTeX comment explaining error"""
        return "@comment{%(id)s: %(message)s}" % \
                {'id': self.id, 'message': self.message}

    def __str__(self):
        return "Error: %(message)s (%(id)s)" % \
                {'id': self.id, 'message': self.message}


def arxiv2bib(id_list):
    """Returns a list of references, corresponding to elts of id_list"""
    d = arxiv2bib_dict(id_list)
    l = []
    for id in id_list:
        try:
            l.append(d[id])
        except:
            l.append(ReferenceErrorInfo("Not found", id))

    return l


def arxiv_request(ids):
    """Sends a request to the arxiv API."""
    q = urlencode([
         ("id_list", ",".join(ids)),
         ("max_results", len(ids))
         ])
    xml = urlopen("http://export.arxiv.org/api/query?" + q)
    # xml.read() returns bytes, but ElementTree.fromstring decodes
    # to unicode when needed (python2) or string (python3)
    return ElementTree.fromstring(xml.read())


def arxiv2bib_dict(id_list):
    """Fetches citations for ids in id_list into a dictionary indexed by id"""
    ids = []
    d = {}

    # validate ids
    for id in id_list:
        if is_valid(id):
            ids.append(id)
        else:
            d[id] = ReferenceErrorInfo("Invalid arXiv identifier", id)

    if len(ids) == 0:
        return d

    # make the api call
    while True:
        xml = arxiv_request(ids)

        # check for error
        entries = xml.findall(ATOM + "entry")
        try:
            first_title = entries[0].find(ATOM + "title")
        except:
            raise FatalError("Unable to connect to arXiv.org API.")

        if first_title is None or first_title.text.strip() != "Error":
            break

        try:
            id = entries[0].find(ATOM + "summary").text.split()[-1]
            del(ids[ids.index(id)])
        except:
            raise FatalError("Unable to parse an error returned by arXiv.org.")

    # Parse each reference and store it in dictionary
    for entry in entries:
        try:
            ref = Reference(entry)
        except NotFoundError as error:
            message, id = error.args
            ref = ReferenceErrorInfo(message, id)
        if ref.id:
            d[ref.id] = ref
        if ref.bare_id:
            if not (ref.bare_id in d) or d[ref.bare_id].updated < ref.updated:
                d[ref.bare_id] = ref

    return d


class Cli(object):
    """Command line interface"""

    def __init__(self, args=None):
        """Parse arguments"""
        self.args = self.parse_args(args)

        if len(self.args.id) == 0:
            self.args.id = [line.strip() for line in sys.stdin]

        # avoid duplicate error messages unless verbose is set
        if self.args.comments and not self.args.verbose:
            self.args.quiet = True

        self.output = []
        self.messages = []
        self.error_count = 0
        self.code = 0

    def run(self):
        """Produce output and error messages"""
        try:
            bib = arxiv2bib(self.args.id)
        except HTTPError as error:
            if error.getcode() == 403:
                raise FatalError("""\
    403 Forbidden error. This usually happens when you make many
    rapid fire requests in a row. If you continue to do this, arXiv.org may
    interpret your requests as a denial of service attack.

    For more information, see http://arxiv.org/help/robots.
    """)
            else:
                raise FatalError(
                  "HTTP Connection Error: {0}".format(error.getcode()))

        self.create_output(bib)
        self.code = self.tally_errors(bib)

    def create_output(self, bib):
        """Format the output and error messages"""
        for b in bib:
            if isinstance(b, ReferenceErrorInfo):
                self.error_count += 1
                if self.args.comments:
                    self.output.append(b.bibtex())
                if not self.args.quiet:
                    self.messages.append(str(b))
            else:
                self.output.append(b.bibtex())

    def print_output(self):
        if not self.output:
            return

        output_string = os.linesep.join(self.output)
        try:
            print(output_string)
        except UnicodeEncodeError:
            print_bytes((output_string + os.linesep).encode('utf-8'))
            if self.args.verbose:
                self.messages.append(
                  'Could not use system encoding; using utf-8')

    def write(self):
        if not self.output:
            return
        output_string = os.linesep.join(self.output)

        with open(arxiv, 'a', encoding="utf8") as f:
            f.write(output_string)
        
    def tally_errors(self, bib):
        """calculate error code"""
        if self.error_count == len(self.args.id):
            self.messages.append("No successful matches")
            return 2
        elif self.error_count > 0:
            self.messages.append("%s of %s matched succesfully" %
              (len(bib) - self.error_count, len(bib)))
            return 1
        else:
            return 0

    def print_messages(self):
        """print messages to stderr"""
        if self.messages:
            self.messages.append("")
            sys.stderr.write(os.linesep.join(self.messages))

    @staticmethod
    def parse_args(args):
        try:
            import argparse
        except:
            sys.exit("Cannot load required module 'argparse'")

        parser = argparse.ArgumentParser(
          description="Get the BibTeX for each arXiv id.",
          epilog="""\
    Returns 0 on success, 1 on partial failure, 2 on total failure.
    Valid BibTeX is written to stdout, error messages to stderr.
    If no arguments are given, ids are read from stdin, one per line.""",
          formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('id', metavar='arxiv_id', nargs="*",
          help="arxiv identifier, such as 1201.1213")
        parser.add_argument('-c', '--comments', action='store_true',
          help="Include @comment fields with error details")
        parser.add_argument('-q', '--quiet', action='store_true',
          help="Display fewer error messages")
        parser.add_argument('-v', '--verbose', action="store_true",
          help="Display more error messages")
        return parser.parse_args(args)


def main(args=None):
    """Run the command line interface"""
    cli = Cli(args)
    try:
        cli.run()
    except FatalError as err:
        sys.stderr.write(err.args[0] + os.linesep)
        return 2
    
    cli.write()
    cli.print_output()
    cli.print_messages()
    return cli.code

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
    print(f"\nThe following {name} keys have been found in your LaTeX files:")
    for key in name_keys:
        print (f'{key}')


def find_all_keys():
    """Calls on the previous functions of finding the keys of all the bibliographies"""
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
                                if key.strip().startswith('Cogprints:'):
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


def open_cogprints_url():
    """Opens Cogprints BibTeX file from its website"""
    for unknown_cogprints_key in check_missing_keys(cogprints_bibtex_file, cogprints_keys, 'Cogprints'):
        print (f'{unknown_cogprints_key}')

        cogprints_url = f'https://web-archive.southampton.ac.uk/cogprints.org/{unknown_cogprints_key[10:]}.bib.html'

        with req.urlopen(cogprints_url) as response:
            cogprints_bibtex_file_content = response.read().decode('utf-8')
            open_bibtex_file(cogprints_bibtex_file, cogprints_bibtex_file_content, fetched_cogprints_keys, 'Cogprints')


def open_dblp_url():
    """Opens DBLP BibTeX file from its website"""
    for unknown_dblp_key in check_missing_keys(dblp_bibtex_file, dblp_keys, 'DBLP'):
        print (f'{unknown_dblp_key}')

        dblp_url = f'https://dblp.org/rec/{unknown_dblp_key[5:]}.bib'

        with req.urlopen(dblp_url) as response:
            dblp_bibtex_file_content = response.read().decode('utf-8')
            open_bibtex_file(dblp_bibtex_file, dblp_bibtex_file_content, fetched_dblp_keys, 'DBLP')


def open_microsoft_url():
    """Opens Microsoft Research BibTeX file from its website"""
    for unknown_microsoft_key in check_missing_keys(microsoft_bibtex_file, microsoft_keys, 'Microsoft Research'):
        print (f'{unknown_microsoft_key}')

        microsoft_url = f'https://www.microsoft.com/en-us/research/publication/{unknown_microsoft_key[10:]}/bibtex/'

        with req.urlopen(microsoft_url) as response:
            microsoft_bibtex_file_content = response.read().decode('utf-8')
            open_bibtex_file(microsoft_bibtex_file, microsoft_bibtex_file_content, fetched_microsoft_keys, 'Microsoft Research')


def open_springer_url():
    """Opens SpringerLink BibTeX file from its website"""
    for unknown_springer_key in check_missing_keys(springer_bibtex_file, springer_keys, 'SpringerLink'):
        print (f'{unknown_springer_key}')

        springer_url = f'https://citation-needed.springer.com/v2/references/10.1007/{unknown_springer_key[9:]}'

        with req.urlopen(springer_url) as response:
            springer_bibtex_file_content = response.read().decode('utf-8')
            open_bibtex_file(springer_bibtex_file, springer_bibtex_file_content, fetched_springer_keys, 'SpringerLink')


def open_url():
    """Calls on the previous functions of opening the BibTeX files from their website"""
    open_cogprints_url()
    open_dblp_url()
    open_microsoft_url()
    open_springer_url()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='Create BibTeX input and output files.')
    arg_parser.add_argument('--config',                         help='Configuration file; file header always starts with "[Defaults]".')
    arg_parser.add_argument('--c',     default='cogprints.bib', help='Cogprints BibTeX input and output file; argument always ends in .bib.')
    arg_parser.add_argument('--d',     default='dblp.bib',      help='DBLP BibTeX input and output file; argument always ends in .bib.')
    arg_parser.add_argument('--m',     default='microsoft.bib', help='Microsoft Research BibTeX input and output file; argument always ends in .bib.')
    arg_parser.add_argument('--s',     default='springer.bib',  help='SpringerLink BibTeX input and output file; argument always ends in .bib.')
    args = arg_parser.parse_args()

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

        cogprints_bibtex_file = args.c
        dblp_bibtex_file = args.d
        microsoft_bibtex_file = args.m
        springer_bibtex_file = args.s

    read_all_existing_files()
    read_latex()
    open_url()

    print('\nAll done. :-)')
    
    sys.exit(main())

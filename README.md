# get_bibtex

[![Python 3.8](https://img.shields.io/badge/Python-3.8-blue?&logo=Python&logoColor=white)](https://www.python.org/)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue?&logo=Python&logoColor=white)](https://www.python.org/)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?&logo=Python&logoColor=white)](https://www.python.org/)

[![Pylint](https://img.shields.io/github/actions/workflow/status/gretaisafantasy/get_bibtex/pylint.yml?branch=main)](https://github.com/gretaisafantasy/get_bibtex/actions/workflows/pylint.yml)
[![License](https://img.shields.io/badge/license-MIT-_red.svg)](https://opensource.org/licenses/MIT)

This script collects various online bibliographies ([arXiv](https://arxiv.org/), [BASE](https://www.base-search.net/), [Cogprints](https://web-archive.southampton.ac.uk/cogprints.org/), [DBLP](https://dblp.org/), [JSTOR](https://www.jstor.org/), [Microsoft Research](https://www.microsoft.com/en-us/research/), and [SpringerLink](https://link.springer.com/) citation keys from all .tex files, downloads the missing BibTeX records to a separate BibTeX file for each of the bibliographies, and automatically add them as references in LaTeX.

## Getting Started

### Dependencies

[Python 3.10](https://www.python.org/downloads/)

### Installation

You can also use get_bibtex.py as a standalone executable. Just copy it to somewhere in your path.

## Usage

```

usage: cite.py [-h] [--config CONFIG] [--a A] [--b B] [--c C] [--d D] [--j J]
               [--m M] [--s S]

Create BibTeX input and output files.

options:
  -h, --help       show this help message and exit
  --config CONFIG  Configuration file; file header always starts with
                   "[Defaults]".
  --a A            ArXiv BibTeX input and output file.
  --b B            BASE BibTeX input and output file.
  --c C            Cogprints BibTeX input and output file.
  --d D            DBLP BibTeX input and output file.
  --j J            JSTOR BibTeX input and output file.
  --m M            Microsoft Research BibTeX input and output file.
  --s S            SpringerLink BibTeX input and output file.

```

## Configuration

## License

Licensed under the MIT License.

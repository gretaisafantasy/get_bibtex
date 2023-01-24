# get_bibtex

[![Python 3.8](https://img.shields.io/badge/Python-3.8-blue?&logo=Python&logoColor=white)](https://www.python.org/)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue?&logo=Python&logoColor=white)](https://www.python.org/)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?&logo=Python&logoColor=white)](https://www.python.org/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?&logo=Python&logoColor=white)](https://www.python.org/)

[![Pylint](https://img.shields.io/github/actions/workflow/status/gretaisafantasy/get_bibtex/pylint.yml?branch=main)](https://github.com/gretaisafantasy/get_bibtex/actions/workflows/pylint.yml)
[![License](https://img.shields.io/badge/license-MIT-_red.svg)](https://opensource.org/licenses/MIT)

`get_bibtex` collects various online bibliographies ([arXiv](https://arxiv.org/), [BASE](https://www.base-search.net/), [Cogprints](https://web-archive.southampton.ac.uk/cogprints.org/), [DBLP](https://dblp.org/), [JSTOR](https://www.jstor.org/), [Microsoft Research](https://www.microsoft.com/en-us/research/), and [SpringerLink](https://link.springer.com/)) citation keys from all .tex files, downloads the missing BibTeX records to a separate BibTeX file for each of the bibliographies, and automatically add them as references in LaTeX.

## Getting Started

### Requirements
- [Python 3](https://www.python.org/downloads/)
- A LaTeX editor, such as TeXstudio, TeXmaker, TeXworks, etc.
- A LaTeX distribution, such as MikTeX, MacTeX, TeX Live, etc.
- Working Internet connection

### Installation

You can use `get_bibtex.py` as a standalone executable. Just copy it to somewhere in your path.

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
It is also possible to change the BibTeX input and output files through a configuration file. Open a new file, write the configuration that you want, and save it. A short `test.cfg`, `test.txt`, and `test.json` files are provided as examples, but other file formats will work too as a configuration file.

### Example

```

[Defaults]
c = c.bib
d = d.bib

```

The file header should always start with **_[Defaults]_** and the keys are the same as in the command line arguments. In the example above, the configuration means that you want to put Cogprints BibTeX input and output file into `c.bib` and DBLP BibTeX input and output file into `d.bib`.



## License

Licensed under the MIT License.

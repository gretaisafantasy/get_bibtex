# get_bibtex

[![Python 3.8](https://img.shields.io/badge/Python-3.8-blue?&logo=Python&logoColor=white)](https://www.python.org/)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue?&logo=Python&logoColor=white)](https://www.python.org/)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?&logo=Python&logoColor=white)](https://www.python.org/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?&logo=Python&logoColor=white)](https://www.python.org/)

[![Pylint](https://img.shields.io/github/actions/workflow/status/gretaisafantasy/get_bibtex/pylint.yml?branch=main)](https://github.com/gretaisafantasy/get_bibtex/actions/workflows/pylint.yml)
[![License](https://img.shields.io/badge/license-MIT-_red.svg)](https://opensource.org/licenses/MIT)

`get_bibtex` collects various online bibliographies ([arXiv](https://arxiv.org/), [BASE](https://www.base-search.net/), [Cogprints](https://web-archive.southampton.ac.uk/cogprints.org/), [DBLP](https://dblp.org/), [JSTOR](https://www.jstor.org/), [Microsoft Research](https://www.microsoft.com/en-us/research/), and [SpringerLink](https://link.springer.com/)) citation keys from all .tex files, downloads the missing BibTeX records to a separate BibTeX file for each of the bibliographies, and automatically adds them as references or as part of a bibliography in LaTeX.

## Getting Started

### Requirements
- [Python 3](https://www.python.org/downloads/).
- A LaTeX editor, such as [TeXstudio](https://www.texstudio.org/), [TeXmaker](https://www.xm1math.net/texmaker/), [TeXworks](https://www.tug.org/texworks/), etc.
- A LaTeX distribution, such as [MikTeX](https://miktex.org/), [MacTeX](https://www.tug.org/mactex/), [TeX Live](https://www.tug.org/texlive/), etc.
- A working internet connection.

### Installation

You can either: 
- download the [`get_bibtex` ZIP](https://github.com/gretaisafantasy/get_bibtex/archive/refs/heads/main.zip) to your computer. Unzip the package, then move it to a new directory named after the package.

OR

- use `get_bibtex.py` as a standalone executable. Just copy it to somewhere in your path.

## How to Use

There are two ways to change the default BibTeX input and output files. The first one is through the command line arguments and the second one is through a configuration file.

## 1) Command Line Arguments

The usage to create BibTeX input and output files for the command line arguments is given below. 

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

### Example

If you want to put JSTOR BibTeX input and output file into `j.bib`, you just have to write `--j j.bib` as the command line argument.

## 2) Configuration File

Open a new file, write the configuration that you want, save it in the same directory as the `get_bibtex` script, and load it through the command line argument with `--config` and the name and file format of the configuration file.

### Example

```

[Defaults]
c = c.bib
d = d.bib

```

As seen on the example above, the file header should always start with `[Defaults]` and the keys are the same as in the command line arguments. That particular configuration means that instead of the default BibTeX input and output file, you want to put Cogprints BibTeX input and output file into `c.bib` and DBLP BibTeX input and output file into `d.bib`.

Some short files named [`sample.cfg`](https://github.com/gretaisafantasy/get_bibtex/blob/main/sample.cfg), [`sample.txt`](https://github.com/gretaisafantasy/get_bibtex/blob/main/sample.txt), and [`sample.json`] are also provided as examples. Keep in mind that besides the provided examples, other kind of file formats will work as a configuration file too.

## License

Licensed under the MIT License.

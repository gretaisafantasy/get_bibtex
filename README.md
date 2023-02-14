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

Since `get_bibtex` is used when people write a paper and wants to cite another paper from one or more of the online bibliography websites, it is imperative to write the correct citations in LaTeX. Some examples of how to write the citations in LaTeX for the various bibliography websites are given in the table below. Essentially, all the citations always start with the (first) name of the website and followed by some parts of the URL path.

| Website Name  | Website URL | Citation |
| :---: | :---: | :--- |
| arXiv | https://arxiv.org/abs/2212.04173 | \cite{Arxiv:2212.04173} |
| | https://arxiv.org/abs/0801.0003 | \cite{Arxiv:0801.0003} |
| | https://arxiv.org/abs/2207.00004 | \cite{Arxiv:2207.00004} |
| BASE | https://www.base-search.net/Record/8f4c0a214b8d4ab0307ea8b0587c9d11fe28eaba0fb27fb35af4c6f9abf8aa31 | \cite{BASE:8f4c0a214b8d4ab0307ea8b0587c9d11fe28eaba0fb27fb35af4c6f9abf8aa31} |
| | https://www.base-search.net/Record/1e1050c7a4a38dca5f52f268d442b9484fd6ceae82acda0374408c6ed6c35b25 | \cite{BASE:1e1050c7a4a38dca5f52f268d442b9484fd6ceae82acda0374408c6ed6c35b25} |
| Cogprints | https://web-archive.southampton.ac.uk/cogprints.org/7736/ | \cite{Cogprints:7336/BibTeX/cogprints-eprint-7336} |
| | https://web-archive.southampton.ac.uk/cogprints.org/120/ | \cite{Cogprints:120/BibTeX/cogprints-eprint-120} |
| DBLP | https://dblp.org/rec/journals/cacm/Dijkstra68a.html?view=bibtex | \cite{DBLP:journals/cacm/Dijkstra68a} |
| | https://dblp.org/rec/conf/ttss/2013.html?view=bibtex | \cite{DBLP:conf/ttss/2013} |
| | https://dblp.org/rec/books/sp/Baumann23.html?view=bibtex | \cite{DBLP:books/sp/Baumann23} |
| | https://dblp.org/rec/reference/sp/0007T0S022.html?view=bibtex | \cite{DBLP:reference/sp/0007T0S022} |
| JSTOR | https://www.jstor.org/stable/10.1363/4103115 | \cite{JSTOR:10.1363/4103115} |
| | https://www.jstor.org/stable/24873277 | \cite{JSTOR:24873277} |
| | https://www.jstor.org/stable/resrep25198 | \cite{JSTOR:resrep25198} |
| | https://www.jstor.org/stable/j.ctv3znzfk | \cite{JSTOR:j.ctv3znzfk} |
| Microsoft Research | https://www.microsoft.com/en-us/research/publication/approximability-budgeted-allocations-improved-lower-bounds-submodular-welfare-maximization-gap/ | \cite{Microsoft:approximability-budgetedallocations-improvedlower-boundssubmodular-welfaremaximization-gap} |
| | https://www.microsoft.com/en-us/research/publication/citeseerx-ai-digital-library-search-engine/ | \cite{Microsoft:citeseerxai-digital-library-searchengine} |
| SpringerLink | https://link.springer.com/chapter/10.1007/978-3-031-04749-7_32 | \cite{Springer:978-3-031-04749-7_32?format=bibtex&flavour=citation} |
| | https://link.springer.com/article/10.1007/s10115-022-01737-x | \cite{Springer:s10115-022-01737-x?format=bibtex&flavour=citation} |

A LaTeX file named [example.tex](https://github.com/gretaisafantasy/get_bibtex/blob/main/example.tex) and the resulting PDF named [example.pdf](https://github.com/gretaisafantasy/get_bibtex/blob/main/example.pdf), which contain all of the citations above, are also available as a reference. 

Make sure that all of the TeX files that you want to use are in the same directory as the `get_bibtex` script before running it.

The software does not erase or modify existing BibTeX entries, so it will only automatically append the downloaded missing BibTeX records to the default BibTeX files, which are separate BibTeX files for each of the bibliographies according to the websites' name.

### Example

The BibTeX records for Cogprints will go to `cogprints.bib`, the BibTeX entries for DBLP will go to `dblp.bib`, and so on.

## Changing the Default BibTeX Input and Output Files

If you do not want to use the default BibTeX input and output files, there are two ways to change them. The first one is through the command line arguments and the second one is through a configuration file.

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

Some short files named [`sample.cfg`](https://github.com/gretaisafantasy/get_bibtex/blob/main/sample.cfg), [`sample.txt`](https://github.com/gretaisafantasy/get_bibtex/blob/main/sample.txt), and [`sample.json`](https://github.com/gretaisafantasy/get_bibtex/blob/main/sample.json) are also provided as examples. Keep in mind that besides the provided examples, other kinds of file formats will work as a configuration file too.

## License

Licensed under the MIT License.

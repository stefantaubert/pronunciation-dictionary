# pronunciation-dictionary

[![PyPI](https://img.shields.io/pypi/v/pronunciation-dictionary.svg)](https://pypi.python.org/pypi/pronunciation-dictionary)
[![PyPI](https://img.shields.io/pypi/pyversions/pronunciation-dictionary.svg)](https://pypi.python.org/pypi/pronunciation-dictionary)
[![MIT](https://img.shields.io/github/license/stefantaubert/pronunciation-dictionary.svg)](LICENSE)

Library to load and save pronunciation dictionaries (any language).

## Features

- Load dictionary from file or URL
  - Parsing of
    - line comments
    - pronunciation comments
    - numbers indicating alternative pronunciations for words
    - weights
  - Multiprocessing for faster deserialization
- Save dictionary to file
  - including numbers for alternative pronunciations
  - include weights
  - set word/weight/pronunciation separator
- Select pronunciation via
  - weight
  - highest/lowest weight
  - first/last
  - random
- Get phoneme set

## Roadmap

- Adding tests

## Example dictionaries and deserialization arguments

- [Montreal Forced Aligner dictionaries](https://github.com/MontrealCorpusTools/mfa-models/tree/main/dictionary)
  - `encoding: "UTF-8"`
- [CMU](https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict)
  - `encoding: "ISO-8859-1"`
  - `consider_numbers: True`
  - `consider_pronunciation_comments: True`
- [LibriSpeech](https://www.openslr.org/resources/11/librispeech-lexicon.txt)
  - `encoding: "UTF-8"`
- [Prosodylab](https://raw.githubusercontent.com/prosodylab/Prosodylab-Aligner/master/eng.dict)
- Old: [CMU 0.7b](http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b)
  - `encoding: "ISO-8859-1"`
  - `consider_comments: True`
  - `consider_numbers: True`

### Excerpt from CMU (as example)

```dict
a.d. EY2 D IY1
a.m. EY2 EH1 M
a.s EY1 Z
aaa T R IH2 P AH0 L EY1
aaberg AA1 B ER0 G
aachen AA1 K AH0 N
aachener AA1 K AH0 N ER0
aaker AA1 K ER0
aalborg AO1 L B AO0 R G # place, danish
aalborg(2) AA1 L B AO0 R G
```

## Installation

```sh
pip install pronunciation-dictionary --user
```

## Usage

```sh
from pronunciation_dictionary import load_dict, save_dict, MultiprocessingOptions, DeserializationOptions, SerializationOptions
```

## Citation

If you want to cite this repo, you can use this bibtex-entry:

```bibtex
@misc{tspd22,
  author = {Taubert, Stefan},
  title = {pronunciation-dictionary},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/stefantaubert/pronunciation-dictionary}}
}
```

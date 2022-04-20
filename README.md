# pronunciation-dictionary

[![PyPI](https://img.shields.io/pypi/v/pronunciation-dictionary.svg)](https://pypi.python.org/pypi/pronunciation-dictionary)
[![PyPI](https://img.shields.io/pypi/pyversions/pronunciation-dictionary.svg)](https://pypi.python.org/pypi/pronunciation-dictionary)
[![MIT](https://img.shields.io/github/license/stefantaubert/pronunciation-dictionary.svg)](LICENSE)

Library and CLI to load/save/modify pronunciation dictionaries (any language).

## Features

- Export vocabulary
- Export phoneme set
- Merge multiple pronunciation dictionaries
- Extract subset of pronunciation dictionary
- Remove characters from vocabulary
- Remove phonemes from pronunciations
- Change formatting
- Select single pronunciation per word

## Roadmap

- Adding tests
- Implementation of printing of statistics
- Implementation of phoneme mapping, e.g., mapping ARPAbet to IPA

## Example dictionaries and deserialization arguments

- [Montreal Forced Aligner dictionaries](https://github.com/MontrealCorpusTools/mfa-models/tree/main/dictionary)
  - `--deserialization-encoding "UTF-8"`
- [CMU](https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict)
  - `--deserialization-encoding "ISO-8859-1"`
  - `--consider-numbers`
  - `--consider-pronunciation-comments`
- [LibriSpeech](https://www.openslr.org/resources/11/librispeech-lexicon.txt)
  - `--deserialization-encoding "UTF-8"`
- [Prosodylab](https://raw.githubusercontent.com/prosodylab/Prosodylab-Aligner/master/eng.dict)
- Old: [CMU 0.7b](http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b)
  - `--deserialization-encoding "ISO-8859-1"`
  - `--consider-comments`
  - `--consider-numbers`

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
pronunciation-dictionary-cli
```

## Citation

If you want to cite this repo, you can use this bibtex-entry:

```bibtex
@misc{tapr22,
  author = {Taubert, Stefan},
  title = {pronunciation-dictionary},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/stefantaubert/pronunciation-dictionary}}
}
```

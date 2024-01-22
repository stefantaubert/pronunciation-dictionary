# pronunciation-dictionary

[![PyPI](https://img.shields.io/pypi/v/pronunciation-dictionary.svg)](https://pypi.python.org/pypi/pronunciation-dictionary)
[![PyPI](https://img.shields.io/pypi/pyversions/pronunciation-dictionary.svg)](https://pypi.python.org/pypi/pronunciation-dictionary)
[![MIT](https://img.shields.io/github/license/stefantaubert/pronunciation-dictionary.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/wheel/pronunciation-dictionary.svg)](https://pypi.python.org/pypi/pronunciation-dictionary/#files)
![PyPI](https://img.shields.io/pypi/implementation/pronunciation-dictionary.svg)
[![PyPI](https://img.shields.io/github/commits-since/stefantaubert/pronunciation-dictionary/latest/master.svg)](https://github.com/stefantaubert/pronunciation-dictionary/compare/v0.0.6...master)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7386813.svg)](https://doi.org/10.5281/zenodo.7386813)

Library to save and load pronunciation dictionaries (language-independent).

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
  - first/last
  - longest/shortest
  - highest/lowest weight
  - random
  - weight
- Get phoneme set

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

### Example

```py
from pathlib import Path

from pronunciation_dictionary import (DeserializationOptions, 
  MultiprocessingOptions, SerializationOptions, 
  get_phoneme_set, load_dict_from_url, save_dict)

dictionary = load_dict_from_url(
  "https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict",
  "ISO-8859-1",
  DeserializationOptions(False, True, True, False),
  MultiprocessingOptions(4, None, 10000)
)

phoneme_set = get_phoneme_set(dictionary)

print(phoneme_set)
# {'Z', 'EY1', 'AH0', 'F', 'AE0', 'UW0', 'CH', 'G', 'V', 'AY1', 'AO2', 'ZH', 'AA1', 'IY1', 'AW0', 'T', 'TH', 'AY2', 'DH', 'S', 'W', 'ER1', 'AA2', 'AE2', 'AE1', 'AW1', 'UW1', 'AH1', 'Y', 'EY2', 'AO0', 'OW2', 'OY2', 'IY2', 'JH', 'N', 'NG', 'P', 'IH2', 'M', 'OW0', 'L', 'UH1', 'IY0', 'EY0', 'HH', 'IH0', 'SH', 'AH2', 'AW2', 'EH2', 'OW1', 'D', 'R', 'IH1', 'AO1', 'B', 'UH2', 'UH0', 'ER0', 'UW2', 'ER2', 'EH0', 'AY0', 'AA0', 'EH1', 'OY1', 'OY0', 'K'}

pronunciations_distmantle = dictionary.get("dismantle")

for pronunciation, weight in pronunciations_distmantle.items():
  print(pronunciation, weight)
# ('D', 'IH0', 'S', 'M', 'AE1', 'N', 'T', 'AH0', 'L') 1.0
# ('D', 'IH0', 'S', 'M', 'AE1', 'N', 'AH0', 'L') 1.0

save_dict(dictionary, Path("/tmp/cmu.dict"), "UTF-8",
          SerializationOptions("DOUBLE-SPACE", False, False))
```

```sh
head /tmp/cmu.dict
# 'bout  B AW1 T
# 'cause  K AH0 Z
# 'course  K AO1 R S
# 'cuse  K Y UW1 Z
# 'em  AH0 M
# 'frisco  F R IH1 S K OW0
# 'gain  G EH1 N
# 'kay  K EY1
# 'm  AH0 M
# 'n  AH0 N
```

## Roadmap

- replace `SerializationOptions`, `DeserializationOptions` and `MultiprocessingOptions` with parameters
- add default parameter values
- add more tests

## Development setup

```sh
# update
sudo apt update
# install Python 3.8, 3.9, 3.10 & 3.11 for ensuring that tests can be run
sudo apt install python3-pip \
  python3.8 python3.8-dev python3.8-distutils python3.8-venv \
  python3.9 python3.9-dev python3.9-distutils python3.9-venv \
  python3.10 python3.10-dev python3.10-distutils python3.10-venv \
  python3.11 python3.11-dev python3.11-distutils python3.11-venv
# install pipenv for creation of virtual environments
python3.8 -m pip install pipenv --user

# check out repo
git clone https://github.com/stefantaubert/pronunciation-dictionary.git
cd pronunciation-dictionary
# create virtual environment
python3.8 -m pipenv install --dev
```

## Running the tests

```sh
# first install the tool like in "Development setup"
# then, navigate into the directory of the repo (if not already done)
cd pronunciation-dictionary
# activate environment
python3.8 -m pipenv shell
# run tests
tox
```

Final lines of test result output:

```log
  py38: commands succeeded
  py39: commands succeeded
  py310: commands succeeded
  py311: commands succeeded
  congratulations :)
```

## License

MIT License

## Acknowledgments

Funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) – Project-ID 416228727 – CRC 1410

## Citation

If you want to cite this repo, you can use this BibTeX-entry generated by GitHub (see *About => Cite this repository*).

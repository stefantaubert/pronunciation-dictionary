import random
from collections import OrderedDict
from multiprocessing import cpu_count
from pathlib import Path
from typing import List
from urllib.request import urlopen

from ordered_set import OrderedSet

from pronunciation_dictionary.parser import (LineParsingOptions,
                                             MultiprocessingOptions,
                                             parse_lines)
from pronunciation_dictionary.types import (Pronunciation, PronunciationDict,
                                            Pronunciations, Symbol, Word)

DEFAULT_OPTS = LineParsingOptions(True, True, True, False)
DEFAULT_MP_OPTS = MultiprocessingOptions(cpu_count(), None, 100000)


def get_dict_from_lines(lines: List[str], options: LineParsingOptions = DEFAULT_OPTS, mp_options: MultiprocessingOptions = DEFAULT_MP_OPTS) -> PronunciationDict:
  if not isinstance(lines, list):
    raise ValueError("Parameter 'lines' needs to be of type 'List[str]'!")
  for line in lines:
    if not isinstance(line, str):
      raise ValueError("Parameter 'lines' needs to have entries of type 'List[str]'!")
  validate_line_parsing_options(options)
  validate_mp_options(mp_options)
  result = parse_lines(lines, options, mp_options)
  return result


def get_dict_from_file(path: Path, encoding: str, options: LineParsingOptions = DEFAULT_OPTS, mp_options: MultiprocessingOptions = DEFAULT_MP_OPTS) -> PronunciationDict:
  validate_line_parsing_options(options)
  validate_mp_options(mp_options)
  try:
    text = path.read_text(encoding)
  except Exception as ex:
    raise ValueError("Path is invalid!") from ex
  lines = text.splitlines()
  result = parse_lines(lines, options, mp_options)
  return result


def get_dict_from_url(url: Path, encoding: str, options: LineParsingOptions = DEFAULT_OPTS, mp_options: MultiprocessingOptions = DEFAULT_MP_OPTS) -> PronunciationDict:
  validate_line_parsing_options(options)
  validate_mp_options(mp_options)
  try:
    lines = read_lines_from_url(url, encoding)
  except Exception as ex:
    raise ValueError("Url is invalid!") from ex
  result = parse_lines(lines, options, mp_options)
  return result


def validate_line_parsing_options(options: LineParsingOptions) -> None:
  if not isinstance(options.consider_comments, bool):
    raise ValueError("Parameter 'consider_comments' needs to be of type 'bool'!")
  if not isinstance(options.consider_pronunciation_comments, bool):
    raise ValueError("Parameter 'consider_pronunciation_comments' needs to be of type 'bool'!")
  if not isinstance(options.consider_weights, bool):
    raise ValueError("Parameter 'consider_weights' needs to be of type 'bool'!")
  if not isinstance(options.consider_word_nrs, bool):
    raise ValueError("Parameter 'consider_word_nrs' needs to be of type 'bool'!")


def validate_mp_options(mp_options: MultiprocessingOptions) -> None:
  if not (isinstance(mp_options.chunksize, int) and mp_options.chunksize > 0):
    raise ValueError("Parameter 'chunksize' is invalid!")
  if not (mp_options.maxtasksperchild is None or (isinstance(mp_options.maxtasksperchild, int) and mp_options.maxtasksperchild > 0)):
    raise ValueError("Parameter 'maxtasksperchild' is invalid!")
  if not (isinstance(mp_options.n_jobs, int) and mp_options.n_jobs > 0):
    raise ValueError("Parameter 'n_jobs' is invalid!")


def read_lines_from_url(url: str, encoding: str) -> List[str]:
  with urlopen(url) as url_content:
    result = [line.decode(encoding) for line in url_content]
  return result


def get_weighted_pronunciation(word: str, dictionary: PronunciationDict) -> Pronunciation:
  if not (isinstance(word, str)):
    raise ValueError("Parameter 'word' needs to be of type 'str'!")
  validate_dictionary(dictionary)
  if not (word in dictionary):
    raise ValueError("Word does not exist in dictionary!")
  pronunciations = dictionary[word]
  if not (isinstance(pronunciations, OrderedDict)):
    raise ValueError("The dictionary is invalid!")
  if not (len(pronunciations) > 0):
    raise ValueError("The dictionary is invalid!")
  result = random.choices(tuple(pronunciations.keys()), tuple(pronunciations.values()), k=1)[0]
  return result


def validate_dictionary(dictionary: PronunciationDict) -> None:
  if not (isinstance(dictionary, OrderedDict)):
    raise ValueError("Parameter 'dictionary' needs to be of type 'OrderedDict'!")


def get_first_pronunciation(word: str, dictionary: PronunciationDict) -> Pronunciation:
  if not (isinstance(word, str)):
    raise ValueError("Parameter 'word' needs to be of type 'str'!")
  validate_dictionary(dictionary)
  if not (word in dictionary):
    raise ValueError("Word does not exist in dictionary!")
  pronunciations = dictionary[word].keys()
  if not (len(pronunciations) > 0):
    raise ValueError("The dictionary is invalid!")
  result = next(iter(pronunciations))
  return result


def get_vocabular(dictionary: PronunciationDict) -> OrderedSet[Word]:
  result = OrderedSet(dictionary.keys())
  return result


def get_phoneme_set(dictionary: PronunciationDict) -> OrderedSet[Symbol]:
  all_symbols = (
    symbol
    for pronunciations_weight_pair in dictionary.values()
    for pronunciation in pronunciations_weight_pair.keys()
    for symbol in pronunciation
  )
  unique_symbols = set(all_symbols)
  unique_symbols = OrderedSet(sorted(unique_symbols))
  return unique_symbols


def convert_weights_to_probabilities_dict(dictionary: PronunciationDict) -> None:
  for pronunciations in dictionary.values():
    convert_weights_to_probabilities(pronunciations)


def convert_weights_to_probabilities(pronunciations: Pronunciations) -> None:
  if not isinstance(pronunciations, OrderedDict):
    raise ValueError("Parameter 'pronunciations' is invalid!")
  sum_probs = sum(pronunciations.values())
  for pronunciation, prob in pronunciations.items():
    normed_prob = prob / sum_probs
    if prob != normed_prob:
      pronunciations[pronunciation] = normed_prob

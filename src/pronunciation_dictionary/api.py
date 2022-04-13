import random
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional
from urllib.request import urlopen

from pronunciation_dictionary.deserialization import (DeserializationOptions,
                                                      MultiprocessingOptions, parse_lines)
from pronunciation_dictionary.io import load_dict, save_dict
from pronunciation_dictionary.serialization import SerializationOptions
from pronunciation_dictionary.types import Pronunciation, PronunciationDict
from pronunciation_dictionary.words_casing_adjustment import change_casing


def save_dict_to_file(dictionary: PronunciationDict, path: Path, encoding: str, options: SerializationOptions):
  validate_dictionary(dictionary)
  save_dict(dictionary, path, encoding, options)


def change_word_casing(dictionary: PronunciationDict, mode: str, ratio: float, mp_options: MultiprocessingOptions) -> None:
  validate_dictionary(dictionary)
  change_casing(dictionary, mode, ratio, mp_options)


def get_dict_from_file(path: Path, encoding: str, options: DeserializationOptions, mp_options: MultiprocessingOptions) -> PronunciationDict:
  validate_line_parsing_options(options)
  validate_mp_options(mp_options)
  return load_dict(path, encoding, options, mp_options)


def get_dict_from_url(url: Path, encoding: str, options: DeserializationOptions, mp_options: MultiprocessingOptions) -> PronunciationDict:
  validate_line_parsing_options(options)
  validate_mp_options(mp_options)
  lines = read_lines_from_url(url, encoding)
  result = parse_lines(lines, options, mp_options)
  return result


def get_dict_from_lines(lines: List[str], options: DeserializationOptions, mp_options: MultiprocessingOptions) -> PronunciationDict:
  if not isinstance(lines, list):
    raise ValueError("Parameter 'lines' needs to be of type 'List[str]'!")
  for line in lines:
    if not isinstance(line, str):
      raise ValueError("Parameter 'lines' needs to have entries of type 'List[str]'!")
  validate_line_parsing_options(options)
  validate_mp_options(mp_options)
  result = parse_lines(lines, options, mp_options)
  return result


def validate_line_parsing_options(options: DeserializationOptions) -> None:
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


def get_weighted_pronunciation(word: str, dictionary: PronunciationDict, seed: Optional[int]) -> Pronunciation:
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
  if seed is not None and not isinstance(seed, int):
    raise ValueError("Seed needs to be of type 'int'!")
  if seed is not None:
    random.seed(seed)
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

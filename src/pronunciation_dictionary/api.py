import random
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional
from urllib.request import urlopen

from pronunciation_dictionary.deserialization import (DeserializationOptions,
                                                      MultiprocessingOptions, deserialize)
from pronunciation_dictionary.io import load_dict, save_dict
from pronunciation_dictionary.serialization import SerializationOptions
from pronunciation_dictionary.types import Pronunciation, PronunciationDict
from pronunciation_dictionary.validation import validate_dictionary
from pronunciation_dictionary.words_casing_adjustment import change_word_casing


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

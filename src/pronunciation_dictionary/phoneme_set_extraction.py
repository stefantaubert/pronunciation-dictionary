from typing import Set

from pronunciation_dictionary.types import PronunciationDict, Symbol
from pronunciation_dictionary.validation import validate_dictionary


def get_phoneme_set(dictionary: PronunciationDict) -> Set[Symbol]:
  try:
    validate_dictionary(dictionary)
  except ValueError as error:
    raise ValueError("dictionary", error.args[1]) from error

  unique_symbols = {
    symbol
    for pronunciations_weight_pair in dictionary.values()
    for pronunciation in pronunciations_weight_pair.keys()
    for symbol in pronunciation
  }

  return unique_symbols

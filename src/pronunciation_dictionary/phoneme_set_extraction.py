from typing import Set

from pronunciation_dictionary.types import PronunciationDict, Symbol
from pronunciation_dictionary.validation import validate_dictionary


def get_phoneme_set(dictionary: PronunciationDict) -> Set[Symbol]:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")

  unique_symbols = {
    symbol
    for pronunciations_weight_pair in dictionary.values()
    for pronunciation in pronunciations_weight_pair.keys()
    for symbol in pronunciation
  }

  return unique_symbols

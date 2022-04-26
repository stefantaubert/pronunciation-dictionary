from typing import Set

from pronunciation_dictionary.types import PronunciationDict, Word
from pronunciation_dictionary.validation import validate_dictionary


def get_vocabulary(dictionary: PronunciationDict) -> Set[Word]:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  result = set(dictionary.keys())
  return result

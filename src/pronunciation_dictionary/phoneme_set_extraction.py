from ordered_set import OrderedSet

from pronunciation_dictionary.types import PronunciationDict, Symbol
from pronunciation_dictionary.validation import validate_dictionary


def get_phoneme_set(dictionary: PronunciationDict) -> OrderedSet[Symbol]:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")

  all_symbols = (
    symbol
    for pronunciations_weight_pair in dictionary.values()
    for pronunciation in pronunciations_weight_pair.keys()
    for symbol in pronunciation
  )
  unique_symbols = set(all_symbols)
  unique_symbols = OrderedSet(sorted(unique_symbols))
  return unique_symbols

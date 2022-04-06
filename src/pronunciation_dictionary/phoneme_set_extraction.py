from pronunciation_dictionary.types import (Pronunciation, PronunciationDict,
                                            Pronunciations, Symbol, Word)
from ordered_set import OrderedSet


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

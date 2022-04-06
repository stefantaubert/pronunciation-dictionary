from pronunciation_dictionary.types import (Pronunciation, PronunciationDict,
                                            Pronunciations, Symbol, Word)
from ordered_set import OrderedSet

def get_vocabular(dictionary: PronunciationDict) -> OrderedSet[Word]:
  result = OrderedSet(dictionary.keys())
  return result

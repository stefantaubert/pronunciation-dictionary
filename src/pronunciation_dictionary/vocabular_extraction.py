from ordered_set import OrderedSet

from pronunciation_dictionary.types import PronunciationDict, Word


def get_vocab(dictionary: PronunciationDict) -> OrderedSet[Word]:
  result = OrderedSet(dictionary.keys())
  return result

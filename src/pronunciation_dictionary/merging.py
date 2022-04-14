from ordered_set import OrderedSet

from pronunciation_dictionary import PronunciationDict
from pronunciation_dictionary.common import merge_pronunciations


def merge_dictionary_files(resulting_dictionary: PronunciationDict, dictionary_instance: PronunciationDict, duplicate_handling: str, ratio: float) -> bool:
  if duplicate_handling == "add":
    dictionary_add_new(resulting_dictionary, dictionary_instance)
  elif duplicate_handling == "replace":
    dictionary_replace(resulting_dictionary, dictionary_instance)
  elif duplicate_handling == "extend":
    assert ratio is not None
    dictionary_extend(resulting_dictionary, dictionary_instance, ratio)
  else:
    assert False


def dictionary_replace(dictionary1: PronunciationDict, dictionary2: PronunciationDict) -> None:
  dictionary1.update(dictionary2)


def dictionary_add_new(dictionary1: PronunciationDict, dictionary2: PronunciationDict) -> None:
  new_keys = OrderedSet(dictionary2.keys()).difference(dictionary1.keys())
  for key in new_keys:
    assert key not in dictionary1
    dictionary1[key] = dictionary2[key]


def dictionary_extend(dictionary1: PronunciationDict, dictionary2: PronunciationDict, ratio: float) -> None:
  keys = OrderedSet(dictionary2.keys())
  same_keys = keys.intersection(dictionary1.keys())
  new_keys = keys.difference(dictionary1.keys())

  for key in same_keys:
    assert key in dictionary1
    merge_pronunciations(dictionary1[key], dictionary2[key], ratio)

  for key in new_keys:
    assert key not in dictionary1
    dictionary1[key] = dictionary2[key]

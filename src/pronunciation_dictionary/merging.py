from typing import Optional

from ordered_set import OrderedSet

from pronunciation_dictionary import PronunciationDict
from pronunciation_dictionary.common import merge_pronunciations
from pronunciation_dictionary.validation import validate_dictionary, validate_ratio


def __validate_mode(mode: str) -> Optional[str]:
  if mode not in ["add", "replace", "extend"]:
    return "Invalid value!"
  return None


def merge_dictionaries(dictionary: PronunciationDict, other_dictionary: PronunciationDict, mode: str, ratio: float) -> bool:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := validate_dictionary(other_dictionary):
    raise ValueError(f"Parameter 'other_dictionary': {msg}")
  if msg := __validate_mode(mode):
    raise ValueError(f"Parameter 'mode': {msg}")
  if msg := validate_ratio(ratio):
    raise ValueError(f"Parameter 'ratio': {msg}")

  if mode == "add":
    dictionary_add_new(dictionary, other_dictionary)
  elif mode == "replace":
    dictionary_replace(dictionary, other_dictionary)
  elif mode == "extend":
    assert ratio is not None
    dictionary_extend(dictionary, other_dictionary, ratio)
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

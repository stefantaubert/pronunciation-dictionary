from collections import OrderedDict
from typing import Iterable
from typing import OrderedDict as ODType

from ordered_set import OrderedSet

from pronunciation_dictionary import PronunciationDict
from pronunciation_dictionary.types import Word


def select_subset_dictionary(dictionary_instance: PronunciationDict, vocabulary: OrderedSet[Word], consider_case: bool) -> OrderedSet[Word]:
  if consider_case:
    oov_voc = select_subset_dictionary_casing(dictionary_instance, vocabulary)
  else:
    oov_voc = select_subset_dictionary_ignore_casing(dictionary_instance, vocabulary)
  return oov_voc


def select_subset_dictionary_casing(dictionary: PronunciationDict, vocabulary: OrderedSet[Word]) -> OrderedSet[Word]:
  existing_vocabulary = OrderedSet(dictionary.keys())
  # copy_voc = vocabulary.intersection(existing_vocabulary)
  remove_voc = existing_vocabulary.difference(vocabulary)
  oov_voc = vocabulary.difference(existing_vocabulary)

  for word in remove_voc:
    assert word in dictionary
    dictionary.pop(word)

  return oov_voc


def get_mapping(words: Iterable[Word]) -> ODType[Word, OrderedSet[Word]]:
  result: ODType[Word, OrderedSet[Word]] = OrderedDict()
  for word in words:
    word_lower = word.lower()
    if word_lower not in result:
      result[word_lower] = OrderedSet((word,),)
    else:
      result[word_lower].add(word)
  return result


def select_subset_dictionary_ignore_casing(dictionary: PronunciationDict, vocabulary: OrderedSet[Word]) -> OrderedSet[Word]:
  dict_word_map = get_mapping(dictionary.keys())
  voc_word_map = get_mapping(vocabulary)

  dict_vocabulary = OrderedSet(dict_word_map.keys())
  voc_vocabulary = OrderedSet(voc_word_map.keys())

  unused_dict_voc = dict_vocabulary.difference(voc_vocabulary)
  oov_voc = voc_vocabulary.difference(dict_vocabulary)

  unused_dict_voc_actual = OrderedSet(
    word
    for word_lower in unused_dict_voc
    for word in dict_word_map[word_lower]
  )

  oov_voc_actual = OrderedSet(
    word
    for word_lower in oov_voc
    for word in voc_word_map[word_lower]
  )

  for word in unused_dict_voc_actual:
    assert word in dictionary
    dictionary.pop(word)

  return oov_voc_actual

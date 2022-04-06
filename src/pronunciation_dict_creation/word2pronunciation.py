from typing import (Callable, Generator, List, Optional,
                    Set, Tuple)
from pronunciation_dict_parser import Pronunciation, Symbol

HYPHEN = "-"


def symbols_join(list_of_pronunciations: List[Pronunciation], join_symbol: Symbol) -> None:
  res = []
  for i, word in enumerate(list_of_pronunciations):
    res.extend(word)
    is_last_word = i == len(list_of_pronunciations) - 1
    if not is_last_word:
      res.append(join_symbol)
  return tuple(res)


def pronunciation_lower(pronunciation: Pronunciation) -> Pronunciation:
  result = tuple(symbol.lower() for symbol in pronunciation)
  return result

def get_pronunciation_from_word(word: Pronunciation, trim_symbols: Set[Symbol], split_on_hyphen: bool, get_pronunciation: Callable[[Pronunciation], Pronunciation], consider_annotation: bool, annotation_split_symbol: Optional[Symbol]) -> Pronunciation:
  if consider_annotation and len(annotation_split_symbol) != 1:
    raise ValueError("annotation_split_symbol has to be a string of length 1.")
  if consider_annotation and is_annotation(word, annotation_split_symbol):
    annotations = get_annotation_content(word, annotation_split_symbol)
    return annotations
  new_pronun = not_annotation_word2pronunciation(
    word, trim_symbols, split_on_hyphen, get_pronunciation)
  return new_pronun


def is_annotation(word: Pronunciation, annotation_split_symbol: Symbol) -> bool:
  # TODO fixed bug if word is ()
  return len(word) > 0 and word[0] == annotation_split_symbol and word[-1] == annotation_split_symbol


def get_annotation_content(annotation: Pronunciation, annotation_split_symbol: Symbol) -> Pronunciation:
  assert is_annotation(annotation, annotation_split_symbol)
  resulting_parts = []
  current_merge = ""
  for symbol in annotation[1:-1]:
    if symbol == annotation_split_symbol:
      if current_merge != "":
        resulting_parts.append(current_merge)
        current_merge = ""
    else:
      current_merge += symbol
  if current_merge != "":
    resulting_parts.append(current_merge)
  return tuple(resulting_parts)


def not_annotation_word2pronunciation(word: Pronunciation, trim_symbols: Set[Symbol], split_on_hyphen: bool, get_pronunciation: Callable[[Pronunciation], Pronunciation]) -> Pronunciation:
  trim_beginning, actual_word, trim_end = trim_word(word, trim_symbols)
  pronunciations = []
  if len(trim_beginning) > 0:
    pronunciations.append(trim_beginning)
  if len(actual_word) > 0:
    actual_pronunciation = add_pronunciation_for_word(
      actual_word, split_on_hyphen, get_pronunciation)
    pronunciations.append(actual_pronunciation)
  if len(trim_end) > 0:
    pronunciations.append(trim_end)
  complete_pronunciation = pronunciation_list_to_pronunciation(pronunciations)
  return complete_pronunciation


def add_pronunciation_for_word(word: Pronunciation, split_on_hyphen: bool, get_pronunciation: Callable[[Pronunciation], Pronunciation]) -> Pronunciation:
  if split_on_hyphen:
    return add_pronunciation_for_splitted_word(word, get_pronunciation)
  result = get_pronunciation(word)
  if not isinstance(result, tuple):
    raise Exception("get_pronunciation needs to return a tuple.")
  return result


def add_pronunciation_for_splitted_word(word: Pronunciation, get_pronunciation: Callable[[Pronunciation], Pronunciation]) -> Pronunciation:
  splitted_words = symbols_split_iterable(word, HYPHEN)
  pronunciations = []
  for single_word in splitted_words:
    if single_word != ():
      item = get_pronunciation(single_word)
      if not isinstance(item, tuple):
        raise Exception("get_pronunciation needs to return a tuple.")
    else:
      item = ()
    pronunciations.append(item)
  pronunciations_with_hyphens = symbols_join(pronunciations, HYPHEN)
  return pronunciations_with_hyphens


def symbols_split_iterable(sentence_symbols: Pronunciation, split_symbols: Set[Symbol]) -> Generator[Pronunciation, None, None]:
  if len(sentence_symbols) == 0:
    return
  current = []
  for symbol in sentence_symbols:
    if symbol in split_symbols:
      yield tuple(current)
      current = []
    else:
      current.append(symbol)
  yield tuple(current)


def trim_word(word: Pronunciation, trim_symbols: Set[Symbol]) -> Tuple[Pronunciation, Pronunciation, Pronunciation]:
  beginning, remaining_word = remove_trim_symbols_at_beginning(word, trim_symbols)
  actual_word, end = remove_trim_symbols_at_end(remaining_word, trim_symbols)
  return beginning, actual_word, end


def remove_trim_symbols_at_end(word: Pronunciation, trim_symbols: Set[Symbol]) -> Tuple[Pronunciation, Pronunciation]:
  word_reversed = word[::-1]
  end_reversed, remaining_word_reversed = remove_trim_symbols_at_beginning(
    word_reversed, trim_symbols)
  end = end_reversed[::-1]
  remaining_word = remaining_word_reversed[::-1]
  return remaining_word, end


def remove_trim_symbols_at_beginning(word: Pronunciation, trim_symbols: Set[Symbol]) -> Tuple[Pronunciation, Pronunciation]:
  beginning = []
  for element in word:
    if element in trim_symbols:
      beginning.append(element)
    else:
      break
  beginning = tuple(beginning)
  remaining_word = word[len(beginning):]
  return beginning, remaining_word


def pronunciation_list_to_pronunciation(pronunciation_list: List[Pronunciation]) -> Pronunciation:
  for element in pronunciation_list:
    assert isinstance(element, tuple)
  flattened_pronunciation_list = tuple(
    pronunciation for pronunciation_tuple in pronunciation_list for pronunciation in pronunciation_tuple)
  return flattened_pronunciation_list

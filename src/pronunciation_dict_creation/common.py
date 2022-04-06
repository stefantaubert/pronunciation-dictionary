from pronunciation_dict_parser import convert_weights_to_probabilities
from collections import OrderedDict
from logging import getLogger
from pathlib import Path
from pronunciation_dict_parser import PronunciationDict
from pronunciation_dict_parser import Symbol
import argparse
from argparse import ArgumentParser
from multiprocessing import cpu_count
from dataclasses import dataclass
from typing import List, Literal, Optional, Set, Tuple
from pronunciation_dict_parser import PronunciationDict, Symbol, Word, Pronunciations, get_dict_from_file, LineParsingOptions, MultiprocessingOptions
from ordered_set import OrderedSet
from pronunciation_dict_creation.argparse_helper import get_optional, parse_codec, parse_positive_integer


DEFAULT_ENCODING = "UTF-8"
DEFAULT_N_JOBS = cpu_count()
DEFAULT_CHUNKSIZE = 1000
DEFAULT_MAXTASKSPERCHILD = None


PROG_SYMBOL_SEP = " "
PROG_WORD_SEP = "  "
PROG_INCLUDE_COUNTER = False
PROG_EMPTY_SYMBOL = ""
PROG_INCL_WEIGHTS = True
PROG_ONLY_FIRST = False
PROG_ENCODING = "UTF-8"
PROG_CONS_COMMENTS = False
PROG_CONS_WORD_NRS = False
PROG_CONS_PRON_COMMENTS = False
PROG_CONS_WEIGHTS = True


@dataclass()
class DefaultParameters():
  vocabulary: OrderedSet[Word]
  consider_annotations: bool
  annotation_split_symbol: Optional[str]
  # handle_duplicates: Literal["ignore", "add", "replace"]
  split_on_hyphen: bool
  trim_symbols: Set[Symbol]
  n_jobs: int
  maxtasksperchild: Optional[int]
  chunksize: int


def get_dictionary(pronunciations_to_i: Pronunciations, words_to_lookup: OrderedSet[Word]) -> Tuple[PronunciationDict, OrderedSet[Word]]:
  resulting_dict = OrderedDict()
  unresolved_words = OrderedSet()
  for i, pronunciations in pronunciations_to_i:
    word = words_to_lookup[i]
    if pronunciations is None:
      unresolved_words.add(word)
      continue
    assert word not in resulting_dict
    resulting_dict[word] = pronunciations
  return resulting_dict, unresolved_words


def update_dictionary(target_dictionary: PronunciationDict, pronunciations_to_i: Pronunciations, words_to_lookup: OrderedSet[Word], handle_duplicates: Literal["ignore", "add", "replace"]) -> OrderedSet[Word]:
  unresolved_words = OrderedSet()
  for i, pronunciations in pronunciations_to_i:
    word = words_to_lookup[i]
    if pronunciations is None:
      unresolved_words.add(unresolved_words)
      continue
    if handle_duplicates == "ignore":
      assert word not in target_dictionary
      target_dictionary[word] = pronunciations
    elif handle_duplicates == "replace":
      target_dictionary[word] = pronunciations
    elif handle_duplicates == "add":
      if word not in target_dictionary:
        target_dictionary[word] = pronunciations
      else:
        target_dictionary[word].update(pronunciations)
    else:
      assert False
  return unresolved_words


DEFAULT_PUNCTUATION = list(OrderedSet(sorted((
  "!", "\"", "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "{", "}", "~", "`",
  "、", "。", "？", "！", "：", "；", "।", "¿", "¡", "【", "】", "，", "…", "‥", "「", "」", "『", "』", "〝", "〟", "″", "⟨", "⟩", "♪", "・", "‹", "›", "«", "»", "～", "′", "“", "”"
))))


def add_encoding_argument(parser: ArgumentParser, variable: str, help_str: str) -> None:
  parser.add_argument(variable, type=parse_codec, metavar='CODEC',
                      help=help_str + "; see all available codecs at https://docs.python.org/3.8/library/codecs.html#standard-encodings", default=DEFAULT_ENCODING)


def add_n_jobs_argument(parser: ArgumentParser) -> None:
  parser.add_argument("-j", "--n-jobs", metavar='N', type=int,
                      choices=range(1, cpu_count() + 1), default=DEFAULT_N_JOBS, help="amount of parallel cpu jobs")


def add_chunksize_argument(parser: ArgumentParser, target: str = "words", default: int = DEFAULT_CHUNKSIZE) -> None:
  parser.add_argument("-c", "--chunksize", type=parse_positive_integer, metavar="NUMBER",
                      help=f"amount of {target} to chunk into one job", default=default)


def add_maxtaskperchild_argument(parser: ArgumentParser) -> None:
  parser.add_argument("-m", "--maxtasksperchild", type=get_optional(parse_positive_integer), metavar="NUMBER",
                      help="amount of tasks per child", default=DEFAULT_MAXTASKSPERCHILD)


class ConvertToOrderedSetAction(argparse._StoreAction):
  def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Optional[List], option_string: Optional[str] = None):
    if values is not None:
      values = OrderedSet(values)
    super().__call__(parser, namespace, values, option_string)


def to_text(pronunciation_dict: PronunciationDict, parts_sep: Symbol = PROG_WORD_SEP, symbol_sep: Symbol = PROG_SYMBOL_SEP, include_counter: bool = PROG_INCLUDE_COUNTER, only_first_pronunciation: bool = PROG_ONLY_FIRST, empty_symbol: Symbol = PROG_EMPTY_SYMBOL, include_weights: bool = PROG_INCL_WEIGHTS) -> str:
  lines = []
  for word, pronunciations in pronunciation_dict.items():
    for counter, (pronunciation, weight) in enumerate(pronunciations.items(), start=1):
      if len(pronunciation) == 0 and len(empty_symbol) > 0:
        pronunciation = tuple(empty_symbol)
      counter_str = f"({counter})" if include_counter and counter > 1 else ""
      word_part = f"{word}{counter_str}{parts_sep}"
      weights_part = ""
      if include_weights:
        weights_part = f"{weight}{parts_sep}"
      pron_part = symbol_sep.join(pronunciation)
      line = f"{word_part}{weights_part}{pron_part}\n"
      lines.append(line)
      if only_first_pronunciation:
        break
  dict_content = "\n".join(lines)
  return dict_content


def try_save_dict(pronunciation_dict: PronunciationDict, path: Path, word_pronunciation_sep: Symbol = PROG_WORD_SEP, symbol_sep: Symbol = PROG_SYMBOL_SEP, include_counter: bool = PROG_INCLUDE_COUNTER, only_first_pronunciation: bool = PROG_ONLY_FIRST, empty_symbol: Symbol = PROG_EMPTY_SYMBOL, encoding: str = PROG_ENCODING, include_weights: bool = PROG_INCL_WEIGHTS) -> bool:
  dict_content = to_text(pronunciation_dict, word_pronunciation_sep, symbol_sep,
                         include_counter, only_first_pronunciation, empty_symbol, include_weights)
  path.parent.mkdir(parents=True, exist_ok=True)
  try:
    path.write_text(dict_content, encoding)
  except Exception as ex:
    return False
  return True


def try_load_dict(path: Path, encoding: str = PROG_ENCODING, consider_comments: bool = PROG_CONS_COMMENTS, consider_word_nrs: bool = PROG_CONS_WORD_NRS, consider_pronunciation_comments: bool = PROG_CONS_PRON_COMMENTS, consider_weights: bool = PROG_CONS_WEIGHTS, n_jobs: int = DEFAULT_N_JOBS, maxtasksperchild: Optional[int] = DEFAULT_MAXTASKSPERCHILD, chunksize: int = DEFAULT_CHUNKSIZE) -> Optional[PronunciationDict]:
  options = LineParsingOptions(consider_comments, consider_word_nrs,
                               consider_pronunciation_comments, consider_weights)
  mp_options = MultiprocessingOptions(n_jobs, maxtasksperchild, chunksize)
  try:
    result = get_dict_from_file(path, encoding, options, mp_options)
  except Exception as ex:
    return None
  return result


def merge_pronunciations(pronunciations1: Pronunciations, pronunciations2: Pronunciations, weights_ratio: float) -> None:
  assert pronunciations1 != pronunciations2
  assert 0 <= weights_ratio <= 1
  convert_weights_to_probabilities(pronunciations1)
  convert_weights_to_probabilities(pronunciations2)
  if weights_ratio != 1:
    for pronunciation1, weight1 in pronunciations1.items():
      if pronunciation1 not in pronunciations2:
        new_weight = weight1 * weights_ratio
        pronunciations1[pronunciation1] = new_weight

  for pronunciation2, weight2 in pronunciations2.items():
    new_weight2 = weight2 * (1 - weights_ratio)
    if pronunciation2 in pronunciations1:
      weight1 = pronunciations1[pronunciation2]
      new_weight1 = weight1 * weights_ratio
      new_weight = new_weight1 + new_weight2
    else:
      new_weight = new_weight2
    pronunciations1[pronunciation2] = new_weight


# def merge_equal_weight_sum(pronunciations1: Pronunciations, pronunciations2: Pronunciations, ratio: float) -> None:
#   assert sum(pronunciations1.values()) * ratio == sum(pronunciations2.values()) * (1 - ratio)
#   for pronunciation2, weight2 in pronunciations2.items():
#     if pronunciation2 in pronunciations1:
#       pronunciations1[pronunciation2] += weight2
#     else:
#       pronunciations1[pronunciations2] = weight2

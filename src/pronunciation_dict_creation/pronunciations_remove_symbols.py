from argparse import ArgumentParser
from collections import OrderedDict
from functools import partial
from logging import getLogger
from multiprocessing.pool import Pool
from pathlib import Path
from tempfile import gettempdir
from pronunciation_dict_parser import PronunciationDict, Symbol
from ordered_set import OrderedSet
from pronunciation_dict_creation.argparse_helper import parse_existing_file
from pronunciation_dict_creation.common import ConvertToOrderedSetAction, DEFAULT_PUNCTUATION, PROG_ENCODING, add_chunksize_argument, try_load_dict, try_save_dict

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from tqdm import tqdm
from functools import partial
from multiprocessing.pool import Pool
from typing import Optional, Set, Tuple
from pronunciation_dict_parser import PronunciationDict, Symbol, Word, Pronunciations
from ordered_set import OrderedSet
from pronunciation_dict_creation.argparse_helper import get_optional, parse_existing_file, parse_non_empty_or_whitespace, parse_path
from pronunciation_dict_creation.common import ConvertToOrderedSetAction, DEFAULT_PUNCTUATION, PROG_ENCODING, add_chunksize_argument, add_maxtaskperchild_argument, add_n_jobs_argument, try_save_dict


DEFAULT_EMPTY_WEIGHT = 1


def get_pronunciations_remove_symbols_parser(parser: ArgumentParser):
  default_removed_out = Path(gettempdir()) / "removed-words.txt"
  parser.description = "Remove symbols from pronunciations."
  parser.add_argument("dictionaries", metavar='dictionaries', type=parse_existing_file, nargs="+",
                      help="dictionary files", action=ConvertToOrderedSetAction)
  parser.add_argument("--symbols", type=str, metavar='SYMBOL', nargs='+',
                      help="remove these symbols from the pronunciations", action=ConvertToOrderedSetAction, default=DEFAULT_PUNCTUATION)
  parser.add_argument("--keep-empty", action="store_true",
                      help="if a pronunciation will be empty after removal, keep the corresponding word in the dictionary and assign the value of empty-symbol")
  parser.add_argument("--empty-symbol", type=get_optional(parse_non_empty_or_whitespace),
                      help="if keep-empty: assign this symbol to the word where no pronunciations result because of the symbol removal", default="sil")
  parser.add_argument("--removed-out", metavar="PATH", type=get_optional(parse_path),
                      help="write removed words (i.e., words that had no pronunciation anymore) to this file", default=default_removed_out)
  add_n_jobs_argument(parser)
  add_chunksize_argument(parser)
  add_maxtaskperchild_argument(parser)
  return remove_symbols_from_pronunciations


def remove_symbols_from_pronunciations(dictionaries: OrderedSet[Path], symbols: OrderedSet[Symbol], keep_empty: bool, empty_symbol: Optional[Symbol], removed_out: Optional[Path], n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> bool:
  assert len(dictionaries) > 0
  logger = getLogger(__name__)

  if keep_empty and empty_symbol is None:
    logger.error("An empty symbol needs to be supplied if keep_empty is true!")
    return False

  for dictionary_path in dictionaries:
    dictionary_instance = try_load_dict(dictionaries[0])
    if dictionary_instance is None:
      logger.error(f"Dictionary '{dictionary_path}' couldn't be read.")
      return False

    removed_words, changed_counter = remove_symbols(
      dictionary_instance, symbols, keep_empty, empty_symbol, n_jobs, maxtasksperchild, chunksize)

    if changed_counter == 0:
      logger.info("Didn't changed anything.")
      return True

    logger.info(f"Changed pronunciations of {changed_counter} word(s).")

    success = try_save_dict(dictionary_instance, dictionary_path)
    if not success:
      logger.error("Dictionary couldn't be written.")
      return False

    logger.info(f"Written dictionary to: {dictionary_path.absolute()}")

    if len(removed_words) > 0:
      logger.warning(f"{len(removed_words)} words were removed.")
      if removed_out is not None:
        content = "\n".join(removed_words)
        removed_out.parent.mkdir(parents=True, exist_ok=True)
        try:
          removed_out.write_text(content, "UTF-8")
        except Exception as ex:
          logger.error("Removed words output couldn't be created!")
          return False
        logger.info(f"Written removed words to: {removed_out.absolute()}")
    else:
      logger.info("No words were removed.")


def remove_symbols(dictionary: PronunciationDict, symbols: OrderedSet[Symbol], keep_empty: bool, empty_symbol: Optional[Symbol], n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> Tuple[OrderedSet[Word], int]:
  process_method = partial(
    process_get_pronunciation,
    symbols=symbols,
  )

  with Pool(
    processes=n_jobs,
    initializer=__init_pool_prepare_cache_mp,
    initargs=(dictionary,),
    maxtasksperchild=maxtasksperchild,
  ) as pool:
    entries = OrderedSet(dictionary.keys())
    iterator = pool.imap(process_method, entries, chunksize)
    pronunciations_to_i = list(tqdm(iterator, total=len(entries), unit="words"))

  changed_counter = 0
  removed_words = OrderedSet()
  for word, new_pronunciations in pronunciations_to_i:
    pronunciations_unchanged = new_pronunciations is None
    if pronunciations_unchanged:
      continue

    if len(new_pronunciations) == 0:
      if keep_empty:
        assert empty_symbol is not None
        empty_pair = ((empty_symbol,), DEFAULT_EMPTY_WEIGHT)
        dictionary[word] = OrderedDict(empty_pair,)
      else:
        removed_words.add(word)
        dictionary.pop(word)
    else:
      dictionary[word] = new_pronunciations
    changed_counter += 1

  return removed_words, changed_counter


process_lookup_dict: PronunciationDict = None


def __init_pool_prepare_cache_mp(lookup_dict: PronunciationDict) -> None:
  global process_lookup_dict
  process_lookup_dict = lookup_dict


def process_get_pronunciation(word: Word, symbols: Set[Symbol]) -> Tuple[Word, Optional[Pronunciations]]:
  global process_lookup_dict
  assert word in process_lookup_dict
  pronunciations = process_lookup_dict[word]
  new_pronunciations = OrderedDict()
  changed_anything = False
  for pronunciation, weight in pronunciations.items():
    new_pronunciation = tuple(
      symbol
      for symbol in pronunciation
      if symbol not in symbols
    )

    if new_pronunciation != pronunciation:
      if len(new_pronunciation) > 0:
        if new_pronunciation in new_pronunciations:
          new_pronunciations[new_pronunciation] += weight
        else:
          new_pronunciations[new_pronunciation] = weight
      changed_anything = True

  if changed_anything:
    return word, new_pronunciations
  return word, None

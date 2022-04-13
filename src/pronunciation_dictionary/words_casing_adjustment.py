from argparse import ArgumentParser, Namespace
from functools import partial
from logging import getLogger
from multiprocessing.pool import Pool
from typing import Literal, Optional, Tuple

from ordered_set import OrderedSet
from tqdm import tqdm

from pronunciation_dictionary.argparse_helper import (add_io_group, add_mp_group,
                                                      parse_existing_file, parse_float_0_to_1)
from pronunciation_dictionary.common import merge_pronunciations
from pronunciation_dictionary.deserialization import DeserializationOptions, MultiprocessingOptions
from pronunciation_dictionary.io import try_load_dict, try_save_dict
from pronunciation_dictionary.serialization import SerializationOptions
from pronunciation_dictionary.types import PronunciationDict, Word


def get_words_casing_adjustment_parser(parser: ArgumentParser):
  parser.description = "Adjust casing of words in dictionary."
  parser.add_argument("dictionary", metavar='dictionary',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("-m", "--mode", type=str, choices=["lower", "upper"],
                      help="mode to change the casing", default="lower")
  parser.add_argument("-r", "--ratio", type=parse_float_0_to_1,
                      help="merge pronunciations weights with these ratio, i.e., existing weights * ratio + weights to merge * (1-ratio)", default=0.5)
  add_io_group(parser)
  add_mp_group(parser)
  return change_casing_ns


def change_casing_ns(ns: Namespace) -> bool:
  logger = getLogger(__name__)
  logger.debug(ns)

  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options)
  if dictionary_instance is None:
    logger.error(f"Dictionary '{ns.dictionary}' couldn't be read.")
    return False

  changed_counter = change_casing(
    dictionary_instance, ns.mode, ns.ratio, mp_options)

  if changed_counter == 0:
    logger.info("Didn't changed anything.")
    return True

  logger.info(f"Changed pronunciations of {changed_counter} word(s).")

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options)
  if not success:
    logger.error("Dictionary couldn't be written.")
    return False

  logger.info(f"Written dictionary to: {ns.dictionary.absolute()}")


def change_casing(dictionary: PronunciationDict, mode: str, ratio: float, mp_options: MultiprocessingOptions) -> int:
  process_method = partial(
    process_change_casing,
    mode=mode,
  )

  with Pool(
    processes=mp_options.n_jobs,
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    entries = OrderedSet(dictionary.keys())
    iterator = pool.imap(process_method, entries, mp_options.chunksize)
    new_words_to_words = dict(tqdm(iterator, total=len(entries), unit="words"))

  changed_counter = 0
  all_words_in_order = OrderedSet(dictionary.keys())
  for word in all_words_in_order:
    new_word = new_words_to_words[word]
    changed_word = new_word is not None
    if changed_word:
      popped_pronunciations = dictionary.pop(word)
      if new_word in dictionary:
        existing_pronunciations = dictionary[word]
        merge_pronunciations(existing_pronunciations, popped_pronunciations, ratio)
      else:
        dictionary[new_word] = popped_pronunciations
      changed_counter += 1

  return changed_counter


def process_change_casing(word: Word, mode: Literal["upper", "lower"]) -> Tuple[Word, Optional[Word]]:
  if mode == "upper":
    new_word = word.upper()
  elif mode == "lower":
    new_word = word.lower()
  else:
    assert False

  if new_word != word:
    return word, new_word
  return word, None

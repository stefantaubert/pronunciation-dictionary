import random
from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from functools import partial
from logging import getLogger
from multiprocessing.pool import Pool
from pathlib import Path
from tempfile import gettempdir
from typing import Literal, Optional, Tuple

from ordered_set import OrderedSet
from tqdm import tqdm

from pronunciation_dictionary.api import get_first_pronunciation
from pronunciation_dictionary.argparse_helper import (
    ConvertToOrderedSetAction, add_chunksize_argument, add_encoding_argument,
    add_io_group, add_maxtaskperchild_argument, add_mp_group,
    add_n_jobs_argument, get_optional, parse_existing_file, parse_float_0_to_1,
    parse_non_empty, parse_non_negative_integer, parse_optional_value,
    parse_path)
from pronunciation_dictionary.common import merge_pronunciations
from pronunciation_dictionary.deserialization import (DeserializationOptions,
                                                      MultiprocessingOptions)
from pronunciation_dictionary.globals import DEFAULT_PUNCTUATION, PROG_WORD_SEP
from pronunciation_dictionary.io import try_load_dict, try_save_dict
from pronunciation_dictionary.serialization import SerializationOptions
from pronunciation_dictionary.types import (PronunciationDict, Pronunciations,
                                            Symbol, Word)


def get_single_pronunciation_selection_parser(parser: ArgumentParser):
  parser.description = "Select a single pronunciation for each word."
  parser.add_argument("dictionary", metavar='dictionary',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("-m", "--mode", type=str, choices=["first", "last", "highest-weight", "lowest-weight", "random"],
                      help="mode to select the target pronunciation", default="highest-weight")
  parser.add_argument("--seed", type=get_optional(parse_non_negative_integer),
                      help="seed if mode is random", default=None)
  add_io_group(parser)
  add_mp_group(parser)
  return remove_multiple_pronunciations_ns


def remove_multiple_pronunciations_ns(ns: Namespace) -> bool:
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

  changed_counter = remove_extra_pronunciations(
    dictionary_instance, ns.mode, ns.seed, mp_options)

  if changed_counter == 0:
    logger.info("Didn't changed anything.")
    return True

  logger.info(f"Changed pronunciations of {changed_counter} word(s).")

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options)
  if not success:
    logger.error("Dictionary couldn't be written.")
    return False

  logger.info(f"Written dictionary to: {ns.dictionary.absolute()}")


process_lookup_dict: PronunciationDict = None


def remove_extra_pronunciations(dictionary: PronunciationDict, mode: str, seed: Optional[int], mp_options: MultiprocessingOptions) -> Tuple[int]:
  if seed is not None:
    random.seed(seed)

  process_method = partial(
    process_merge,
    mode=mode,
  )

  with Pool(
    processes=mp_options.n_jobs,
    initializer=__init_pool_prepare_cache_mp,
    initargs=(dictionary,),
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    entries = OrderedSet(dictionary.keys())
    iterator = pool.imap(process_method, entries, mp_options.chunksize)
    new_pronunciations_to_words = dict(tqdm(iterator, total=len(entries), unit="words"))

  changed_counter = 0

  for word, new_pronunciations in new_pronunciations_to_words.items():
    changed_pronunciation = new_pronunciations is not None
    if changed_pronunciation:
      dictionary[word] = new_pronunciations
      changed_counter += 1

  return changed_counter


def __init_pool_prepare_cache_mp(lookup_dict: PronunciationDict) -> None:
  global process_lookup_dict
  process_lookup_dict = lookup_dict


def process_merge(word: Word, mode: Literal["first", "last", "highest-weight", "lowest-weight", "random"]) -> Tuple[Word, Optional[Pronunciations]]:
  global process_lookup_dict
  assert word in process_lookup_dict
  pronunciations = process_lookup_dict[word]
  assert len(pronunciations) > 0
  if len(pronunciations) == 1:
    return word, None

  if mode == "first":
    pronunciation = next(iter(pronunciations.keys()))
  elif mode == "last":
    pronunciation = next(reversed(pronunciations.keys()))
  elif mode == "highest-weight":
    pronunciation, _ = next(sorted(pronunciations.items(), key=lambda kv: kv[1], reverse=False))
  elif mode == "lowest-weight":
    pronunciation, _ = next(sorted(pronunciations.items(), key=lambda kv: kv[1], reverse=True))
  elif mode == "random":
    pronunciation = random.choice(pronunciations.keys())
  else:
    assert False

  sum_weights = sum(pronunciations.values())
  result = OrderedDict(
    (pronunciation, sum_weights),
  )
  return word, result

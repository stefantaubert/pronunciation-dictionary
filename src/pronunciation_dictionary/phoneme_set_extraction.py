from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from functools import partial
from logging import getLogger
from multiprocessing.pool import Pool
from pathlib import Path
from tempfile import gettempdir
from typing import Optional, Set, Tuple, cast

from ordered_set import OrderedSet
from tqdm import tqdm

from pronunciation_dictionary.argparse_helper import (ConvertToOrderedSetAction,
                                                      add_chunksize_argument,
                                                      add_deserialization_group, add_io_group,
                                                      add_maxtaskperchild_argument, add_mp_group,
                                                      add_n_jobs_argument, get_optional,
                                                      parse_existing_file, parse_path)
from pronunciation_dictionary.deserialization import DeserializationOptions, MultiprocessingOptions
from pronunciation_dictionary.globals import DEFAULT_PUNCTUATION
from pronunciation_dictionary.io import try_load_dict, try_save_dict
from pronunciation_dictionary.serialization import SerializationOptions
from pronunciation_dictionary.types import PronunciationDict, Pronunciations, Symbol, Word


def get_phoneme_set_extraction_parser(parser: ArgumentParser):
  default_removed_out = Path(gettempdir()) / "removed-words.txt"
  parser.description = "Remove symbols from pronunciations."
  parser.add_argument("dictionaries", metavar='dictionaries', type=parse_existing_file, nargs="+",
                      help="dictionary files", action=ConvertToOrderedSetAction)
  parser.add_argument("output", metavar="output", type=parse_path,
                      help="output phoneme set to this file", default=default_removed_out)
  parser.add_argument("-u", "--unsorted", action="store_true",
                      help="do not sort vocabulary in output")
  add_deserialization_group(parser)
  add_mp_group(parser)
  return get_phoneme_set_from_ns


def get_phoneme_set_from_ns(ns: Namespace) -> bool:
  logger = getLogger(__name__)
  logger.debug(ns)
  assert len(ns.dictionaries) > 0

  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  total_vocabulary = OrderedSet()
  for dictionary_path in ns.dictionaries:
    dictionary_instance = try_load_dict(dictionary_path, ns.encoding, lp_options, mp_options)
    if dictionary_instance is None:
      logger.error(f"Dictionary '{dictionary_path}' couldn't be read.")
      return False

    vocabulary = get_phoneme_set(dictionary_instance)
    total_vocabulary.update(vocabulary)

  sort = not ns.unsorted
  result = total_vocabulary
  if sort:
    result = sorted(result)
  content = "\n".join(result)

  try:
    ns.output.parent.mkdir(parents=True, exist_ok=True)
    cast(Path, ns.output).write_text(content, ns.encoding)
  except Exception as ex:
    logger.error("Phoneme set couldn't be saved!")
    return False

  logger.info(f"Written phoneme set containing {len(result)} phonemes to: {ns.output.absolute()}")
  return True


def get_phoneme_set(dictionary: PronunciationDict) -> OrderedSet[Symbol]:
  all_symbols = (
    symbol
    for pronunciations_weight_pair in dictionary.values()
    for pronunciation in pronunciations_weight_pair.keys()
    for symbol in pronunciation
  )
  unique_symbols = set(all_symbols)
  unique_symbols = OrderedSet(sorted(unique_symbols))
  return unique_symbols

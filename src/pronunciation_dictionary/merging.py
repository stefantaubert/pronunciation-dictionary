from argparse import ArgumentParser, Namespace
from logging import getLogger
from pathlib import Path
from typing import Literal, Optional

from ordered_set import OrderedSet

from pronunciation_dictionary import PronunciationDict
from pronunciation_dictionary.argparse_helper import (
    ConvertToOrderedSetAction, add_chunksize_argument, add_io_group,
    add_maxtaskperchild_argument, add_mp_group, add_n_jobs_argument,
    get_optional, parse_existing_file, parse_float_0_to_1, parse_path)
from pronunciation_dictionary.common import merge_pronunciations
from pronunciation_dictionary.deserialization import (DeserializationOptions,
                                                      MultiprocessingOptions)
from pronunciation_dictionary.io import try_load_dict, try_save_dict
from pronunciation_dictionary.serialization import SerializationOptions


def get_merging_parser(parser: ArgumentParser):
  parser.description = "Merge multiple dictionaries into one."
  parser.add_argument("dictionaries", metavar='dictionaries', type=parse_existing_file, nargs="+",
                      help="dictionary files", action=ConvertToOrderedSetAction)
  parser.add_argument("output_dictionary", metavar='output-dictionary', type=parse_path,
                      help="file to the output dictionary")
  parser.add_argument("--duplicate-handling", type=str,
                      choices=["add", "extend", "replace"], help="sets how existing pronunciations should be handled: add = add missing pronunciations; extend = add missing pronunciations and extend existing ones; replace: add missing pronunciations and replace existing ones.", default="add")
  parser.add_argument("--ratio", type=get_optional(parse_float_0_to_1),
                      help="merge pronunciations weights with these ratio, i.e., existing weights * ratio + weights to merge * (1-ratio); only relevant on 'extend'", default=0.5)
  add_io_group(parser)
  add_mp_group(parser)
  return merge_dictionary_files


def merge_dictionary_files(ns: Namespace) -> bool:
  logger = getLogger(__name__)
  logger.debug(ns)
  assert len(ns.dictionaries) > 0
  if len(ns.dictionaries) == 1:
    logger.error("Please supply more than one dictionary!")
    return False

  if ns.duplicate_handling == "extend" and ns.ratio is None:
    logger.error("Parameter 'ratio' is required on extending!")
    return False

  resulting_dictionary = None

  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  for dictionary in ns.dictionaries:
    dictionary_instance = try_load_dict(dictionary, ns.encoding, lp_options, mp_options)
    if dictionary_instance is None:
      logger.error(f"Dictionary '{dictionary}' couldn't be read.")
      return False
    if resulting_dictionary is None:
      resulting_dictionary = dictionary_instance
      continue

    if ns.duplicate_handling == "add":
      dictionary_add_new(resulting_dictionary, dictionary_instance)
    elif ns.duplicate_handling == "replace":
      dictionary_replace(resulting_dictionary, dictionary_instance)
    elif ns.duplicate_handling == "extend":
      assert ns.ratio is not None
      dictionary_extend(resulting_dictionary, dictionary_instance, ns.ratio)
    else:
      assert False

  success = try_save_dict(resulting_dictionary, ns.output_dictionary, ns.encoding, s_options)
  if not success:
    logger.error("Dictionary couldn't be written.")
    return False

  logger.info(f"Written dictionary to: {ns.output_dictionary.absolute()}")


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

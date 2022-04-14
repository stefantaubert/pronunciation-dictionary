from argparse import ArgumentParser, Namespace
from logging import getLogger

from pronunciation_dictionary.deserialization import DeserializationOptions, MultiprocessingOptions
from pronunciation_dictionary.io import try_load_dict, try_save_dict
from pronunciation_dictionary.merging import merge_dictionary_files
from pronunciation_dictionary.serialization import SerializationOptions
from pronunciation_dictionary_cli.argparse_helper import (ConvertToOrderedSetAction, add_io_group,
                                                          add_mp_group, get_optional,
                                                          parse_existing_file, parse_float_0_to_1,
                                                          parse_path)


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
  return merge_dictionary_files_ns


def merge_dictionary_files_ns(ns: Namespace) -> bool:
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

    merge_dictionary_files(resulting_dictionary, dictionary_instance,
                           ns.duplicate_handling, ns.ratio)

  success = try_save_dict(resulting_dictionary, ns.output_dictionary, ns.encoding, s_options)
  if not success:
    logger.error("Dictionary couldn't be written.")
    return False

  logger.info(f"Written dictionary to: {ns.output_dictionary.absolute()}")

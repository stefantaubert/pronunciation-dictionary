from argparse import ArgumentParser, Namespace
from logging import getLogger

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions, try_load_dict, try_save_dict)
from pronunciation_dictionary_cli.argparse_helper import (ConvertToOrderedSetAction,
                                                          add_deserialization_group, add_mp_group,
                                                          add_serialization_group,
                                                          parse_existing_file)


def get_formatting_parser(parser: ArgumentParser):
  parser.description = ""

  parser.add_argument("dictionaries", metavar='dictionaries', type=parse_existing_file, nargs="+",
                      help="dictionary files", action=ConvertToOrderedSetAction)
  add_deserialization_group(parser)
  add_serialization_group(parser)
  add_mp_group(parser)

  return adjust_formatting


def adjust_formatting(ns: Namespace):
  logger = getLogger(__name__)

  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  s_options = SerializationOptions(ns.parts_sep, ns.include_numbers, ns.include_weights)

  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  for dictionary in ns.dictionaries:
    dictionary_instance = try_load_dict(dictionary, ns.encoding, lp_options, mp_options)
    if dictionary_instance is None:
      logger.error(f"Dictionary '{dictionary}' couldn't be read.")
      return False

    success = try_save_dict(dictionary_instance, dictionary, ns.encoding, s_options)
    if not success:
      logger.error("Dictionary couldn't be written.")
      return False

    logger.info(f"Written dictionary to: {dictionary.absolute()}")

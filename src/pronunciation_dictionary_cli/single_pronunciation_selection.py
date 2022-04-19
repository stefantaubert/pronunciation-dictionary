from argparse import ArgumentParser, Namespace
from logging import getLogger

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions, select_single_pronunciation)
from pronunciation_dictionary_cli.argparse_helper import (add_io_group, add_mp_group, get_optional,
                                                          parse_existing_file,
                                                          parse_non_negative_integer)
from pronunciation_dictionary_cli.io import try_load_dict, try_save_dict


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

  changed_counter = select_single_pronunciation(
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

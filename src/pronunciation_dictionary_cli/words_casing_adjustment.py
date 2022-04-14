from argparse import ArgumentParser, Namespace
from logging import getLogger

from pronunciation_dictionary.deserialization import DeserializationOptions, MultiprocessingOptions
from pronunciation_dictionary.io import try_load_dict, try_save_dict
from pronunciation_dictionary.serialization import SerializationOptions
from pronunciation_dictionary.words_casing_adjustment import change_casing
from pronunciation_dictionary_cli.argparse_helper import (add_io_group, add_mp_group,
                                                          parse_existing_file, parse_float_0_to_1)


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

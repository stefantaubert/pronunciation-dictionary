from argparse import ArgumentParser, Namespace
from logging import getLogger
from pathlib import Path
from tempfile import gettempdir

from pronunciation_dictionary.deserialization import DeserializationOptions, MultiprocessingOptions
from pronunciation_dictionary.io import try_load_dict, try_save_dict
from pronunciation_dictionary.pronunciations_remove_symbols import remove_symbols_from_pronunciations
from pronunciation_dictionary.serialization import SerializationOptions
from pronunciation_dictionary_cli.argparse_helper import (ConvertToOrderedSetAction, add_io_group,
                                                          add_mp_group, get_optional,
                                                          parse_existing_file,
                                                          parse_non_empty_or_whitespace, parse_path)
from pronunciation_dictionary_cli.globals import DEFAULT_PUNCTUATION

DEFAULT_EMPTY_WEIGHT = 1


def get_pronunciations_remove_symbols_parser(parser: ArgumentParser):
  default_removed_out = Path(gettempdir()) / "removed-words.txt"
  parser.description = "Remove symbols from pronunciations."
  parser.add_argument("dictionary", metavar='dictionary',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("-s", "--symbols", type=str, metavar='SYMBOL', nargs='+',
                      help="remove these symbols from the pronunciations", action=ConvertToOrderedSetAction, default=DEFAULT_PUNCTUATION)
  parser.add_argument("-k", "--keep-empty", action="store_true",
                      help="if a pronunciation will be empty after removal, keep the corresponding word in the dictionary and assign the value of empty-symbol")
  parser.add_argument("-es", "--empty-symbol", type=get_optional(parse_non_empty_or_whitespace),
                      help="if keep-empty: assign this symbol to the word where no pronunciations result because of the symbol removal", default="sil")
  parser.add_argument("-ro", "--removed-out", metavar="PATH", type=get_optional(parse_path),
                      help="write removed words (i.e., words that had no pronunciation anymore) to this file", default=default_removed_out)
  add_io_group(parser)
  add_mp_group(parser)
  return remove_symbols_from_pronunciations


def remove_symbols_from_pronunciations(ns: Namespace) -> bool:
  logger = getLogger(__name__)
  logger.debug(ns)

  if ns.keep_empty and ns.empty_symbol is None:
    logger.error("An empty symbol needs to be supplied if keep_empty is true!")
    return False

  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options)
  if dictionary_instance is None:
    logger.error(f"Dictionary '{ns.dictionary}' couldn't be read.")
    return False

  removed_words, changed_counter = remove_symbols_from_pronunciations(
    dictionary_instance, ns.symbols, ns.keep_empty, ns.empty_symbol, mp_options)

  if changed_counter == 0:
    logger.info("Didn't changed anything.")
    return True

  logger.info(f"Changed pronunciations of {changed_counter} word(s).")

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options)
  if not success:
    logger.error("Dictionary couldn't be written.")
    return False

  logger.info(f"Written dictionary to: {ns.dictionary.absolute()}")

  if len(removed_words) > 0:
    logger.warning(f"{len(removed_words)} words were removed.")
    if ns.removed_out is not None:
      content = "\n".join(removed_words)
      ns.removed_out.parent.mkdir(parents=True, exist_ok=True)
      try:
        ns.removed_out.write_text(content, "UTF-8")
      except Exception as ex:
        logger.error("Removed words output couldn't be created!")
        return False
      logger.info(f"Written removed words to: {ns.removed_out.absolute()}")
  else:
    logger.info("No words were removed.")

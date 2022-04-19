from argparse import ArgumentParser, Namespace
from logging import getLogger
from pathlib import Path
from typing import cast

from ordered_set import OrderedSet

from pronunciation_dictionary import DeserializationOptions, MultiprocessingOptions, get_vocabulary
from pronunciation_dictionary_cli.argparse_helper import (ConvertToOrderedSetAction,
                                                          add_deserialization_group,
                                                          add_encoding_argument, add_mp_group,
                                                          parse_existing_file, parse_path)
from pronunciation_dictionary_cli.io import try_load_dict


def get_vocabulary_extraction_parser(parser: ArgumentParser):
  parser.description = "Export vocabulary (i.e., words that are contained in the dictionaries)."
  parser.add_argument("dictionaries", metavar='dictionaries', type=parse_existing_file, nargs="+",
                      help="dictionary files", action=ConvertToOrderedSetAction)
  parser.add_argument("output", metavar="output", type=parse_path,
                      help="output vocabulary to this file")
  add_encoding_argument(parser, "-e", "--output-encoding", "encoding of the vocabulary file")
  parser.add_argument("-u", "--unsorted", action="store_true",
                      help="do not sort vocabulary in output")
  add_deserialization_group(parser)
  add_mp_group(parser)
  return get_vocabulary_ns


def get_vocabulary_ns(ns: Namespace) -> bool:
  logger = getLogger(__name__)
  logger.debug(ns)
  assert len(ns.dictionaries) > 0

  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  total_vocabulary = OrderedSet()
  for dictionary_path in ns.dictionaries:
    dictionary_instance = try_load_dict(
      dictionary_path, ns.deserialization_encoding, lp_options, mp_options)
    if dictionary_instance is None:
      logger.error(f"Dictionary '{dictionary_path}' couldn't be read.")
      return False

    vocabulary = get_vocabulary(dictionary_instance)
    total_vocabulary.update(vocabulary)

  sort = not ns.unsorted
  result = total_vocabulary
  if sort:
    result = sorted(result)
  content = "\n".join(result)

  try:
    ns.output.parent.mkdir(parents=True, exist_ok=True)
    cast(Path, ns.output).write_text(content, ns.output_encoding)
  except Exception as ex:
    logger.error("Vocabulary couldn't be saved!")
    logger.debug(ex)
    return False

  logger.info(f"Written vocabulary containing {len(result)} words to: {ns.output.absolute()}")
  return True

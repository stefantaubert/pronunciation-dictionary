from argparse import ArgumentParser, Namespace
from logging import getLogger
from pathlib import Path
from tempfile import gettempdir
from typing import cast

from ordered_set import OrderedSet

from pronunciation_dictionary.deserialization import DeserializationOptions, MultiprocessingOptions
from pronunciation_dictionary.io import try_load_dict, try_save_dict
from pronunciation_dictionary.serialization import SerializationOptions
from pronunciation_dictionary.subset_extraction import select_subset_dictionary
from pronunciation_dictionary.types import Word
from pronunciation_dictionary_cli.argparse_helper import (add_encoding_argument, add_io_group,
                                                          add_mp_group, get_optional,
                                                          parse_existing_file, parse_path)


def get_subset_extraction_parser(parser: ArgumentParser):
  parser.description = "Extract subset of dictionary."
  default_oov_out = Path(gettempdir()) / "oov.txt"
  parser.add_argument("dictionary", metavar='dictionary',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("vocabulary", metavar='vocabulary',
                      type=parse_existing_file, help="vocabulary that should be extracted")
  parser.add_argument("output_dictionary", metavar='output-dictionary',
                      type=parse_path, help="file to the output dictionary")
  add_encoding_argument(parser, "-ve", "--vocabulary-encoding", "encoding of the vocabulary file")
  parser.add_argument("--oov-out", metavar="PATH", type=get_optional(parse_path),
                      help="write out-of-vocabulary (OOV) words (i.e., words that did not exist in the dictionary) to this file (encoding will be the same as the one from the vocabulary file)", default=default_oov_out)
  parser.add_argument("--consider-case", action="store_true",
                      help="only extract entries matching the exact casing of the vocabulary")
  add_io_group(parser)
  add_mp_group(parser)
  return extract_subset_ns


def extract_subset_ns(ns: Namespace) -> bool:
  logger = getLogger(__name__)
  logger.debug(ns)

  try:
    vocabulary_content = cast(Path, ns.vocabulary).read_text(ns.vocabulary_encoding)
  except Exception as ex:
    logger.error("Vocabulary couldn't be read.")
    return False

  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options)
  if dictionary_instance is None:
    logger.error(f"Dictionary '{ns.dictionary}' couldn't be read.")
    return False
  logger.info(f"Parsed dictionary containing {len(dictionary_instance)} words.")

  vocabulary = OrderedSet(vocabulary_content.splitlines())
  logger.info(f"Parsed vocabulary containing {len(vocabulary)} words.")

  oov_voc = select_subset_dictionary(dictionary_instance, vocabulary, ns.consider_case)

  if len(dictionary_instance) == 0:
    logger.info(f"The target dictionary is empty! Skipped saving.")
  else:
    success = try_save_dict(dictionary_instance, ns.output_dictionary, ns.encoding, s_options)
    if not success:
      logger.error("Dictionary couldn't be written.")
      return False

    logger.info(
      f"Written dictionary containing {len(dictionary_instance)} words to: {ns.output_dictionary.absolute()}")

  if len(oov_voc) > 0:
    logger.info(f"{len(oov_voc)} word(s) were not contained in the dictionary!")
    if ns.oov_out is not None:
      oov_content = "\n".join(oov_voc)
      try:
        ns.oov_out.parent.mkdir(parents=True, exist_ok=True)
        ns.oov_out.write_text(oov_content, "UTF-8")
      except Exception as ex:
        logger.error("OOV output couldn't be created!")
        logger.debug(ex)
        return False
      logger.info(f"Written OOV-words to: {ns.oov_out.absolute()}")
  else:
    logger.info("All words were contained in the target dictionary!")

  return True

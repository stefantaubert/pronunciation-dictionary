from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from logging import getLogger
from pathlib import Path
from tempfile import gettempdir
from typing import Literal, Optional, cast
from pronunciation_dictionary import PronunciationDict
from ordered_set import OrderedSet
from pronunciation_dictionary.argparse_helper import add_chunksize_argument, add_encoding_argument, add_io_group, add_maxtaskperchild_argument, add_mp_group, add_n_jobs_argument, get_optional, parse_existing_file, parse_float_0_to_1, parse_path
from pronunciation_dictionary.argparse_helper import ConvertToOrderedSetAction
from pronunciation_dictionary.common import merge_pronunciations
from pronunciation_dictionary.deserialization import DeserializationOptions, MultiprocessingOptions
from pronunciation_dictionary.io import try_load_dict, try_save_dict
from pronunciation_dictionary.serialization import SerializationOptions
from pronunciation_dictionary.types import Word


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

  if len(dictionary_instance) == 0:
    logger.warning(f"The target dictionary is empty! Skipped saving.")
  else:
    success = try_save_dict(dictionary_instance, ns.output_dictionary, ns.encoding, s_options)
    if not success:
      logger.error("Dictionary couldn't be written.")
      return False

    logger.info(
      f"Written dictionary containing {len(dictionary_instance)} words to: {ns.output_dictionary.absolute()}")

  vocabulary = OrderedSet(vocabulary_content.splitlines())
  logger.info(f"Parsed vocabulary containing {len(vocabulary)} words.")
  if ns.consider_case:
    oov_voc = select_subset_dictionary_casing(dictionary_instance, vocabulary)
  else:
    oov_voc = select_subset_dictionary_ignore_casing(dictionary_instance, vocabulary)

  if len(oov_voc) > 0:
    logger.warning(f"{len(oov_voc)} word(s) were not contained in the dictionary!")
    if ns.oov_out is not None:
      oov_content = "\n".join(oov_voc)
      try:
        ns.oov_out.parent.mkdir(parents=True, exist_ok=True)
        ns.oov_out.write_text(oov_content, "UTF-8")
      except Exception as ex:
        logger.error("OOV output couldn't be created!")
        return False
      logger.info(f"Written OOV to: {ns.oov_out.absolute()}")
  else:
    logger.info("All words were contained in the target dictionary!")

  return True


def select_subset_dictionary_casing(dictionary: PronunciationDict, vocabulary: OrderedSet[Word]) -> OrderedSet[Word]:
  existing_vocabulary = OrderedSet(dictionary.keys())
  # copy_voc = vocabulary.intersection(existing_vocabulary)
  remove_voc = existing_vocabulary.difference(vocabulary)
  oov_voc = vocabulary.difference(existing_vocabulary)

  for word in remove_voc:
    assert word in dictionary
    dictionary.pop(word)

  return oov_voc


def select_subset_dictionary_ignore_casing(dictionary: PronunciationDict, vocabulary: OrderedSet[Word]) -> OrderedSet[Word]:
  word_map = OrderedDict()
  for word in dictionary.keys():
    word_lower = word.lower()
    if word_lower not in word_map:
      word_map[word_lower] = OrderedSet((word,),)
    else:
      word_map[word_lower].add(word)

  vocabulary_lower = OrderedSet(
    word.lower() for word in vocabulary
  )

  existing_vocabulary = OrderedSet(word_map.keys())
  # copy_voc = vocabulary.intersection(existing_vocabulary)
  remove_voc = existing_vocabulary.difference(vocabulary_lower)
  oov_voc = vocabulary_lower.difference(existing_vocabulary)

  remove_voc_actual = OrderedSet(
    word
    for word_lower in remove_voc
    for word in word_map[word_lower]
  )

  oov_voc_actual = OrderedSet(
    word
    for word_lower in oov_voc
    for word in word_map[word_lower]
  )

  for word in remove_voc_actual:
    assert word in dictionary
    dictionary.pop(word)

  return oov_voc_actual

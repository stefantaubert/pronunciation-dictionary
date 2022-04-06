from pronunciation_dict_parser import get_first_pronunciation
from tempfile import gettempdir
from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from tqdm import tqdm
from functools import partial
from multiprocessing.pool import Pool
from typing import Optional, Set, Tuple
from pronunciation_dict_parser import PronunciationDict, Symbol, Word, Pronunciations, Pronunciation
from ordered_set import OrderedSet
from pronunciation_dict_creation.argparse_helper import get_optional, parse_existing_file, parse_non_empty_or_whitespace, parse_path
from pronunciation_dict_creation.common import ConvertToOrderedSetAction, DEFAULT_PUNCTUATION, DefaultParameters, PROG_ENCODING, add_chunksize_argument, add_encoding_argument, add_maxtaskperchild_argument, add_n_jobs_argument, get_dictionary, try_load_dict, try_save_dict
from pronunciation_dict_creation.word2pronunciation import get_pronunciation_from_word


def get_app_try_add_vocabulary_from_pronunciations_parser(parser: ArgumentParser):
  default_oov_out = Path(gettempdir()) / "oov.txt"
  parser.description = "Transcribe vocabulary with a given pronunciation dictionary and add it to an existing pronunciation dictionary or create one."
  # todo support multiple files
  parser.add_argument("vocabulary", metavar='vocabulary', type=parse_existing_file,
                      help="file containing the vocabulary (words separated by line)")
  parser.add_argument("dictionary", metavar='dictionary', type=parse_path,
                      help="file containing the output dictionary")
  parser.add_argument("reference_dictionary", metavar='reference-dictionary', type=parse_existing_file,
                      help="file containing the reference pronunciation dictionary")
  parser.add_argument("--ignore-case", action="store_true",
                      help="ignore case while looking up in reference-dictionary")
  parser.add_argument("--trim", type=parse_non_empty_or_whitespace, metavar='SYMBOL', nargs='*',
                      help="trim these symbols from the start and end of a word before looking it up in the reference pronunciation dictionary", action=ConvertToOrderedSetAction, default=DEFAULT_PUNCTUATION)
  parser.add_argument("--consider-annotations", action="store_true",
                      help="consider /.../-styled annotations")
  parser.add_argument("--split-on-hyphen", action="store_true",
                      help="split words on hyphen symbol before lookup")
  parser.add_argument("--oov-out", metavar="PATH", type=get_optional(parse_path),
                      help="write out-of-vocabulary (OOV) words (i.e., words that did not exist in the reference dictionary) to this file (encoding will be the same as the one from the vocabulary file)", default=default_oov_out)
  add_encoding_argument(parser, "--encoding", "encoding of vocabulary")
  add_n_jobs_argument(parser)
  add_chunksize_argument(parser)
  add_maxtaskperchild_argument(parser)
  return get_pronunciations_files


def get_pronunciations_files(vocabulary: Path, encoding: str, dictionary: Path, reference_dictionary: Path, ignore_case: bool, trim: OrderedSet[Symbol], consider_annotations: bool, split_on_hyphen: bool, oov_out: Optional[Path], n_jobs, maxtasksperchild: Optional[int], chunksize: int) -> bool:
  assert vocabulary.is_file()
  assert reference_dictionary.is_file()
  logger = getLogger(__name__)

  try:
    vocabulary_content = vocabulary.read_text(encoding)
  except Exception as ex:
    logger.error("Vocabulary couldn't be read.")
    return False

  reference_dictionary_instance = try_load_dict(reference_dictionary)
  if reference_dictionary_instance is None:
    logger.error("Reference dictionary couldn't be read.")
    return False

  vocabulary_words = OrderedSet(vocabulary_content.splitlines())
  params = DefaultParameters(vocabulary_words, consider_annotations, "/",
                             split_on_hyphen, trim, n_jobs, maxtasksperchild, chunksize)

  dictionary_instance, unresolved_words = get_pronunciations(
    params, reference_dictionary_instance, ignore_case)

  success = try_save_dict(dictionary_instance, dictionary)
  if not success:
    logger.error("Dictionary couldn't be written.")
    return False

  logger.info(f"Written dictionary to: {dictionary.absolute()}")

  if len(unresolved_words) > 0:
    logger.warning("Not all words were contained in the reference dictionary")
    if oov_out is not None:
      unresolved_out_content = "\n".join(unresolved_words)
      oov_out.parent.mkdir(parents=True, exist_ok=True)
      try:
        oov_out.write_text(unresolved_out_content, "UTF-8")
      except Exception as ex:
        logger.error("Unresolved output couldn't be created!")
        return False
      logger.info(f"Written unresolved to: {oov_out.absolute()}")
  else:
    logger.info("Complete vocabulary is contained in output!")

  return True


def get_pronunciations(default_params: DefaultParameters, lookup_dict: PronunciationDict, lookup_ignore_case: bool) -> Tuple[PronunciationDict, OrderedSet[Word]]:
  lookup_method = partial(
    process_get_pronunciation,
    ignore_case=lookup_ignore_case,
    trim_symbols=default_params.trim_symbols,
    split_on_hyphen=default_params.split_on_hyphen,
    consider_annotations=default_params.consider_annotations,
    annotation_split_symbol=default_params.annotation_split_symbol,
  )

  if lookup_ignore_case:
    lookup_dict = dict_words_to_lower(lookup_dict)

  with Pool(
    processes=default_params.n_jobs,
    initializer=__init_pool_prepare_cache_mp,
    initargs=(default_params.vocabulary, lookup_dict),
    maxtasksperchild=default_params.maxtasksperchild,
  ) as pool:
    entries = range(len(default_params.vocabulary))
    iterator = pool.imap(lookup_method, entries, default_params.chunksize)
    pronunciations_to_i = list(tqdm(iterator, total=len(entries), unit="words"))

  return get_dictionary(pronunciations_to_i, default_params.vocabulary)


process_unique_words: OrderedSet[Word] = None
process_lookup_dict: PronunciationDict = None


def __init_pool_prepare_cache_mp(words: OrderedSet[Word], lookup_dict: PronunciationDict) -> None:
  global process_unique_words
  global process_lookup_dict
  process_unique_words = words
  process_lookup_dict = lookup_dict


def process_get_pronunciation(word_i: int, ignore_case: bool, trim_symbols: Set[Symbol], split_on_hyphen: bool, consider_annotations: bool, annotation_split_symbol: Optional[Symbol]) -> Tuple[int, Optional[Pronunciations]]:
  global process_unique_words
  global process_lookup_dict
  assert 0 <= word_i < len(process_unique_words)
  word = process_unique_words[word_i]

  # TODO support all entries; also create all combinations with hyphen then
  lookup_method = partial(
    lookup_first_entry_in_dict,
    ignore_case=ignore_case,
  )

  pronunciation = get_pronunciation_from_word(
    word=tuple(word),
    trim_symbols=trim_symbols,
    split_on_hyphen=split_on_hyphen,
    get_pronunciation=lookup_method,
    consider_annotation=consider_annotations,
    annotation_split_symbol=annotation_split_symbol,
  )

  if None in pronunciation:
    return word_i, None
  return word_i, OrderedSet((pronunciation,))


def lookup_first_entry_in_dict(word: Pronunciation, ignore_case: bool) -> Pronunciation:
  global process_lookup_dict
  word_str = "".join(word)
  if ignore_case:
    word_str = word_str.lower()
  result = None
  if word_str in process_lookup_dict:
    result = get_first_pronunciation(word_str, process_lookup_dict)
  if result is None:
    return (None,)
  return result


def dict_words_to_lower(lookup_dict: PronunciationDict) -> PronunciationDict:
  result = PronunciationDict()
  for word, pronunciations in lookup_dict.items():
    word = word.lower()
    if word in result:
      result[word].update(pronunciations)
    else:
      result[word] = pronunciations
  return result

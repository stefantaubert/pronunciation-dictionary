import re
from collections import OrderedDict
from dataclasses import dataclass
from functools import partial
from logging import getLogger
from multiprocessing.pool import Pool
from typing import List, Optional, Tuple

from tqdm import tqdm

from pronunciation_dictionary.common import MultiprocessingOptions
from pronunciation_dictionary.types import Pronunciation, PronunciationDict, Weight, Word
from pronunciation_dictionary.validation import validate_mp_options, validate_type

WORD_PRON_PATTERN = re.compile(r"(\S+)\s+(.+)")
WORD_WEIGHT_PRON_PATTERN = re.compile(r"(\S+)\s+([0-9\.]+)\s+(.+)")

# e.g. `ABBE(1)`
WORD_ALT_PATTERN = re.compile(r"(\S+)(\([0-9]+\))")
PRON_COMMENT_PATTERN = re.compile(r"(.*\S+)\s+(#.*)")
PRON_SYMB_SEP_PATTERN = re.compile(r"\s+")
DEFAULT_WEIGHT: Weight = 1.0


@dataclass()
class DeserializationOptions():
  consider_comments: bool
  consider_word_nrs: bool
  consider_pronunciation_comments: bool
  consider_weights: bool


def validate_deserialization_options(options: DeserializationOptions) -> Optional[str]:
  if msg := validate_type(options.consider_comments, bool):
    return f"Property 'consider_comments': {msg}"
  if msg := validate_type(options.consider_word_nrs, bool):
    return f"Property 'consider_word_nrs': {msg}"
  if msg := validate_type(options.consider_pronunciation_comments, bool):
    return f"Property 'consider_pronunciation_comments': {msg}"
  if msg := validate_type(options.consider_weights, bool):
    return f"Property 'consider_weights': {msg}"
  return None


def deserialize(lines: List[str], options: DeserializationOptions, mp_options: MultiprocessingOptions) -> PronunciationDict:
  if msg := validate_type(lines, list):
    return f"Property 'lines': {msg}"
  if msg := validate_deserialization_options(options):
    raise ValueError(f"Parameter 'options': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  if len(lines) == 0:
    return OrderedDict()

  logger = getLogger(__name__)

  process_method = partial(
    process_get_pronunciation,
    options=options,
  )

  with Pool(
    processes=mp_options.n_jobs,
    initializer=__init_pool_prepare_cache_mp,
    initargs=(lines,),
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    entries = range(len(lines))
    iterator = pool.imap(process_method, entries, mp_options.chunksize)
    result = dict(tqdm(iterator, total=len(entries), unit="lines"))

  pronunciation_dict: PronunciationDict = OrderedDict()
  for line_i in range(len(lines)):
    line_nr = line_i + 1
    assert line_i in result
    values, messages = result[line_i]
    for message in messages:
      logger.info(f"Line {line_nr}: {message}")
    if values is None:
      continue
    word, weight, pronunciation = values
    had_weight = weight is not None

    if weight is None:
      weight = DEFAULT_WEIGHT

    if had_weight and weight == 0:
      logger.info(
        f"Line {line_nr}: Ignored line because to word \"{word}\" the pronunciation \"{' '.join(pronunciation)}\" had zero weight.")
    if word in pronunciation_dict:
      if pronunciation in pronunciation_dict[word]:
        if had_weight:
          existing_weight = pronunciation_dict[word]
          if weight != existing_weight:
            logger.warning(
              f"Line {line_nr}: Ignored line because to word \"{word}\" the pronunciation \"{' '.join(pronunciation)}\" was already assigned previously but with another weight ({existing_weight} vs. {weight})!.")
          else:
            logger.info(
              f"Line {line_nr}: Ignored line because to word \"{word}\" the pronunciation \"{' '.join(pronunciation)}\" was already assigned previously (with same weight of {weight}).")
        else:
          logger.info(
            f"Line {line_nr}: Ignored line because to word \"{word}\" the pronunciation \"{' '.join(pronunciation)}\" was already assigned previously.")
        continue
      pronunciation_dict[word][pronunciation] = weight
    else:
      pronunciation_dict[word] = OrderedDict(((pronunciation, weight),))

  return pronunciation_dict


process_lines: List[str] = None


def __init_pool_prepare_cache_mp(lines: List[str]) -> None:
  global process_lines
  process_lines = lines


def process_get_pronunciation(line_i: int, options: DeserializationOptions) -> Tuple[int, Optional[Tuple[Tuple[Word, Optional[Weight], Pronunciation], List[str]]]]:
  global process_lines
  assert 0 <= line_i < len(process_lines)
  line = process_lines[line_i]
  return line_i, parse_line(line, options)


def parse_line(line: str, options: DeserializationOptions) -> Optional[Tuple[Tuple[Word, Optional[Weight], Pronunciation], List[str]]]:
  line = line.strip()
  line_is_empty = line == ""
  if line_is_empty:
    return None, ["Ignored empty line."]

  if options.consider_comments:
    is_comment = line.startswith(";;;")
    if is_comment:
      return None, [f"Ignored comment -> \"{line}\""]

  if options.consider_weights:
    word_weight_pronun_match = re.fullmatch(WORD_WEIGHT_PRON_PATTERN, line)
    is_invalid_line = word_weight_pronun_match is None
    if is_invalid_line:
      return None, [f"Ignored invalid line -> \"{line}\""]
    word = word_weight_pronun_match.group(1)
    weight = word_weight_pronun_match.group(2)
    pronunciation = word_weight_pronun_match.group(3)
    try:
      weight = float(weight)
    except ValueError as error:
      return None, [f"Weight couldn't be parsed -> \"{weight}\""]
  else:
    word_pronun_match = re.fullmatch(WORD_PRON_PATTERN, line)
    is_invalid_line = word_pronun_match is None
    if is_invalid_line:
      return None, [f"Ignored invalid line -> \"{line}\""]
    word = word_pronun_match.group(1)
    weight = None
    pronunciation = word_pronun_match.group(2)

  msgs = []

  if options.consider_word_nrs:
    word_nr_match = re.fullmatch(WORD_ALT_PATTERN, word)
    has_word_nr = word_nr_match is not None
    if has_word_nr:
      word = word_nr_match.group(1)
      msgs.append(f"Got alternate pronunciation \"{word_nr_match.group(2)}\" for word \"{word}\"")

  if options.consider_pronunciation_comments:
    comment_match = re.fullmatch(PRON_COMMENT_PATTERN, pronunciation)
    has_comment = comment_match is not None
    if has_comment:
      pronunciation = comment_match.group(1)
      msgs.append(
        f"Got comment for word \"{word}\" and pronunciation \"{pronunciation}\" -> \"{comment_match.group(2)}\"")

  symbols = re.split(PRON_SYMB_SEP_PATTERN, pronunciation)
  pronunciation = tuple(symbols)
  return (word, weight, pronunciation), msgs

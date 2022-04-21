from functools import partial
from multiprocessing.pool import Pool
from typing import Literal, Optional, Tuple

from ordered_set import OrderedSet
from tqdm import tqdm

from pronunciation_dictionary.common import merge_pronunciations
from pronunciation_dictionary.mp_options import MultiprocessingOptions
from pronunciation_dictionary.types import PronunciationDict, Word
from pronunciation_dictionary.validation import (validate_dictionary, validate_mp_options,
                                                 validate_ratio)


def __validate_mode(mode: str) -> Optional[str]:
  if mode not in ["all", "start", "end", "both"]:
    return "Value needs to be 'all', 'start', 'end' or 'both'!"
  return None


def __validate_symbols(symbols: str) -> Optional[str]:
  if not isinstance(symbols, str):
    return "Value needs of type 'str'!"
  return None


def remove_symbols_from_words(dictionary: PronunciationDict, symbols: str, mode: str, ratio: float, mp_options: MultiprocessingOptions) -> Tuple[OrderedSet[Word], OrderedSet[Word]]:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := __validate_symbols(symbols):
    raise ValueError(f"Parameter 'symbols': {msg}")
  if msg := __validate_mode(mode):
    raise ValueError(f"Parameter 'mode': {msg}")
  if msg := validate_ratio(ratio):
    raise ValueError(f"Parameter 'ratio': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  if symbols == "":
    return OrderedSet(), 0

  process_method = partial(
    process_get_word,
    symbols=symbols,
    mode=mode,
  )

  with Pool(
    processes=mp_options.n_jobs,
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    entries = OrderedSet(dictionary.keys())
    iterator = pool.imap(process_method, entries, mp_options.chunksize)
    new_words_to_words = dict(tqdm(iterator, total=len(entries), unit="words"))

  removed_words_entirely = OrderedSet()
  removed_words = OrderedSet()
  all_words_in_order = OrderedSet(dictionary.keys())
  for word in all_words_in_order:
    new_word = new_words_to_words[word]
    changed_word = new_word is not None
    if changed_word:
      popped_pronunciations = dictionary.pop(word)
      if new_word in dictionary:
        existing_pronunciations = dictionary[new_word]
        merge_pronunciations(existing_pronunciations, popped_pronunciations, ratio)
      else:
        if new_word == "":
          removed_words_entirely.add(word)
        else:
          dictionary[new_word] = popped_pronunciations
      removed_words.add(word)

  return removed_words_entirely, removed_words


def process_get_word(word: Word, symbols: str, mode: Literal["all", "start", "end", "both"]) -> Tuple[Word, Optional[Word]]:
  if mode == "all":
    new_word = "".join(
      symbol
      for symbol in word
      if symbol not in symbols
    )
  elif mode == "start":
    new_word = word.lstrip(symbols)
  elif mode == "end":
    new_word = word.rstrip(symbols)
  elif mode == "both":
    new_word = word.strip(symbols)
  else:
    assert False

  if new_word != word:
    return word, new_word
  return word, None

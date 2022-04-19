from functools import partial
from multiprocessing.pool import Pool
from typing import Literal, Optional, Tuple

from ordered_set import OrderedSet
from tqdm import tqdm

from pronunciation_dictionary.common import MultiprocessingOptions, merge_pronunciations
from pronunciation_dictionary.types import PronunciationDict, Word


def remove_symbols(dictionary: PronunciationDict, symbols: str, mode: str, ratio: float, mp_options: MultiprocessingOptions) -> Tuple[OrderedSet[Word], int]:
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

  changed_counter = 0
  removed_words = OrderedSet()
  all_words_in_order = OrderedSet(dictionary.keys())
  for word in all_words_in_order:
    new_word = new_words_to_words[word]
    changed_word = new_word is not None
    if changed_word:
      popped_pronunciations = dictionary.pop(word)
      if new_word in dictionary:
        existing_pronunciations = dictionary[word]
        merge_pronunciations(existing_pronunciations, popped_pronunciations, ratio)
      else:
        if new_word == "":
          removed_words.add(word)
        else:
          dictionary[new_word] = popped_pronunciations
      changed_counter += 1

  return removed_words, changed_counter


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

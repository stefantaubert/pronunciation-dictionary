from functools import partial
from multiprocessing.pool import Pool
from typing import Literal, Optional, Tuple

from ordered_set import OrderedSet
from tqdm import tqdm

from pronunciation_dictionary.common import merge_pronunciations
from pronunciation_dictionary.deserialization import MultiprocessingOptions
from pronunciation_dictionary.types import PronunciationDict, Word
from pronunciation_dictionary.validation import validate_dictionary


def change_casing(dictionary: PronunciationDict, mode: str, ratio: float, mp_options: MultiprocessingOptions) -> int:
  if mode not in ["lower", "upper"]:
    raise ValueError("Parameter 'mode': Invalid value!")
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")

  process_method = partial(
    process_change_casing,
    mode=mode,
  )

  with Pool(
    processes=mp_options.n_jobs,
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    iterator = pool.imap(process_method, dictionary.keys(), mp_options.chunksize)
    new_words_to_words = dict(tqdm(iterator, total=len(dictionary), unit="words"))

  changed_counter = 0
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
        dictionary[new_word] = popped_pronunciations
      changed_counter += 1

  return changed_counter


def process_change_casing(word: Word, mode: Literal["upper", "lower"]) -> Tuple[Word, Optional[Word]]:
  if mode == "upper":
    new_word = word.upper()
  elif mode == "lower":
    new_word = word.lower()
  else:
    assert False

  if new_word != word:
    return word, new_word
  return word, None

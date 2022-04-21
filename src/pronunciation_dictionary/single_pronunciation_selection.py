from collections import OrderedDict
from functools import partial
from multiprocessing.pool import Pool
from typing import Literal, Optional, Tuple

from ordered_set import OrderedSet
from tqdm import tqdm

from pronunciation_dictionary.mp_options import MultiprocessingOptions
from pronunciation_dictionary.pronunciation_selection import (get_first_pronunciation,
                                                              get_last_pronunciation,
                                                              get_pronunciation_with_highest_weight,
                                                              get_pronunciation_with_lowest_weight,
                                                              get_random_pronunciation,
                                                              get_weighted_pronunciation)
from pronunciation_dictionary.types import PronunciationDict, Pronunciations, Word
from pronunciation_dictionary.validation import (validate_dictionary, validate_mp_options,
                                                 validate_seed)

process_lookup_dict: PronunciationDict = None

SelectionMode = Literal[
  "first",
  "last",
  "highest-weight",
  "lowest-weight",
  "random",
  "weighted",
]


def __validate_mode(mode: str) -> Optional[str]:
  if mode not in [
    "first",
    "last",
    "highest-weight",
    "lowest-weight",
    "random",
    "weighted",
  ]:
    return "Invalid value!"
  return None


def select_single_pronunciation(dictionary: PronunciationDict, mode: SelectionMode, seed: Optional[int], mp_options: MultiprocessingOptions) -> int:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := __validate_mode(mode):
    raise ValueError(f"Parameter 'mode': {msg}")
  if seed is not None and (msg := validate_seed(seed)):
    raise ValueError(f"Parameter 'seed': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  process_method = partial(
    process_merge,
    mode=mode,
    seed=seed,
  )

  with Pool(
    processes=mp_options.n_jobs,
    initializer=__init_pool_prepare_cache_mp,
    initargs=(dictionary,),
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    entries = OrderedSet(dictionary.keys())
    iterator = pool.imap(process_method, entries, mp_options.chunksize)
    new_pronunciations_to_words = dict(tqdm(iterator, total=len(entries), unit="words"))

  changed_counter = 0

  for word, new_pronunciations in new_pronunciations_to_words.items():
    changed_pronunciation = new_pronunciations is not None
    if changed_pronunciation:
      dictionary[word] = new_pronunciations
      changed_counter += 1

  return changed_counter


def __init_pool_prepare_cache_mp(lookup_dict: PronunciationDict) -> None:
  global process_lookup_dict
  process_lookup_dict = lookup_dict


def process_merge(word: Word, mode: SelectionMode, seed: Optional[int]) -> Tuple[Word, Optional[Pronunciations]]:
  global process_lookup_dict
  assert word in process_lookup_dict
  pronunciations = process_lookup_dict[word]
  assert len(pronunciations) > 0
  if len(pronunciations) == 1:
    return word, None

  if mode == "first":
    pronunciation = get_first_pronunciation(pronunciations)
  elif mode == "last":
    pronunciation = get_last_pronunciation(pronunciations)
  elif mode == "highest-weight":
    pronunciation, _ = get_pronunciation_with_highest_weight(pronunciations)
  elif mode == "lowest-weight":
    pronunciation, _ = get_pronunciation_with_lowest_weight(pronunciations)
  elif mode == "random":
    pronunciation = get_random_pronunciation(pronunciations, seed)
  elif mode == "weighted":
    pronunciation = get_weighted_pronunciation(pronunciations, seed)
  else:
    assert False

  sum_weights = sum(pronunciations.values())
  result = OrderedDict(
    (pronunciation, sum_weights),
  )
  return word, result

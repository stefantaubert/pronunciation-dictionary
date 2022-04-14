import random
from collections import OrderedDict
from functools import partial
from multiprocessing.pool import Pool
from typing import Literal, Optional, Tuple

from ordered_set import OrderedSet
from tqdm import tqdm

from pronunciation_dictionary.deserialization import MultiprocessingOptions
from pronunciation_dictionary.types import PronunciationDict, Pronunciations, Word

process_lookup_dict: PronunciationDict = None


def remove_extra_pronunciations(dictionary: PronunciationDict, mode: str, seed: Optional[int], mp_options: MultiprocessingOptions) -> Tuple[int]:
  if seed is not None:
    random.seed(seed)

  process_method = partial(
    process_merge,
    mode=mode,
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


def process_merge(word: Word, mode: Literal["first", "last", "highest-weight", "lowest-weight", "random"]) -> Tuple[Word, Optional[Pronunciations]]:
  global process_lookup_dict
  assert word in process_lookup_dict
  pronunciations = process_lookup_dict[word]
  assert len(pronunciations) > 0
  if len(pronunciations) == 1:
    return word, None

  if mode == "first":
    pronunciation = next(iter(pronunciations.keys()))
  elif mode == "last":
    pronunciation = next(reversed(pronunciations.keys()))
  elif mode == "highest-weight":
    pronunciation, _ = next(sorted(pronunciations.items(), key=lambda kv: kv[1], reverse=False))
  elif mode == "lowest-weight":
    pronunciation, _ = next(sorted(pronunciations.items(), key=lambda kv: kv[1], reverse=True))
  elif mode == "random":
    pronunciation = random.choice(pronunciations.keys())
  else:
    assert False

  sum_weights = sum(pronunciations.values())
  result = OrderedDict(
    (pronunciation, sum_weights),
  )
  return word, result

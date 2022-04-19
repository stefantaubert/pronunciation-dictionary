
import random
from typing import Optional

from pronunciation_dictionary.types import Pronunciation, Pronunciations


def get_first_pronunciation(pronunciations: Pronunciations) -> Pronunciation:
  assert len(pronunciations) > 0
  pronunciation = next(iter(pronunciations.keys()))
  return pronunciation


def get_last_pronunciation(pronunciations: Pronunciations) -> Pronunciation:
  assert len(pronunciations) > 0
  pronunciation = next(reversed(pronunciations.keys()))
  return pronunciation


def get_pronunciation_with_highest_weight(pronunciations: Pronunciations) -> Pronunciation:
  assert len(pronunciations) > 0
  pronunciation, _ = next(sorted(pronunciations.items(), key=lambda kv: kv[1], reverse=False))
  return pronunciation


def get_pronunciation_with_lowest_weight(pronunciations: Pronunciations) -> Pronunciation:
  assert len(pronunciations) > 0
  pronunciation, _ = next(sorted(pronunciations.items(), key=lambda kv: kv[1], reverse=True))
  return pronunciation


def get_random_pronunciation(pronunciations: Pronunciations, seed: Optional[int]) -> Pronunciation:
  assert len(pronunciations) > 0
  if seed is not None:
    random.seed(seed)
  pronunciation = random.choice(pronunciations.keys())
  return pronunciation


def get_weighted_pronunciation(pronunciations: Pronunciations, seed: Optional[int]) -> Pronunciation:
  assert len(pronunciations) > 0
  if seed is not None:
    random.seed(seed)
  pronunciation = random.choices(tuple(pronunciations.keys()),
                                 tuple(pronunciations.values()), k=1)[0]
  return pronunciation

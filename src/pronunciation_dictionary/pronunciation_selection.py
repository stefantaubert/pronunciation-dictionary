import random
from collections import OrderedDict
from typing import Optional

from pronunciation_dictionary.types import Pronunciation, Pronunciations
from pronunciation_dictionary.validation import validate_seed, validate_type


def validate_pronunciations(pronunciations: Pronunciations) -> Optional[str]:
  if msg := validate_type(pronunciations, OrderedDict):
    return msg
  if not len(pronunciations) > 0:
    return "At least one pronunciation is required!"
  return None


def get_first_pronunciation(pronunciations: Pronunciations) -> Pronunciation:
  if msg := validate_pronunciations(pronunciations):
    raise ValueError(f"Parameter 'pronunciations': {msg}")
  pronunciation = next(iter(pronunciations.keys()))
  return pronunciation


def get_last_pronunciation(pronunciations: Pronunciations) -> Pronunciation:
  if msg := validate_pronunciations(pronunciations):
    raise ValueError(f"Parameter 'pronunciations': {msg}")
  pronunciation = next(reversed(pronunciations.keys()))
  return pronunciation


def get_pronunciation_with_highest_weight(pronunciations: Pronunciations) -> Pronunciation:
  if msg := validate_pronunciations(pronunciations):
    raise ValueError(f"Parameter 'pronunciations': {msg}")
  pronunciation, _ = next(sorted(pronunciations.items(), key=lambda kv: kv[1], reverse=False))
  return pronunciation


def get_pronunciation_with_lowest_weight(pronunciations: Pronunciations) -> Pronunciation:
  if msg := validate_pronunciations(pronunciations):
    raise ValueError(f"Parameter 'pronunciations': {msg}")
  pronunciation, _ = next(sorted(pronunciations.items(), key=lambda kv: kv[1], reverse=True))
  return pronunciation


def get_random_pronunciation(pronunciations: Pronunciations, seed: Optional[int]) -> Pronunciation:
  if msg := validate_pronunciations(pronunciations):
    raise ValueError(f"Parameter 'pronunciations': {msg}")
  if seed is not None and (msg := validate_seed(seed)):
    raise ValueError(f"Parameter 'seed': {msg}")

  if seed is not None:
    random.seed(seed)
  pronunciation = random.choice(pronunciations.keys())
  return pronunciation


def get_weighted_pronunciation(pronunciations: Pronunciations, seed: Optional[int]) -> Pronunciation:
  if msg := validate_pronunciations(pronunciations):
    raise ValueError(f"Parameter 'pronunciations': {msg}")
  if seed is not None and (msg := validate_seed(seed)):
    raise ValueError(f"Parameter 'seed': {msg}")

  if seed is not None:
    random.seed(seed)
  pronunciation = random.choices(tuple(pronunciations.keys()),
                                 tuple(pronunciations.values()), k=1)[0]
  return pronunciation

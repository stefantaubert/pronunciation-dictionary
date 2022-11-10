import random
from typing import Optional

from pronunciation_dictionary.types import Pronunciation, Pronunciations
from pronunciation_dictionary.validation import validate_pronunciations, validate_seed


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
  pronunciation, _ = sorted(pronunciations.items(), key=lambda kv: kv[1], reverse=True)[0]
  return pronunciation


def get_pronunciation_with_lowest_weight(pronunciations: Pronunciations) -> Pronunciation:
  if msg := validate_pronunciations(pronunciations):
    raise ValueError(f"Parameter 'pronunciations': {msg}")
  pronunciation, _ = sorted(pronunciations.items(), key=lambda kv: kv[1], reverse=False)[0]
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

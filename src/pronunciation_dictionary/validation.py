from collections import OrderedDict
from typing import Any, Optional, Union

from pronunciation_dictionary.mp_options import MultiprocessingOptions
from pronunciation_dictionary.types import Pronunciation, PronunciationDict, Pronunciations


class ValidationError():
  # pylint: disable=no-self-use
  @property
  def default_message(self) -> str:
    return ""


class InternalError(ValidationError):
  @property
  def default_message(self) -> str:
    return "Internal error!"


def _contain_whitespace(chars: str) -> bool:
  for char in chars:
    if char in (" ", "\t"):
      return True
  return False


def validate_dictionary(dictionary: PronunciationDict) -> None:
  if not (isinstance(dictionary, OrderedDict)):
    raise ValueError("dictionary", "Type needs to be 'OrderedDict'!")
  for word, pronunciations in dictionary.items():
    try:
      validate_word(word)
    except ValueError as error:
      raise ValueError("dictionary", error.args[1]) from error
    if not isinstance(pronunciations, OrderedDict):
      raise ValueError("dictionary", "Pronunciations need to be of type 'OrderedDict'!")
    for pronunciation, weight in pronunciations.items():
      try:
        validate_pronunciation(pronunciation)
      except ValueError as error:
        raise ValueError("dictionary", error.args[1]) from error
      try:
        validate_weight(weight)
      except ValueError as error:
        raise ValueError("dictionary", error.args[1]) from error


def validate_word(word: str) -> None:
  if not isinstance(word, str):
    raise ValueError("word", "Word need to be of type 'str'!")
  if len(word) == 0:
    raise ValueError("word", "Empty words is not allowed!")
  if _contain_whitespace(word):
    raise ValueError("word", "Word contains whitespace which is not allowed!")


def validate_pronunciation(pronunciation: Pronunciation) -> None:
  if not isinstance(pronunciation, tuple):
    raise ValueError("pronunciation", "Pronunciation need to be of type 'tuple'!")

  if len(pronunciation) == 0:
    raise ValueError("pronunciation", "Pronunciation is empty!")

  all_phonemes_are_str = all(isinstance(phoneme, str) for phoneme in pronunciation)
  if not all_phonemes_are_str:
    raise ValueError("pronunciation", "Phonemes need to be of type 'str'!")

  whitespace_in_any_phoneme = any(
    _contain_whitespace(phoneme)
    for phoneme in pronunciation
  )
  if whitespace_in_any_phoneme:
    raise ValueError("pronunciation", "Pronunciation contains whitespace which is not allowed!")


def validate_weight(weight: Union[float, int]) -> None:
  if not isinstance(weight, (float, int)):
    raise ValueError("weight", "Weight needs to be of type 'float' or 'int'!")


def validate_ratio(ratio: float) -> Optional[str]:
  if not 0 <= ratio <= 1:
    return "Value needs to be in interval [0, 1]!"
  return None


def validate_mp_options(mp_options: MultiprocessingOptions) -> Optional[str]:
  if not (isinstance(mp_options.chunksize, int) and mp_options.chunksize > 0):
    return "Property 'chunksize' is invalid!"
  if not (mp_options.maxtasksperchild is None or (isinstance(mp_options.maxtasksperchild, int) and mp_options.maxtasksperchild > 0)):
    return "Property 'maxtasksperchild' is invalid!"
  if not (isinstance(mp_options.n_jobs, int) and mp_options.n_jobs > 0):
    return "Property 'n_jobs' is invalid!"
  return None


def validate_seed(seed: int) -> Optional[str]:
  if not 0 < seed and not isinstance(seed, int):
    return "Invalid value!"
  return None


def validate_type(obj: Any, t: type) -> Optional[str]:
  if not isinstance(obj, t):
    return f"Value needs of type '{t.__name__}'!"
  return None


def validate_pronunciations(pronunciations: Pronunciations) -> Optional[str]:
  if msg := validate_type(pronunciations, OrderedDict):
    return msg
  if not len(pronunciations) > 0:
    return "At least one pronunciation is required!"
  return None

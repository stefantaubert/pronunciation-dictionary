
from collections import OrderedDict
from typing import Any, Optional

from pronunciation_dictionary.mp_options import MultiprocessingOptions
from pronunciation_dictionary.types import PronunciationDict, Pronunciations


class ValidationError():
  # pylint: disable=no-self-use
  @property
  def default_message(self) -> str:
    return ""


class InternalError(ValidationError):
  @property
  def default_message(self) -> str:
    return "Internal error!"


def validate_dictionary(dictionary: PronunciationDict) -> Optional[str]:
  return validate_type(dictionary, OrderedDict)


def _validate_dictionary_deep(dictionary: PronunciationDict) -> Optional[str]:
  if not (isinstance(dictionary, OrderedDict)):
    return "Type needs to be 'OrderedDict'!"
  if len(dictionary) > 0:
    for k1, v1 in dictionary.items():
      if not isinstance(k1, str):
        return "Keys need to be of type 'str'!"
      if not isinstance(v1, OrderedDict):
        return "Values need to be of type 'OrderedDict'!"
      for k2, v2 in v1.items():
        if not isinstance(k2, tuple):
          return "Keys need to be of type 'tuple'!"
        if not isinstance(v2, float):
          return "Values need to be of type 'float'!"
  return None


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

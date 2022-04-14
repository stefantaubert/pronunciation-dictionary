
from collections import OrderedDict
from typing import Optional

from pronunciation_dictionary.types import PronunciationDict


class ValidationError():
  # pylint: disable=no-self-use
  @property
  def default_message(self) -> str:
    return ""


class InternalError(ValidationError):
  @property
  def default_message(self) -> str:
    return "Internal error!"


def _validate_dictionary(dictionary: PronunciationDict) -> Optional[str]:
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

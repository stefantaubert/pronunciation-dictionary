from dataclasses import dataclass
from logging import getLogger
from multiprocessing.sharedctypes import Value
from typing import Generator, Literal, Optional

from pronunciation_dictionary.globals import LIB_NAME
from pronunciation_dictionary.types import PronunciationDict
from pronunciation_dictionary.validation import validate_dictionary


@dataclass()
class SerializationOptions():
  parts_sep: Literal["TAB", "SPACE", "DOUBLE-SPACE"]
  include_counter: bool
  include_weights: bool


part_separators = {
  "TAB": "\t",
  "SPACE": " ",
  "DOUBLE-SPACE": "  ",
}


def validate_serialization_options(options: SerializationOptions) -> Optional[str]:
  if options.parts_sep not in ["TAB", "SPACE", "DOUBLE-SPACE"]:
    return "Property 'parts_sep' is invalid!"
  if not isinstance(options.include_counter, bool):
    return "Property 'include_counter' is invalid!"
  if not isinstance(options.include_weights, bool):
    return "Property 'include_weights' is invalid!"
  return None


def serialize(dictionary: PronunciationDict, options: SerializationOptions) -> Generator[str, None, None]:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := validate_serialization_options(options):
    raise ValueError(f"Parameter 'options': {msg}")
  part_separator = part_separators[options.parts_sep]
  for word, pronunciations in dictionary.items():
    if part_separator in word:
      raise ValueError(
        f"Parameter 'dictionary': Word \"{word}\" contains separator which is not allowed!")
    for counter, (pronunciation, weight) in enumerate(pronunciations.items(), start=1):
      if len(pronunciation) == 0:
        raise ValueError(
          f"Parameter 'dictionary': At least one pronunciation to word \"{word}\" is empty!")
      pron_part = " ".join(pronunciation)
      part_separator_in_any_phoneme = any(part_separator in phoneme for phoneme in pronunciation)
      if part_separator_in_any_phoneme:
        raise ValueError(
          f"Parameter 'dictionary': Pronunciation \"{pron_part}\" to word \"{word}\" contains separator which is not allowed!")
      counter_str = f"({counter})" if options.include_counter and counter > 1 else ""
      word_part = f"{word}{counter_str}{part_separator}"
      weights_part = ""
      if options.include_weights:
        weights_part = f"{weight}{part_separator}"
      line = f"{word_part}{weights_part}{pron_part}"
      yield line

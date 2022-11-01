from dataclasses import dataclass
from typing import Generator, Literal, Optional

from pronunciation_dictionary.types import Pronunciation, PronunciationDict, Pronunciations
from pronunciation_dictionary.validation import validate_dictionary

_PHONEME_SEP = " "


@dataclass()
class SerializationOptions():
  parts_sep: Literal["TAB", "SPACE", "DOUBLE-SPACE"]
  include_counter: bool
  include_weights: bool


_part_separators = {
  "TAB": "\t",
  "SPACE": " ",
  "DOUBLE-SPACE": "  ",
}


def _validate_serialization_options(options: SerializationOptions) -> Optional[str]:
  if options.parts_sep not in ["TAB", "SPACE", "DOUBLE-SPACE"]:
    return "Property 'parts_sep' is invalid!"
  if not isinstance(options.include_counter, bool):
    return "Property 'include_counter' is invalid!"
  if not isinstance(options.include_weights, bool):
    return "Property 'include_weights' is invalid!"
  return None


def serialize(dictionary: PronunciationDict, options: SerializationOptions) -> Generator[str, None, None]:
  try:
    validate_dictionary(dictionary)
  except ValueError as error:
    raise ValueError("dictionary", error.args[1]) from error

  if msg := _validate_serialization_options(options):
    raise ValueError("options", msg)

  part_separator = _part_separators[options.parts_sep]
  for word, pronunciations in dictionary.items():
    yield from _get_lines_for_pronunciation(word, pronunciations, part_separator, options.include_weights, options.include_counter)


def _get_lines_for_pronunciation(word: str, pronunciations: Pronunciations, part_separator: str, include_weights: bool, include_counter: bool) -> Generator[str, None, None]:
  for counter, (pronunciation, weight) in enumerate(pronunciations.items(), start=1):
    yield _get_line_for_pronunciation(word, pronunciation, counter, include_counter, part_separator, weight, include_weights)


def _get_line_for_pronunciation(word: str, pronunciation: Pronunciation, counter: int, include_counter: bool, part_separator: str, weight: float, include_weights: bool):
  word_part = word
  if include_counter:
    word_part = _get_word_serialized_with_counter(word, counter)
  weights_part = ""
  if include_weights:
    weights_part = f"{_get_weight_serialized(weight)}{part_separator}"
  pron_part = _get_pronunciation_serialized(pronunciation)
  line = f"{word_part}{part_separator}{weights_part}{pron_part}"
  return line


def _get_weight_serialized(weight: float) -> str:
  result = str(weight)
  return result


def _get_word_serialized_with_counter(word: str, counter: int) -> str:
  assert counter > 0
  counter_str = f"({counter})" if counter > 1 else ""
  word_part = f"{word}{counter_str}"
  return word_part


def _get_pronunciation_serialized(pronunciation: Pronunciation) -> str:
  pron_part = _PHONEME_SEP.join(pronunciation)
  return pron_part

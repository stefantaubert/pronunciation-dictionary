from dataclasses import dataclass
from typing import Literal

from pronunciation_dictionary.types import PronunciationDict, Symbol


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


def to_text(pronunciation_dict: PronunciationDict, options: SerializationOptions) -> str:
  lines = []
  part_separator = part_separators[options.parts_sep]
  for word, pronunciations in pronunciation_dict.items():
    for counter, (pronunciation, weight) in enumerate(pronunciations.items(), start=1):
      assert len(pronunciation) > 0
      counter_str = f"({counter})" if options.include_counter and counter > 1 else ""
      word_part = f"{word}{counter_str}{part_separator}"
      weights_part = ""
      if options.include_weights:
        weights_part = f"{weight}{part_separator}"
      pron_part = " ".join(pronunciation)
      line = f"{word_part}{weights_part}{pron_part}"
      lines.append(line)
  dict_content = "\n".join(lines)
  return dict_content

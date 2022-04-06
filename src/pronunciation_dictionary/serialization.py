from dataclasses import dataclass
from pronunciation_dictionary.types import PronunciationDict, Symbol


@dataclass()
class SerializationOptions():
  parts_sep: Symbol
  include_counter: bool
  include_weights: bool


def to_text(pronunciation_dict: PronunciationDict, options: SerializationOptions) -> str:
  lines = []
  for word, pronunciations in pronunciation_dict.items():
    for counter, (pronunciation, weight) in enumerate(pronunciations.items(), start=1):
      assert len(pronunciation) > 0
      counter_str = f"({counter})" if options.include_counter and counter > 1 else ""
      word_part = f"{word}{counter_str}{options.parts_sep}"
      weights_part = ""
      if options.include_weights:
        weights_part = f"{weight}{options.parts_sep}"
      pron_part = " ".join(pronunciation)
      line = f"{word_part}{weights_part}{pron_part}\n"
      lines.append(line)
  dict_content = "\n".join(lines)
  return dict_content

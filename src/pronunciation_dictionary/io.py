from pathlib import Path
from typing import List
from urllib.request import urlopen

from pronunciation_dictionary.deserialization import (DeserializationOptions, deserialize,
                                                      validate_deserialization_options)
from pronunciation_dictionary.mp_options import MultiprocessingOptions
from pronunciation_dictionary.serialization import (SerializationOptions,
                                                    _validate_serialization_options, serialize)
from pronunciation_dictionary.types import PronunciationDict
from pronunciation_dictionary.validation import (validate_dictionary, validate_mp_options,
                                                 validate_type)


def save_dict(dictionary: PronunciationDict, path: Path, encoding: str, options: SerializationOptions) -> None:
  try:
    validate_dictionary(dictionary)
  except ValueError as error:
    raise ValueError("dictionary", error.args[1]) from error
  if msg := validate_type(path, Path):
    raise ValueError(f"Parameter 'path': {msg}")
  if msg := validate_type(encoding, str):
    raise ValueError(f"Parameter 'encoding': {msg}")
  if msg := _validate_serialization_options(options):
    raise ValueError(f"Parameter 'options': {msg}")

  lines_gen = serialize(dictionary, options)
  dict_content = "\n".join(lines_gen)
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(dict_content, encoding)


def load_dict(path: Path, encoding: str, options: DeserializationOptions, mp_options: MultiprocessingOptions) -> PronunciationDict:
  if msg := validate_type(path, Path):
    raise ValueError(f"Parameter 'path': {msg}")
  if msg := validate_type(encoding, str):
    raise ValueError(f"Parameter 'encoding': {msg}")
  if msg := validate_deserialization_options(options):
    raise ValueError(f"Parameter 'options': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  text = path.read_text(encoding)
  lines = text.splitlines()
  result = deserialize(lines, options, mp_options)
  return result


def load_dict_from_url(url: str, encoding: str, options: DeserializationOptions, mp_options: MultiprocessingOptions) -> PronunciationDict:
  if msg := validate_type(url, str):
    raise ValueError(f"Parameter 'url': {msg}")
  if msg := validate_type(encoding, str):
    raise ValueError(f"Parameter 'encoding': {msg}")
  if msg := validate_deserialization_options(options):
    raise ValueError(f"Parameter 'options': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  lines = __read_lines_from_url(url, encoding)
  result = deserialize(lines, options, mp_options)
  return result


def __read_lines_from_url(url: str, encoding: str) -> List[str]:
  with urlopen(url) as url_content:
    result = [line.decode(encoding) for line in url_content]
  return result

from logging import getLogger
from pathlib import Path
from typing import Optional

from pronunciation_dictionary.deserialization import (DeserializationOptions,
                                                      MultiprocessingOptions,
                                                      parse_lines)
from pronunciation_dictionary.serialization import (SerializationOptions,
                                                    to_text)
from pronunciation_dictionary.types import PronunciationDict


def save_dict(pronunciation_dict: PronunciationDict, path: Path, encoding: str, options: SerializationOptions):
  dict_content = to_text(pronunciation_dict, options)
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(dict_content, encoding)


def try_save_dict(pronunciation_dict: PronunciationDict, path: Path, encoding: str, options: SerializationOptions) -> bool:
  try:
    save_dict(pronunciation_dict, path, encoding, options)
  except Exception as ex:
    logger = getLogger(__name__)
    logger.debug(ex)
    return False
  return True


def load_dict(path: Path, encoding: str, options: DeserializationOptions, mp_options: MultiprocessingOptions) -> PronunciationDict:
  text = path.read_text(encoding)
  lines = text.splitlines()
  result = parse_lines(lines, options, mp_options)
  return result


def try_load_dict(path: Path, encoding: str, options: DeserializationOptions, mp_options: MultiprocessingOptions) -> Optional[PronunciationDict]:
  try:
    result = load_dict(path, encoding, options, mp_options)
  except Exception as ex:
    logger = getLogger(__name__)
    logger.debug(ex)
    return None
  return result

from logging import getLogger
from pathlib import Path
from typing import Optional

from pronunciation_dictionary import DeserializationOptions, MultiprocessingOptions
from pronunciation_dictionary import load_dict, save_dict
from pronunciation_dictionary import SerializationOptions
from pronunciation_dictionary import PronunciationDict


def try_save_dict(pronunciation_dict: PronunciationDict, path: Path, encoding: str, options: SerializationOptions) -> bool:
  try:
    save_dict(pronunciation_dict, path, encoding, options)
  except Exception as ex:
    logger = getLogger(__name__)
    logger.debug(ex)
    return False
  return True


def try_load_dict(path: Path, encoding: str, options: DeserializationOptions, mp_options: MultiprocessingOptions) -> Optional[PronunciationDict]:
  try:
    result = load_dict(path, encoding, options, mp_options)
  except Exception as ex:
    logger = getLogger(__name__)
    logger.debug(ex)
    return None
  return result

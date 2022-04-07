import argparse
import codecs
from argparse import ArgumentParser, ArgumentTypeError
from functools import partial
from multiprocessing import cpu_count
from pathlib import Path
from typing import Callable, List, Optional, TypeVar

from ordered_set import OrderedSet

from pronunciation_dictionary.globals import DEFAULT_CHUNKSIZE, DEFAULT_ENCODING, DEFAULT_MAXTASKSPERCHILD, DEFAULT_N_JOBS

T = TypeVar("T")


def add_mp_group(parser: ArgumentParser) -> None:
  mp_group = parser.add_argument_group('multiprocessing arguments')
  add_n_jobs_argument(mp_group)
  add_chunksize_argument(mp_group)
  add_maxtaskperchild_argument(mp_group)


def add_io_group(parser: ArgumentParser) -> None:
  """ use this for modification of dictionary content """
  group = parser.add_argument_group('I/O arguments used for serialization/deserialization')
  add_encoding_argument(group, "-e", "--encoding",
                        "encoding used for serialization/deserialization")
  group.add_argument("-cc", "--consider-comments", action="store_true",
                     help="consider line comments while deserialization")
  group.add_argument("-cn", "--consider-numbers", action="store_true",
                     help="consider word numbers used to separate different pronunciations while serialization/deserialization")
  group.add_argument("-cp", "--consider-pronunciation-comments", action="store_true",
                     help="consider comments in pronunciations while deserialization")
  group.add_argument("-cw", "--consider-weights", action="store_true",
                     help="consider weights while serialization/deserialization")
  group.add_argument("-ps", "--parts-sep", type=parse_non_empty,
                     help="symbol to separate word/weight/pronunciation in a line while serialization", choices=["TAB", "SPACE", "DOUBLE-SPACE"], default="DOUBLE-SPACE")


def add_serialization_group(parser: ArgumentParser) -> None:
  group = parser.add_argument_group('serialization arguments')
  add_encoding_argument(group, "-se", "--serialization-encoding", "encoding")
  group.add_argument("-ps", "--parts-sep", type=parse_non_empty,
                     help="symbol to separate word/weight/pronunciation in a line", choices=["TAB", "SPACE", "DOUBLE-SPACE"], default="DOUBLE-SPACE")
  group.add_argument("-in", "--include-numbers", action="store_true",
                     help="include word numbers")
  group.add_argument("-iw", "--include-weights", action="store_true",
                     help="include weights")


def add_deserialization_group(parser: ArgumentParser) -> None:
  group = parser.add_argument_group('deserialization arguments')
  add_encoding_argument(group, "-de", "--deserialization-encoding", "encoding")
  group.add_argument("-cc", "--consider-comments", action="store_true",
                     help="consider line comments while deserialization")
  group.add_argument("-cn", "--consider-numbers", action="store_true",
                     help="consider word numbers used to separate different pronunciations")
  group.add_argument("-cp", "--consider-pronunciation-comments", action="store_true",
                     help="consider comments in pronunciations")
  group.add_argument("-cw", "--consider-weights", action="store_true",
                     help="consider weights")


def add_encoding_argument(parser: ArgumentParser, short_var: str, variable: str, help_str: str) -> None:
  parser.add_argument(short_var, variable, type=parse_codec, metavar='CODEC',
                      help=help_str + "; see all available codecs at https://docs.python.org/3.8/library/codecs.html#standard-encodings", default=DEFAULT_ENCODING)

def add_n_jobs_argument(parser: ArgumentParser) -> None:
  parser.add_argument("-j", "--n-jobs", metavar='N', type=int,
                      choices=range(1, cpu_count() + 1), default=DEFAULT_N_JOBS, help="amount of parallel cpu jobs")


def add_chunksize_argument(parser: ArgumentParser, target: str = "words", default: int = DEFAULT_CHUNKSIZE) -> None:
  parser.add_argument("-c", "--chunksize", type=parse_positive_integer, metavar="NUMBER",
                      help=f"amount of {target} to chunk into one job", default=default)


def add_maxtaskperchild_argument(parser: ArgumentParser) -> None:
  parser.add_argument("-mt", "--maxtasksperchild", type=get_optional(parse_positive_integer), metavar="NUMBER",
                      help="amount of tasks per child", default=DEFAULT_MAXTASKSPERCHILD)


class ConvertToOrderedSetAction(argparse._StoreAction):
  def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Optional[List], option_string: Optional[str] = None):
    if values is not None:
      values = OrderedSet(values)
    super().__call__(parser, namespace, values, option_string)


def parse_codec(value: str) -> str:
  value = parse_required(value)
  try:
    codecs.lookup(value)
  except LookupError as error:
    raise ArgumentTypeError("Codec was not found!") from error
  return value


def parse_path(value: str) -> Path:
  value = parse_required(value)
  try:
    path = Path(value)
  except ValueError as error:
    raise ArgumentTypeError("Value needs to be a path!") from error
  return path


def parse_optional_value(value: str, method: Callable[[str], T]) -> Optional[T]:
  if value is None:
    return None
  return method(value)


def get_optional(method: Callable[[str], T]) -> Callable[[str], Optional[T]]:
  result = partial(
    parse_optional_value,
    method=method,
  )
  return result


def parse_existing_file(value: str) -> Path:
  path = parse_path(value)
  if not path.is_file():
    raise ArgumentTypeError("File was not found!")
  return path


def parse_existing_directory(value: str) -> Path:
  path = parse_path(value)
  if not path.is_dir():
    raise ArgumentTypeError("Directory was not found!")
  return path


def parse_required(value: Optional[str]) -> str:
  if value is None:
    raise ArgumentTypeError("Value must not be None!")
  return value


def parse_non_empty(value: Optional[str]) -> str:
  value = parse_required(value)
  if value == "":
    raise ArgumentTypeError("Value must not be empty!")
  return value


def parse_non_empty_or_whitespace(value: str) -> str:
  value = parse_required(value)
  if value.strip() == "":
    raise ArgumentTypeError("Value must not be empty or whitespace!")
  return value


def parse_float(value: str) -> float:
  value = parse_required(value)
  try:
    value = float(value)
  except ValueError as error:
    raise ArgumentTypeError("Value needs to be a decimal number!") from error
  return value


def parse_positive_float(value: str) -> float:
  value = parse_float(value)
  if not value > 0:
    raise ArgumentTypeError("Value needs to be greater than zero!")
  return value


def parse_non_negative_float(value: str) -> float:
  value = parse_float(value)
  if not value >= 0:
    raise ArgumentTypeError("Value needs to be greater than or equal to zero!")
  return value


def parse_float_0_to_1(value: str) -> float:
  value = parse_float(value)
  if not 0 <= value <= 1:
    raise ArgumentTypeError("Value needs to be between zero (incl.) and one (incl.)!")
  return value


def parse_integer(value: str) -> int:
  value = parse_required(value)
  if not value.isdigit():
    raise ArgumentTypeError("Value needs to be an integer!")
  value = int(value)
  return value


def parse_positive_integer(value: str) -> int:
  value = parse_integer(value)
  if not value > 0:
    raise ArgumentTypeError("Value needs to be greater than zero!")
  return value


def parse_non_negative_integer(value: str) -> int:
  value = parse_integer(value)
  if not value >= 0:
    raise ArgumentTypeError("Value needs to be greater than or equal to zero!")
  return value

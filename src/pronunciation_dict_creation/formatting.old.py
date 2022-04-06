from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from typing import Optional

from pronunciation_dict_parser.app.common import \
    add_default_input_formatting_arguments
from pronunciation_dict_parser.app.helper import save_dictionary_as_txt
from pronunciation_dict_parser.core.parser import parse_dictionary_from_txt
from pronunciation_dict_parser.core.types import Symbol


def get_formatting_parser(parser: ArgumentParser):
  parser.description = ""
  parser.add_argument("path", metavar='path', type=Path,
                      help="path to dictionary")
  add_default_input_formatting_arguments(parser)
  parser.add_argument("--output-path", metavar='PATH', type=Path,
                      help="custom path to write the dictionary if not same")
  parser.add_argument("--output-include-counter", action="store_true",
                      help="include counter for multiple pronunciations per word in output")
  parser.add_argument("--output-only-first-pronunciation", action="store_true",
                      help="include only the first pronunciation in output")
  parser.add_argument("--output-symbol-sep", type=str, metavar="CHAR",
                      help="custom output separator of symbols", default=None)
  parser.add_argument("--output-empty-symbol", type=str, metavar="CHAR",
                      help="symbol to use if no pronunciation exist", default=None)
  parser.add_argument("--output-pronunciation-sep", type=str, metavar="CHAR",
                      help="custom output separator of word and pronunciation", default=None)
  parser.add_argument("--output-encoding", type=str, metavar="ENCODING",
                      help="custom output encoding", default=None)
  parser.add_argument("-o", "--overwrite", action="store_true",
                      help="overwrite file if it exists")
  return app_adjust_formatting


def app_adjust_formatting(path: Path, output_path: Optional[Path], pronunciation_sep: Symbol, symbol_sep: Symbol, have_counter: bool, empty_symbol: Optional[Symbol], encoding: str, output_pronunciation_sep: Optional[Symbol], output_symbol_sep: Optional[Symbol], output_include_counter: bool, output_only_first_pronunciation: bool, output_empty_symbol: Optional[Symbol], output_encoding: Optional[str], overwrite: bool):
  logger = getLogger(__name__)

  if not path.exists():
    logger.error("File does not exist!")
    return

  if not overwrite and output_path.is_file():
    logger.error("Output file already exists!")
    return

  pronunciation_dict = parse_dictionary_from_txt(
    path, encoding, pronunciation_sep, symbol_sep, have_counter, empty_symbol)

  if output_encoding is None:
    output_encoding = encoding
  if output_pronunciation_sep is None:
    output_pronunciation_sep = pronunciation_sep
  if output_symbol_sep is None:
    output_symbol_sep = symbol_sep
  if output_empty_symbol is None:
    output_empty_symbol = empty_symbol
  assert output_include_counter is not None
  assert output_only_first_pronunciation is not None

  save_dictionary_as_txt(path, pronunciation_dict, output_encoding, output_pronunciation_sep,
                         output_symbol_sep, output_include_counter, output_only_first_pronunciation, output_empty_symbol)

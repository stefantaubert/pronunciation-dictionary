import argparse
import importlib.metadata
import logging
import sys
from argparse import ArgumentParser
from logging import getLogger
from typing import Callable, Generator, List, Tuple

from pronunciation_dictionary_cli.formatting_adjustment import get_formatting_parser
from pronunciation_dictionary_cli.merging import get_merging_parser
from pronunciation_dictionary_cli.phoneme_set_extraction import get_phoneme_set_extraction_parser
from pronunciation_dictionary_cli.pronunciations_remove_symbols import \
  get_pronunciations_remove_symbols_parser
from pronunciation_dictionary_cli.single_pronunciation_selection import \
  get_single_pronunciation_selection_parser
from pronunciation_dictionary_cli.subset_extraction import get_subset_extraction_parser
from pronunciation_dictionary_cli.vocabulary_extraction import get_vocabulary_extraction_parser
from pronunciation_dictionary_cli.words_casing_adjustment import get_words_casing_adjustment_parser
from pronunciation_dictionary_cli.words_remove_symbols import get_words_remove_symbols_parser

__version__ = importlib.metadata.version("pronunciation-dictionary")

INVOKE_HANDLER_VAR = "invoke_handler"


Parsers = Generator[Tuple[str, str, Callable], None, None]


def formatter(prog):
  return argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=40)


def _init_parser():
  main_parser = ArgumentParser(
    formatter_class=formatter,
    description="This program provides methods to modify pronunciation dictionaries.",
  )
  main_parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
  subparsers = main_parser.add_subparsers(help="description")

  methods: Parsers = (
    ("export-vocabulary", "export vocabulary from dictionaries",
     get_vocabulary_extraction_parser),
    ("export-phonemes", "export phoneme set from dictionaries",
     get_phoneme_set_extraction_parser),
    ("merge", "merge dictionaries into one",
     get_merging_parser),
    ("extract", "extract subset of dictionary vocabulary",
     get_subset_extraction_parser),
    ("remove-symbols-from-pronunciations", "remove phonemes/symbols from pronunciations",
     get_pronunciations_remove_symbols_parser),
    ("remove-symbols-from-words", "remove characters/symbols from words",
     get_words_remove_symbols_parser),
    ("change-formatting", "change formatting of dictionaries",
     get_formatting_parser),
    ("select-single-pronunciation", "select a single pronunciation by discarding all alternative ones",
     get_single_pronunciation_selection_parser),
    ("change-word-casing", "transform all words to upper- or lowercase",
     get_words_casing_adjustment_parser),
  )

  for command, description, method in methods:
    method_parser = subparsers.add_parser(
      command, help=description, formatter_class=formatter)
    method_parser.set_defaults(**{
      INVOKE_HANDLER_VAR: method(method_parser),
    })

  return main_parser


def configure_logger() -> None:
  loglevel = logging.DEBUG if __debug__ else logging.INFO
  main_logger = getLogger()
  main_logger.setLevel(loglevel)
  main_logger.manager.disable = logging.NOTSET
  if len(main_logger.handlers) > 0:
    console = main_logger.handlers[0]
  else:
    console = logging.StreamHandler()
    main_logger.addHandler(console)

  logging_formatter = logging.Formatter(
    '[%(asctime)s.%(msecs)03d] (%(levelname)s) %(message)s',
    '%Y/%m/%d %H:%M:%S',
  )
  console.setFormatter(logging_formatter)
  console.setLevel(loglevel)


def parse_args(args: List[str]):
  configure_logger()
  logger = getLogger(__name__)
  logger.debug("Received args:")
  logger.debug(args)
  parser = _init_parser()
  received_args = parser.parse_args(args)
  params = vars(received_args)

  if INVOKE_HANDLER_VAR in params:
    invoke_handler: Callable[[ArgumentParser], None] = params.pop(INVOKE_HANDLER_VAR)
    invoke_handler(received_args)
  else:
    parser.print_help()


def run():
  arguments = sys.argv[1:]
  parse_args(arguments)


if __name__ == "__main__":
  run()

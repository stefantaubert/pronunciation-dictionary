import sys
import argparse
import logging
from argparse import ArgumentParser
from logging import getLogger
from typing import Callable, Dict, Generator, List, Tuple
from pronunciation_dict_creation.downloading import get_downloading_parser
from pronunciation_dict_creation.from_lookup_dict import get_app_try_add_vocabulary_from_pronunciations_parser
from pronunciation_dict_creation.merging import get_merging_parser
from pronunciation_dict_creation.pronunciations_remove_symbols import get_pronunciations_remove_symbols_parser
from pronunciation_dict_creation.words_remove_symbols import get_words_remove_symbols_parser

__version__ = "0.0.1"

INVOKE_HANDLER_VAR = "invoke_handler"


Parsers = Generator[Tuple[str, str, Callable], None, None]


def formatter(prog):
  return argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=40)


def _init_parser():
  main_parser = ArgumentParser(
    formatter_class=formatter,
    description="This program provides methods to create pronunciation dictionaries.",
  )
  main_parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
  subparsers = main_parser.add_subparsers(help="description")

  methods: Dict[str, Tuple[Parsers, str]] = (
    ("download", "download public dictionary",
     get_downloading_parser),
    ("create-from-dict", "add vocabulary with a dictionary",
     get_app_try_add_vocabulary_from_pronunciations_parser),
    ("merge", "merge dictionaries",
     get_merging_parser),
    ("remove-symbols-from-pronunciations", "remove symbols from pronunciations",
     get_pronunciations_remove_symbols_parser),
    ("remove-symbols-from-words", "remove symbols from words",
     get_words_remove_symbols_parser),
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
    invoke_handler(**params)
  else:
    parser.print_help()


if __name__ == "__main__":
  arguments = sys.argv[1:]
  parse_args(arguments)

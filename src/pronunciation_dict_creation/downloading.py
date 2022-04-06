from collections import OrderedDict
from dataclasses import dataclass
from logging import getLogger

from pronunciation_dict_parser import PronunciationDict
from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from tempfile import gettempdir


from pathlib import Path

from pronunciation_dict_parser import get_dict_from_url, MultiprocessingOptions, LineParsingOptions
from pronunciation_dict_creation.argparse_helper import parse_path

from pronunciation_dict_creation.common import PROG_ENCODING, try_save_dict, to_text

# https://github.com/MontrealCorpusTools/mfa-models/tree/main/dictionary/english


@dataclass()
class PublicDict():
  url: str
  encoding: str
  description: str
  options: LineParsingOptions


public_dicts = OrderedDict((
  ("cmu", PublicDict(
    "https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict",
    "ISO-8859-1", "CMU (ARPA)", LineParsingOptions(False, True, True, False))),
  ("cmu-alt", PublicDict(
    "http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b",
    "ISO-8859-1", "CMU (ARPA)", LineParsingOptions(True, True, False, False))),
  ("librispeech", PublicDict(
    "https://www.openslr.org/resources/11/librispeech-lexicon.txt",
    "UTF-8", "LibriSpeech (ARPA)", LineParsingOptions(False, False, False, False))),
  ("mfa-arpa", PublicDict(
    "https://raw.githubusercontent.com/MontrealCorpusTools/mfa-models/main/dictionary/english.dict", "UTF-8", "MFA V1 (ARPA)", LineParsingOptions(False, False, False, False))),
  ("mfa-arpa-v2", PublicDict(
    "https://raw.githubusercontent.com/MontrealCorpusTools/mfa-models/main/dictionary/english/us_arpa/v2.0.0/english_us_arpa.dict", "UTF-8", "MFA V2 (ARPA)", LineParsingOptions(False, False, False, False))),
  ("mfa-ipa-v2", PublicDict(
    "https://raw.githubusercontent.com/MontrealCorpusTools/mfa-models/main/dictionary/english/mfa/v2.0.0/english_mfa.dict", "UTF-8", "MFA V2 (IPA)", LineParsingOptions(False, False, False, False))),
  ("prosodylab", PublicDict(
    "https://raw.githubusercontent.com/prosodylab/Prosodylab-Aligner/master/eng.dict",
    "UTF-8", "Prosodylab (ARPA)", LineParsingOptions(False, False, False, False))),
))


def get_downloading_parser(parser: ArgumentParser):
  parser.description = "Download a public dictionary."
  default_path = Path(gettempdir()) / "pronunciations.dict"
  parser.add_argument("dictionary", metavar='NAME', choices=list(public_dicts.keys()),
                      type=str, help="pronunciation dictionary")
  parser.add_argument("--path", type=parse_path, metavar='PATH',
                      help="file where to output pronunciation dictionary", default=default_path)
  # todo add mp params
  return app_download


def app_download(dictionary: str, path: Path) -> bool:
  logger = getLogger(__name__)

  pronunciation_dict = download_dict(dictionary)
  success = try_save_dict(pronunciation_dict, path)
  if not success:
    logger.error("Dictionary couldn't be written.")
    return False

  logger.info(f"Written dictionary to: {path.absolute()}")
  return True


def download_dict(dictionary: str) -> PronunciationDict:
  assert dictionary in public_dicts

  logger = getLogger(__name__)
  dictionary_info = public_dicts[dictionary]

  logger.info(f"Downloading {dictionary_info.description}...")

  pronunciation_dict = get_dict_from_url(dictionary_info.url, dictionary_info.encoding)
  return pronunciation_dict

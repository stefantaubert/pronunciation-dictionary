from tqdm import tqdm
from dataclasses import dataclass
from email.policy import default
from functools import partial
from multiprocessing.pool import Pool
from typing import Literal, Optional, Set, Tuple
from pronunciation_dict_parser import Pronunciation, PronunciationDict, Symbol, Word, Pronunciations
from ordered_set import OrderedSet


from pronunciation_dict_creation.common import DefaultParameters


def try_add_vocabulary_from_g2p(default_params: DefaultParameters) -> OrderedSet[Word]:
  pass


def try_add_vocabulary_from_epitran(default_params: DefaultParameters, lang: str):
  pass


def try_add_vocabulary_from_hanzy(default_params: DefaultParameters) -> OrderedSet[Word]:
  pass

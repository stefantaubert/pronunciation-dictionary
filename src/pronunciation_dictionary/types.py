from collections import OrderedDict
from dataclasses import dataclass
from typing import List, Optional
from typing import OrderedDict as OrderedDictType
from typing import Protocol, Tuple, TypeVar

Word = str
Symbol = str
Weight = float
Pronunciation = Tuple[Symbol, ...]
Pronunciations = OrderedDictType[Pronunciation, Weight]
PronunciationDict = OrderedDictType[Word, Pronunciations]

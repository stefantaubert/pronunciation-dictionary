from typing import OrderedDict as OrderedDictType
from typing import Tuple

Word = str
Symbol = str
Weight = float
Pronunciation = Tuple[Symbol, ...]
Pronunciations = OrderedDictType[Pronunciation, Weight]
PronunciationDict = OrderedDictType[Word, Pronunciations]

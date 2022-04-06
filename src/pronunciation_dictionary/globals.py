from multiprocessing import cpu_count
from ordered_set import OrderedSet

DEFAULT_ENCODING = "UTF-8"
DEFAULT_N_JOBS = cpu_count()
DEFAULT_CHUNKSIZE = 1000
DEFAULT_MAXTASKSPERCHILD = None


PROG_SYMBOL_SEP = " "
PROG_WORD_SEP = "  "
PROG_INCLUDE_COUNTER = False
PROG_EMPTY_SYMBOL = ""
PROG_INCL_WEIGHTS = True
PROG_ONLY_FIRST = False
PROG_ENCODING = "UTF-8"
PROG_CONS_COMMENTS = False
PROG_CONS_WORD_NRS = False
PROG_CONS_PRON_COMMENTS = False
PROG_CONS_WEIGHTS = True

DEFAULT_PUNCTUATION = list(OrderedSet(sorted((
  "!", "\"", "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "{", "}", "~", "`",
  "、", "。", "？", "！", "：", "；", "।", "¿", "¡", "【", "】", "，", "…", "‥", "「", "」", "『", "』", "〝", "〟", "″", "⟨", "⟩", "♪", "・", "‹", "›", "«", "»", "～", "′", "“", "”"
))))

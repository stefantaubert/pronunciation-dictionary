
def prepare_dict_mode(lookup_dict: PronunciationDict, lookup_ignore_case: bool, mode: Literal["first", "all"]) -> PronunciationDict:
  if mode == "all" and not lookup_ignore_case:
    return lookup_dict
  result = PronunciationDict()
  for word, pronunciations in lookup_dict.items():
    if lookup_ignore_case:
      word = word.lower()
    if mode == "first":
      pronunciations = OrderedSet((pronunciations[0],))
    if word in result:
      if mode == "all":
        result[word].update(pronunciations)
    else:
      result[word] = pronunciations
  return result

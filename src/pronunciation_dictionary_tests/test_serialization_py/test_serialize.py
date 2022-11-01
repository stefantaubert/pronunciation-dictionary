from pronunciation_dictionary.serialization import SerializationOptions, serialize
from pronunciation_dictionary.types import PronunciationDict, Pronunciations


def test_weights_are_excluded():
  dictionary = PronunciationDict()
  test_pronunciations = Pronunciations()
  test_pronunciations[("T", "E", "S", "T1")] = 0.25
  test_pronunciations[("T", "E", "S", "T2")] = 0.75

  test_pronunciations_2 = Pronunciations()
  test_pronunciations_2[("X", "Y")] = 1.0
  dictionary["test"] = test_pronunciations
  dictionary["XY"] = test_pronunciations_2

  lines = list(serialize(dictionary, SerializationOptions("TAB", True, False)))

  assert len(lines) == 3
  assert lines[0] == 'test\tT E S T1'
  assert lines[1] == 'test(2)\tT E S T2'
  assert lines[2] == 'XY\tX Y'


def test_weights_are_included():
  dictionary = PronunciationDict()
  test_pronunciations = Pronunciations()
  test_pronunciations[("T", "E", "S", "T1")] = 0.25
  test_pronunciations[("T", "E", "S", "T2")] = 0.75

  test_pronunciations_2 = Pronunciations()
  test_pronunciations_2[("X", "Y")] = 1.0
  dictionary["test"] = test_pronunciations
  dictionary["XY"] = test_pronunciations_2

  lines = list(serialize(dictionary, SerializationOptions("TAB", True, True)))

  assert len(lines) == 3
  assert lines[0] == 'test\t0.25\tT E S T1'
  assert lines[1] == 'test(2)\t0.75\tT E S T2'
  assert lines[2] == 'XY\t1.0\tX Y'

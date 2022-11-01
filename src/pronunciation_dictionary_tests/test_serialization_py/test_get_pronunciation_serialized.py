from pronunciation_dictionary.serialization import _get_pronunciation_serialized


def test_one_phoneme__returns_phoneme():
  result = _get_pronunciation_serialized(("A",))
  assert result == "A"


def test_two_one_phoneme__returns_phonemes_separated_py_space():
  result = _get_pronunciation_serialized(("A", "B"))
  assert result == "A B"

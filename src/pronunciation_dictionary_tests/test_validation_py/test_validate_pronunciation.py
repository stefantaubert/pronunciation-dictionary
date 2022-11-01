from pytest import raises

from pronunciation_dictionary.validation import validate_pronunciation


def test_normal_not_raises_error():
  validate_pronunciation(("A", "B"))


def test_empty_pronunciation_raises_error():
  with raises(ValueError) as error:
    validate_pronunciation(tuple())

  assert error.value.args == (
    "pronunciation",
    "Pronunciation is empty!"
  )


def test_whitespace_in_phoneme_raises_error():
  pronunciations = ("T", "A ")

  with raises(ValueError) as error:
    validate_pronunciation(pronunciations)

  assert error.value.args == (
    "pronunciation",
    'Pronunciation contains whitespace which is not allowed!'
  )


def test_whitespace_as_phoneme_raises_error():
  pronunciations = ("T", " ")

  with raises(ValueError) as error:
    validate_pronunciation(pronunciations)

  assert error.value.args == (
    "pronunciation",
    'Pronunciation contains whitespace which is not allowed!'
  )

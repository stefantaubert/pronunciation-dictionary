from pytest import raises

from pronunciation_dictionary.validation import validate_word


def test_normal_not_raise_error():
  validate_word("test")


def test_empty_word_raises_error():
  with raises(ValueError) as error:
    validate_word("")

  assert error.value.args == (
    "word",
    "Empty words is not allowed!"
  )


def test_word_is_int_raises_error():
  with raises(ValueError) as error:
    validate_word(2)

  assert error.value.args == (
    "word",
    "Word need to be of type 'str'!"
  )


def test_word_contains_whitespace_raises_error():
  with raises(ValueError) as error:
    validate_word("tes t")

  assert error.value.args == (
    "word",
    "Word contains whitespace which is not allowed!"
  )

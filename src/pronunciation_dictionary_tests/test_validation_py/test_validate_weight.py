from pytest import raises

from pronunciation_dictionary.validation import validate_weight


def test_int_is_valid():
  validate_weight(2)


def test_float_is_valid():
  validate_weight(2.2)


def test_str_raises_value_error():
  with raises(ValueError) as error:
    validate_weight("test")

  assert error.value.args == (
    "weight",
    "Weight needs to be of type 'float' or 'int'!"
  )

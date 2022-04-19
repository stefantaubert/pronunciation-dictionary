import pytest

from pronunciation_dictionary.validation import validate_dictionary


def test_dict__raises_ValueError():
  result = validate_dictionary({})
  assert result

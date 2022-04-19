import pytest

from pronunciation_dictionary import validate_dictionary


def test_dict__raises_ValueError():
  with pytest.raises(ValueError):
    validate_dictionary({})
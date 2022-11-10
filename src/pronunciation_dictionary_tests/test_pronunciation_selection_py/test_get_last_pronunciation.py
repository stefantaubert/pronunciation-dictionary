from collections import OrderedDict

import pytest

from pronunciation_dictionary.pronunciation_selection import get_last_pronunciation


def test_component():
  pronunciations = OrderedDict()
  pronunciations[("c",)] = 1.0
  pronunciations[("b", "f")] = 2.0
  pronunciations[("a",)] = 2.0
  pronunciations[("x",)] = 2.0
  pronunciations[("z", "y")] = 2.0
  pronunciations[("x", "x")] = 1.0
  result = get_last_pronunciation(pronunciations)
  assert result == ("x", "x")


def test_two_different_returns_last():
  pronunciations = OrderedDict()
  pronunciations[("a",)] = 1.0
  pronunciations[("b",)] = 2.0
  result = get_last_pronunciation(pronunciations)
  assert result == ("b",)


def test_three_with_two_same_returns_last():
  pronunciations = OrderedDict()
  pronunciations[("c",)] = 1.0
  pronunciations[("b",)] = 2.0
  pronunciations[("a",)] = 2.0
  result = get_last_pronunciation(pronunciations)
  assert result == ("a",)


def test_two_same_returns_last():
  pronunciations = OrderedDict()
  pronunciations[("b",)] = 1.0
  pronunciations[("a",)] = 1.0
  result = get_last_pronunciation(pronunciations)
  assert result == ("a",)


def test_one_returns_one():
  pronunciations = OrderedDict()
  pronunciations[("a",)] = 1.0
  result = get_last_pronunciation(pronunciations)
  assert result == ("a",)


def test_empty_raise_error():
  pronunciations = OrderedDict()
  with pytest.raises(ValueError) as error:
    get_last_pronunciation(pronunciations)

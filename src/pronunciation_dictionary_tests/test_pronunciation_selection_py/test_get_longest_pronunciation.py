from collections import OrderedDict

import pytest

from pronunciation_dictionary.pronunciation_selection import get_longest_pronunciation


def test_component():
  pronunciations = OrderedDict()
  pronunciations[("c",)] = 1.0
  pronunciations[("b", "f")] = 2.0
  pronunciations[("a",)] = 2.0
  pronunciations[("x",)] = 2.0
  pronunciations[("z", "y", "a")] = 2.0
  pronunciations[("x", "x", "b")] = 1.0
  result = get_longest_pronunciation(pronunciations)
  assert result == ("z", "y", "a")


def test_one_returns_one():
  pronunciations = OrderedDict()
  pronunciations[("a",)] = 1.0
  result = get_longest_pronunciation(pronunciations)
  assert result == ("a",)


def test_two_same_returns_first():
  pronunciations = OrderedDict()
  pronunciations[("a",)] = 1.0
  pronunciations[("b",)] = 1.0
  result = get_longest_pronunciation(pronunciations)
  assert result == ("a",)


def test_long_short_returns_long():
  pronunciations = OrderedDict()
  pronunciations[("a",)] = 1.0
  pronunciations[("b", "c")] = 1.0
  result = get_longest_pronunciation(pronunciations)
  assert result == ("b", "c")


def test_three_with_two_same_returns_first():
  pronunciations = OrderedDict()
  pronunciations[("c",)] = 1.0
  pronunciations[("b",)] = 2.0
  pronunciations[("a",)] = 2.0
  result = get_longest_pronunciation(pronunciations)
  assert result == ("c",)


def test_empty_raise_error():
  pronunciations = OrderedDict()
  with pytest.raises(ValueError) as error:
    get_longest_pronunciation(pronunciations)

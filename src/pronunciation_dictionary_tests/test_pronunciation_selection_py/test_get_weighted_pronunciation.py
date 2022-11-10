from collections import OrderedDict

import pytest

from pronunciation_dictionary.pronunciation_selection import get_weighted_pronunciation


def test_component():
  pronunciations = OrderedDict()
  pronunciations[("b", "f")] = 1e-20
  pronunciations[("a",)] = 1e-20
  pronunciations[("c",)] = 1e-20
  pronunciations[("x",)] = 1e-20
  pronunciations[("z", "y")] = 1e20
  pronunciations[("x", "x")] = 1e-20
  result = get_weighted_pronunciation(pronunciations, None)
  assert result == ("z", "y")


def test_two_really_different_returns_most_probable():
  pronunciations = OrderedDict()
  pronunciations[("a",)] = 1e-20
  pronunciations[("b",)] = 1e20
  result = get_weighted_pronunciation(pronunciations, None)
  assert result == ("b",)


def test_two_same_with_seed_returns_always_same():
  pronunciations = OrderedDict()
  pronunciations[("b",)] = 1.0
  pronunciations[("a",)] = 1.0
  result = get_weighted_pronunciation(pronunciations, 123)
  assert result == ("b",)


def test_one_returns_one():
  pronunciations = OrderedDict()
  pronunciations[("a",)] = 1.0
  result = get_weighted_pronunciation(pronunciations, None)
  assert result == ("a",)


def test_empty_raise_error():
  pronunciations = OrderedDict()
  with pytest.raises(ValueError) as error:
    get_weighted_pronunciation(pronunciations, None)

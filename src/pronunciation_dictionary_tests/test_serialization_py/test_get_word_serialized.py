from pronunciation_dictionary.serialization import _get_word_serialized_with_counter


def test_counter_2_is_included():
  result = _get_word_serialized_with_counter("test", 2)
  assert result == "test(2)"


def test_counter_3_is_included():
  result = _get_word_serialized_with_counter("test", 3)
  assert result == "test(3)"


def test_counter_1__is_not_included():
  result = _get_word_serialized_with_counter("test", 1)
  assert result == "test"

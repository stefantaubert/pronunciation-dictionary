from pronunciation_dictionary.serialization import _get_weight_serialized


def test_float_is_converted_to_str():
  result = _get_weight_serialized(1.2)
  assert result == "1.2"


def test_int_is_converted_to_str():
  result = _get_weight_serialized(2)
  assert result == "2"

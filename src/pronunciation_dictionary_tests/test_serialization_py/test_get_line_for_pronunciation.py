from pronunciation_dictionary.serialization import _get_line_for_pronunciation


def test_counter_weight():
  line = _get_line_for_pronunciation("test", ("T", "E", "S", "T1"), 2, True, "\t", 2.1, True)

  assert line == "test(2)\t2.1\tT E S T1"


def test_no_counter_weight():
  line = _get_line_for_pronunciation("test", ("T", "E", "S", "T1"), 2, False, "\t", 2.1, True)

  assert line == "test\t2.1\tT E S T1"


def test_counter_no_weight():
  line = _get_line_for_pronunciation("test", ("T", "E", "S", "T1"), 2, True, "\t", 2.1, False)

  assert line == "test(2)\tT E S T1"


def test_no_counter_no_weight():
  line = _get_line_for_pronunciation("test", ("T", "E", "S", "T1"), 2, False, "\t", 2.1, False)

  assert line == "test\tT E S T1"

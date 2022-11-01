from pytest import raises

from pronunciation_dictionary.types import PronunciationDict, Pronunciations
from pronunciation_dictionary.validation import validate_dictionary


def test_normal_dict_raises_error():
  with raises(ValueError) as error:
    validate_dictionary({})

  assert error.value.args == (
    "dictionary",
    "Type needs to be 'OrderedDict'!"
  )


def test_pronunciations_normal_dict_raises_error():
  dictionary = PronunciationDict()
  dictionary["test"] = {}
  with raises(ValueError) as error:
    validate_dictionary(dictionary)

  assert error.value.args == (
    "dictionary",
    "Pronunciations need to be of type 'OrderedDict'!"
  )


def test_error_in_word_updates_first_argument():
  dictionary = PronunciationDict()
  dictionary["te st"] = Pronunciations()
  dictionary["te st"][("A", "B")] = 1.2

  with raises(ValueError) as error:
    validate_dictionary(dictionary)

  assert error.value.args == (
    "dictionary",
    "Word contains whitespace which is not allowed!"
  )


def test_error_in_pronunciation_updates_first_argument():
  dictionary = PronunciationDict()
  dictionary["test"] = Pronunciations()
  dictionary["test"][("A", "B ")] = 1.2

  with raises(ValueError) as error:
    validate_dictionary(dictionary)

  assert error.value.args == (
    "dictionary",
    "Pronunciation contains whitespace which is not allowed!"
  )


def test_error_in_weight_updates_first_argument():
  dictionary = PronunciationDict()
  dictionary["test"] = Pronunciations()
  dictionary["test"][("A", "B")] = "test"

  with raises(ValueError) as error:
    validate_dictionary(dictionary)

  assert error.value.args == (
    "dictionary",
    "Weight needs to be of type 'float' or 'int'!"
  )

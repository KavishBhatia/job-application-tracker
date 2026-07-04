import pytest

from src.utils import parse_optional_int


@pytest.mark.parametrize("value", [None, "", "   "])
def test_parse_optional_int_blank_returns_none(value):
    assert parse_optional_int(value) is None


def test_parse_optional_int_non_numeric_returns_none():
    assert parse_optional_int("not a number") is None


def test_parse_optional_int_plain_integer_string():
    assert parse_optional_int("3") == 3


def test_parse_optional_int_float_like_string():
    assert parse_optional_int("3.0") == 3


def test_parse_optional_int_actual_int_passthrough():
    assert parse_optional_int(4) == 4

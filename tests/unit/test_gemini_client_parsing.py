import pytest

from src.llm.gemini_client import LLMParsingError, _parse_response
from src.models import ParsedApplication


def test_parse_response_well_formed_json():
    result = _parse_response('{"company": "Acme", "role": "Backend Engineer"}')
    assert result == ParsedApplication(company="Acme", role="Backend Engineer")


def test_parse_response_missing_company():
    with pytest.raises(LLMParsingError):
        _parse_response('{"role": "Backend Engineer"}')


def test_parse_response_missing_role():
    with pytest.raises(LLMParsingError):
        _parse_response('{"company": "Acme"}')


def test_parse_response_invalid_json():
    with pytest.raises(LLMParsingError):
        _parse_response("not json at all")


def test_parse_response_empty_values():
    with pytest.raises(LLMParsingError):
        _parse_response('{"company": "", "role": ""}')

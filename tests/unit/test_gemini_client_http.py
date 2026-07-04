import os

import httpx
import pytest

from src.llm import gemini_client
from src.llm.gemini_client import LLMApiError


def _use_mock_transport(monkeypatch, handler):
    monkeypatch.setattr(
        gemini_client,
        "_get_http_client",
        lambda: httpx.Client(transport=httpx.MockTransport(handler)),
    )


def test_call_gemini_api_success(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def handler(request):
        assert request.headers["x-goog-api-key"] == "test-key"
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {"content": {"parts": [{"text": '{"company": "Acme", "role": "Engineer"}'}]}}
                ]
            },
        )

    _use_mock_transport(monkeypatch, handler)
    result = gemini_client._call_gemini_api("some prompt")
    assert result == '{"company": "Acme", "role": "Engineer"}'


def test_call_gemini_api_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(LLMApiError):
        gemini_client._call_gemini_api("some prompt")


def test_call_gemini_api_http_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def handler(request):
        return httpx.Response(500, text="server error")

    _use_mock_transport(monkeypatch, handler)
    with pytest.raises(LLMApiError):
        gemini_client._call_gemini_api("some prompt")


def test_call_gemini_api_timeout(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def handler(request):
        raise httpx.TimeoutException("timed out")

    _use_mock_transport(monkeypatch, handler)
    with pytest.raises(LLMApiError):
        gemini_client._call_gemini_api("some prompt")


def test_call_gemini_api_malformed_response_shape(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def handler(request):
        return httpx.Response(200, json={"unexpected": "shape"})

    _use_mock_transport(monkeypatch, handler)
    with pytest.raises(LLMApiError):
        gemini_client._call_gemini_api("some prompt")


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_LLM_TEST") != "1",
    reason="live Gemini smoke test only runs when RUN_LIVE_LLM_TEST=1 and a real GEMINI_API_KEY is set",
)
def test_call_gemini_api_live_smoke():
    result = gemini_client._call_gemini_api(
        gemini_client._build_prompt("Applied at Acme for Backend Engineer role")
    )
    parsed = gemini_client._parse_response(result)
    assert parsed.company
    assert parsed.role

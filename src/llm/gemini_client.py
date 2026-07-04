import json
import os

import httpx

from src.models import ParsedApplication

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)
TIMEOUT_SECONDS = 10.0

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "company": {"type": "string"},
        "role": {"type": "string"},
    },
    "required": ["company", "role"],
}


class LLMApiError(Exception):
    """Raised when the Gemini API call itself fails (missing key, network, non-200, bad shape)."""


class LLMParsingError(Exception):
    """Raised when the Gemini response text isn't valid, well-formed JSON with company/role."""


def _build_prompt(text: str) -> str:
    return (
        "Extract the company name and job role/title from this sentence about a job "
        "application. The sentence may be phrased in any way.\n\n"
        f"Sentence: {text}"
    )


def _get_http_client() -> httpx.Client:
    return httpx.Client(timeout=TIMEOUT_SECONDS)


def _call_gemini_api(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise LLMApiError("GEMINI_API_KEY is not configured")

    request_body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": RESPONSE_SCHEMA,
        },
    }

    client = _get_http_client()
    try:
        response = client.post(
            GEMINI_ENDPOINT,
            json=request_body,
            headers={"x-goog-api-key": api_key},
        )
    except httpx.HTTPError as exc:
        raise LLMApiError(f"Network error calling Gemini API: {exc}") from exc
    finally:
        client.close()

    if response.status_code != 200:
        raise LLMApiError(f"Gemini API returned status {response.status_code}: {response.text}")

    try:
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, ValueError) as exc:
        raise LLMApiError(f"Unexpected Gemini API response shape: {exc}") from exc


def _parse_response(raw_text: str) -> ParsedApplication:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise LLMParsingError(f"Gemini response was not valid JSON: {exc}") from exc

    company = str(data.get("company", "")).strip()
    role = str(data.get("role", "")).strip()

    if not company or not role:
        raise LLMParsingError("Gemini response missing company or role")

    return ParsedApplication(company=company, role=role)


def extract_application(text: str) -> ParsedApplication:
    prompt = _build_prompt(text)
    raw_text = _call_gemini_api(prompt)
    return _parse_response(raw_text)

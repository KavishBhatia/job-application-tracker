# Quickstart: Log Job Applications

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- A free-tier Gemini API key (optional for basic functioning — see below): https://ai.google.dev/ → "Get API key"

## Setup

```bash
uv sync
cp .env.example .env
# edit .env and set GEMINI_API_KEY=<your-key>   (optional — see "Running without a Gemini key" below)
```

`uv sync` creates `.venv` and installs all dependencies (including dev dependencies like `pytest`) from `pyproject.toml`/`uv.lock`.

## Run

```bash
uv run uvicorn src.app:app --reload
```

Open http://localhost:8000

## Validation scenarios

These map directly to the spec's acceptance scenarios (`spec.md`) and the API contract (`contracts/api.md`).

### 1. Log an application via free text (User Story 1)

1. On `/`, type `Applied at XYZ company for ABC role` into the add-application field and submit.
2. Expect: a confirm screen pre-filled with company `XYZ company` and role `ABC role`.
3. Confirm without edits. Expect: the new entry appears in the list on `/` with today's date and status `Applied`.
4. Repeat with a differently-phrased sentence (e.g. `Sent my resume to Acme for a Backend Engineer position`). Expect: company `Acme`, role `Backend Engineer` are still correctly identified (per `research.md`'s schema-constrained Gemini call).
5. Try submitting an empty sentence. Expect: rejected with a prompt to enter details — no blank row is created (FR-009).

### 2. Manual fallback when parsing fails (FR-008)

1. Temporarily unset `GEMINI_API_KEY` (or set it to an invalid value) and restart the app.
2. Submit any free-text sentence. Expect: the confirm screen appears with company/role blank and a "could not parse automatically" notice — you are not blocked from filling them in manually and saving.

### 3. Update status (User Story 2)

1. On an existing entry, open its status dropdown. Expect: exactly `Applied, Interviewing, Offer, Rejected, Withdrawn`.
2. Change it to `Interviewing`. Expect: the list reflects the new status immediately and after a page reload.

### 4. Export and re-import round trip (User Story 3)

1. With at least one application logged, visit `/export.csv` (and separately `/export.xlsx`). Expect: a downloaded file with all current entries.
2. Immediately import that same file via the import form on `/`. Expect: a summary reporting all rows skipped as duplicates, zero newly imported, zero rejected — the list is unchanged.
3. Edit the exported file to add one genuinely new row (new company/role/date) and one row with a blank `company`. Re-import it. Expect: the summary reports 1 imported, 1 rejected, and the rest skipped as duplicates; the new row appears in the list.

## Running without a Gemini key

The app is fully usable with no `GEMINI_API_KEY` configured: listing, status updates, export, and import all work with zero LLM involvement. Only the free-text auto-parse step is affected — it falls back to the manual-entry confirm screen (see scenario 2 above).

## Running the test suite

```bash
uv run pytest
```

All tests run offline by default (Gemini calls are mocked at the `httpx` boundary — no real API key required). An optional live smoke test against the real Gemini API can be enabled with:

```bash
RUN_LIVE_LLM_TEST=1 uv run pytest tests/unit/test_gemini_client_http.py
```

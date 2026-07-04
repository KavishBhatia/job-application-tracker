# API Contract: Log Job Applications

Server-rendered FastAPI app. Routes return HTML (Jinja2 templates) for browser navigation; where noted, a route accepts form/multipart data rather than JSON, consistent with a plain server-rendered UI (no separate frontend/API consumer per `research.md`'s Project Type decision).

## `GET /`

Renders `index.html`: the full list of applications (all columns from `data-model.md`), each row's status as an editable dropdown, and the free-text "add application" form.

## `POST /applications/parse`

Accepts form data: `text` (the free-text sentence, required), `job_post_url` (optional).

- Calls `extract_application(text)` (see `research.md`, `plan.md` project structure — `src/llm/gemini_client.py`).
- **Success**: renders `confirm_add.html` pre-filled with the extracted `company`/`role` (editable fields), `job_post_url` carried through, `date_applied` shown read-only as today's date, `status` dropdown defaulted to `Applied`.
- **Failure** (`LLMApiError` or `LLMParsingError` — missing/invalid API key, rate limit, timeout, ambiguous sentence): renders the same `confirm_add.html` with `company`/`role` left blank and an inline notice: "Could not parse automatically — please fill in manually." The original `text` is preserved as the eventual `source_text`. The user is never blocked from proceeding (FR-008).
- Rejects empty/whitespace-only `text` with a validation message, re-rendering the form (FR-009) — no call to `extract_application` is made in this case.

## `POST /applications`

Accepts form data: `company` (required), `role` (required), `job_post_url` (optional), `source_text` (optional, hidden field carried from the parse step), `status` (optional, defaults to `Applied`).

- Creates a new `applications` row with `date_applied = today()` set server-side, ignoring any client-supplied date (FR-004).
- Redirects to `GET /`.

## `POST /applications/{id}/status`

Accepts form data: `status` (required, must be one of the five `ApplicationStatus` values).

- Updates the row's `status`. No transition restrictions (any value to any other value is valid, per `data-model.md`).
- Invalid `status` values are rejected with a 422-equivalent validation error (pydantic `Enum` validation).
- Redirects to `GET /`.

## `GET /export.csv`

Streams a CSV file (`Content-Disposition: attachment`) with columns: `id, company, role, date_applied, status, job_post_url, source_text`, one row per application, ordered by `id`.

## `GET /export.xlsx`

Same column set and order as `/export.csv`, streamed as an Excel workbook (`openpyxl`, in-memory `BytesIO`).

## `POST /import`

Accepts multipart file upload: `file` (`.csv` or `.xlsx`, dispatched by extension).

Expects the same column headers as export. Any `id` column present is ignored — imported rows always receive a fresh autoincrement `id` (this sidesteps ID-collision handling entirely).

Per row:
- Reject if `company` or `role` is missing/blank, or `status` is present but invalid (FR-014).
- Otherwise, skip if `(company, role, date_applied)` (trimmed, case-folded) matches an existing row (FR-013).
- Otherwise, insert — `date_applied` from the file, falling back to `today()` if blank (see `data-model.md`); `status` from the file, falling back to `Applied` if blank.

Response: renders `index.html` (updated list) plus a summary banner: counts of rows imported, skipped as duplicates, and rejected (FR-014, SC-005).

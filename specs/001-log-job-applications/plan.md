# Implementation Plan: Log Job Applications

**Branch**: `001-log-job-applications` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-log-job-applications/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

A personal, single-user web app for logging job applications. The primary requirement is frictionless capture: the user types a free-text sentence (e.g. "Applied at XYZ company for ABC role"), and the system uses Google's Gemini API to flexibly extract company and role regardless of phrasing, auto-stamps the date, and lets the user confirm/correct before saving. Secondary capabilities: a status dropdown (Applied, Interviewing, Offer, Rejected, Withdrawn), an optional job posting link field, and CSV/Excel export and import with duplicate-skipping. Technical approach (see `research.md`): FastAPI (sync routes) + Jinja2 templates, SQLite via stdlib `sqlite3`, Gemini called directly via `httpx` REST (not the SDK) with schema-constrained JSON output, and `csv`/`openpyxl` for import/export — all chosen to minimize dependencies per the Simplicity & YAGNI principle.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `fastapi`, `uvicorn`, `jinja2`, `python-multipart` (form + file uploads), `httpx` (Gemini REST calls + test client), `openpyxl`, `python-dotenv`, `pytest`

**Storage**: SQLite via stdlib `sqlite3` (no ORM), single `applications` table, file at `data/job_applications.db`

**Testing**: `pytest`; FastAPI `TestClient` (httpx-based) for route/integration tests; `httpx.MockTransport` to mock the Gemini network boundary; `monkeypatch` to stub `extract_application` in route-level tests

**Target Platform**: Local machine, single-user self-hosted web server (`localhost`)

**Project Type**: Single project — server-rendered web application (FastAPI + Jinja2, no separate frontend)

**Performance Goals**: N/A — single user, no concurrency/throughput requirement

**Constraints**: Must remain fully usable (list, status updates, export, import) with zero Gemini API availability; Gemini calls must have an explicit timeout so a hung request never blocks the UI indefinitely

**Scale/Scope**: Single user; dozens to low hundreds of application entries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Simplicity & YAGNI**: Mostly satisfied — minimal dependency set, no ORM, no async, no frontend build, no enforced status-transition state machine. **One violation requires justification**: the Gemini API dependency. See Complexity Tracking below. Justified and accepted.
- **II. Test-First Development (NON-NEGOTIABLE)**: Satisfied — `spec.md` FR-015 explicitly requires automated tests per user story (overriding `tasks-template.md`'s default test-optionality per the Development Workflow section below). Test strategy (§ Testing above) keeps the full suite offline/deterministic via mocking at the `httpx` boundary, so Test-First is achievable without a live API key.
- **Development Workflow**: `spec.md` exists and precedes this plan ✅. Tests will precede implementation for every unit in the order listed in `quickstart.md` / to be sequenced in `tasks.md` by `/speckit-tasks`. `/speckit-tasks` MUST order test tasks immediately before their corresponding implementation tasks, per the constitution.

**Result: PASS (with one documented, justified complexity — see below). No blocking violations.**

## Project Structure

### Documentation (this feature)

```text
specs/001-log-job-applications/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
├── app.py                        # FastAPI app factory, mounts routers + Jinja2Templates, loads .env
├── db.py                         # sqlite3 connection helper, schema init, CRUD functions
├── models.py                     # pydantic schemas: ApplicationOut, ApplicationCreate, StatusUpdate,
│                                  #   ApplicationStatus(str, Enum), ParsedApplication
├── routes/
│   ├── __init__.py
│   ├── applications.py           # GET / (list), POST /applications/parse, POST /applications,
│   │                              #   POST /applications/{id}/status
│   └── io.py                     # GET /export.csv, GET /export.xlsx, POST /import
├── llm/
│   ├── __init__.py
│   └── gemini_client.py          # extract_application(text) -> ParsedApplication
│                                  #   _call_gemini_api(prompt) -> str      (network boundary)
│                                  #   _parse_response(raw_text) -> ParsedApplication (pure)
│                                  #   LLMApiError, LLMParsingError
├── io_formats/
│   ├── __init__.py
│   ├── csv_io.py                 # to_csv(rows) -> str ; from_csv(file) -> list[dict]
│   └── excel_io.py               # to_excel(rows) -> bytes ; from_excel(file) -> list[dict]
├── templates/
│   ├── base.html
│   ├── index.html                # list + per-row status dropdown + free-text add form
│   └── confirm_add.html          # LLM-parsed review/edit form before save
└── static/
    └── style.css

tests/
├── unit/
│   ├── test_gemini_client_parsing.py   # pure response-parsing, no network
│   ├── test_gemini_client_http.py      # httpx.MockTransport, boundary only
│   ├── test_db.py
│   ├── test_csv_io.py
│   └── test_excel_io.py
└── integration/
    ├── test_routes_applications.py     # TestClient, gemini_client mocked via monkeypatch
    └── test_routes_io.py                # export/import round-trip via TestClient

data/                              # gitignored; holds job_applications.db
.env.example                       # committed, documents GEMINI_API_KEY
requirements.txt
```

**Structure Decision**: Single project (Option 1), adapted for a small FastAPI web app rather than a CLI/library. `src/` holds all application code; `tests/` mirrors it with `unit/` (no network, no TestClient) and `integration/` (TestClient-driven, LLM boundary mocked) — this split lets the fast, network-free unit tests run on every save while integration tests still validate full request/response cycles, all without ever touching the real Gemini API.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| External LLM API (Google Gemini) for free-text parsing — introduces a network dependency, an API secret, non-deterministic output, and dedicated error-handling paths | The feature's core, explicit requirement (FR-002) is parsing free-text sentences in arbitrary, varied phrasing — a concrete, current requirement stated in the spec, not a speculative one | Fixed-pattern regex/keyword extraction was evaluated and rejected: it cannot generalize across arbitrary phrasing, and approximating LLM-level flexibility would require an ever-growing, hand-maintained pattern library — itself a larger, more brittle Simplicity violation than one isolated, well-tested API call behind a single function (`extract_application`), which keeps the rest of the app fully functional even with zero LLM availability |

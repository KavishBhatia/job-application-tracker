# Tasks: Log Job Applications

**Input**: Design documents from `/specs/001-log-job-applications/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md (all present)

**Tests**: Required — `spec.md` FR-015 explicitly mandates automated tests for every user story (the project constitution's Test-First Development principle is NON-NEGOTIABLE and overrides this template's default test-optionality). Every test task below MUST be written and observed to fail before its corresponding implementation task.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths are absolute-relative to the repository root, per `plan.md`'s Project Structure (single project: `src/`, `tests/`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per plan.md: `src/routes/`, `src/llm/`, `src/io_formats/`, `src/templates/`, `src/static/`, `tests/unit/`, `tests/integration/`, `data/`
- [X] T002 Create `requirements.txt` (fastapi, uvicorn, jinja2, python-multipart, httpx, openpyxl, python-dotenv, pytest) and install into a virtualenv
- [X] T003 [P] Create `.env.example` in repo root documenting `GEMINI_API_KEY`
- [X] T004 [P] Add to `.gitignore`: `.env`, `data/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.venv/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create SQLite schema-init function in `src/db.py` for the `applications` table (`id, company, role, date_applied, status, job_post_url, source_text`) per data-model.md
- [X] T006 [P] Define `ApplicationStatus` enum and pydantic schemas (`ApplicationOut`, `ApplicationCreate`, `StatusUpdate`, `ParsedApplication`) in `src/models.py`
- [X] T007 Create FastAPI app factory in `src/app.py`: instantiate app, mount `Jinja2Templates`, run DB schema-init on startup, load `.env` via `python-dotenv` (depends on T005)
- [X] T008 [P] Create base Jinja2 template `src/templates/base.html` and `src/static/style.css`
- [X] T009 [P] Create shared pytest fixtures in `tests/conftest.py`: temp SQLite DB file per test (monkeypatched db path) and a FastAPI `TestClient` fixture

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Log an application by typing a sentence (Priority: P1) 🎯 MVP

**Goal**: A user types a free-text sentence describing an application; the system extracts company/role via Gemini, lets the user confirm/correct, auto-stamps today's date, and adds it to the list.

**Independent Test**: Type a free-text sentence, confirm the pre-filled company/role, and verify a new entry appears in the list with today's date — delivers value with no other story implemented.

### Tests for User Story 1 (write first, confirm they FAIL before implementing) ⚠️

- [X] T010 [P] [US1] Unit test `_parse_response` in `tests/unit/test_gemini_client_parsing.py`: well-formed JSON → `ParsedApplication`; missing `company`/`role` keys → `LLMParsingError`
- [X] T011 [P] [US1] Unit test `_call_gemini_api` using `httpx.MockTransport` in `tests/unit/test_gemini_client_http.py`: 200 success, 4xx/5xx, and timeout all handled, non-200/timeout → `LLMApiError`
- [X] T012 [P] [US1] Unit test `create_application()` and `list_applications()` in `tests/unit/test_db.py` (uses `conftest.py` temp DB fixture)
- [X] T013 [P] [US1] Integration test in `tests/integration/test_routes_applications.py`: parse→confirm→save happy path (LLM mocked via `monkeypatch`), empty-text submission rejected, LLM-failure fallback renders blank manual-entry form

### Implementation for User Story 1

- [X] T014 [P] [US1] Implement `_call_gemini_api`, `_parse_response`, `extract_application`, `LLMApiError`, `LLMParsingError` in `src/llm/gemini_client.py` per research.md's verified REST contract (endpoint, `x-goog-api-key` header, `response_schema`-constrained JSON) (depends on T010, T011 failing first)
- [X] T015 [P] [US1] Implement shared `_insert(...)` helper plus `create_application()` (sets `date_applied = today()`) and `list_applications()` in `src/db.py` (depends on T012 failing first)
- [X] T016 [US1] Implement `GET /`, `POST /applications/parse`, `POST /applications` in `src/routes/applications.py` per contracts/api.md (depends on T013 failing first, T014, T015)
- [X] T017 [P] [US1] Create `src/templates/index.html`: application list (company, role, date, status as plain text for now, job post link), free-text add-application form
- [X] T018 [P] [US1] Create `src/templates/confirm_add.html`: editable company/role fields, read-only date, status dropdown defaulted to `Applied`, "couldn't parse automatically" fallback notice
- [X] T019 [US1] Register the applications router in `src/app.py` (depends on T016)

**Checkpoint**: User Story 1 is fully functional and independently testable — users can log applications via free text with manual fallback, and view their list.

---

## Phase 4: User Story 2 - Track application status (Priority: P2)

**Goal**: A user can view and change an application's status via a dropdown with exactly five options.

**Independent Test**: Create an entry, change its status via the dropdown, confirm it persists after reload.

### Tests for User Story 2 (write first, confirm they FAIL before implementing) ⚠️

- [X] T020 [P] [US2] Integration test in `tests/integration/test_routes_applications.py` (extend existing file): dropdown offers exactly the five status values; valid status update persists; invalid status value is rejected; status can change in any order including "backwards"

### Implementation for User Story 2

- [X] T021 [US2] Implement `update_status()` in `src/db.py` (depends on T020 failing first)
- [X] T022 [US2] Implement `POST /applications/{id}/status` in `src/routes/applications.py` per contracts/api.md (depends on T021)
- [X] T023 [US2] Update `src/templates/index.html`: replace the plain-text status with an interactive dropdown wired to the status endpoint (depends on T022)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Bulk export and import (Priority: P3)

**Goal**: A user can export their full application list as CSV/Excel and re-import a file to bulk-add applications, with duplicates skipped and invalid rows reported.

**Independent Test**: Export the current list, re-import the same file, and confirm all rows are reported as skipped duplicates with the list unchanged; then import a file with one new and one invalid row and confirm correct counts.

### Tests for User Story 3 (write first, confirm they FAIL before implementing) ⚠️

- [X] T024 [P] [US3] Unit test `to_csv`/`from_csv` round trip in `tests/unit/test_csv_io.py`
- [X] T025 [P] [US3] Unit test `to_excel`/`from_excel` round trip in `tests/unit/test_excel_io.py`
- [X] T026 [P] [US3] Unit test `application_exists()` dedupe check (case-folded/trimmed match on company+role+date) in `tests/unit/test_db.py` (extend existing file)
- [X] T027 [P] [US3] Integration test in `tests/integration/test_routes_io.py`: export→re-import round trip (all rows skipped as duplicates, list unchanged); mixed file with one new row and one row missing `company` reports correct imported/skipped/rejected counts

### Implementation for User Story 3

- [X] T028 [P] [US3] Implement `to_csv(rows)` and `from_csv(file)` in `src/io_formats/csv_io.py` (depends on T024 failing first)
- [X] T029 [P] [US3] Implement `to_excel(rows)` and `from_excel(file)` in `src/io_formats/excel_io.py` (depends on T025 failing first)
- [X] T030 [P] [US3] Implement `application_exists()` and `insert_imported_row()` (reusing the `_insert` helper from T015) in `src/db.py` (depends on T026 failing first)
- [X] T031 [US3] Implement `GET /export.csv`, `GET /export.xlsx`, `POST /import` (row validation, dedupe-skip, import/skip/reject counts) in `src/routes/io.py` per contracts/api.md (depends on T027 failing first, T028, T029, T030)
- [X] T032 [US3] Update `src/templates/index.html`: add export links and an import form with a result summary banner (depends on T031)
- [X] T033 [US3] Register the io router in `src/app.py` (depends on T031)

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T034 [P] Add stdlib `logging` configuration so Gemini/API errors are logged server-side (per plan.md's Parsing safety net) in `src/app.py`
- [X] T035 [P] Add an optional live Gemini smoke test gated behind `RUN_LIVE_LLM_TEST=1` + `pytest.mark.skipif`, excluded from the default run, in `tests/unit/test_gemini_client_http.py`
- [X] T036 Run all quickstart.md validation scenarios manually end-to-end (including the "running without a Gemini key" scenario)
- [X] T037 Run the full `pytest` suite and confirm it passes entirely offline with no `GEMINI_API_KEY` set

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational completion; proceed in priority order (P1 → P2 → P3) since US2 and US3 both build on `src/templates/index.html` and `src/app.py` router registration introduced in US1
- **Polish (Phase 6)**: Depends on all three user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories — the true MVP
- **User Story 2 (P2)**: Builds on US1's `index.html` and `src/app.py` (replaces static status text with an interactive dropdown) but does not require US3
- **User Story 3 (P3)**: Builds on US1's `index.html`/`src/app.py` and reuses US1's `_insert` DB helper, but does not require US2

### Within Each User Story

- Tests MUST be written and confirmed failing before implementation (Test-First, NON-NEGOTIABLE per constitution)
- Models/DB helpers before routes; routes before template wiring; router registration last

### Parallel Opportunities

- T003, T004 (Setup) in parallel
- T006, T008, T009 (Foundational) in parallel, after T005/T007
- All four US1 test tasks (T010-T013) in parallel with each other
- T014 and T015 (US1 implementation, different files) in parallel; T017 and T018 (templates) in parallel
- All four US3 test tasks (T024-T027) in parallel; T028, T029, T030 (US3 implementation, different files) in parallel
- T034 and T035 (Polish) in parallel

---

## Parallel Example: User Story 1

```bash
# Tests for User Story 1 (run together):
Task: "Unit test _parse_response in tests/unit/test_gemini_client_parsing.py"
Task: "Unit test _call_gemini_api via httpx.MockTransport in tests/unit/test_gemini_client_http.py"
Task: "Unit test create_application()/list_applications() in tests/unit/test_db.py"
Task: "Integration test parse/confirm/save flow in tests/integration/test_routes_applications.py"

# Implementation for User Story 1 (independent files, run together):
Task: "Implement gemini_client.py per research.md's REST contract"
Task: "Implement create_application()/list_applications() in src/db.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run quickstart.md scenarios 1 and 2 (free-text logging + manual fallback)
5. Demo if ready — this alone is a usable application-logging tool

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. User Story 1 → validate independently → MVP demo
3. User Story 2 → validate independently (status tracking now works)
4. User Story 3 → validate independently (export/import now works)
5. Polish (Phase 6) → full quickstart.md run-through, full offline test suite pass

---

## Notes

- [P] tasks touch different files and have no incomplete dependency between them
- [Story] label maps each task to its user story for traceability
- Every implementation task's preceding test(s) must be observed failing first, per the constitution's Test-First principle
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently before moving to the next

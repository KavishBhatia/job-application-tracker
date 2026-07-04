# Tasks: Interview Rounds Tracking and Feedback

**Input**: Design documents from `/specs/002-interview-rounds-feedback/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md (all present)

**Tests**: Required — `spec.md` FR-009 explicitly mandates automated tests per user story (constitution's Test-First Development is NON-NEGOTIABLE and overrides this template's default test-optionality). Every test task below MUST be written and observed to fail before its corresponding implementation task.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths are relative to the repository root, extending the existing structure from feature 001

---

## Phase 1: Setup

- [X] T001 Run `uv run pytest` to confirm the existing 35-passed/1-skipped baseline is clean before modifying shared code (`src/db.py`, `src/io_formats/`, `src/routes/`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema migration and shared plumbing that ALL three user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete. This is also the highest-stakes phase in the feature — it must not corrupt or lose the user's existing real data in `data/job_applications.db`.

### Tests (write first, confirm they FAIL before implementing) ⚠️

- [X] T002 [P] Unit test in `tests/unit/test_db.py`: manually create the *old* 7-column `applications` table (pre-feature schema), insert a row, run `db.init_db()` against that same file, assert `total_rounds`/`current_round`/`feedback` columns now exist via `PRAGMA table_info` and the pre-existing row survived unchanged (this is the test that actually protects real user data)
- [X] T003 [P] Unit test in `tests/unit/test_db.py`: calling `db.init_db()` twice against a fresh path does not raise (idempotency)
- [X] T004 [P] Unit test in `tests/unit/test_db.py`: `create_application()` and `insert_imported_row()` accept `total_rounds`/`current_round`/`feedback` and persist them; omitting them defaults all three to `None`
- [X] T005 [P] Unit test in `tests/unit/test_utils.py` (new file): `parse_optional_int()` returns `None` for `None`/blank/whitespace-only/non-numeric input, and the correct int for plain numeric strings and float-like strings (e.g. `"3.0"`)

### Implementation

- [X] T006 Extend `SCHEMA` in `src/db.py` with `total_rounds INTEGER`, `current_round INTEGER`, `feedback TEXT` (nullable, no defaults), and add a migration step in `init_db()`: query `PRAGMA table_info(applications)` and run `ALTER TABLE applications ADD COLUMN <name> <type>` for any of the three not already present (depends on T002, T003 failing first)
- [X] T007 Extend `_insert(...)` in `src/db.py` with the three new optional params (update both the Python signature AND the `INSERT INTO ... VALUES (...)` SQL string/tuple together), and pass them through in `create_application(...)` and `insert_imported_row(...)` (depends on T004 failing first, T006)
- [X] T008 [P] Create `src/utils.py` with `parse_optional_int(value) -> Optional[int]` (returns `None` on any blank/unparseable input, handles `"3.0"`-style float strings via `int(float(text))`) (depends on T005 failing first)

**Checkpoint**: Foundation ready — schema supports the new fields on both fresh and pre-existing databases, without data loss.

---

## Phase 3: User Story 1 - Update interview progress on an existing application (Priority: P1) 🎯 MVP

**Goal**: A user can add or update total rounds, current round, and feedback on an already-logged application, without re-entering any other field.

**Independent Test**: Log an application, then separately update its rounds/feedback via the table, and confirm the new values persist after a page reload.

### Tests (write first, confirm they FAIL before implementing) ⚠️

- [X] T009 [P] [US1] Unit test in `tests/unit/test_db.py`: `update_details()` updates only `total_rounds`/`current_round`/`feedback`, leaving company/role/date/status/job_post_url/source_text untouched
- [X] T010 [P] [US1] Integration test in `tests/integration/test_routes_applications.py`: `POST /applications/{id}/details` — valid update persists; updating only one of the three fields preserves the other two; `current_round` greater than `total_rounds` saves successfully (no rejection); a non-numeric round value is stored as unset rather than erroring

### Implementation

- [X] T011 [US1] Implement `update_details(application_id, total_rounds, current_round, feedback)` in `src/db.py` (depends on T009 failing first)
- [X] T012 [US1] Implement `POST /applications/{application_id}/details` in `src/routes/applications.py`, using `parse_optional_int` for the two round fields and blank-to-`None` for feedback, redirecting to `/` (303) (depends on T010 failing first, T011, T008)
- [X] T013 [US1] Add a details edit `<td>`/`<form>` per row (total rounds, current round, feedback inputs + a `button--secondary` "Save" button, posting to `/applications/{id}/details`) in `src/templates/index.html` (depends on T012)
- [X] T014 [P] [US1] Extend the existing `input[type="text"], input[type="url"], input[type="file"]` CSS selector in `src/static/style.css` to also cover `input[type="number"]`, reusing existing tokens

**Checkpoint**: User Story 1 is fully functional and independently testable — users can record and update interview progress on any existing application.

---

## Phase 4: User Story 2 - Optionally record rounds and feedback when first logging an application (Priority: P2)

**Goal**: A user can optionally fill in total rounds, current round, and feedback at the moment they log a new application.

**Independent Test**: Log a new application while filling in the three fields, and confirm the saved entry shows those values immediately; separately confirm leaving them blank still saves successfully.

### Tests (write first, confirm they FAIL before implementing) ⚠️

- [X] T015 [P] [US2] Integration test in `tests/integration/test_routes_applications.py`: `POST /applications` with `total_rounds`/`current_round`/`feedback` form fields creates a row with those values; omitting them (blank strings) creates a row with all three as `None` and does not 422

### Implementation

- [X] T016 [US2] Extend `POST /applications` in `src/routes/applications.py` to accept the three new `Form("")` fields, parse via `parse_optional_int`/blank-to-`None`, and pass through to `db.create_application` (depends on T015 failing first, T007, T008)
- [X] T017 [US2] Add total rounds / current round / feedback inputs to `src/templates/confirm_add.html`, before the existing hidden inputs (depends on T016)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Round and feedback data survives export and import (Priority: P3)

**Goal**: Exporting includes the three new fields; importing accepts them and never rejects a row solely due to an invalid round value.

**Independent Test**: Set rounds/feedback on an application, export, and confirm the file contains those values; separately, import a file with a non-numeric round value and confirm the row still imports.

### Tests (write first, confirm they FAIL before implementing) ⚠️

- [X] T018 [P] [US3] Unit tests in `tests/unit/test_csv_io.py` and `tests/unit/test_excel_io.py`: `to_csv`/`to_excel` include `total_rounds`/`current_round`/`feedback` columns; `from_csv`/`from_excel` still tolerate old files that predate this feature (missing these columns entirely)
- [X] T019 [P] [US3] Integration test in `tests/integration/test_routes_io.py`: importing a row with a non-numeric `total_rounds` value still imports successfully (not rejected) with that field left unset; exporting then re-importing an application with rounds/feedback set preserves those values

### Implementation

- [X] T020 [P] [US3] Extend `COLUMNS` in `src/io_formats/csv_io.py` with `total_rounds`, `current_round`, `feedback` (depends on T018 failing first)
- [X] T021 [P] [US3] Extend `COLUMNS` in `src/io_formats/excel_io.py` with `total_rounds`, `current_round`, `feedback` (depends on T018 failing first)
- [X] T022 [US3] Extend the per-row import handling in `src/routes/io.py` to parse `total_rounds`/`current_round` via `parse_optional_int` and `feedback` via blank-to-`None`, passing through to `db.insert_imported_row`, without adding these fields to the rejection criteria (depends on T019 failing first, T020, T021, T008)

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T023 [P] Optionally add `total_rounds`/`current_round`/`feedback` fields to `ApplicationOut`/`ApplicationCreate` in `src/models.py` for documentation consistency (non-blocking — actual routes validate via raw `Form()` params, not these classes)
- [X] T024 Run the `quickstart.md` backward-compatibility check manually: restart the app against the real, existing `data/job_applications.db` (not a fresh one) and confirm all previously-logged applications still display correctly with the new fields blank
- [X] T025 Run all `quickstart.md` validation scenarios end-to-end (update on existing entry, creation-time entry, export/import round trip)
- [X] T026 Run the full `uv run pytest` suite and confirm everything passes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (schema must exist before any story can read/write the new fields)
- **User Stories (Phase 3+)**: All depend on Foundational completion; proceed in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all three user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on `_insert`/`create_application`/`insert_imported_row` changes at all — `update_details()` is a standalone `UPDATE` statement. True MVP, fully independent.
- **User Story 2 (P2)**: Depends on the Foundational `_insert`/`create_application` extension (T007) and `parse_optional_int` (T008) — does not depend on US1.
- **User Story 3 (P3)**: Depends on the Foundational `_insert`/`insert_imported_row` extension (T007) and `parse_optional_int` (T008) — does not depend on US1 or US2.

### Within Each Phase

- Tests MUST be written and confirmed failing before implementation (Test-First, NON-NEGOTIABLE per constitution)
- DB/utility functions before routes; routes before template wiring

### Parallel Opportunities

- T002, T003, T004, T005 (Foundational tests) in parallel
- T008 (parse_optional_int) in parallel with T006/T007 (different files)
- T009, T010 (US1 tests) in parallel
- T014 (CSS) in parallel with T011-T013
- T018, T019 (US3 tests) in parallel; T020, T021 (US3 COLUMNS, different files) in parallel
- T023 (Polish) in parallel with T024/T025 (manual checks)

---

## Parallel Example: Foundational Phase

```bash
# Tests (run together):
Task: "Migration test: old table -> init_db() -> columns added, data intact, in tests/unit/test_db.py"
Task: "Idempotency test: init_db() called twice on fresh path, in tests/unit/test_db.py"
Task: "create_application()/insert_imported_row() persist new fields, in tests/unit/test_db.py"
Task: "parse_optional_int() handles blank/non-numeric/float-string input, in tests/unit/test_utils.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (baseline check)
2. Complete Phase 2: Foundational (schema migration — the highest-stakes work in this feature)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run `quickstart.md` scenario 1 (update on existing entry) AND the backward-compatibility check against real data
5. Demo if ready — this alone lets users track round progress on anything they've already logged

### Incremental Delivery

1. Setup + Foundational → schema safely extended, real data verified intact
2. User Story 1 → validate independently → MVP (round tracking on existing entries)
3. User Story 2 → validate independently (creation-time entry now works)
4. User Story 3 → validate independently (export/import now includes the new fields)
5. Polish → backward-compat + full quickstart run-through + full offline test suite pass

---

## Notes

- [P] tasks touch different files and have no incomplete dependency between them
- [Story] label maps each task to its user story for traceability
- The Foundational phase's migration test (T002) is the single most important test in this feature — it is the only thing standing between this feature and silently corrupting the user's real, already-existing data
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently before moving to the next

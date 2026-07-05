# Tasks: Separate Pages Navigation

**Input**: Design documents from `/specs/003-separate-pages/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md (all present)

**Tests**: Required — this project's constitution mandates Test-First Development (NON-NEGOTIABLE), which overrides this template's default test-optionality. Every test task below MUST be written and observed to fail before its corresponding implementation task.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths are relative to the repository root, extending the existing structure from features 001/002

---

## Phase 1: Setup

- [X] T001 Run `uv run pytest -q` to confirm the existing 67-passed/1-skipped baseline is clean before restructuring `src/routes/applications.py`, `src/routes/io.py`, and `src/templates/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The persistent navigation shared by all three pages — required before any page-specific work is meaningful, since FR-003 requires the nav on every page.

### Tests (write first, confirm they FAIL before implementing) ⚠️

- [X] T002 [P] Integration test in `tests/integration/test_routes_applications.py`: `GET /` response includes `href="/"`, `href="/applications"`, and `href="/import-export"` nav links

### Implementation

- [X] T003 Add a `<nav>` element to the `<header>` in `src/templates/base.html` with three links: `/` ("Add Application"), `/applications` ("Applications"), `/import-export` ("Import / Export") — plain links, no active-page highlighting (depends on T002 failing first)

**Checkpoint**: Shared nav exists and renders on the one page that currently exists (`/`). Ready for page-specific work.

---

## Phase 3: User Story 1 - Navigate between dedicated pages (Priority: P1) 🎯 MVP

**Goal**: Three separate pages exist — "Add Application" (home), "Applications", "Import / Export" — each showing only its own content, reachable via the nav.

**Independent Test**: Load the app, confirm `/` shows only the add form, `/applications` shows only the table, `/import-export` shows only export/import controls.

### Tests (write first, confirm they FAIL before implementing) ⚠️

- [X] T004 [P] [US1] Integration test in `tests/integration/test_routes_applications.py`: `GET /` renders the add-application form (`id="text"` present) and does NOT render the applications table (`<table` absent) or import/export controls (`Export as CSV` absent)
- [X] T005 [P] [US1] Integration test in `tests/integration/test_routes_applications.py`: after creating an application, `GET /applications` renders the table (company/role text present) and does NOT render the add-application form (`id="text"` absent) or import/export controls (`Export as CSV` absent)
- [X] T006 [P] [US1] Integration test in `tests/integration/test_routes_io.py`: `GET /import-export` renders the export links and import form (`Export as CSV` and `id="file"` present) and does NOT render the add-application form (`id="text"` absent) or the applications table (`<table` absent)
- [X] T007 [US1] Update `test_status_dropdown_offers_exactly_five_options` in `tests/integration/test_routes_applications.py` to call `client.get("/applications")` instead of `client.get("/")` (confirm this now FAILS — `/applications` doesn't exist yet)

### Implementation

- [X] T008 [P] [US1] Create `src/templates/add.html` (extends `base.html`) containing only the "Log a new application" form section extracted from `src/templates/index.html` (depends on T004 failing first)
- [X] T009 [P] [US1] Create `src/templates/applications.html` (extends `base.html`) containing the applications table section extracted from `src/templates/index.html`, unchanged column layout for now — row collapse/expand comes in User Story 3 (depends on T005 failing first)
- [X] T010 [P] [US1] Create `src/templates/import_export.html` (extends `base.html`) containing the export links + import form section extracted from `src/templates/index.html` (depends on T006 failing first)
- [X] T011 [US1] In `src/routes/applications.py`: change `GET /` to render `add.html` (drop the now-unneeded `applications`/`statuses` context), and change `parse_application`'s empty-text branch to render `add.html` with `parse_error` instead of `index.html` (depends on T008)
- [X] T012 [US1] Add `GET /applications` in `src/routes/applications.py` rendering `applications.html` with the `applications`/`statuses` context that `GET /` used to provide (depends on T009, T007 failing first)
- [X] T013 [US1] Add `GET /import-export` in `src/routes/io.py` rendering `import_export.html` (depends on T010)
- [X] T014 [US1] Update `POST /import` in `src/routes/io.py` to render `import_export.html` instead of `index.html` (same `import_summary` context) (depends on T010, T006 failing first)
- [X] T015 [US1] Delete `src/templates/index.html` now that all of its content has moved to `add.html`/`applications.html`/`import_export.html` and no route references it (depends on T011, T012, T013, T014)

**Checkpoint**: The three pages exist with persistent nav and mutually exclusive content (User Story 1 acceptance scenarios 1-4 satisfied).

**Note**: `uv run pytest` will NOT be fully green yet at this checkpoint. Tests that `POST` a mutation with `follow_redirects=True` and then check for table content (e.g. `test_create_application_and_list`) still redirect to `/` — now the add-application page — until User Story 2's redirect-target change lands next. This is an accepted, temporary, and deliberate coupling between US1 and US2 (both required for a working app), not a bug to chase down here.

---

## Phase 4: User Story 2 - Land on the Applications page after a change (Priority: P2)

**Goal**: After adding an application or updating its status/details, the user is redirected to `/applications` instead of `/`.

**Independent Test**: Submit the add-application flow and confirm you land on `/applications` seeing the new entry; update a status or details and confirm you land back on `/applications` with the update visible.

### Tests (write first, confirm they FAIL before implementing) ⚠️

- [X] T016 [P] [US2] Integration test in `tests/integration/test_routes_applications.py`: `POST /applications` with `follow_redirects=False` returns a 303 with `Location: /applications`
- [X] T017 [P] [US2] Integration test in `tests/integration/test_routes_applications.py`: `POST /applications/{id}/status` and `POST /applications/{id}/details`, each with `follow_redirects=False`, return a 303 with `Location: /applications`

### Implementation

- [X] T018 [US2] In `src/routes/applications.py`, change the `RedirectResponse` target from `"/"` to `"/applications"` in `create_application`, `update_application_status`, and `update_application_details` (depends on T016, T017 failing first)

**Checkpoint**: User Stories 1 and 2 together are fully functional — `uv run pytest` should now be fully green, since the pre-existing `follow_redirects=True` tests correctly land on `/applications`, where the table now lives.

---

## Phase 5: User Story 3 - Expand a row to see and edit full details (Priority: P3)

**Goal**: Table rows collapse by default to company/role/date/status; clicking a row reveals job posting link, total rounds, current round, and feedback in place, editable, without leaving the page.

**Independent Test**: On `/applications` with a logged application, confirm the row shows only 4 fields, click it to reveal the rest, edit and save rounds/feedback, click again to collapse.

### Tests (write first, confirm they FAIL before implementing) ⚠️

- [X] T019 [P] [US3] Integration test in `tests/integration/test_routes_applications.py`: for a created application, the text between `<thead>` and `</thead>` in the `GET /applications` response contains "Company", "Role", "Date Applied", "Status" and does NOT contain "Job Posting", "Total Rounds", "Current Round", or "Feedback"
- [X] T020 [P] [US3] Integration test in `tests/integration/test_routes_applications.py`: for a created application with rounds/feedback set via `/applications/{id}/details`, the `GET /applications` response contains an element with `class="app-detail"` and a `hidden` attribute, and that element's content includes the total rounds, current round, and feedback values

### Implementation

- [X] T021 [US3] Restructure `src/templates/applications.html`: reduce `<thead>` to Company/Role/Date Applied/Status; change the `<tbody>` loop to emit two `<tr>`s per application — a summary row (`class="app-row"`) with those four `<td>`s (status dropdown unchanged, still auto-submits on change) and a detail row (`<tr class="app-detail" hidden>`) with one `<td colspan="4">` containing the job posting link (if present) and a single `<form>` wrapping total rounds / current round / feedback inputs plus a Save button, posting to `/applications/{id}/details` (depends on T019, T020 failing first; this retires the `form="id"` cross-cell technique from feature 002, since all three fields now share one `<td>`)
- [X] T022 [P] [US3] Add an inline `<script>` in `src/templates/applications.html` that toggles the `hidden` attribute on an `.app-row`'s matching `.app-detail` sibling when the row is clicked, ignoring clicks whose target is inside a `<select>` (via `event.target.closest('select')`) so changing status doesn't also toggle the row (depends on T021)
- [X] T023 [P] [US3] Add CSS in `src/static/style.css` for `.app-row` (`cursor: pointer`) and `.app-detail` (padding/background reusing existing `--bg-panel`/spacing tokens) (depends on T021)

**Checkpoint**: All three user stories are independently functional and satisfied.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T024 Run all `quickstart.md` validation scenarios manually in a browser (page navigation, redirect-after-mutation, expand/collapse, regression check) — the row click-to-expand interaction cannot be exercised by `pytest`/`TestClient` (no browser) and must be verified this way, consistent with the existing untested theme-toggle script
- [X] T025 Run the full `uv run pytest` suite and confirm everything passes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (nav must exist before pages can be meaningfully "reachable via persistent navigation")
- **User Stories (Phase 3+)**: All depend on Foundational completion; proceed in priority order (P1 → P2 → P3). US2 depends on US1's `/applications` route existing (its redirect target). US3 depends on US1's `applications.html` existing (it restructures that template's rows).
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Within Each Phase

- Tests MUST be written and confirmed failing before implementation (Test-First, NON-NEGOTIABLE per constitution)
- Template creation before route wiring; route wiring before deleting the old combined template

### Parallel Opportunities

- T002 (Foundational test) has no parallel sibling in this phase
- T004, T005, T006 (US1 tests) in parallel; T008, T009, T010 (US1 template extraction, different files) in parallel
- T016, T017 (US2 tests) in parallel
- T019, T020 (US3 tests) in parallel; T022 (JS), T023 (CSS) in parallel once T021 lands

---

## Parallel Example: User Story 1 Tests

```bash
# Tests (run together):
Task: "GET / renders add form only, in tests/integration/test_routes_applications.py"
Task: "GET /applications renders table only, in tests/integration/test_routes_applications.py"
Task: "GET /import-export renders export/import only, in tests/integration/test_routes_io.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (baseline check)
2. Complete Phase 2: Foundational (shared nav)
3. Complete Phase 3: User Story 1
4. **Note**: the app is not fully coherent yet at this point (POST redirects still land on the now-form-only `/`) — User Story 2 is a required companion, not optional polish, despite being P2

### Incremental Delivery

1. Setup + Foundational → nav exists
2. User Story 1 → three pages exist and show the right content each
3. User Story 2 → redirect targets fixed → app is fully coherent again, full test suite green
4. User Story 3 → rows collapse/expand → declutters the table per the original motivation for this feature
5. Polish → manual quickstart run-through (including the JS-only interaction) + full offline test suite pass

---

## Notes

- [P] tasks touch different files and have no incomplete dependency between them
- [Story] label maps each task to its user story for traceability
- Unlike features 001/002, this feature touches no `src/db.py`, `src/models.py`, or `src/io_formats/*` — it is purely routing/template/front-end restructuring
- The US1/US2 coupling noted above is real and expected — it is not a sign the stories were split incorrectly, just a consequence of `/` changing meaning partway through the feature
- Commit after each task or logical group

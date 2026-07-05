# Implementation Plan: Separate Pages Navigation

**Branch**: `003-separate-pages` | **Date**: 2026-07-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-separate-pages/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Split the existing single-page UI (add-application form + applications table + import/export controls all on `/`) into three dedicated pages — an "Add Application" home page (`/`), an "Applications" page (`/applications`), and an "Import / Export" page (`/import-export`) — reachable via a persistent header nav. All three mutating endpoints (`POST /applications`, `POST /applications/{id}/status`, `POST /applications/{id}/details`) redirect to `/applications` instead of `/` so the user sees the effect of their action. On the Applications page, each row collapses to company/role/date/status by default and expands in place (vanilla JS, no new dependency) to reveal the job posting link, total rounds, current round, and feedback. Purely a routing/template/front-end restructuring — no schema or data changes (see `research.md`).

## Technical Context

**Language/Version**: Python 3.11+ (unchanged from features 001/002)

**Primary Dependencies**: unchanged — `fastapi`, `uvicorn`, `jinja2`, `python-multipart`, `httpx`, `openpyxl`, `python-dotenv`, `pytest`. No new dependency for this feature — expand/collapse uses plain vanilla JS, matching the existing inline theme-toggle script pattern in `base.html`.

**Storage**: SQLite via stdlib `sqlite3` (unchanged). No schema changes — `db.py` is untouched by this feature.

**Testing**: `pytest`, FastAPI `TestClient` (unchanged infrastructure). Existing integration tests move their assertions to the new page routes; a few new tests assert route content and redirect targets. The row expand/collapse *interaction* is client-side JS and cannot be exercised by `TestClient` (no browser) — verified manually per `quickstart.md`, consistent with the existing (untested) theme-toggle script.

**Target Platform**: Local machine, single-user (unchanged)

**Project Type**: Single project, extends the existing structure (unchanged)

**Performance Goals**: N/A (unchanged — single user, no concurrency requirement)

**Constraints**: All existing functionality (parsing, confirm-before-save, status values, CSV/Excel export/import, duplicate-skipping) must continue to work unchanged after the split (FR-015) — this is a restructuring, not a rewrite.

**Scale/Scope**: Unchanged — single user, dozens to low hundreds of rows.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Simplicity & YAGNI**: Satisfied. No new dependency, no client-side framework, no build step — the expand/collapse toggle is the same class of small inline vanilla-JS script the app already uses for the theme toggle. No new pydantic schemas or abstractions introduced. Splitting one template into three is the simplest way to satisfy FR-001/004/005/006 (mutually exclusive page content) — a single template with conditional sections would need the same content duplicated behind more complex conditionals for no benefit, since the pages have no shared UI besides the nav.
- **II. Test-First Development (NON-NEGOTIABLE)**: Satisfied. Test plan (below) is written before implementation: existing tests are updated to target the new routes first (and will fail against the current single-page routing), new tests for route content and redirect targets are written before the routes exist.
- **Development Workflow**: `spec.md` exists and precedes this plan. Tests precede implementation for every route/template change, sequenced in `tasks.md`.

**Result: PASS. No violations, no complexity to justify.**

## Project Structure

### Documentation (this feature)

```text
specs/003-separate-pages/
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
├── routes/
│   ├── applications.py           # MODIFIED: GET / now renders add.html only; NEW GET /applications
│   │                              #   renders applications.html; the three mutating handlers'
│   │                              #   RedirectResponse targets change from "/" to "/applications"
│   └── io.py                     # MODIFIED: NEW GET /import-export renders import_export.html;
│                                  #   POST /import renders import_export.html instead of index.html
└── templates/
    ├── base.html                  # MODIFIED: adds a <nav> with links to /, /applications, /import-export
    ├── add.html                   # NEW: the add-application form, split out of index.html
    ├── applications.html          # NEW: the table, split out of index.html, with two-<tr>-per-row
    │                              #   expand/collapse markup + inline toggle script
    ├── import_export.html         # NEW: export links + import form, split out of index.html
    ├── confirm_add.html           # UNCHANGED (still POSTs to /applications)
    └── index.html                 # REMOVED — fully replaced by the three templates above

tests/
└── integration/
    ├── test_routes_applications.py  # MODIFIED: table-content assertions move to GET /applications;
    │                                 #   redirect-target assertions added; new GET / and GET /applications
    │                                 #   content tests
    └── test_routes_io.py            # MODIFIED: minor — asserts against import_export.html content;
                                      #   new GET /import-export test
```

**Structure Decision**: Extends the existing single-project structure (`src/`, `tests/` at repo root) — no new top-level directories, no new dependencies. `src/db.py`, `src/models.py`, `src/utils.py`, `src/io_formats/*`, and `src/templates/confirm_add.html` are all untouched, since this feature is purely about page/route/template restructuring, not data or business logic.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally left empty.

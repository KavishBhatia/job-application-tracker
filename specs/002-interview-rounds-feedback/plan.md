# Implementation Plan: Interview Rounds Tracking and Feedback

**Branch**: `002-interview-rounds-feedback` | **Date**: 2026-07-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-interview-rounds-feedback/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Extend the existing single-user job application tracker so each application can optionally carry total interview rounds, current round, and a free-text feedback note — settable at creation time and editable later on an existing entry, and included in CSV/Excel export/import. This is an additive schema change to the existing SQLite `applications` table (three new nullable columns), with a safe idempotent migration since real user data already exists in `data/job_applications.db`. No new dependencies, no new project, no frontend framework — extends the existing FastAPI + Jinja2 + stdlib `sqlite3` stack (see `research.md` for the concrete mechanism choices).

## Technical Context

**Language/Version**: Python 3.11+ (unchanged from feature 001)

**Primary Dependencies**: unchanged — `fastapi`, `uvicorn`, `jinja2`, `python-multipart`, `httpx`, `openpyxl`, `python-dotenv`, `pytest`. No new dependency for this feature.

**Storage**: SQLite via stdlib `sqlite3` (unchanged), `applications` table extended with `total_rounds INTEGER`, `current_round INTEGER`, `feedback TEXT` (all nullable), added via an idempotent in-`init_db()` migration (see `research.md`) rather than a fresh schema assumption, since real data already exists in `data/job_applications.db`.

**Testing**: `pytest`, FastAPI `TestClient`, `httpx.MockTransport` (unchanged infrastructure). New migration-specific test builds the pre-feature 7-column table manually to exercise the `ALTER TABLE` path, which the existing `temp_db` fixture (fresh installs) never touches.

**Target Platform**: Local machine, single-user (unchanged)

**Project Type**: Single project, extends the existing structure (unchanged)

**Performance Goals**: N/A (unchanged — single user, no concurrency requirement)

**Constraints**: The migration MUST be non-destructive to existing rows in a pre-existing `data/job_applications.db` — this is the binding constraint for this feature, driven by FR-008/SC-004.

**Scale/Scope**: Unchanged — single user, dozens to low hundreds of rows.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Simplicity & YAGNI**: Satisfied. No new dependency, no migrations framework (an idempotent `PRAGMA table_info` + `ALTER TABLE` check in `init_db()` is the minimal correct mechanism — see `research.md`). One new shared helper (`parse_optional_int`) is justified by two concrete, identical call sites (the new endpoint and CSV/Excel import), not speculative reuse. No new pydantic schema added for the new endpoint since the actual routes don't use the existing ones either — avoids compounding an already-unused pattern.
- **II. Test-First Development (NON-NEGOTIABLE)**: Satisfied — spec.md FR-009 explicitly requires tests per user story. Test plan (below) explicitly includes the migration-safety test, which is the one test that actually protects the user's existing real data — this is the highest-stakes test in this feature and must not be skipped.
- **Development Workflow**: `spec.md` exists and precedes this plan. Tests precede implementation for every unit, sequenced below.

**Result: PASS. No violations, no complexity to justify.**

## Project Structure

### Documentation (this feature)

```text
specs/002-interview-rounds-feedback/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
├── contracts/            # Phase 1 output (/speckit-plan command)
└── tasks.md              # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
├── db.py                         # MODIFIED: migration in init_db(), _insert/create_application/
│                                  #   insert_imported_row gain 3 optional params, new update_details()
├── utils.py                      # NEW: parse_optional_int(value) -> Optional[int]
├── models.py                     # OPTIONAL/MINOR: add fields to ApplicationOut/ApplicationCreate
│                                  #   (documentation only — routes use raw Form(), unchanged)
├── routes/
│   ├── applications.py           # MODIFIED: POST /applications gains 3 form fields;
│   │                              #   NEW POST /applications/{id}/details endpoint
│   └── io.py                     # MODIFIED: import row handling parses the 3 new fields
├── io_formats/
│   ├── csv_io.py                 # MODIFIED: COLUMNS list extended
│   └── excel_io.py               # MODIFIED: COLUMNS list extended
└── templates/
    ├── confirm_add.html          # MODIFIED: 3 new optional inputs before hidden fields
    ├── index.html                # MODIFIED: new <td> per row with a details edit form + Save button
    └── (style.css already covers input[type=number] via existing selector extension)

tests/
├── unit/
│   ├── test_db.py                 # MODIFIED: migration test (old-table + ALTER TABLE), new CRUD tests
│   ├── test_csv_io.py             # MODIFIED: column-inclusion + backward-compat tests
│   └── test_excel_io.py           # MODIFIED: column-inclusion + backward-compat tests
└── integration/
    ├── test_routes_applications.py  # MODIFIED: extended create + new /details endpoint tests
    └── test_routes_io.py            # MODIFIED: non-numeric round value import test
```

**Structure Decision**: Extends the existing single-project structure from feature 001 (`src/`, `tests/` at repo root) — no new top-level directories. Only `src/utils.py` is a new file; everything else is a modification to existing modules, consistent with this being an additive schema/field change rather than a new subsystem.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally left empty.

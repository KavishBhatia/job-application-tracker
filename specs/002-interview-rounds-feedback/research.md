# Phase 0 Research: Interview Rounds Tracking and Feedback

## Decision: Idempotent in-code schema migration via `PRAGMA table_info`, no migrations library

**Rationale**: Real user data already exists in `data/job_applications.db` (gitignored, personal, never recreated from scratch). `CREATE TABLE IF NOT EXISTS` alone will not add columns to an already-existing table, so `init_db()` needs an explicit migration step: after running `SCHEMA`, query `PRAGMA table_info(applications)` for the set of existing column names, and run `ALTER TABLE applications ADD COLUMN <name> <type>` for any of `total_rounds`, `current_round`, `feedback` not already present. This is ~10-15 lines, runs safely on every startup (idempotent — a no-op once columns exist), and needs no external migrations framework (Alembic, etc.) — a personal single-table SQLite app doesn't need versioned migration files. Consistent with the constitution's Simplicity & YAGNI principle.

**Alternatives considered**: catching `sqlite3.OperationalError` and string-matching "duplicate column name" — rejected in favor of `PRAGMA table_info` since it's inspectable/testable without depending on a driver-specific error message string. A dedicated migrations library — rejected as speculative complexity for a single table with three additive, nullable columns.

**Test implication**: the existing `temp_db` fixture (fresh installs only) never exercises the `ALTER TABLE` branch, since a fresh `CREATE TABLE` already includes the new columns. A dedicated test must manually build the *old* 7-column table, insert a row, run `init_db()` against that same file, and assert the new columns exist and the row survived — this is the test that actually protects the user's real data file.

## Decision: New columns are nullable, no defaults, no cross-field validation

**Rationale**: `total_rounds INTEGER`, `current_round INTEGER`, `feedback TEXT` — all nullable, matching the existing style of `job_post_url`/`source_text`. Per FR-003, no relationship is enforced between `current_round` and `total_rounds` (current can exceed total, either can be set without the other). This keeps the schema and validation logic minimal.

**Alternatives considered**: a `CHECK` constraint enforcing `current_round <= total_rounds` — rejected, contradicts FR-003 and the user's explicit choice not to add cross-field validation.

## Decision: Form fields declared as `str = Form("")`, parsed to `Optional[int]` in the route body

**Rationale**: An empty HTML `<input type="number">` submits an empty string, not an absent field. Declaring the FastAPI parameter as `Optional[int] = Form(None)` would make pydantic attempt to coerce `""` to `int` and fail with a 422 on the common case of "user left it blank." Declaring it as `str = Form("")` (matching the existing pattern already used for `job_post_url`/`source_text`) and parsing manually avoids this entirely.

**Alternatives considered**: `Optional[int] = Form(None)` — rejected, breaks on blank submission as described above.

## Decision: Shared `parse_optional_int` helper in a new `src/utils.py`

**Rationale**: Both the new `/applications/{id}/details` endpoint and the CSV/Excel import path in `routes/io.py` need identical behavior: turn a blank or unparseable value into `None` rather than raising or rejecting. A single ~8-line function used at exactly these two call sites is justified by concrete, identical duplicated need — not speculative. Handles both plain strings (`"3"`) and values that may arrive as `"3.0"` (a float round-tripped through Excel) via `int(float(text))`.

**Alternatives considered**: duplicating the parsing logic in both places — rejected, unnecessary duplication for identical behavior (this is what the shared-helper exception to YAGNI is for, per the constitution's own principle of avoiding premature abstraction only when there isn't a concrete current need — here there are two concrete current call sites).

## Decision: Non-numeric round values do not reject an imported row

**Rationale**: Per FR-007, only a missing company/role or an invalid status value continue to reject a row on import — existing behavior, unchanged. A non-numeric `total_rounds`/`current_round` value is optional data; the `parse_optional_int` helper returns `None` on any parse failure, and the row still imports with that field left unset.

**Alternatives considered**: rejecting rows with invalid round values — rejected, contradicts FR-007 and User Story 3's acceptance scenario 3.

## Decision: Extend `COLUMNS` in `csv_io.py`/`excel_io.py`; existing hardcoded-column tests must be updated

**Rationale**: Both files already have a single `COLUMNS` list driving both read and write; appending `total_rounds`, `current_round`, `feedback` covers export automatically (`routes/io.py` needs no changes to pick this up) and import continues to tolerate files that don't have these columns at all (existing `from_csv`/`from_excel` behavior already returns whatever keys are present in the file's header row — confirmed by existing `test_from_csv_missing_optional_columns` / `test_excel_from_excel_missing_optional_columns`, which continue to demonstrate backward compatibility with old export files that predate this feature).

**Alternatives considered**: a separate "extended" export format — rejected, unnecessary complexity; one column list already handles this cleanly.

## Decision: No new pydantic schema for the `/details` endpoint; skip cross-field additions unless trivial

**Rationale**: `ApplicationCreate`, `StatusUpdate`, and `ApplicationOut` in `src/models.py` are currently unused by the actual routes — every route validates via raw `Form(...)` scalar parameters, not these classes. Adding a new `DetailsUpdate` pydantic schema that nothing uses would be dead code matching a pattern already present but inert. The new endpoint follows the actual established convention (raw `Form()` params) instead.

**Alternatives considered**: wiring the new endpoint through pydantic models and updating the unused ones to match — rejected as out of scope; would require touching working, unrelated code paths for a documentation-only benefit.

## Decision: Per-row "details" edit form is a separate `<form>`/`<td>` from the status form, with an explicit Save button

**Rationale**: A `<form>` element cannot span multiple `<td>`s, so the three new fields (total rounds, current round, feedback) live together in one new `<td>` with their own `<form action="/applications/{id}/details">`. Unlike the single-field status dropdown (which auto-submits on change), this is a multi-field edit — auto-submitting on every keystroke would be poor UX (partial saves mid-typing) and isn't how any other multi-field form in this app behaves. An explicit small "Save" button (reusing the existing `.button--secondary` style token) is added instead.

**Alternatives considered**: the HTML5 `form="id"` attribute technique (one `<form>` element, inputs scattered across separate `<td>`s referencing it by id) — noted as a valid fallback for finer column-by-column layout, but not adopted now since it adds indirection with no concrete current need.

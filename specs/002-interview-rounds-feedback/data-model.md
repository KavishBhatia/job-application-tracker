# Data Model: Interview Rounds Tracking and Feedback

## Entity: `JobApplication` (extended)

Extends the existing `applications` table (see `specs/001-log-job-applications/data-model.md` for the original 6 columns: `id, company, role, date_applied, status, job_post_url, source_text`) with three new nullable columns:

| Field | Type | Constraints / Notes |
|---|---|---|
| `total_rounds` | `INTEGER` (nullable) | Optional. No relationship enforced with `current_round` (FR-003). |
| `current_round` | `INTEGER` (nullable) | Optional. Can exceed `total_rounds`, can be set without `total_rounds` being set, and vice versa. |
| `feedback` | `TEXT` (nullable) | Optional. A single free-text note per application (not per-round — see spec Assumptions). Overwritten in place on each update, no history retained. |

No new entity is introduced — this is a same-table extension, not a new related table, per the confirmed decision that feedback is a flat per-application field rather than a per-round history.

### Migration (existing installations)

Since `data/job_applications.db` already contains real user rows created before this feature, `init_db()` performs an additive, idempotent migration:

1. Run the existing `CREATE TABLE IF NOT EXISTS applications (...)` — now including the three new columns in its definition, so **fresh installs** get them for free.
2. Query `PRAGMA table_info(applications)` to get the actual current column names.
3. For each of `total_rounds`, `current_round`, `feedback` not present in that set, run `ALTER TABLE applications ADD COLUMN <name> <type>`.

Existing rows are untouched by step 3 beyond gaining the new columns with `NULL` values — no data is rewritten, no row is dropped or recreated. This satisfies FR-008/SC-004 (existing applications remain fully intact).

### Validation rules

- All three fields are optional at every entry point (creation, later edit, import) — no `NOT NULL`, no default value requirement.
- No cross-field validation between `total_rounds` and `current_round` (FR-003) — both are independent, freely editable integers.
- `feedback` has no length limit beyond SQLite's own `TEXT` column capacity (effectively unbounded for this app's scale).

### Relationship to import/export (`io_formats`)

`csv_io.py` and `excel_io.py`'s shared `COLUMNS` list is extended to `["id", "company", "role", "date_applied", "status", "job_post_url", "source_text", "total_rounds", "current_round", "feedback"]`. Both `to_csv`/`to_excel` write all ten columns; `from_csv`/`from_excel` continue to tolerate files with fewer columns (old export files predating this feature import cleanly, with the three new fields simply absent from each row's dict — handled by `.get()` with `None`/blank defaults in the import route, not by the io_formats layer itself).

# API Contract Changes: Interview Rounds Tracking and Feedback

Extends `specs/001-log-job-applications/contracts/api.md`. Only new/changed routes and fields are documented here; all other routes are unchanged.

## `POST /applications/parse` and `GET /` (unchanged endpoints, template context grows)

No route signature changes. `confirm_add.html` and `index.html` now also receive/display `total_rounds`, `current_round`, `feedback` values where present.

## `POST /applications` (extended)

Accepts three new optional form fields, in addition to the existing ones (`company`, `role`, `job_post_url`, `source_text`, `status`):

- `total_rounds` (optional, numeric string or blank)
- `current_round` (optional, numeric string or blank)
- `feedback` (optional, free text or blank)

Blank or missing values for any of the three are stored as `NULL`/unset — never rejected, never required. Behavior otherwise unchanged (creates the row with `date_applied = today()`, redirects to `/`).

## `POST /applications/{application_id}/details` (new)

Accepts form data: `total_rounds` (optional), `current_round` (optional), `feedback` (optional) — same optionality and blank-handling as above.

- Updates only these three fields on the given application; `company`, `role`, `date_applied`, `status`, `job_post_url`, `source_text` are untouched.
- A non-numeric `total_rounds`/`current_round` value is treated as unset (`NULL`) rather than causing an error — mirrors import behavior (FR-007).
- Redirects to `/` (303), consistent with `POST /applications/{id}/status`.

## `GET /export.csv`, `GET /export.xlsx` (extended)

Now include `total_rounds`, `current_round`, `feedback` as three additional columns, appended after the existing `source_text` column.

## `POST /import` (extended row handling)

Per-row, in addition to existing validation (company/role required, status must be valid):

- `total_rounds`/`current_round`: parsed as integers if present and numeric; blank, missing, or non-numeric values are treated as unset (`NULL`) and do **not** cause the row to be rejected (FR-007, User Story 3 Acceptance Scenario 3).
- `feedback`: taken as-is if present and non-blank, otherwise `NULL`.

Import summary counts (imported/skipped-as-duplicate/rejected) are unchanged in meaning — these three fields never move a row between those categories on their own.

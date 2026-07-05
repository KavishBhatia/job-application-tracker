# Quickstart: Separate Pages Navigation

## Prerequisites

Same as `specs/001-log-job-applications/quickstart.md` — `uv sync`, optional `GEMINI_API_KEY` in `.env`.

## Run

```bash
uv run uvicorn src.app:app --reload
```

Open http://localhost:8000

## Validation scenarios

These map to this feature's spec acceptance scenarios (`spec.md`) and `contracts/api.md`.

### 1. Navigate between dedicated pages (User Story 1)

1. Open the app at `/`. Expect: the "Add Application" page — only the sentence-input form, no table, no import/export controls.
2. Click the nav link to "Applications". Expect: the table of logged applications, no add-application form, no import/export controls.
3. Click the nav link to "Import / Export". Expect: export links and the import form, no add-application form, no table.
4. From any of the three pages, confirm the nav is visible and lets you reach either other page directly.

### 2. Land on Applications after a change (User Story 2)

1. From the "Add Application" page, log a new application through the usual sentence → confirm flow.
2. Expect: after saving, you land on the "Applications" page and see the new entry.
3. On the "Applications" page, change an existing application's status via its dropdown.
4. Expect: you remain on (or return to) the "Applications" page with the updated status visible.
5. Expand a row, update its total rounds/current round/feedback, and save.
6. Expect: you land on the "Applications" page with the updated values visible.

### 3. Expand/collapse row details (User Story 3)

1. On the "Applications" page, confirm each row shows only company, role, date applied, and status.
2. Click a row. Expect: it expands in place to show the job posting link (if any), total rounds, current round, and feedback — with the rounds/feedback fields editable and a Save button.
3. Click the same row again. Expect: it collapses back to the compact view.
4. Expand two different rows at once. Expect: both stay expanded independently; collapsing one doesn't affect the other.
5. On a collapsed row, change its status via the dropdown. Expect: the row does **not** expand as a side effect.
6. Reload the page. Expect: all rows are collapsed again (expand/collapse state is not persisted, per spec Assumptions).

## Regression check (existing functionality must be unaffected, FR-015)

1. Log an application via the free-text parse flow — confirm Gemini parsing (or the manual fallback) still works.
2. Export the applications list as CSV and Excel from the "Import / Export" page — confirm both downloads work and include all expected columns.
3. Re-import the exported CSV — confirm duplicates are correctly skipped.
4. Import a CSV with an invalid status value — confirm that row is still rejected.

## Running the test suite

```bash
uv run pytest
```

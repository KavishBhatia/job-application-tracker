# Quickstart: Interview Rounds Tracking and Feedback

## Prerequisites

Same as `specs/001-log-job-applications/quickstart.md` — `uv sync`, optional `GEMINI_API_KEY` in `.env`.

## Run

```bash
uv run uvicorn src.app:app --reload
```

Open http://localhost:8000

## Validation scenarios

These map to this feature's spec acceptance scenarios (`spec.md`) and `contracts/api.md`.

### 1. Update rounds/feedback on an existing application (User Story 1)

1. Log an application (or use an existing one).
2. In its row, fill in total rounds (e.g. `4`), current round (e.g. `1`), and feedback (e.g. "Went well, waiting to hear back"), then click Save.
3. Expect: the row now shows all three values, and they persist after reloading `/`.
4. Update only the current round to `2`, leaving the other two fields as shown. Expect: only current round changes; total rounds and feedback are unchanged.
5. Set current round to a value greater than total rounds (e.g. current round `5`, total rounds `4`). Expect: saves successfully, no warning or rejection.

### 2. Set rounds/feedback at creation time (User Story 2)

1. Start logging a new application via the free-text flow.
2. On the confirm screen, fill in total rounds, current round, and feedback before saving.
3. Expect: the new entry appears in the list with those values already set.
4. Repeat leaving all three blank. Expect: the application still saves successfully.

### 3. Export/import preserves rounds and feedback (User Story 3)

1. With at least one application having rounds/feedback set, export as CSV (or Excel).
2. Expect: the exported file includes `total_rounds`, `current_round`, `feedback` columns with the correct values.
3. Re-import that same file. Expect: values are skipped as duplicates (unchanged data), same as any other re-import.
4. Edit the exported file: add a new row with a non-numeric `total_rounds` value (e.g. `"N/A"`) but valid company/role. Re-import. Expect: the row is still imported (not rejected), with `total_rounds` left blank/unset.

## Backward compatibility check (critical for this feature)

1. Before pulling this feature's code, note how many applications exist in your current `data/job_applications.db` (e.g. via the list view or `sqlite3 data/job_applications.db "SELECT COUNT(*) FROM applications;"`).
2. After upgrading and restarting the app (`uv run uvicorn src.app:app --reload`) against that **same, existing** database file (do not delete it), confirm:
   - The same number of applications still appear in the list.
   - Every previously-logged application still shows its original company/role/date/status/job posting link correctly.
   - Total rounds, current round, and feedback show as blank/unset on those pre-existing rows (expected — they didn't have this data before).

## Running the test suite

```bash
uv run pytest
```

# Data Model: Log Job Applications

## Entity: `JobApplication`

Single table, `applications`, in the SQLite database (`data/job_applications.db`).

| Field | Type | Constraints / Notes |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Assigned by SQLite; never supplied by the client, including on import (an `id` column present in an imported file is ignored). |
| `company` | `TEXT NOT NULL` | Non-empty after trimming whitespace. User-editable at creation (via the confirm/edit step, FR-003) and not locked afterward. |
| `role` | `TEXT NOT NULL` | Non-empty after trimming whitespace. Same editability as `company`. |
| `date_applied` | `TEXT` (ISO `YYYY-MM-DD`) `NOT NULL` | See "Date reconciliation" below — behavior differs between manual entry and import. |
| `status` | `TEXT NOT NULL DEFAULT 'Applied'` | One of the fixed `ApplicationStatus` enum values (see below). Validated at the application layer (pydantic), not via a DB `CHECK` constraint — keeps the schema minimal and keeps validation logic in one place (`models.py`). |
| `job_post_url` | `TEXT` (nullable) | Optional (FR-005). Stored as entered; no reachability check, only basic well-formedness (non-empty if provided). |
| `source_text` | `TEXT` (nullable) | The original free-text sentence, if this row originated from the free-text flow (User Story 1). `NULL` for rows created via import, since those have no originating sentence. |

### `ApplicationStatus` enum

Exactly five values, matching FR-007 / the status dropdown:

```
Applied, Interviewing, Offer, Rejected, Withdrawn
```

No transition graph is enforced — any value can move to any other value (e.g. "Interviewing" → "Applied" is allowed), per spec Acceptance Scenario US2-3. This is a deliberate Simplicity choice: the tool has one user who may need to correct mistakes, so a transition state machine would be speculative complexity with no current need.

### Date reconciliation (manual entry vs. import)

The spec's FR-004 ("system MUST automatically record the date... users MUST NOT be able to manually set or backdate this date when logging via free text") applies specifically to the free-text/manual add path (User Story 1). It does not apply to import (User Story 3), which exists specifically to bring in historical records that may predate the import action:

- **Free-text add path** (`POST /applications`): `date_applied` is always set server-side to `today()`. Any client-supplied date value for this path is ignored.
- **Import path** (`POST /import`): `date_applied` is read from the imported row's `date_applied` column. If that column is absent or blank for a given row, it falls back to `today()`.

### Duplicate detection (import only)

Per FR-013, a row is treated as a duplicate — and skipped — if an existing row already matches on all three of: `company`, `role`, `date_applied`, compared after trimming whitespace and case-folding `company`/`role` (so `"Google"` and `" google "` are the same key). `job_post_url` is intentionally excluded from the dedupe key, so adding or correcting a link later never creates a duplicate.

### Row validation on import (FR-014)

A row is rejected (not imported, reported separately from successful imports and duplicate skips) if:
- `company` or `role` is missing/blank after trimming, or
- `status` is present but is not one of the five valid `ApplicationStatus` values.

A row with a missing/blank `status` is not rejected — it defaults to `"Applied"` (see spec Assumptions).

### Out of scope for this data model

- No `created_at`/`updated_at` timestamps — no stated requirement needs them (YAGNI); can be added later if a concrete need (e.g., sorting by last change) appears.
- No multi-user fields (owner/user_id) — spec Assumptions confirm this is a single-user tool with no auth.

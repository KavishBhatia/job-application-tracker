# Data Model: Separate Pages Navigation

## No database schema changes

This feature introduces no new persisted fields and no new tables. `src/db.py`'s `applications` table (see `specs/001-log-job-applications/data-model.md` and `specs/002-interview-rounds-feedback/data-model.md` for its current 10 columns) is unchanged. `init_db()`'s migration logic is unchanged.

## Entity: `Page` (navigational concept, not persisted)

Not a database entity — a UI/routing concept representing which of the three views a user is on. Not stored anywhere; determined entirely by which route served the current response.

| Page | Route | Content |
|---|---|---|
| Add Application | `GET /` | Sentence-based add-application form only |
| Applications | `GET /applications` | The applications table (collapsed rows + expandable detail rows) |
| Import / Export | `GET /import-export` | Export links + import form |

## Row expand/collapse state (client-side only, not persisted)

Per FR-010–FR-013 and the spec's Assumptions, whether a given application row is expanded or collapsed is transient UI state:

- Held only in the DOM (the `hidden` attribute on that row's detail `<tr>`), toggled by a client-side script.
- Not written to the database, not passed in any URL, not part of any request/response payload.
- Resets to fully collapsed on every page load/reload, per the spec's explicit assumption that expansion state does not need to persist across navigation.
- Independent per row — toggling one row's `hidden` attribute has no effect on any other row's.

## Relationship to existing `JobApplication` entity

Unchanged. Every field the Applications page reads or writes (`company`, `role`, `date_applied`, `status`, `job_post_url`, `total_rounds`, `current_round`, `feedback`) already exists per features 001/002. This feature only changes *which page* renders them and *how much is visible by default* — not what is stored or how it's validated.

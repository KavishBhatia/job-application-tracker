# API Contract Changes: Separate Pages Navigation

Extends `specs/001-log-job-applications/contracts/api.md` and `specs/002-interview-rounds-feedback/contracts/api.md`. Only new/changed routes are documented here; request/response bodies for unchanged fields are unaffected.

## `GET /` (changed)

Previously rendered `index.html` with the add-application form, applications table, and import/export controls all together. Now renders `add.html`, containing **only** the sentence-based add-application form (`text`, `job_post_url` inputs, "Continue" button posting to `/applications/parse`). No `applications` or `import_summary` context is needed for this route anymore.

## `GET /applications` (new)

Renders `applications.html`: the full applications table, one summary `<tr>` per application (company, role, date applied, status) plus a hidden detail `<tr>` per application (job posting link, total rounds, current round, feedback — editable). Context: `applications` (from `db.list_applications()`), `statuses` (for the status dropdown), same as the table context `GET /` used to provide.

## `GET /import-export` (new)

Renders `import_export.html`: the CSV/Excel export links and the import file-upload form. No applications data needed in context.

## `POST /applications/parse` and `confirm_add.html` (unchanged)

No route signature or template changes. Still reached from the "Add Application" page's form, still renders `confirm_add.html` on success or falls back with a `parse_error`/`parse_notice`.

## `POST /applications` (redirect target changed)

Request body unchanged (`company`, `role`, `job_post_url`, `source_text`, `status`, `total_rounds`, `current_round`, `feedback`, `date_applied` — all as established by features 001/002). Redirect target changes from `RedirectResponse(url="/", status_code=303)` to `RedirectResponse(url="/applications", status_code=303)`.

## `POST /applications/{application_id}/status` (redirect target changed)

Request body unchanged. Redirect target changes from `"/"` to `"/applications"`.

## `POST /applications/{application_id}/details` (redirect target changed)

Request body unchanged. Redirect target changes from `"/"` to `"/applications"`.

## `GET /export.csv`, `GET /export.xlsx` (unchanged)

Download endpoints, not pages — unaffected by the page split. Reachable from the new "Import / Export" page's links, same URLs as before.

## `POST /import` (template target changed, no redirect)

Request/response behavior unchanged (same validation, same "Imported: X, Skipped as duplicates: Y, Rejected: Z" summary). Renders `import_export.html` directly (200, no redirect) instead of `index.html`, with `import_summary` in context — same direct-render-with-summary pattern as before, just pointed at the new template.

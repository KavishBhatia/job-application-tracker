# Phase 0 Research: Separate Pages Navigation

## Decision: Three separate Jinja2 templates + three GET routes, no client-side router

**Rationale**: The app is server-rendered (FastAPI + Jinja2, no SPA framework), and each of the three pages has fully disjoint content (per FR-004/005/006, "MUST NOT display" the other pages' controls) except the shared header/nav. The simplest way to satisfy that is one template and one `GET` route per page, each a full page render — consistent with how `confirm_add.html` already works as its own full-page render reached via a `POST`. No client-side routing library is needed or justified.

**Alternatives considered**: A single template with conditional `{% if page == "..." %}` blocks — rejected, since the pages share no body content (only the nav), so conditionals would just be a worse way to express what three separate templates already express directly, and would still need to override `content` differently per route.

## Decision: Redirect target for all three mutating endpoints changes from `/` to `/applications`

**Rationale**: FR-007/FR-008 and User Story 2 require the user to land on the Applications page after adding an application or updating status/details. Today all three handlers (`POST /applications`, `POST /applications/{id}/status`, `POST /applications/{id}/details`) already do `RedirectResponse(url="/", status_code=303)` — since `/` used to serve the page with the table. The only change needed is the redirect URL string, from `"/"` to `"/applications"`; the 303-redirect-after-POST pattern itself (already correct for avoiding re-submit-on-refresh) is unchanged.

**Alternatives considered**: Rendering the Applications template directly from each POST handler (no redirect) — rejected, breaks the existing POST-redirect-GET pattern and would resubmit the form on browser refresh, a regression from current behavior.

## Decision: Row expand/collapse via a same-page vanilla JS click toggle on a `hidden` sibling `<tr>`, no accordion library

**Rationale**: Per FR-010/011/012/013 and User Story 3, expanding must happen in place, independently per row, without navigating away, and must not be triggered by the status dropdown. The simplest implementation reuses the native HTML `hidden` attribute (already boolean, no CSS needed beyond what the browser provides by default) on a second `<tr class="app-detail">` per application, toggled by a click listener on the summary `<tr>`. This mirrors the existing inline `<script>` pattern already used for the theme toggle in `base.html` — no new JS file is strictly required, though a separate `static/app.js` is acceptable if the script grows large enough to be worth separating; either is consistent with Simplicity & YAGNI.

**Alternatives considered**: The native `<details>`/`<summary>` element — rejected, because `<details>` cannot syntactically wrap `<tr>`/`<td>` table structure without breaking valid table semantics (a `<details>` can't be a direct child of `<tbody>`). A JS accordion library — rejected as unjustified complexity for a single, simple show/hide toggle.

**Implementation note**: the click listener must ignore clicks whose target is inside a `<select>` (or its `<option>`s), via `event.target.closest('select')`, so changing an application's status does not also toggle row expansion (FR-013). This requires no library — a single `if` check.

## Decision: Detail row uses a single `<form>` in one `<td colspan="N">`, retiring the cross-cell `form="id"` technique

**Rationale**: Feature 002 needed the HTML5 `form="id"` attribute technique (one `<form>`, inputs scattered across separate `<td>`s) specifically because total rounds / current round / feedback were three separate always-visible table columns. Now that these fields move into a single collapsible detail row with one `<td>`, a single ordinary `<form>` wrapping all three inputs plus the Save button works directly — no cross-cell trick needed. This is a simplification enabled by the new layout, not an additional decision to make from scratch.

**Alternatives considered**: keeping the `form="id"` technique for consistency with the previous feature — rejected, since it would be strictly more complex than necessary once the fields share one cell.

## Decision: `POST /import` keeps rendering a template directly (no redirect), now pointed at `import_export.html`

**Rationale**: `POST /import` currently renders `index.html` directly with an `import_summary` in context, rather than redirecting — this lets it show the "Imported: X, Skipped: Y, Rejected: Z" summary inline without needing flash-message/session infrastructure. That pattern is unaffected by the page split; it simply needs to render `import_export.html` instead of `index.html`, since that's now the page containing the import control.

**Alternatives considered**: Redirecting to `/import-export` with the summary passed via query string or a flash mechanism — rejected as unnecessary complexity; the existing direct-render pattern already works and needs no behavioral change, only a template name change.

## Decision: Persistent nav is a plain `<nav>` with three links in `base.html`, no active-page highlighting

**Rationale**: FR-003 requires the nav to be present and usable on all three pages ("persistent"); it does not require indicating which page is currently active. Per the approved plan, active-page highlighting is explicitly deferred as optional future polish (YAGNI) — three plain links reaching `/`, `/applications`, `/import-export` fully satisfy the functional requirement and SC-001 (reach any other page in one click).

**Alternatives considered**: passing an `active_page` context variable from every route and adding conditional `class="active"` in the nav template — rejected for this pass as unnecessary for the stated requirements; can be added later without restructuring anything else if wanted.

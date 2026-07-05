# Feature Specification: Separate Pages Navigation

**Feature Branch**: `003-separate-pages`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "Split the single crowded page into three dedicated pages reachable via persistent header navigation: an \"Add Application\" page with the sentence-based add form (this becomes the home page), an \"Applications\" page listing all logged applications, and an \"Import / Export\" page for CSV/Excel import and export. On the Applications page, each row shows only company, role, date applied, and status by default, decluttering the table; clicking a row expands it in place to reveal the job posting link, total rounds, current round, and feedback (all editable), and collapses back when clicked again. After adding an application or updating its status/details, the user lands on the Applications page to see the result."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate between dedicated pages (Priority: P1) 🎯 MVP

A user visiting the tracker sees a focused "Add Application" page first, and can move to a separate "Applications" page or a separate "Import / Export" page at any time using a persistent navigation menu, instead of scrolling through one long page containing everything at once.

**Why this priority**: This is the structural core of the feature — without separate pages and navigation between them, nothing else in this feature has anywhere to live. It is also immediately valuable on its own: it declutters the experience even before the row-expansion behavior is added.

**Independent Test**: Load the app, confirm the "Add Application" page appears first with only the add-application form. Use the navigation menu to reach the "Applications" page and confirm it shows the table without the add form or import/export controls. Use the navigation menu to reach the "Import / Export" page and confirm it shows only export and import controls. Confirm the navigation menu is present and usable from all three pages.

**Acceptance Scenarios**:

1. **Given** a user opens the tracker, **When** the home page loads, **Then** they see the "Add Application" page with the sentence-based add form and no applications table or import/export controls.
2. **Given** a user is on any of the three pages, **When** they select a different page from the navigation menu, **Then** they are taken to that page and it shows only the content relevant to it.
3. **Given** a user is on the "Applications" page, **When** they view it, **Then** they see all previously logged applications and no add-application form or import/export controls.
4. **Given** a user is on the "Import / Export" page, **When** they view it, **Then** they see the export and import controls and no add-application form or applications table.

---

### User Story 2 - Land on the Applications page after making a change (Priority: P2)

After a user adds a new application, or updates an existing application's status or interview details, they are taken to the "Applications" page so they can immediately see the effect of what they just did.

**Why this priority**: This ensures the split into separate pages doesn't break the existing, already-valuable workflow of adding and updating applications — users must not be stranded on the add-application page after saving, unable to see their new entry without manually navigating away.

**Independent Test**: From the "Add Application" page, submit a new application and confirm the user ends up on the "Applications" page seeing the new entry. From the "Applications" page, change an application's status or update its interview details and confirm the user remains on (or returns to) the "Applications" page seeing the updated values.

**Acceptance Scenarios**:

1. **Given** a user completes the add-application flow, **When** they save the new application, **Then** they are shown the "Applications" page with the new entry visible.
2. **Given** a user changes an application's status on the "Applications" page, **When** the change is saved, **Then** they remain on the "Applications" page and see the updated status.
3. **Given** a user updates an application's interview rounds or feedback, **When** the change is saved, **Then** they are shown the "Applications" page with the updated values visible.

---

### User Story 3 - Expand a row to see and edit full details (Priority: P3)

On the "Applications" page, each application initially shows only its company, role, date applied, and status, keeping the table compact and easy to scan. Clicking anywhere on a row reveals the rest of that application's details — the job posting link, total interview rounds, current round, and feedback — in place, without navigating to a different page. Clicking the row again (or clicking a different row) collapses it back to the compact view.

**Why this priority**: This is a refinement of the "Applications" page's usability once it exists as its own page — valuable, but the page is still functional (just more crowded per row) without it, so it is lower priority than establishing the pages themselves and preserving the add/update workflow.

**Independent Test**: On the "Applications" page with at least one logged application, confirm each row initially shows only company, role, date applied, and status. Click a row and confirm it expands to reveal the job posting link, total rounds, current round, and feedback, with the rounds and feedback fields editable and savable. Click the row again and confirm it collapses back to the compact view.

**Acceptance Scenarios**:

1. **Given** the "Applications" page has logged applications, **When** it loads, **Then** each row shows only company, role, date applied, and status.
2. **Given** a collapsed row, **When** the user clicks it, **Then** it expands in place to show the job posting link, total rounds, current round, and feedback for that application.
3. **Given** an expanded row, **When** the user clicks it again, **Then** it collapses back to showing only company, role, date applied, and status.
4. **Given** an expanded row, **When** the user edits the total rounds, current round, or feedback and saves, **Then** the updated values are persisted and visible next time that row is expanded.
5. **Given** a collapsed row, **When** the user changes its status dropdown, **Then** the row does not expand as a side effect of that interaction.

---

### Edge Cases

- An application with no job posting link: the expanded row shows no link (rather than a broken or empty link element).
- An application with no interview rounds or feedback recorded yet: the expanded row shows those fields empty and editable, not as errors.
- Multiple rows expanded at once: each row expands and collapses independently of the others.
- Navigating directly to the "Applications" or "Import / Export" page (not via the home page first) works the same as reaching it through navigation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide three distinct pages: an "Add Application" page, an "Applications" page, and an "Import / Export" page.
- **FR-002**: The system MUST make the "Add Application" page the default page a user sees when opening the tracker.
- **FR-003**: The system MUST provide a persistent navigation menu, visible on all three pages, that allows moving directly to any of the other two pages.
- **FR-004**: The "Add Application" page MUST contain only the sentence-based add-application form and MUST NOT display the applications table or import/export controls.
- **FR-005**: The "Applications" page MUST display all logged applications and MUST NOT display the add-application form or import/export controls.
- **FR-006**: The "Import / Export" page MUST contain the export controls and the import control, and MUST NOT display the add-application form or the applications table.
- **FR-007**: After a user successfully adds a new application, the system MUST show the user the "Applications" page with the new entry present.
- **FR-008**: After a user updates an existing application's status, or its interview rounds/current round/feedback, the system MUST show the user the "Applications" page reflecting the update.
- **FR-009**: On the "Applications" page, each application row MUST, by default, display only company, role, date applied, and status.
- **FR-010**: The system MUST allow a user to reveal an application's job posting link, total rounds, current round, and feedback by interacting with (clicking) its row, without leaving the "Applications" page.
- **FR-011**: The system MUST allow a user to hide a row's revealed details by interacting with it again, returning it to showing only company, role, date applied, and status.
- **FR-012**: Revealing or hiding one row's details MUST NOT affect the revealed/hidden state of any other row.
- **FR-013**: Changing a row's status MUST NOT, by itself, reveal or hide that row's details.
- **FR-014**: The total rounds, current round, and feedback fields MUST remain editable and savable while a row's details are revealed, consistent with existing editing behavior.
- **FR-015**: All existing application functionality (parsing a sentence into company/role, confirming details before saving, status values, CSV/Excel export and import, duplicate-skipping on import) MUST continue to work unchanged after the page split.

### Key Entities

- **Page**: One of the three distinct views a user can be on ("Add Application", "Applications", "Import / Export"). Not a data entity — a navigational concept.
- **Application** (existing entity, unchanged): a logged job application with company, role, date applied, status, optional job posting link, and optional total rounds / current round / feedback.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can identify which of the three pages they are on, and reach either of the other two, within a single interaction (one click), from any page.
- **SC-002**: After adding an application or updating one's status or interview details, the user sees the result on the Applications page without any additional manual navigation.
- **SC-003**: A user can view an application's full details (job posting link, rounds, feedback) and return to the compact list view without a full page navigation, in two clicks or fewer (one to expand, one to collapse).
- **SC-004**: On a list of applications, the default (collapsed) view surfaces only the four most identifying fields per application (company, role, date applied, status), reducing per-row information density compared to the previous single-page table.

## Assumptions

- Only one type of navigation menu is needed (a simple, always-visible menu); no user roles or permissions affect which pages are visible.
- "Persistent" navigation means present and usable on every page, not that it must remain scrolled into view at all times (e.g., a header that scrolls with the page is acceptable).
- This is a single-user personal tool, so there is no concept of multiple users needing different default/home pages.
- Row expansion state does not need to persist across page reloads or navigation away and back — it is expected to reset to fully collapsed each time the "Applications" page is loaded.
- This feature is purely about information architecture and navigation; it introduces no new data fields and does not change what data is recorded about an application.

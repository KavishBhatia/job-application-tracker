# Feature Specification: Log Job Applications

**Feature Branch**: `001-log-job-applications`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Add a way to log job applications by entering a free-text sentence (e.g. \"Applied at XYZ company for ABC role\"), written in whatever phrasing feels natural. The system extracts the company and role from that sentence, automatically records the date the entry was created (never user-entered), and lets the user set/update an application status via a dropdown: Applied, Interviewing, Offer, Rejected, Withdrawn. The user can optionally provide a link to the job posting when adding an application (entered as a separate field, not extracted from the free text), which is stored and shown alongside the entry. If the system can't confidently extract company/role from the text, the user can fill them in manually before saving - never blocked. Users can export their full application list as CSV or Excel, and import a CSV/Excel file to bulk-add applications (skip rows that duplicate an existing company+role+date entry). Automated tests are required for every user story in this feature - the project constitution mandates Test-First development, which overrides this template's default test-optionality."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Log an application by typing a sentence (Priority: P1)

A job seeker wants to record that they've applied somewhere without filling out a form. They type a natural sentence describing what happened (e.g., "Applied at XYZ company for ABC role"), and the system figures out the company and role on its own, stamps the entry with today's date, and adds it to their list.

**Why this priority**: This is the core value of the feature — fast, frictionless logging. Without it, there is no product; every other capability (status tracking, import/export) operates on entries created this way.

**Independent Test**: Can be fully tested by typing a free-text sentence describing an application and confirming a new entry appears in the list with the correct company, role, and today's date — delivers value on its own even with no other capability built.

**Acceptance Scenarios**:

1. **Given** the application list is empty, **When** the user types "Applied at XYZ company for ABC role" and submits, **Then** a new entry appears in the list with company "XYZ company", role "ABC role", and date applied equal to today.
2. **Given** the user types a sentence in different phrasing (e.g., "Sent my resume to Acme for a Backend Engineer position"), **When** they submit it, **Then** the system still correctly identifies "Acme" as the company and "Backend Engineer" as the role.
3. **Given** the user has typed a sentence, **When** the system shows the identified company and role before saving, **Then** the user can edit either value before confirming, and the edited values are what get saved.
4. **Given** the user submits an empty or whitespace-only entry, **When** they attempt to save, **Then** the system rejects it and prompts them to enter application details.

---

### User Story 2 - Track application status (Priority: P2)

A job seeker wants to know at a glance where each application stands, and update that status as things progress (e.g., moving from "Applied" to "Interviewing").

**Why this priority**: Status tracking is the primary ongoing value of the tool after the initial log — it's what makes the list useful for follow-up, not just a historical record. It depends on User Story 1 (an entry must exist to have a status).

**Independent Test**: Can be fully tested by creating an entry, changing its status via the dropdown, and confirming the new status is reflected and persists.

**Acceptance Scenarios**:

1. **Given** an existing application entry, **When** the user opens its status dropdown, **Then** they see exactly the options: Applied, Interviewing, Offer, Rejected, Withdrawn.
2. **Given** an existing application entry with status "Applied", **When** the user selects "Interviewing" from the dropdown, **Then** the entry's displayed status updates to "Interviewing" and remains "Interviewing" after reloading the list.
3. **Given** an existing entry, **When** the user changes its status multiple times in any order (including moving "backwards", e.g., "Interviewing" to "Applied"), **Then** each change is accepted and reflected.

---

### User Story 3 - Bulk export and import applications (Priority: P3)

A job seeker wants to back up their application list, work with it in a spreadsheet, or bring in a list of applications they'd already been tracking elsewhere.

**Why this priority**: Valuable for data portability and recovery, but not required for the tool to deliver its core day-to-day value — a user can log and track applications fully without ever exporting or importing.

**Independent Test**: Can be fully tested by exporting the current list to a file, then importing that same file back in, and confirming no duplicate entries are created and all data reappears correctly.

**Acceptance Scenarios**:

1. **Given** the user has one or more logged applications, **When** they export their list, **Then** they can choose either a CSV file or an Excel file containing all their applications.
2. **Given** a previously exported file, **When** the user imports it back into an application list that already contains those same entries, **Then** no duplicate entries are created, and the system reports how many rows were skipped as duplicates.
3. **Given** a file containing new applications not already in the list, **When** the user imports it, **Then** each new row becomes a new entry, and the system reports how many rows were successfully imported.
4. **Given** a file containing some rows with missing required information (e.g., no company or no role), **When** the user imports it, **Then** those rows are rejected and reported to the user, while valid rows are still imported.

---

### Edge Cases

- What happens when the free-text sentence contains no discernible company or role? The entry is not blocked — the user is prompted to fill in the missing field(s) manually before saving, per User Story 1.
- What happens when a user submits an empty or whitespace-only free-text entry? The system rejects it and prompts for details, rather than creating a blank entry.
- What happens when an imported row is missing a status value? It defaults to "Applied" (see Assumptions).
- What happens when an imported row has a status value that isn't one of the five valid options? The row is rejected and reported, consistent with other invalid-row handling.
- What happens when two entries legitimately share the same company, role, and date (e.g., a genuine re-application on the same day)? This is treated as a duplicate and will be skipped on import; this is an accepted limitation (see Assumptions).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to add a job application by entering a free-text sentence describing it (e.g., "Applied at XYZ company for ABC role").
- **FR-002**: System MUST automatically identify the company name and role from the entered sentence, regardless of the exact phrasing or word order used.
- **FR-003**: System MUST show the user the identified company and role before the entry is saved, and MUST allow the user to correct either value prior to confirming.
- **FR-004**: System MUST automatically record the date an application entry is created; users MUST NOT be able to manually set or backdate this date when logging via free text.
- **FR-005**: Users MUST be able to optionally attach a link to the job posting when adding an application, entered as a field separate from the free-text sentence.
- **FR-006**: System MUST display each logged application together with its company, role, date applied, status, and job posting link (if one was provided).
- **FR-007**: Users MUST be able to set and change an application's status, choosing from exactly these options: Applied, Interviewing, Offer, Rejected, Withdrawn.
- **FR-008**: If the system cannot confidently identify the company and/or role from the entered sentence, it MUST let the user fill in the missing field(s) manually rather than blocking the entry from being saved.
- **FR-009**: System MUST reject empty or whitespace-only free-text submissions and prompt the user to enter application details instead of creating a blank entry.
- **FR-010**: Users MUST be able to export their full list of logged applications as a CSV file.
- **FR-011**: Users MUST be able to export their full list of logged applications as an Excel file.
- **FR-012**: Users MUST be able to import a CSV or Excel file to bulk-add applications to their list.
- **FR-013**: When importing, the system MUST skip any row whose company, role, and date applied all match an existing entry, and MUST report how many rows were imported versus skipped as duplicates.
- **FR-014**: When importing, the system MUST reject rows missing required information (company or role) or containing an invalid status value, and MUST report these rejections separately from successful imports and duplicate skips.
- **FR-015**: Automated tests MUST validate the behavior described in each user story above, written before the corresponding functionality is implemented (Test-First development, per project constitution).

### Key Entities

- **Job Application**: A single logged application. Key attributes: company name, role/title, date applied (system-recorded, not user-editable at creation), status (one of the five fixed options), an optional link to the job posting, and the original free-text sentence it was created from (if created that way, versus import).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can go from typing a sentence describing a new application to seeing it appear correctly in their list in under 30 seconds.
- **SC-002**: Users can change an application's status in a single interaction, without leaving or reloading the list view.
- **SC-003**: A user can export their full application list and re-import that same file with zero data loss and zero unintended duplicate entries.
- **SC-004**: Every application a user attempts to log is saved successfully — either with automatically identified company/role, or with the user's manual corrections — with none silently lost due to identification failure.
- **SC-005**: When importing a file containing a mix of valid, duplicate, and invalid rows, a user can tell from the result exactly how many rows fell into each category, with no ambiguity about what happened to their data.

## Assumptions

- Rows in an imported file with a missing/blank status default to "Applied"; rows with a status value that doesn't match one of the five valid options are rejected and reported rather than guessed at.
- Applications with identical company, role, and date applied are always treated as duplicates during import (even if they represent a genuine same-day re-application) — an accepted limitation favoring safety against accidental duplicate imports over this rarer edge case.
- The job posting link, if provided, is stored and displayed as-is; the system does not verify that the link is reachable or well-formed beyond basic sanity.
- This is a single-user tool with no login/authentication or multi-user access control — all applications belong to the one person using it.
- No limit is placed on the number of applications a user can log; the tool is expected to comfortably handle a personal job search's worth of entries (dozens to low hundreds).

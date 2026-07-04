# Feature Specification: Interview Rounds Tracking and Feedback

**Feature Branch**: `002-interview-rounds-feedback`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "Let users optionally record, for each logged job application, how many interview rounds the process is expected to have, which round they are currently on, and free-text feedback they've received - so they can track interview progress and remember feedback alongside the application, without requiring this information up front since it's often unknown when first applying. Users can fill these in when first logging an application, or add/edit them later on an existing entry. These fields are included when exporting or importing the application list, consistent with every other field."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update interview progress on an existing application (Priority: P1)

A job seeker learns more about an application's process after applying (e.g., a recruiter tells them there are 4 rounds, or they finish round 2). They go to their already-logged application and record the total number of rounds, which round they're currently on, and any feedback they've received, without re-entering the company, role, or any other detail.

**Why this priority**: This is the core, ongoing value of the feature. Total rounds and current progress are usually unknown at the moment of applying, so most of this feature's value comes from updating an existing entry as the process unfolds, not from data entered at creation time.

**Independent Test**: Can be fully tested by logging an application, then separately updating its total rounds, current round, and feedback, and confirming the new values are shown and persist after a page reload — delivers value even if creation-time entry (User Story 2) didn't exist.

**Acceptance Scenarios**:

1. **Given** an existing logged application with no rounds or feedback set, **When** the user sets total rounds to 4, current round to 1, and feedback to "Went well, waiting to hear back", **Then** the application now displays all three values.
2. **Given** an application with rounds/feedback already set, **When** the user updates only the current round (leaving total rounds and feedback unchanged), **Then** only the current round changes; the other two values are preserved.
3. **Given** an application, **When** the user sets a current round value without ever setting a total rounds value (or vice versa), **Then** the save succeeds — neither field requires the other to be set.
4. **Given** an application, **When** the user changes current round to a value greater than total rounds (e.g., current round 5 with total rounds 4), **Then** the save succeeds without any warning or rejection — these two values are independent and unrestricted.

---

### User Story 2 - Optionally record rounds and feedback when first logging an application (Priority: P2)

A job seeker already knows some details upfront (e.g., a referral told them the process has 3 rounds) and wants to record that at the moment they log the application, instead of coming back to it later.

**Why this priority**: A convenience on top of User Story 1's core capability — useful when the information happens to be known upfront, but the feature is fully usable without it (via User Story 1 alone).

**Independent Test**: Can be fully tested by logging a new application while filling in total rounds, current round, and/or feedback during that same flow, and confirming the saved entry shows those values immediately — independent of ever using the later-edit capability.

**Acceptance Scenarios**:

1. **Given** the user is logging a new application, **When** they fill in total rounds, current round, and feedback before saving, **Then** the new entry is created with those values already set.
2. **Given** the user is logging a new application, **When** they leave total rounds, current round, and feedback all blank, **Then** the application still saves successfully with all three left unset.

---

### User Story 3 - Round and feedback data survives export and import (Priority: P3)

A job seeker exports their application list to back it up or work with it in a spreadsheet, and expects their round-tracking and feedback notes to be included, not silently dropped.

**Why this priority**: Extends existing, already-valuable export/import capability to stay consistent with the rest of the data; lower priority since it depends on both prior stories and export/import already working for every other field.

**Independent Test**: Can be fully tested by setting rounds/feedback on an application, exporting the list, and confirming the exported file contains those values — independent of whether the file is ever re-imported.

**Acceptance Scenarios**:

1. **Given** applications with total rounds, current round, and feedback set, **When** the user exports their list (CSV or Excel), **Then** the exported file includes all three values alongside every other existing field.
2. **Given** a previously exported file containing these three fields, **When** the user imports it, **Then** the imported applications retain the same total rounds, current round, and feedback values.
3. **Given** an imported file where a row has a non-numeric or blank value for total rounds or current round, **When** the user imports it, **Then** that row is still imported successfully (not rejected), with the unparseable field simply left unset — consistent with these fields being optional.

---

### Edge Cases

- What happens to applications logged before this feature existed? They continue to display and function correctly, with total rounds, current round, and feedback simply shown as unset until the user edits them.
- What happens if current round is set higher than total rounds, or either is set without the other? Both succeed — there is no enforced relationship between the two values (see User Story 1, Acceptance Scenario 4).
- What happens when an imported row has an invalid (non-numeric) round value? The row still imports; that specific field is left unset rather than causing the whole row to be rejected (see User Story 3, Acceptance Scenario 3).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to add or update total interview rounds, current round, and feedback on an existing logged application, without needing to re-enter any other field of that application.
- **FR-002**: Total rounds, current round, and feedback MUST all be optional; leaving any or all of them blank MUST NOT prevent saving or updating an application.
- **FR-003**: The system MUST NOT enforce any relationship between total rounds and current round (e.g., current round is not required to be less than or equal to total rounds).
- **FR-004**: Users MUST be able to optionally provide total rounds, current round, and feedback at the moment they first log a new application, with the same optionality described in FR-002.
- **FR-005**: Every displayed application MUST show its current total rounds, current round, and feedback values when set.
- **FR-006**: Exporting the application list MUST include total rounds, current round, and feedback alongside all existing fields.
- **FR-007**: Importing a file MUST accept total rounds, current round, and feedback when present in the file, and MUST NOT reject a row solely because one of these three fields is blank or not a valid number — only a missing company/role or an invalid status value continue to reject a row (existing behavior unchanged).
- **FR-008**: Applications that existed before this feature was added MUST continue to display and remain fully usable, with total rounds, current round, and feedback simply shown as unset until a user sets them.
- **FR-009**: Automated tests MUST validate the behavior described in each user story above, written before the corresponding functionality is implemented (Test-First development, per project constitution).

### Key Entities

- **Job Application** (extended): in addition to its existing attributes (company, role, date applied, status, job posting link), each application now optionally has: total interview rounds (a whole number), current round (a whole number), and feedback (free text). All three are independent of each other and of every other attribute.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can update an existing application's round progress and feedback in a single action, without navigating to a separate page.
- **SC-002**: A user who doesn't know the total number of rounds when applying can log the application immediately and add that information later without re-entering any other detail about the application.
- **SC-003**: Exporting and then re-importing a user's full application list preserves 100% of round and feedback data, with zero data loss.
- **SC-004**: Every application a user had logged before this feature existed remains fully intact and usable immediately after the feature is added — zero existing applications are lost or corrupted.

## Assumptions

- Feedback is a single free-text note per application, not a separate note per individual interview round.
- No validation relationship is enforced between current round and total rounds; both are independent, freely-editable optional numbers.
- This feature introduces no notifications, reminders, or alerts tied to round changes — the three fields are purely informational and displayed/edited on demand.

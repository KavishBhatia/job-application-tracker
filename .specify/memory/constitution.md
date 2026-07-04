<!--
Sync Impact Report
- Version change: (none) → 1.0.0
- Modified principles: n/a (initial ratification)
- Added sections:
  - Core Principles: I. Simplicity & YAGNI, II. Test-First Development (NON-NEGOTIABLE)
  - Technology Constraints
  - Development Workflow
  - Governance
- Removed sections: Principle slots III–V from the template (not used; this project
  defines 2 principles, not 5)
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Constitution Check gate is generic/dynamic, no edit needed)
  - ✅ .specify/templates/spec-template.md (no constitution-specific references)
  - ✅ .specify/templates/tasks-template.md (no constitution-specific references)
  - ✅ .specify/templates/checklist-template.md (no constitution-specific references)
  - n/a .specify/templates/commands/*.md (directory does not exist in this spec-kit version)
- Follow-up TODOs: none
-->

# Job Application Tracker Constitution

A personal hobby tool to track job applications, statuses, and follow-ups.

## Core Principles

### I. Simplicity & YAGNI

Every feature starts with the simplest design that solves the problem. Speculative
abstractions, unused configuration options, or infrastructure built for hypothetical
future requirements are NOT permitted. Three similar lines of code are preferred over
a premature abstraction. Any added complexity (a new dependency, service, or
architectural layer) MUST be justified by a concrete, current need documented in the
feature's plan — not a possible future one.

**Rationale**: This is a solo-maintained personal project. Complexity that isn't
earning its keep today is pure maintenance debt tomorrow.

### II. Test-First Development (NON-NEGOTIABLE)

Tests MUST be written before implementation code, MUST fail initially, and
implementation MUST be written only to make them pass (Red-Green-Refactor). No
feature is considered complete without an automated test exercising its behavior.
Bug fixes MUST include a failing regression test written before the fix.

**Rationale**: Test-first is the cheapest way to keep a personal project reliable
without a team to catch regressions through review.

## Technology Constraints

This project does not mandate a specific technology stack. Each feature's
implementation plan selects the simplest tool or library that solves the problem,
consistent with the Simplicity & YAGNI principle above, and records that choice in
the feature's `plan.md` rather than in this document.

## Development Workflow

As a solo-maintained personal project, formal multi-reviewer approval is not
required. Every feature MUST still:

1. Have a written spec (`spec.md`) before implementation begins.
2. Have failing tests written before implementation, per Test-First Development.
3. Pass its full test suite before being marked complete.

The `/speckit-tasks` output MUST order test-writing tasks before their corresponding
implementation tasks, reflecting principle II above.

## Governance

This constitution supersedes any conflicting ad-hoc practice. Amendments require:

1. Editing this file with a clear rationale for the change.
2. A version bump per the policy below.
3. Propagating any resulting changes to `.specify/templates/*.md`.

Versioning policy (semantic versioning):
- **MAJOR**: Backward-incompatible governance/principle removals or redefinitions.
- **MINOR**: A new principle or section added, or materially expanded guidance.
- **PATCH**: Clarifications, wording, or typo fixes with no semantic change.

Every `/speckit-plan` run MUST include a Constitution Check confirming the plan does
not violate these principles. Unresolved violations MUST be documented and justified
in the plan's Complexity Tracking section, or the plan MUST be simplified.

**Version**: 1.0.0 | **Ratified**: 2026-07-04 | **Last Amended**: 2026-07-04

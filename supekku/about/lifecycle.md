---
verified_at:
  date: '2026-03-05'
  sha: '01753be0aa705c00f094a63af39e54d3df0d62bd'
---

# Requirement Lifecycle & Traceability (Code-Truth)

This document describes the current implemented lifecycle behavior.

## Canonical Requirement Statuses

Requirement lifecycle statuses are:

- `pending`
- `in-progress`
- `active`
- `retired`

Source of truth: `supekku/scripts/lib/requirements/lifecycle.py`.

Coverage (verification) statuses are:
- `planned`
- `in-progress`
- `verified`
- `failed`
- `blocked`

Source of truth: `supekku/scripts/lib/blocks/verification.py`.

Change artifact statuses (delta / revision / audit) are:
- `draft`
- `pending`
- `in-progress`
- `completed`
- `deferred`

Source of truth: `supekku/scripts/lib/changes/lifecycle.py`.

## Status Updates: What Is Automatic vs Manual

Status can change from multiple paths.

### 1) Coverage aggregation during sync (automatic)

When requirements are synchronized, coverage blocks from specs/deltas/plans/audits
are aggregated and mapped to requirement status.

Current precedence:

- any `failed` or `blocked` -> `in-progress`
- all `verified` -> `active`
- any `in-progress` or mixed statuses -> `in-progress`
- all `planned` -> `pending`

Coverage drift across sources emits a warning (not an error).

Source of truth: `supekku/scripts/lib/requirements/registry.py`
(`_apply_coverage_blocks`, `_compute_status_from_coverage`, `_check_coverage_drift`).

### 2) Revision lifecycle ingestion during sync (automatic, tolerant)

Revision lifecycle payloads can set requirement `status` during sync.
Current ingestion is tolerant and may accept non-canonical strings from payloads.

Source of truth: `supekku/scripts/lib/requirements/registry.py`
(`_apply_revision_requirement`, `_create_placeholder_record`).

### 3) Manual status edits (supported)

Manual edits to `.spec-driver/registry/requirements.yaml` are still possible but
discouraged; treat the registry as derived and reconcile via specs/coverage or
revisions instead.
There is no first-class CLI command for direct requirement status mutation.

Library API exists: `RequirementsRegistry.set_status(...)`.

## Traceability Fields

Traceability arrays are synchronized from relations/evidence sources:

- `implemented_by`:
  - delta `applies_to.requirements`
  - delta `relations` entries with `type: implements`
  - structured `supekku:delta.relationships@v1` `requirements.implements`
- `verified_by`:
  - audit `relations` entries with `type: verifies`
- `coverage_evidence`:
  - `artefact` IDs from `supekku:verification.coverage@v1` entries across
    specs, deltas, plans, and audits

Source of truth: `supekku/scripts/lib/requirements/registry.py`.

## Requirement Sources (Spec Bundles)

Requirements are canonical when present in SPEC/PROD markdown files.

Some specs also include `requirements/*.md` files in their bundle. Current
behavior:
- These files are not consumed by sync or lifecycle logic.
- Requirement identity still must appear in the spec markdown to be tracked.

## Operational Workflow (Current)

These labels are descriptive; tooling does not enforce the workflow shape.

### Prospective (delta-driven)

1. Create delta: `uv run spec-driver create delta "Title" ...`
2. Optional: create phases explicitly via `uv run spec-driver create phase --plan IP-XXX`
3. Implement and update parent spec coverage blocks
4. Complete delta: `uv run spec-driver complete delta DE-XXX`
5. Sync/validate as needed:
   - `uv run spec-driver sync`
   - `uv run spec-driver validate --sync`

Notes:

- `create delta` scaffolds delta + DR + IP + notes, but does **not** auto-create
  `phase-01.md`.
- `complete delta` enforces coverage verification by default unless bypassed.
- `complete delta` updates requirement lifecycle in revision sources by default
  and can create a completion revision for untracked requirements.

Source of truth:
`supekku/scripts/lib/changes/creation.py`,
`supekku/scripts/complete_delta.py`,
`supekku/scripts/lib/changes/coverage_check.py`.

### Retrospective (audit/discovery)

1. Capture audit evidence and verification relationships
2. Run sync to refresh traceability/lifecycle from current artifacts
3. Reconcile any mixed or drifting coverage statuses

Notes:
- Retrospective flow is typically higher maturity: audits surface reality first,
  then revisions are applied to reconcile specs with codebase truth.

## Coverage Gate Reminder

For delta close-out, `complete delta` requires each delta requirement to have
`status: verified` in parent spec coverage blocks (`supekku:verification.coverage@v1`),
unless bypassed with `--force` or `SPEC_DRIVER_ENFORCE_COVERAGE=false`.

See: `specify/decisions/ADR-004-canonical_workflow_loop.md` and
`supekku/scripts/lib/changes/coverage_check.py`.

## Metadata & Schema References

- `supekku:verification.coverage@v1` → `supekku/scripts/lib/blocks/verification.py`
- `supekku:delta.relationships@v1` → `supekku/scripts/lib/blocks/delta.py`
- `supekku:spec.relationships@v1` → `supekku/scripts/lib/blocks/relationships.py`
- `supekku:revision.change@v1` → `supekku/scripts/lib/blocks/revision.py`

## Non-Canonical Status Terms to Avoid

Do not use these as requirement lifecycle statuses:

- `implemented`
- `verified`
- `live`
- `in_progress`

Use canonical forms listed at the top of this document.

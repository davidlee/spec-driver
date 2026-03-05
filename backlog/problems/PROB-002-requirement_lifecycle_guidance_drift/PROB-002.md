---
id: PROB-002
name: Requirement lifecycle guidance drift
created: '2026-03-05'
updated: '2026-03-05'
status: captured
kind: problem
---

# Requirement lifecycle guidance drift

## Problem Statement
Agents and users lack a clear, discoverable, and consistent mental model for
requirement lifecycle and traceability. Current guidance conflicts across specs,
docs, memories, and implementation, leading to incorrect updates and loss of
confidence in the lifecycle contract.

## Evidence
- SPEC-122 documents `live`, while code uses `active`.
- `docs/delta-completion-workflow.md` uses `passed` and `implemented`, which are
  non-canonical.
- PROD-009 baseline statuses (`asserted`, `legacy_verified`, `deprecated`) are
  not accepted by the coverage schema.
- Requirement detail files in spec bundles are not consumed by sync, yet appear
  in some specs.

## Impact
- Agents apply incorrect status values or guidance.
- Lifecycle drift warnings are hard to interpret due to mixed terminology.
- Users receive inconsistent answers to edge cases (requirement changes, partial
  fulfillment, requirement moves, provenance).

## Proposed Solutions
- Maintain a concise code-truth lifecycle reference at `supekku/about/lifecycle.md`.
- Add a dedicated lifecycle guidance memory for agents (discoverable via
  `spec-driver list memories`).
- Patch SPEC-122 to align status terminology with code (`active`).
- Decide whether PROD-009 baseline statuses are near-term or aspirational; update
  spec language accordingly after discussion.
- Implement DE-043 coverage validation fixes to prevent silent status corruption.

## Decisions Needed
- Confirm that SPEC-122 should align to code (`active`).
- Decide whether to treat PROD-009 baseline statuses as future/aspirational or to
  adopt them via schema changes.
- Decide how to treat requirement detail files: informational only vs canonical
  with required identity records in the spec file.

## Related
- ISSUE-034 (resolve links does not support backlog items)

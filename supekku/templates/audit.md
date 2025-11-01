---
id: AUD-XXX
kind: audit
status: draft|in-review|complete
spec_refs:
  - SPEC-101
prod_refs:
  - PROD-020
code_scope:
  - internal/content/**
audit_window:
  start: 2024-06-01
  end: 2024-06-08
summary: >-
  Snapshot of how the inspected code aligns with referenced PROD/SPEC artefacts.
findings:
  - id: FIND-001
    description: Content reconciler skips schema enforcement.
    outcome: drift|aligned|risk
    linked_issue: ISSUE-018
    linked_delta: DE-021
patch_level:
  - artefact: SPEC-101
    status: divergent
    notes: Implementation missing strict mode path.
  - artefact: PROD-020
    status: aligned
next_actions:
  - type: delta
    id: DE-021
  - type: issue
    id: ISSUE-052
---

{{ audit_verification_block }}

## Observations
- …

## Evidence
- Code references, logs, test results

## Recommendations
- …

---
id: AUD-XXX
kind: audit
status: draft
mode: conformance
delta_ref: DE-XXX
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
    outcome: drift
    disposition:
      status: pending
      kind: spec_patch
      refs:
        - kind: spec
          ref: SPEC-101
      drift_refs: []
      rationale: ""
---

{{ audit_verification_block }}

## Observations
- …

## Evidence
- Code references, logs, test results

## Recommendations
- …

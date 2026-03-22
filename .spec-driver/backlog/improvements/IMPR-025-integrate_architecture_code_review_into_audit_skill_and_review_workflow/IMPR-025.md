---
id: IMPR-025
name: Integrate architecture/code review into audit skill and review workflow
created: "2026-03-22"
updated: "2026-03-22"
status: idea
kind: improvement
relations:
  - type: follows_from
    target: DE-109
    note: "DE-109 establishes the review state machine, disposition model, and structured findings data"
  - type: relates_to
    target: DE-079
    note: "audit disposition model — the other half of the review↔audit traceability chain"
---

# Integrate architecture/code review into audit skill and review workflow

## Problem

Architecture and code review currently operate as informal, skill-driven processes. The audit skill has a mature reconciliation workflow with structured findings, dispositions, and validator enforcement (DE-079). DE-109 introduces a parallel structured review lifecycle with its own disposition model. These two systems should converge:

- Audit should consume review dispositions as inputs (deferred findings become audit targets)
- Architecture/code review findings should flow into the same structured data model
- The audit skill should be able to verify that review dispositions were honoured

## Desired Outcome

- Audit reconciliation can reference and verify review finding dispositions
- `fix` dispositions with `resolved_at` are verifiable by audit (sha is ancestor of HEAD, fix persists)
- `defer` dispositions with `backlog_ref` are tracked through audit (was the backlog item addressed?)
- `waive` dispositions are audit scrutiny points (was the waiver justified?)
- The audit-change skill integrates review findings as a first-class input alongside conformance findings

## Context

- DE-109 DR-109 §3.8 (review → audit traceability) explicitly defers audit-side consumption
- The audit disposition model (`core/frontmatter_metadata/audit.py`) and review disposition model (`review_state_machine.py`) share structural patterns but solve different domain problems
- Consolidation of the two disposition models may be warranted at this point (3rd instance threshold)

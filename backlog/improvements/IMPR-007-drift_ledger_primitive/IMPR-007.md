---
id: IMPR-007
name: Drift Ledger primitive
created: '2026-03-05'
updated: '2026-03-05'
status: idea
kind: improvement
---

# Drift Ledger primitive

## Summary
Introduce a Drift Ledger (DL) primitive to track divergence between normative
truth (specs/ADRs/policies), observed truth (code/contracts/runtime), and
ambiguous or missing intent. The ledger is the adjudication queue and
resolution record, distinct from audits, revisions, and deltas.

## Why this matters
Current workflows have to improvise reconciliation registers. A first-class DL
would unify contradiction discovery, design adjudication, and resolution
tracking across projects and maturity levels.

## Scope (initial)
- Support contradictions between documents
- Support canon vs implementation drift
- Track ambiguous intent and open questions
- Capture adjudication + resolution links

## Out of Scope (initial)
- Automated adjudication
- Mandatory enforcement in runtime gates

## Proposed next step
Draft a DL schema and format and test it on DE-047 (spec corpus reconciliation).
See `drift-ledger-schema-draft.md` in this folder.

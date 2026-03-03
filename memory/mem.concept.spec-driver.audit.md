---
id: mem.concept.spec-driver.audit
name: Audits
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- audit
- verification
summary: Audits (AUD-*) compare implementation against specs. They reconcile realised
  behavior against intent and feed explicit spec reconciliation before closure.
priority:
  severity: medium
  weight: 6
provenance:
  sources:
  - kind: doc
    ref: supekku/about/glossary.md
  - kind: doc
    note: Audit / Patch-Level Review section
    ref: supekku/about/processes.md
  - kind: doc
    note: Retrospective (Audit-driven) workflow
    ref: supekku/about/lifecycle.md
---

# Audits

## Role in the Loop

The audit is the **verify** step of the [[mem.pattern.spec-driver.core-loop]].
In high-rigor flow, audits/contracts establish observed truth, then specs are
patched to match that observed truth before final closure.

## Two Modes

**Conformance audit** (typical in town-planner):
- Validates that implementation matches spec intent
- Produces `verifies` [[mem.concept.spec-driver.relations|relations]]
- Projects evidence back into [[mem.concept.spec-driver.verification|coverage]]
- Drives any required post-audit spec reconciliation

**Discovery/backfill audit** (typical in settler):
- Applied to existing code that predates spec-driver
- Discovers what the code actually does
- Feeds spec/requirement creation or updates
- May generate follow-up [[mem.concept.spec-driver.delta|deltas]]

## Where They Live

`change/audits/AUD-XXX/AUD-XXX.md`

Template: `.spec-driver/templates/audit-template.md`

## Posture Variance

- **Pioneer**: audits are rare — feedback is informal
- **Settler**: both discovery and conformance audits are valid
- **Town Planner**: conformance audits are the default; evidence is mandatory

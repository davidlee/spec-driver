---
id: mem.fact.project.de-011-enum-sources
name: DE-011 enum sources hardcoded
kind: memory
status: active
memory_type: fact
updated: '2026-03-05'
verified: '2026-03-05'
tags:
- internal
- de-011
- enums
- cli
summary: DE-011 will hardcode enum sources for spec.kind and requirement.kind (no
  lifecycle constants available).
scope:
  paths:
  - change/deltas/DE-011-cli-enhanced-filtering-and-self-documentation/phases/phase-02.md
provenance:
  sources:
  - kind: doc
    note: Phase 2 sheet open question + enum list
    ref: change/deltas/DE-011-cli-enhanced-filtering-and-self-documentation/phases/phase-02.md
  - kind: conversation
    note: User decision on 2026-03-05
    ref: session
---

# DE-011 enum sources hardcoded

## Decision
For DE-011 enum introspection (schema show enums.*), `spec.kind` and
`requirement.kind` will be hardcoded:
- `spec.kind`: `[
  "prod",
  "tech",
]`
- `requirement.kind`: `[
  "FR",
  "NF",
]`

Rationale: there are no lifecycle constants for these values today.

## Context
This resolves the Phase 2 open question in the DE-011 phase sheet.

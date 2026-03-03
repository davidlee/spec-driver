---
id: mem.concept.spec-driver.revision
name: Spec Revisions
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- revision
- seed
summary: Spec Revisions (RE-*) document intent to change specs before code moves.
  They preserve documentation lineage and track requirement movements.
priority:
  severity: medium
  weight: 6
provenance:
  sources:
  - kind: doc
    ref: supekku/about/glossary.md
  - kind: doc
    note: Spec Revision Workflow section
    ref: supekku/about/processes.md
---

# Spec Revisions

## Role in the Loop

Revisions are the **intent** step — they capture the decision to change
[[mem.concept.spec-driver.spec|specs]] before any code moves. In the
[[mem.concept.spec-driver.philosophy|idealised form]], this is how truth
evolves: deliberately, with a documented trail.

## What They Capture

- Which specs are changing and why
- Requirement movements (e.g., FR-003 moves from SPEC-A to SPEC-B)
- Source and destination specs
- Rationale for the change

## Command

```bash
uv run spec-driver create revision "Summary of spec changes"
```

Creates `change/revisions/RE-XXX-slug/RE-XXX.md`.

## Posture Variance

- **Pioneer/Settler**: revisions are optional — specs may be updated directly
  as part of delta work
- **Town Planner**: revisions precede [[mem.concept.spec-driver.delta|deltas]]
  — the canonical flow is `revision → spec updates → delta(s) → implementation`

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
summary: Spec Revisions (RE-*) document requirement/spec change intent and lineage.
  In canonical delta-first flow they typically follow
  audit findings; revision-first is a town-planner concession path.
priority:
  severity: medium
  weight: 6
scope:
  commands:
  - uv run spec-driver create revision
  paths:
  - supekku/scripts/lib/requirements/registry.py
provenance:
  sources:
  - kind: code
    note: Completion path can auto-create revision updates for requirements
    ref: supekku/scripts/complete_delta.py
  - kind: code
    note: Completion updates revision sources for requirement lifecycle changes
    ref: supekku/scripts/lib/requirements/registry.py
  - kind: doc
    note: Canonical vs concession-path framing
    ref: change/deltas/DE-038-canonical_workflow_alignment/DR-038.md
---

# Spec Revisions

## Role in the Loop

Revisions capture requirement/spec change intent with lineage.

- In the canonical delta-first model, revisions most often appear after
  implementation/audit when patching specs to observed truth.
- In town-planner mode, revision-first remains a valid higher-ceremony
  concession path.

## What They Capture

- Which specs are changing and why
- New/changed requirements (often before implementation exists)
- Requirement movements (e.g., FR-003 moves from SPEC-A to SPEC-B)
- Source and destination specs
- Rationale for the change

## Command

```bash
uv run spec-driver create revision "Summary of spec changes"
```

Creates `change/revisions/RE-XXX-slug/RE-XXX.md`.

## Posture Variance

- **Pioneer/Settler**: revisions are optional and often post-audit/post-implementation
  reconciliation artifacts, not required entry points.
- **Settler completion nuance**: if requirements are not tracked in existing
  revision sources, delta completion can create completion revision updates as
  part of requirement lifecycle persistence.
- **Town Planner**: revision-first is a valid high-rigor path; then
  `revision → delta/DR/IP/phases → implementation → audit/contracts → spec reconciliation → closure`

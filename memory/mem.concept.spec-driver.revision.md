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
summary: Spec Revisions (RE-*) document intent before delivery, often introducing
  new/changed requirements. They preserve lineage and feed downstream delta execution.
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

Revisions are the **intent** step. They capture requirement/spec change intent
before delivery artifacts are executed.

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

- **Pioneer/Settler**: revisions are optional — specs may be updated directly
  as part of delta work
- **Town Planner**: revision-first is the default high-rigor path; then
  `revision → delta/DR/IP/phases → implementation → audit/contracts → spec reconciliation → closure`

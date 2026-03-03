---
id: mem.concept.spec-driver.design-revision
name: Design Revisions
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- design-revision
summary: 'Design Revisions (DR-*) translate delta intent into concrete code-level
  design: current vs target behaviour, hotspots, and test impacts.'
priority:
  severity: medium
  weight: 5
provenance:
  sources:
  - kind: doc
    ref: supekku/about/glossary.md
  - kind: doc
    note: Design Revision section
    ref: supekku/about/processes.md
---

# Design Revisions

## Role in the Loop

The DR is the **design** step of the [[mem.pattern.spec-driver.core-loop]].
It translates a [[mem.concept.spec-driver.delta|delta's]] intent into a
concrete technical design.

## What a DR Captures

- **Current behaviour** — how the system works today
- **Target behaviour** — what it should look like after the delta
- **Code hotspots** — files and modules that will change
- **Interface changes** — API surface modifications
- **Test impacts** — what tests need to change or be added

## Where It Lives

`change/deltas/DE-XXX-slug/DR-XXX.md` — always alongside its parent delta.

## Posture Variance

- **Pioneer**: no DRs — design happens informally
- **Settler**: optional — used when the change is non-trivial
- **Town Planner**: expected for any change with architectural impact

---
id: mem.concept.spec-driver.design-revision
name: Design Revisions
kind: memory
status: active
memory_type: concept
updated: "2026-03-06"
verified: "2026-03-06"
confidence: high
tags: [spec-driver, design-revision]
summary: "Design Revisions (DR-*) translate delta intent into concrete code-level design: current vs target behaviour, hotspots, and test impacts."
priority:
  severity: medium
  weight: 5
provenance:
  sources:
    - kind: adr
      ref: ADR-004
    - kind: code
      ref: supekku/scripts/lib/changes/creation.py
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

Posture affects how explicitly DRs are expected and where they live, but the
main question is execution scope.

- Significant, risky, or architecturally meaningful changes should usually have
  an explicit DR or equivalent design artefact.
- When deltas are active, the DR normally lives inside the delta bundle.
- When deltas are not active, equivalent design notes may live in cards,
  artefact docs, or other local planning records.

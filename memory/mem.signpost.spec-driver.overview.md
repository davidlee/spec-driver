---
id: mem.signpost.spec-driver.overview
name: Spec-Driver Overview
kind: memory
status: active
memory_type: signpost
updated: '2026-03-05'
verified: '2026-03-05'
tags:
- spec-driver
- overview
- workflow
summary: 'Concise overview of spec-driver: core loop, ceremony modes, key artifacts,
  and common commands.'
scope:
  commands:
  - uv run spec-driver create delta
  - uv run spec-driver complete delta
  - uv run spec-driver sync
  - uv run spec-driver validate
provenance:
  sources:
  - kind: memory
    ref: mem.pattern.spec-driver.core-loop
  - kind: memory
    ref: mem.signpost.spec-driver.ceremony
  - kind: memory
    ref: mem.signpost.spec-driver.file-map
---

# Spec-Driver Overview

Spec-driver is the framework this repo uses to keep specs, change intent,
implementation, and verification in sync. It emphasizes traceability: every
requirement should be linked to the change that implements it and the evidence
that verifies it.

## Core Loop (Canonical Narrative)
`capture → delta (scope/design/plan) → implement → audit/contracts → revision/spec reconciliation → close`

See [[mem.pattern.spec-driver.core-loop]] for the full loop and concession paths.

## Ceremony (Read Your Mode)
Ceremony determines *how strictly* the loop is followed. Always check the
project’s ceremony mode and read the matching guidance:
- [[mem.signpost.spec-driver.ceremony]]

## Key Artifacts
- Specs: [[mem.concept.spec-driver.spec]]
- Deltas: [[mem.concept.spec-driver.delta]]
- Design Revisions: [[mem.concept.spec-driver.design-revision]]
- Implementation Plans: [[mem.concept.spec-driver.plan]]
- Audits: [[mem.concept.spec-driver.audit]]
- Revisions: [[mem.concept.spec-driver.revision]]

## Requirement Lifecycle
- Code-truth reference: `supekku/about/lifecycle.md`
- Agent guidance: [[mem.concept.spec-driver.requirement-lifecycle]]

## Common Commands
- `uv run spec-driver create delta "Title" --spec SPEC-XXX --requirement SPEC-XXX.FR-YYY`
- `uv run spec-driver create phase --plan IP-XXX`
- `uv run spec-driver complete delta DE-XXX`
- `uv run spec-driver sync`
- `uv run spec-driver validate`
- `uv run spec-driver list requirements --spec SPEC-XXX`
- `uv run spec-driver show delta DE-XXX`

## File Map
For where things live, see [[mem.signpost.spec-driver.file-map]].

## Philosophy
For the underlying posture and convergence model, see
[[mem.concept.spec-driver.philosophy]].

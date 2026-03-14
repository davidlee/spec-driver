---
id: mem.concept.spec-driver.delta
name: Deltas
kind: memory
status: active
memory_type: concept
updated: "2026-03-06"
verified: "2026-03-06"
confidence: high
tags: [spec-driver, delta]
summary: "Deltas (DE-*) are declarative change bundles — the mechanism for applying revision intent to code. They scope work, link requirements, and carry verification strategy toward audit/reconciliation."
priority:
  severity: high
  weight: 8
provenance:
  sources:
    - kind: adr
      ref: ADR-004
    - kind: code
      ref: supekku/cli/create.py
    - kind: code
      ref: supekku/scripts/lib/changes/creation.py
    - kind: code
      ref: supekku/scripts/complete_delta.py
---

# Deltas

## Role in the Loop

The delta is the **scope** step of the [[mem.pattern.spec-driver.core-loop]].
It declares the intended change and carries execution toward observed truth,
revision, and reconciled [[mem.concept.spec-driver.spec|specs]].

## What a Delta Contains

- **Scope**: what will change and why
- **Inputs**: referenced specs, requirements, backlog items
- **Relationships**: `implements` links to requirements
  (see [[mem.concept.spec-driver.relations]])
- **Risks**: known risks and mitigations
- **Verification strategy**: how changes will be verified

## The Delta Bundle

A delta directory contains its companions:

```
change/deltas/DE-XXX-slug/
  DE-XXX.md          # The delta itself
  DR-XXX.md          # Design revision (optional)
  IP-XXX.md          # Implementation plan (optional)
  phases/            # Phase sheets (optional)
  notes.md           # Implementation notes
```

## Command

```bash
uv run spec-driver create delta "Title" --spec SPEC-### --requirement SPEC-###.FR-###
```

## Status Lifecycle

```
draft → in_progress → completed
```

## Completion

When all work is done, follow [[mem.pattern.spec-driver.delta-completion]].
Use `uv run spec-driver complete delta DE-XXX` to close out.

## Posture Variance

- **Pioneer**: deltas are not used — cards serve this role
- **Settler**: deltas are the standard work unit
- **Town Planner**: deltas follow [[mem.concept.spec-driver.revision|revisions]]

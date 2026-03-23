---
id: mem.fact.architecture.core-misplaced-modules
name: "core/ contains misplaced integration hubs"
kind: memory
status: active
memory_type: fact
created: '2026-03-24'
updated: '2026-03-24'
verified: '2026-03-24'
confidence: high
tags:
- architecture
- core
- migration
- coupling
summary: >-
  artifact_view.py (11 registry imports) and enums.py (5 cross-area imports)
  are integration hubs misplaced in core/. Must reclassify before
  spec_driver.core can migrate honestly.
scope:
  globs:
  - supekku/scripts/lib/core/**
  - spec_driver/core/**
  paths:
  - supekku/scripts/lib/core/artifact_view.py
  - supekku/scripts/lib/core/enums.py
provenance:
  sources:
  - DE-125
---

# core/ contains misplaced integration hubs

## Problem

`supekku/scripts/lib/core/` has 38 cross-area imports (excluding self-references).
Two modules account for most of it:

- **`artifact_view.py`** (456 lines) — imports 11 registries: Spec, Change,
  Decision, Requirement, Memory, Card, Policy, Standard, Backlog, Drift. This is
  a lookup/resolution service, not core infrastructure.
- **`enums.py`** (111 lines) — imports status constants from `backlog`, `blocks`,
  `changes`, `decisions`, `drift`. This aggregates domain lifecycle enums into a
  single namespace.

## Why it matters

`spec_driver.core` is the bottom of the outer layer contract. If the actual
`core/` modules drag in half the codebase via these two files, nothing above
them can migrate cleanly. The contract becomes aspirational rather than
enforceable.

## Likely reclassification

- `artifact_view.py` → `orchestration` or a dedicated resolution service
  (it composes registries to resolve artifact IDs).
- `enums.py` → either split into per-domain lifecycle modules, or move to a
  shared `domain.lifecycle` module that re-exports from domain sub-areas.

## Remaining core modules

Most other `core/` modules (`paths.py`, `repo.py`, `spec_utils.py`,
`frontmatter_schema.py`, `artifact_ids.py`, `config.py`) are genuinely
foundational and can migrate to `spec_driver.core` once the two integration
hubs are reclassified.

## Related

- [[DE-125]] — discovered during post-pilot architectural reflection
- [[mem.pattern.architecture.domain-migration]] — migration pattern

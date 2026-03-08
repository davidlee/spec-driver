---
id: mem.fact.spec-driver.status-enums
name: Canonical Status Enums
kind: memory
status: active
memory_type: fact
updated: '2026-03-09'
verified: '2026-03-09'
confidence: high
tags:
- spec-driver
- lifecycle
- status
- sharp-edge
summary: Authoritative status enums for all entity types, including governance artifacts
  and unified backlog lifecycle (DE-075).
priority:
  severity: high
  weight: 10
scope:
  commands:
  - uv run spec-driver complete delta
  - complete delta
  - uv run spec-driver sync
  - uv run spec-driver validate
  - uv run spec-driver edit --status
  paths:
  - supekku/scripts/lib/requirements/lifecycle.py
  - supekku/scripts/lib/requirements/registry.py
  - supekku/scripts/lib/changes/lifecycle.py
  - supekku/scripts/lib/blocks/verification.py
  - supekku/scripts/lib/specs/lifecycle.py
  - supekku/scripts/lib/decisions/lifecycle.py
  - supekku/scripts/lib/policies/lifecycle.py
  - supekku/scripts/lib/standards/lifecycle.py
  - supekku/scripts/lib/memory/lifecycle.py
  - supekku/scripts/lib/backlog/models.py
  - supekku/scripts/lib/core/enums.py
  - supekku/scripts/lib/formatters/theme.py
provenance:
  sources:
  - kind: code
    note: Requirement lifecycle constants
    ref: supekku/scripts/lib/requirements/lifecycle.py
  - kind: code
    note: Change artifact status constants
    ref: supekku/scripts/lib/changes/lifecycle.py
  - kind: code
    note: Verification coverage status constants
    ref: supekku/scripts/lib/blocks/verification.py
  - kind: code
    note: Governance artifact lifecycle constants (DE-075 phase 1)
    ref: supekku/scripts/lib/specs/lifecycle.py
  - kind: code
    note: Unified backlog lifecycle (DEC-075-05)
    ref: supekku/scripts/lib/backlog/models.py
  - kind: code
    note: Central enum registry
    ref: supekku/scripts/lib/core/enums.py
---

# Canonical Status Enums

## Requirement Lifecycle

- `pending`, `in-progress`, `active`, `retired`

Legacy alias: `complete` normalized to `completed`

## Change Artifact Lifecycle

- `draft`, `pending`, `in-progress`, `completed`, `deferred`

## Verification Coverage

- `planned`, `in-progress`, `verified`, `failed`, `blocked`

## Spec Lifecycle (DE-075)

- `stub`, `draft`, `active`, `deprecated`, `archived`

## ADR Lifecycle (DE-075)

- `draft`, `proposed`, `accepted`, `rejected`, `deprecated`, `superseded`, `revision-required`

## Policy Lifecycle (DE-075)

- `draft`, `required`, `deprecated`

Note: policies use enforcement-level terms, not `active`.

## Standard Lifecycle (DE-075)

- `draft`, `required`, `default`, `deprecated`

## Memory Lifecycle (DE-075)

- `draft`, `active`, `review`, `superseded`, `archived`

## Backlog Lifecycle — Unified (DEC-075-05)

Base: `open`, `triaged`, `in-progress`, `resolved`
Risk extensions: `accepted`, `expired`

All backlog kinds share the base set. Risks add `accepted`/`expired`.
Theme keys use `backlog.status.*` (unified), not per-kind prefixes.

ENUM_REGISTRY paths: `backlog.status` (base 4), `risk.status` (base + extensions).

## Important Caveats

- Revision lifecycle ingestion in requirements registry tolerates non-canonical
  status strings (no hard-validate on read). Follow-up: shared validator.
- Frontmatter schemas still use `".+"` patterns — enum enforcement is a separate delta.

## Non-Canonical Terms to Avoid

- `implemented` → use `resolved` (backlog) or `active` (requirement)
- `live` → use `active` (spec)
- `idea` → use `open` (backlog)
- `captured` → use `open` (backlog)
- `suspected` → use `open` (risk)
- `obsolete` / `deprecated` (memory) → use `archived` or `superseded`
- `active` (policy) → use `required`

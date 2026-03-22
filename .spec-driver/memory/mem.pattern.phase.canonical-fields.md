---
id: mem.pattern.phase.canonical-fields
name: Phase canonical frontmatter fields
kind: memory
status: active
memory_type: pattern
created: "2026-03-22"
updated: "2026-03-22"
verified: "2026-03-22"
confidence: high
tags: [phase, frontmatter, dr-106, canonical]
summary: >-
  Canonical phase fields: plan, delta, objective, entrance_criteria,
  exit_criteria. Validated by PhaseSheet Pydantic model.
scope:
  globs:
    - supekku/scripts/lib/changes/phase_model.py
    - supekku/scripts/lib/changes/creation.py
    - supekku/scripts/lib/changes/artifacts.py
    - "**/.spec-driver/deltas/*/phases/*.md"
provenance:
  sources:
    - kind: delta
      note: DR-106 DEC-005 — canonical field set
      ref: DE-106
    - kind: code
      note: PhaseSheet Pydantic model
      ref: supekku/scripts/lib/changes/phase_model.py
---

# Phase canonical frontmatter fields

## Summary

New-format phases carry five canonical fields in frontmatter (beyond base
artifact fields like `id`, `status`, `kind`):

| Field               | Type      | Required | Written by                       |
| ------------------- | --------- | -------- | -------------------------------- |
| `plan`              | string    | yes      | `create_phase()`                 |
| `delta`             | string    | yes      | `create_phase()`                 |
| `objective`         | string    | no       | `create_phase()` from plan entry |
| `entrance_criteria` | list[str] | no       | `create_phase()` from plan entry |
| `exit_criteria`     | list[str] | no       | `create_phase()` from plan entry |

## Validation

- `PhaseSheet` Pydantic model in `phase_model.py` (`extra="ignore"`)
- `has_canonical_fields()` returns True when `plan` and `delta` are present
- Validator uses this to distinguish new-format from legacy phases

## Excluded fields (intentional)

`verification`, `tasks`, `risks` are **not** in frontmatter. They live in
markdown prose sections. See DE-106 notes.md "Accepted Structured Data Losses".

## See also

- [[mem.pattern.phase.contract-vs-progress]] contract vs progress split
- [[mem.pattern.phase.frontmatter-block-precedence]] reading order
- [[PROD-006]] FR-001 updated to reference canonical frontmatter

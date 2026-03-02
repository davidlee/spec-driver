---
id: MEM-002
name: Formatter Separation of Concerns
kind: memory
status: active
memory_type: pattern
created: '2026-03-02'
updated: '2026-03-02'
confidence: high
verified: '2026-03-02'
review_by: '2026-06-02'
tags:
- architecture
- formatters
summary: >-
  Formatters are pure functions in formatters/. No business logic. No side
  effects. Same input always produces same output.
owners:
- platform-team
audience:
- human
- agent
visibility:
- pre
- on_demand
scope:
  globs:
  - "supekku/scripts/lib/formatters/**"
  languages:
  - py
priority:
  severity: medium
  weight: 5
provenance:
  sources:
  - kind: doc
    ref: CLAUDE.md
    note: Pure Functions Over Stateful Objects section
requires_reading:
- CLAUDE.md
relations:
- type: relates_to
  target: MEM-001
  annotation: Complementary pattern
---

# Formatter Separation of Concerns

## Summary

All display formatting lives in `supekku/scripts/lib/formatters/`. Formatters
are pure functions: `(input) -> str`, no side effects, no business logic.

## Pattern

```python
# formatters/{artifact}_formatters.py
def format_{artifact}_list_item(artifact: Artifact) -> str:
  """Pure function: same input -> same output, no side effects."""
  return f"{artifact.id}\t{artifact.status}\t{artifact.name}"
```

## Rules

1. Create `formatters/{artifact}_formatters.py` for each artifact family
2. Export in `formatters/__init__.py`
3. Write comprehensive tests in `formatters/{artifact}_formatters_test.py`
4. CLI/scripts call formatters — never format inline

## Rationale

- Testable without CLI harness or I/O
- Reusable across commands and scripts
- Changes to display are isolated from domain logic

## Context

Established in CLAUDE.md Architecture Guide. Decision formatters were the
reference pattern; memory formatters followed the same structure.

---
id: MEM-001
name: Skinny CLI Pattern
kind: memory
status: active
memory_type: pattern
created: '2026-03-02'
updated: '2026-03-02'
confidence: high
tags:
- architecture
- cli
summary: >-
  CLI files orchestrate only — no business logic or formatting inline.
  Delegate to domain packages + formatters.
owners:
- platform-team
audience:
- human
- agent
visibility:
- pre
scope:
  globs:
  - "supekku/cli/**"
  paths:
  - supekku/cli/memory.py
  - supekku/cli/list.py
  commands:
  - "create memory"
  - "list memories"
  - "show memory"
  languages:
  - py
priority:
  severity: medium
  weight: 5
provenance:
  sources:
  - kind: doc
    ref: CLAUDE.md
    note: Skinny CLI section in Architecture Guide
requires_reading:
- CLAUDE.md
relations:
- type: relates_to
  target: MEM-002
  annotation: Complementary pattern
---

# Skinny CLI Pattern

## Summary

CLI command files are thin orchestration layers. They parse arguments, load from
registries, apply filters, delegate formatting, and output results. No business
logic or display formatting lives in CLI files.

## Pattern

```python
@app.command("list")
def list_items(filters):
  registry = ItemRegistry(root)          # Load
  items = registry.filter(filters)       # Filter (domain)
  for item in items:
    output = format_item(item, options)  # Format (formatters/)
    print(output)                        # Output
```

## Rationale

- Keeps CLI files under 150 lines
- Business logic is testable without CLI harness
- Formatters are reusable across CLI and scripts
- Changes to display don't require touching domain code

## Context

Established in CLAUDE.md Architecture Guide. All artifact families (specs,
decisions, changes, memories) follow this pattern.

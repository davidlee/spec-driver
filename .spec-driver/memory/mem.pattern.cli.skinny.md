---
id: mem.pattern.cli.skinny
name: Skinny CLI Pattern
kind: memory
status: active
memory_type: pattern
updated: '2026-03-10'
confidence: high
tags:
- architecture
- cli
summary: CLI files orchestrate only — no business logic or formatting inline. Delegate
  to domain packages + formatters.
priority:
  severity: medium
  weight: 5
scope:
  commands:
  - create memory
  - list memories
  - show memory
  globs:
  - supekku/cli/**
  languages:
  - py
  paths:
  - supekku/cli/memory.py
  - supekku/cli/list.py
provenance:
  sources:
  - kind: doc
    note: Skinny CLI section in Architecture Guide
    ref: CLAUDE.md
requires_reading:
- CLAUDE.md
verified: '2026-03-10'
verified_sha: 81d9554da083f6a891dd37fabb59bb1c87186f6b
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

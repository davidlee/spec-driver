---
id: mem.pattern.spec-driver.frontmatter-compaction
name: Frontmatter compaction via FieldMetadata persistence annotations
kind: memory
status: active
memory_type: pattern
created: '2026-03-03'
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- frontmatter
- compaction
- metadata
summary: Compact frontmatter serialization is driven by FieldMetadata persistence/default
  annotations with write-side-only semantics and read-side tolerance.
priority:
  severity: high
  weight: 8
scope:
  commands:
  - uv run spec-driver compact delta
  - uv run spec-driver compact delta --dry-run
  globs:
  - supekku/scripts/lib/core/frontmatter_metadata/**
  - supekku/cli/compact*
  - supekku/scripts/lib/blocks/metadata/schema.py
provenance:
  sources:
  - kind: doc
    note: DE-036 design decisions and contract
    ref: change/deltas/DE-036-frontmatter_metadata_compaction_and_canonicalization_controls/DR-036.md
  - kind: doc
    note: Compaction semantics matrix (§10.5)
    ref: change/deltas/DE-036-frontmatter_metadata_compaction_and_canonicalization_controls/phases/phase-01.md
  - kind: code
    note: Compaction pure function entry point
    ref: supekku/scripts/lib/core/frontmatter_metadata/compaction.py
  - kind: code
    note: FieldMetadata persistence/default annotations
    ref: supekku/scripts/lib/blocks/metadata/schema.py
  - kind: code
    note: Compact CLI command surface
    ref: supekku/cli/compact.py
---

# Frontmatter compaction via FieldMetadata persistence annotations

## Summary

`compact_frontmatter(data, metadata, mode)` applies field-level persistence
rules from `FieldMetadata.persistence` and `FieldMetadata.default_value` to
serialize lean frontmatter without changing parse semantics.

## Context

- `canonical`: always keep
- `derived`: omit in compact mode
- `optional`: omit when absent, `None`, or default-equivalent
- `default-omit`: omit when value equals `default_value`

Unknown fields are passed through unchanged for forward compatibility.

## Where

- Core logic: `supekku/scripts/lib/core/frontmatter_metadata/compaction.py`
- Field schema: `supekku/scripts/lib/blocks/metadata/schema.py`
- CLI entry point: `supekku/cli/compact.py` (`uv run spec-driver compact delta`)

## Contract

- Write-side only: compaction changes serialization, not runtime meaning.
- Read-side tolerant: compacted and full frontmatter parse equivalently.
- Pilot family is deltas for now.

## Design Constraints

- DEC-036-001: apply compaction on sync/automation commands, not manual authoring.
- DEC-036-003: delta frontmatter is the pilot non-memory family.

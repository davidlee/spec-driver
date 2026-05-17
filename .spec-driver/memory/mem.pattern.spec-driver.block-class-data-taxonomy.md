---
id: mem.pattern.spec-driver.block-class-data-taxonomy
name: 'Block-class data taxonomy: cached .data vs .parse()'
kind: memory
status: active
memory_type: pattern
created: '2026-05-17'
updated: '2026-05-17'
verified: '2026-05-17'
confidence: high
tags:
- spec-driver
- blocks
- metadata
- wrappers
summary: 'DeltaRelationshipsBlock and RelationshipsBlock cache parsed YAML on .data;
  RevisionChangeBlock parses on demand via .parse(). Validation wrappers must match:
  by-block for cached classes, by-data for parse-on-demand classes. Default new blocks
  to cached-.data shape.'
---

# Block-class data taxonomy: cached .data vs .parse()

## Summary

Two shapes coexist in `supekku/scripts/lib/blocks/`:

- **Cached-`.data` shape** (`DeltaRelationshipsBlock`, `RelationshipsBlock`):
  the parsed YAML mapping is cached as `block.data`. Validation wrappers take
  the *block* and reach into `block.data` internally.
- **Parse-on-demand shape** (`RevisionChangeBlock`): YAML is re-parsed each
  call via `block.parse()`. Validation wrappers must take the parsed *data*
  directly, because re-parsing inside the wrapper would double the cost and
  defeat the caller's parse cycle.

This shape difference is invisible until you write a wrapper and the type
signatures don't line up.

## Context

Surfaced during DE-118 IP-118-P03 C5 (RevisionChangeBlock migration). Three
sibling relationship-block wrappers (`validate_delta_relationships`,
`validate_spec_relationships`, `validate_spec_capabilities`) all take blocks;
`validate_revision_change` takes data. The asymmetry is not a code smell —
it is a faithful reflection of the underlying block-class shape.

## How to apply

- Before authoring a new validation wrapper, inspect the block class: does it
  expose `.data` (cached) or only `.parse()` (on-demand)?
- For *new* block classes, default to the cached-`.data` shape unless there
  is a concrete reason to defer parsing (e.g. mutation-cycle semantics).
- When surveying or documenting wrapper APIs, surface the data-vs-block
  divergence explicitly so readers do not assume uniformity.

## Related

- DE-118 (Block schema unification) — DR-118 §4 "ID-kwarg wrappers"
- `supekku/scripts/lib/blocks/delta.py`, `relationships.py`, `revision.py`

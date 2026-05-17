---
id: mem.pattern.spec-driver.metadata-test-placement
name: Metadata test file placement (mirror rule)
kind: memory
status: active
memory_type: pattern
created: '2026-05-17'
updated: '2026-05-17'
verified: '2026-05-17'
confidence: high
tags:
- spec-driver
- metadata
- testing
- convention
summary: When a module has a sibling <source>_metadata.py declaration file, its tests
  go in <source>_metadata_test.py; otherwise fall back to <source>_test.py (or the
  existing test colocation if migration would be churn).
---

# Metadata test file placement (mirror rule)

## Summary

In `supekku/scripts/lib/blocks/`, block schemas split into two paired modules:
a `<source>.py` parser/loader/marker module and a `<source>_metadata.py`
declarative `BlockMetadata` declaration. The mirror rule for tests:

- Primary: tests for `<source>_metadata.py` go in `<source>_metadata_test.py`
  (colocated with the metadata declaration, not the parser).
- Fallback: if no `<source>_metadata.py` exists (e.g. `sessions_schema.py`
  declares its metadata inline), tests stay with the source file
  (`sessions_schema_test.py`) or extend the existing co-located test class
  (e.g. `workflow_metadata_test.py::WorkflowSessionsTest`) when migrating
  established tests would add churn without clear benefit.

## Context

- Surfaced during DE-118 IP-118-P03 (2026-05-11) while deciding where the
  per-block curated corpora should live as hand-rolled validators retired.
- Reaffirmed in DE-118 IP-118-P04 4.2 (2026-05-16): `sessions_schema.py` has
  no `_metadata.py` sibling, so the 6 synthetic-corpus tests for the
  `additional_properties=_SESSION_ENTRY` swap extended the existing
  `WorkflowSessionsTest` class rather than spawning a new file.

## How to apply

- When adding tests for a block: check for `<source>_metadata.py` first; if
  present, place tests in `<source>_metadata_test.py`.
- When migrating a hand-rolled validator to `MetadataValidator`, the parallel
  test corpus belongs in the metadata-test file, not the loader-test file.
- Don't move pre-existing tests just to satisfy the primary form — the
  fallback exists to prevent churn.

## Related

- DE-118 (Block schema unification)
- DR-118 §5 (verification methodology)

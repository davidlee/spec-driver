---
id: mem.fact.validation.cross-project-refs-skipped
name: validator skips cross-project namespace:ID references
kind: memory
status: active
memory_type: fact
updated: '2026-03-23'
verified: '2026-03-23'
confidence: high
tags:
- validation
- references
summary: References with a colon (namespace:ID pattern, e.g. autobahn:DE-001) are treated as cross-project and excluded from unresolved reference validation
scope:
  paths:
    - supekku/scripts/lib/validation/validator.py
  globs:
    - supekku/scripts/lib/relations/**
provenance:
  sources: ["validator.py:_validate_unresolved_references"]
---

# validator skips cross-project namespace:ID references

- `_validate_unresolved_references` in `validator.py` skips any edge whose `target` contains a colon (`:`).
- Convention: cross-project references use `namespace:ID` format (e.g. `autobahn:DE-001`, `autobahn:DE-004`).
- These appear in `relations` blocks as `target: "autobahn:DE-001"`.
- The reference graph (`build_reference_graph`) indexes only local artifacts, so cross-project targets are inherently unresolvable.
- Without this skip, every cross-project relation would produce a false-positive unresolved reference warning.

---
id: mem.concept.spec.assembly-only-taxonomy
name: Assembly-only tech specs direction
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
review_by: '2026-06-03'
confidence: high
tags: [specs, taxonomy, de-035, contracts]
summary: Deprecate unit tech specs as first-class; treat assembly specs + contracts as primary model with legacy unit compatibility.
priority:
  severity: high
  weight: 8
scope:
  commands: [sync, list specs, validate]
  globs:
  - supekku/scripts/sync_specs.py
  - supekku/scripts/lib/specs/**
  - supekku/scripts/lib/validation/validator.py
  languages: [md, py]
  paths:
  - change/revisions/RE-018-assembly_only_tech_specs_deprecate_unit_spec_generation/RE-018.md
  - change/deltas/DE-035-assembly_only_tech_specs_and_unit_spec_deprecation/DE-035.md
  - change/deltas/DE-035-assembly_only_tech_specs_and_unit_spec_deprecation/DR-035.md
  - change/deltas/DE-035-assembly_only_tech_specs_and_unit_spec_deprecation/IP-035.md
  - specify/product/PROD-015/PROD-015.md
  - specify/product/PROD-012/PROD-012.md
provenance:
  sources:
  - kind: doc
    note: Revision direction for assembly-only model
    ref: change/revisions/RE-018-assembly_only_tech_specs_deprecate_unit_spec_generation/RE-018.md
  - kind: doc
    note: Implementation scope and compatibility constraints
    ref: change/deltas/DE-035-assembly_only_tech_specs_and_unit_spec_deprecation/DE-035.md
  - kind: doc
    note: Accepted baseline that now requires supersede/amend follow-up
    ref: specify/decisions/ADR-003-separate_unit_and_assembly_specs.md
---

# Assembly-only tech specs direction

## Summary

Default model direction: treat assembly specs as the only first-class authored
tech spec type, and treat contracts as the canonical observed-code artifact.
Do not generate new unit specs as a standard workflow.

## Context

This does not require an immediate hard migration. Existing `category: unit`
records remain supported during transition and should be handled in
compatibility mode (warn/deprecate, not fail).

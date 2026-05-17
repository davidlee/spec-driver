---
id: mem.pattern.spec-driver.metadata-validator-strictness
name: MetadataValidator strict_unknown_keys + additional_properties semantics
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
- validation
summary: MetadataValidator(metadata, strict_unknown_keys=False) is the unified block
  validator. strict_unknown_keys is a per-instance opt-in; flip True at retirement
  call sites to preserve hand-rolled rejection. FieldMetadata.additional_properties
  handles dynamic-key objects (the _entry_shape replacement). Both compose with the
  recursive object-validation algorithm at every depth.
---

# MetadataValidator strict_unknown_keys + additional_properties semantics

## Summary

`MetadataValidator(metadata, strict_unknown_keys: bool = False)` is the
single block-validation surface after DE-118. Two mechanisms control
unknown-key handling:

- `strict_unknown_keys` (constructor arg, default `False`). When `True`, any
  key in the data that is not declared in `properties` and not matched by
  `additional_properties` is rejected. Propagates recursively through nested
  objects via the instance attribute.
- `FieldMetadata.additional_properties: FieldMetadata | None` (per-field).
  When set, declares the shape that *unknown* keys must conform to (the
  dynamic-key idiom — e.g. `workflow.sessions` per-entry shape).

Composition algorithm in `_validate_field` for object types: validate
declared `properties` first; then for each undeclared key in the data, apply
`additional_properties` if set, else reject if `strict_unknown_keys`, else
accept silently.

## Context

DE-118 (DEC-001, DEC-004) introduced both mechanisms to retire 7 hand-rolled
block validators in favour of a single `MetadataValidator`. The 7 retirement
call sites pass `strict_unknown_keys=True` to preserve hand-rolled rejection
semantics. Workflow.* blocks remain `False` (DEC-006 deferral → IMPR-035 →
DE-137).

DR-118 DEC-004 documents an explicit non-regression: when `properties=None,
additional_properties=<shape>, data={}`, the validator passes silently.
A `min_entries` invariant for dynamic-key maps is deferred (OQ-NON-EMPTY).

## How to apply

- New block validators: instantiate `MetadataValidator(METADATA,
  strict_unknown_keys=True)` at the loader call site unless there is a
  documented reason to accept extras.
- New dynamic-key fields: declare `additional_properties=<FieldMetadata>`,
  not a sentinel key like `_entry_shape`.
- Strictness *governance* (CLI flag, alias autocorrect, per-kind
  workflow.toml) is DE-137's territory, not DE-118's. Do not introduce
  cross-cutting strict-flag surface here.

## Sharp edges

- ID-equality checks (e.g. `block.data["delta"] == delta_id`) cannot be
  expressed in metadata. Use a thin wrapper helper alongside the metadata
  declaration (see `mem.pattern.spec-driver.block-class-data-taxonomy`).
- Pre-existing consumer data that violates a newly-strict field will fail
  at first contact. Document via IMPR-035 (or successor) when widening.

## Related

- DE-118 (Block schema unification)
- DR-118 §7 DEC-001, DEC-004, DEC-006
- IMPR-035 (workflow.* strict-flip deferral)
- `mem.pattern.spec-driver.block-class-data-taxonomy`

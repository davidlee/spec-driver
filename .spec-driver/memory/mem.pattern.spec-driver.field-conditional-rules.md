---
id: mem.pattern.spec-driver.field-conditional-rules
slug: field-conditional-rules
name: Object-scoped FieldMetadata.conditional_rules (per-item if/then)
kind: memory
status: active
memory_type: pattern
created: '2026-05-29'
updated: '2026-05-29'
verified: '2026-05-29'
confidence: medium
tags:
- metadata
- validator
- spec-driver
summary: FieldMetadata.conditional_rules apply per object (incl. array items) via
  _apply_conditional_rules in _validate_object; mirror of BlockMetadata top-level
  rules
---

# Object-scoped FieldMetadata.conditional_rules (per-item if/then)

## Summary

`FieldMetadata.conditional_rules: list[ConditionalRule]` (additive, default `[]`)
lets any **object** — top-level block, nested object, or array item — carry its
own if/then requirement rules. The single helper
`MetadataValidator._apply_conditional_rules(obj, rules, path_prefix)` runs them:

- `validate()` calls it for `BlockMetadata.conditional_rules` with `path_prefix=""`
  (so a top-level error reads `origin`, **no leading dot**).
- `_validate_object()` calls it for `field_meta.conditional_rules` with
  `path_prefix=field_path` (so an array-item error reads `requirements[2].origin`).

Because array items dispatch `_validate_field → _validate_object`, declaring rules
on the array **item** `FieldMetadata` makes them fire per element, with the
condition field resolved as a direct key of the item
(`_get_nested_value(item, "action")`).

## Context

- Files: `blocks/metadata/schema.py` (`FieldMetadata`, `ConditionalRule`),
  `blocks/metadata/validator.py` (`_apply_conditional_rules`, `_validate_object`).
- First real consumer: `REVISION_CHANGE_METADATA.requirements[]` item
  (`blocks/revision_metadata.py`) — move→{origin,destination},
  introduce/modify→{destination} (DE-142 P01).
- **Gotcha**: JSON-Schema generation (`metadata_to_json_schema`) only projects
  `BlockMetadata.conditional_rules` into `allOf`. Per-item
  `FieldMetadata.conditional_rules` are **not** emitted to JSON Schema — runtime
  validation is correct but generated schema lacks the if/then. Fix if a
  JSON-schema consumer needs parity.
- Path-join rule is load-bearing: `f"{prefix}.{field}" if prefix else field`.
  Regression-guarded by VT-142-ENGINE-003 (empty rules → no behaviour change).
- Related: [[mem.pattern.spec-driver.metadata-validator-strictness]],
  [[mem.pattern.validation.per-kind-block-wiring]].

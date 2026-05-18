---
id: mem.pattern.spec-driver.metadata-validator-strictness
name: MetadataValidator strict-mode + alias contract
kind: memory
status: active
memory_type: pattern
created: '2026-05-17'
updated: '2026-05-18'
verified: '2026-05-18'
confidence: high
tags:
- spec-driver
- blocks
- metadata
- validation
summary: After DE-137 IP-137-P01, MetadataValidator(metadata) is constructed once and `.validate(data, *, strict, accept_tolerated)` controls strictness per call. Field-NAME and field-VALUE aliases are declared on BlockMetadata.field_aliases / FieldMetadata.field_aliases / .aliases / .tolerated_aliases. The validator is report-only — ValidationError.fix_hint/fix_kind drive `--fix` rewrites.
---

# MetadataValidator strict-mode + alias contract

## Summary

`MetadataValidator(metadata)` is the single block-validation surface
across the codebase. The constructor takes only the metadata; strictness
is controlled per call:

```python
errors = MetadataValidator(meta).validate(
  data,
  strict=True,          # default False (loader-tolerant)
  accept_tolerated=True,  # default True; False == --no-tolerated-aliases
)
```

Three orthogonal alias mechanisms compose with the recursive validation
algorithm:

- `BlockMetadata.field_aliases` / `FieldMetadata.field_aliases`:
  field-NAME aliases applied at any object-schema layer (top-level or
  nested object). Under strict, emits a warning carrying
  `fix_kind="rename_key"` + `fix_hint=<canonical_key>`. Collision
  (both alias and canonical present) is `error` severity, no merge.
- `FieldMetadata.aliases`: field-VALUE aliases applied after per-field
  dispatch. Under strict, emits a warning with
  `fix_kind="rewrite_value"` + `fix_hint=<canonical_value>`.
- `FieldMetadata.tolerated_aliases`: time-bounded migration-window
  aliases (`ToleratedAlias(canonical, sunset_after, rationale)`).
  Accepted silently when `accept_tolerated=True` (default) and tolerant;
  warning under strict; rejected with `error` severity under
  `accept_tolerated=False`. `--fix` never rewrites tolerated aliases —
  migrations handle them.

`FieldMetadata.additional_properties` still applies for dynamic-key
maps (e.g. `workflow.sessions`), unchanged from DE-118.

## Strict-vs-tolerant unknown-key rule

`strict=True` rejects keys not in `metadata.fields` (top-level) or in
`field_meta.properties` (nested), unless declared as field_aliases or
covered by `additional_properties`. `strict=False` silently accepts
unknown keys.

## Did-you-mean

Under strict on an unrecognised enum value, the validator populates
`ValidationError.fix_hint` with the closest match via
`spec_driver.core.string_utils.closest_match` (`difflib.get_close_matches`
at cutoff 0.6). Typos surface; semantic alternatives (`live`, `wip`,
…) miss the cutoff — those belong in `FieldMetadata.aliases`.

## Report-only validator

The validator never mutates the supplied data. Loaders that need
canonical values at read time call
`supekku.scripts.lib.blocks.metadata.aliases.normalize_field(kind,
field, value)`. `validate workspace --fix` consumes
`ValidationError.fix_hint` + `.fix_kind` to apply the canonical
replacement to the source file.

## How to apply

- New per-kind metadata: populate `enum_values` literally on each
  `status` `FieldMetadata`, never derive from a lifecycle constant
  (the lifecycle constant is now the derived re-export — see
  `mem.fact.spec-driver.status-enums`). Add `aliases` only when the
  corpus carries legacy values that must canonicalise on read.
- Loader sites: instantiate `MetadataValidator(METADATA)` once at
  module scope; call `.validate(data, strict=False)` at every load.
  CLI surfaces (e.g. `validate workspace`) pass `strict=True`.
- Migrating an existing dynamic-key field: declare
  `additional_properties=<FieldMetadata>`, not a sentinel key.

## Historical retirement (DE-118 → DE-137)

DE-118 introduced the `strict_unknown_keys` constructor kwarg and
unified 7 hand-rolled validators. DE-137 IP-137-P01 retired the kwarg
(DEC-137-14) and moved strictness to a per-call argument plus the
alias mechanism. The 5 production retirement sites (snapshot_compare,
spec/delta/revision relationship wrappers) now pass `strict=True`
explicitly to `.validate(...)`.

## Sharp edges

- ID-equality checks (e.g. `block.data["delta"] == delta_id`) cannot be
  expressed in metadata. Use a thin wrapper helper alongside the
  metadata declaration (see
  `mem.pattern.spec-driver.block-class-data-taxonomy`).
- Pre-existing consumer data that violates a newly-strict field will
  fail at first contact under `strict=True`. The loader-default
  (`strict=False`) absorbs the divergence silently; the CLI surfaces it.
- `_strict` / `_accept_tolerated` instance attributes are reset at the
  top of every `validate()` call. Concurrent calls on the same
  validator from multiple threads would race — keep one validator per
  thread or reconstruct per call.

## Related

- DE-118 (Block schema unification — origin)
- DR-137 §5.2 (DEC-137-14, DEC-137-23, F-30, F-54)
- `mem.fact.spec-driver.status-enums`
- `mem.pattern.spec-driver.block-class-data-taxonomy`

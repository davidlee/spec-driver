# supekku.scripts.lib.blocks.metadata.validator

Metadata-driven validation engine.

This module provides runtime validation of data against block metadata schemas.
The validator produces path-aware error messages for developer-friendly output.

DE-137 IP-137-P01 (DEC-137-14, DEC-137-23, F-30, F-54):

- `MetadataValidator.__init__` no longer accepts ``strict_unknown_keys``;
  strictness is controlled per call via
  ``validate(*, strict=..., accept_tolerated=...)``.
- Two-pass dispatch: ``BlockMetadata.field_aliases`` /
  ``FieldMetadata.field_aliases`` rename keys before per-field dispatch
  (Pass 1); ``FieldMetadata.aliases`` normalise values after dispatch (Pass 2).
- ``ValidationError`` carries ``severity`` plus ``fix_hint`` / ``fix_kind`` so
  ``validate --fix`` can dispatch on the canonical correction.

The validator is report-only — it never mutates the supplied data. Loaders
that want canonical values at read time should call
``blocks.metadata.aliases.normalize_field``; ``validate workspace --fix``
applies the canonical replacements to the source files using
``ValidationError.fix_hint`` / ``.fix_kind``.

## Constants

- `__all__`

## Classes

### MetadataValidator

Validates data against block metadata definition.

Usage::

  metadata = BlockMetadata(...)
  validator = MetadataValidator(metadata)
  errors = validator.validate(data, strict=True)

``strict`` (default ``False``) flips unknown-key rejection, enum-violation
reporting, and emits warnings for alias rewrites. ``accept_tolerated``
(default ``True``) accepts ``FieldMetadata.tolerated_aliases`` entries
silently; setting it to ``False`` makes those entries reject under
``strict``.

``_strict`` and ``_accept_tolerated`` are reset at the top of every
``validate`` call. They live as instance attributes so internal
helpers can consult them without threading kwargs through every
recursion frame.

#### Methods

- `validate(self, data) -> list[ValidationError]`: Validate data against metadata.
- `__init__(self, metadata)`
- `_apply_field_aliases(self, data, field_aliases, parent_path) -> list[ValidationError]`: Report alias keys; emit collision errors and strict warnings (F-54).

Pure: never mutates *data*. The diagnostic carries ``fix_hint`` /
``fix_kind`` so ``--fix`` can apply the canonical replacement to the
source file. Per-field dispatch in ``_validate_fields`` honours alias
keys explicitly so report-only behaviour does not skip validation of
the value living under the alias.
- `_get_nested_value(self, data, path) -> Any`: Get value from nested path (e.g., 'metadata.revision').
- `_handle_alias_rewrite(self, value, canonical, field_path) -> list[ValidationError]`
- `_handle_tolerated(self, value, entry, field_path) -> list[ValidationError]`
- `_has_nested_value(self, data, path) -> bool`: Check if nested path exists.
- `_reverse_aliases(self, fields, data, parent_path) -> dict[Tuple[str, str]]`: Resolve canonical-key -> alias-key when only the alias is present.

Looks at every layer-relevant ``field_aliases`` declaration. The
caller (``_validate_fields``) supplies *fields* and the surrounding
block-or-property ``field_aliases`` map via the parent's
``BlockMetadata`` / ``FieldMetadata`` (already applied as warnings in
``_apply_field_aliases``). This helper just makes the per-field
dispatch in ``_validate_fields`` find the value under the alias key.
- `_validate_array(self, value, field_meta, field_path) -> list[ValidationError]` - -- array ----------------------------------------------------------------
- `_validate_bool(self, value, field_meta, field_path) -> list[ValidationError]`
- `_validate_conditional_rules(self, data) -> list[ValidationError]`: Validate conditional rules (if/then logic). - -- conditional rules ---------------------------------------------------
- `_validate_const(self, value, field_meta, field_path) -> list[ValidationError]` - -- scalar handlers ------------------------------------------------------
- `_validate_enum(self, value, field_meta, field_path) -> list[ValidationError]`: Validate an enum value, honouring aliases, tolerated_aliases, did-you-mean. - -- enum -----------------------------------------------------------------
- `_validate_field(self, value, field_meta, field_path) -> list[ValidationError]`: Dispatch validation for *value* against *field_meta*.
- `_validate_fields(self, data, fields, parent_path) -> list[ValidationError]`: Validate fields recursively.

Honours ``BlockMetadata.field_aliases`` / ``FieldMetadata.field_aliases``
by looking up the value under the alias key when the canonical key is
absent — keeps per-field dispatch correct without mutating *data*.
- `_validate_int(self, value, field_meta, field_path) -> list[ValidationError]`
- `_validate_object(self, value, field_meta, field_path) -> list[ValidationError]`: Validate an object-typed field (declared + additional/strict pass). - -- object ---------------------------------------------------------------
- `_validate_string(self, value, field_meta, field_path) -> list[ValidationError]`

### ValidationError

Validation error with path context.

Attributes:
  path: Dot-notation path (e.g., "specs.primary[0]")
  message: Human-readable error message
  expected: Expected value/type (optional)
  actual: Actual value found (optional)
  severity: "error" (default; affects exit code) or "warning" (advisory).
  fix_hint: Canonical replacement value when ``--fix`` can resolve.
  fix_kind: Discriminator telling ``--fix`` whether to rename the key
    (``rename_key``) or rewrite the value (``rewrite_value``).

#### Methods

- `__str__(self) -> str`: Format error for display.

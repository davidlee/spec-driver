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

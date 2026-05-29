"""Metadata-driven validation engine.

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
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from spec_driver.core.string_utils import closest_match

from .schema import BlockMetadata, ConditionalRule, FieldMetadata

SEVERITY_ERROR: Literal["error"] = "error"
SEVERITY_WARNING: Literal["warning"] = "warning"

FIX_KIND_RENAME_KEY: Literal["rename_key"] = "rename_key"
FIX_KIND_REWRITE_VALUE: Literal["rewrite_value"] = "rewrite_value"


@dataclass
class ValidationError:
  """Validation error with path context.

  Attributes:
    path: Dot-notation path (e.g., "specs.primary[0]")
    message: Human-readable error message
    expected: Expected value/type (optional)
    actual: Actual value found (optional)
    severity: "error" (default; affects exit code) or "warning" (advisory).
    fix_hint: Canonical replacement value when ``--fix`` can resolve.
    fix_kind: Discriminator telling ``--fix`` whether to rename the key
      (``rename_key``) or rewrite the value (``rewrite_value``).
  """

  path: str
  message: str
  expected: str | None = None
  actual: str | None = None
  severity: Literal["error", "warning"] = SEVERITY_ERROR
  fix_hint: str | None = None
  fix_kind: Literal["rename_key", "rewrite_value"] | None = None

  def __str__(self) -> str:
    """Format error for display."""
    parts = [f"{self.path}: {self.message}"]
    if self.expected:
      parts.append(f"expected {self.expected}")
    if self.actual:
      parts.append(f"got {self.actual}")
    return " - ".join(parts)


class MetadataValidator:
  """Validates data against block metadata definition.

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
  """

  def __init__(self, metadata: BlockMetadata):
    self.metadata = metadata
    self._strict: bool = False
    self._accept_tolerated: bool = True

  def validate(
    self,
    data: dict[str, Any],
    *,
    strict: bool = False,
    accept_tolerated: bool = True,
  ) -> list[ValidationError]:
    """Validate data against metadata."""
    self._strict = strict
    self._accept_tolerated = accept_tolerated

    errors: list[ValidationError] = []

    if not isinstance(data, dict):
      errors.append(
        ValidationError(
          path="<root>",
          message="block must be a mapping",
          expected="object",
          actual=type(data).__name__,
          severity=SEVERITY_ERROR,
        )
      )
      return errors

    errors.extend(self._apply_field_aliases(data, self.metadata.field_aliases, ""))
    errors.extend(self._validate_fields(data, self.metadata.fields, ""))

    if strict:
      known = set(self.metadata.fields) | set(self.metadata.field_aliases or {})
      for key in data:
        if key not in known:
          errors.append(
            ValidationError(path=key, message="unknown key", severity=SEVERITY_ERROR)
          )

    if self.metadata.conditional_rules:
      errors.extend(
        self._apply_conditional_rules(data, self.metadata.conditional_rules, "")
      )

    return errors

  def _apply_field_aliases(
    self,
    data: dict[str, Any],
    field_aliases: Any,
    parent_path: str,
  ) -> list[ValidationError]:
    """Report alias keys; emit collision errors and strict warnings (F-54).

    Pure: never mutates *data*. The diagnostic carries ``fix_hint`` /
    ``fix_kind`` so ``--fix`` can apply the canonical replacement to the
    source file. Per-field dispatch in ``_validate_fields`` honours alias
    keys explicitly so report-only behaviour does not skip validation of
    the value living under the alias.
    """
    errors: list[ValidationError] = []
    if not field_aliases:
      return errors

    for alias_key, canonical_key in field_aliases.items():
      if alias_key not in data:
        continue
      alias_path = f"{parent_path}.{alias_key}" if parent_path else alias_key
      if canonical_key in data:
        errors.append(
          ValidationError(
            path=alias_path,
            message=(
              f"field name conflict: both {alias_key!r} (alias) and "
              f"{canonical_key!r} (canonical) are present"
            ),
            expected=canonical_key,
            actual=alias_key,
            severity=SEVERITY_ERROR,
          )
        )
        continue
      if self._strict:
        errors.append(
          ValidationError(
            path=alias_path,
            message=f"field name {alias_key!r} is an alias for {canonical_key!r}",
            expected=canonical_key,
            actual=alias_key,
            severity=SEVERITY_WARNING,
            fix_hint=canonical_key,
            fix_kind=FIX_KIND_RENAME_KEY,
          )
        )

    return errors

  def _validate_fields(
    self,
    data: dict[str, Any],
    fields: dict[str, FieldMetadata],
    parent_path: str,
  ) -> list[ValidationError]:
    """Validate fields recursively.

    Honours ``BlockMetadata.field_aliases`` / ``FieldMetadata.field_aliases``
    by looking up the value under the alias key when the canonical key is
    absent — keeps per-field dispatch correct without mutating *data*.
    """
    errors: list[ValidationError] = []
    aliases = self._reverse_aliases(fields, data, parent_path)

    for field_name, field_meta in fields.items():
      field_path = f"{parent_path}.{field_name}" if parent_path else field_name
      present_key = field_name if field_name in data else aliases.get(field_name)

      if field_meta.required and present_key is None:
        errors.append(
          ValidationError(
            path=field_path, message="is required", severity=SEVERITY_ERROR
          )
        )
        continue

      if present_key is None:
        continue

      errors.extend(self._validate_field(data[present_key], field_meta, field_path))

    return errors

  def _reverse_aliases(
    self,
    fields: dict[str, FieldMetadata],
    data: dict[str, Any],
    parent_path: str,
  ) -> dict[str, str]:
    """Resolve canonical-key -> alias-key when only the alias is present.

    Looks at every layer-relevant ``field_aliases`` declaration. The
    caller (``_validate_fields``) supplies *fields* and the surrounding
    block-or-property ``field_aliases`` map via the parent's
    ``BlockMetadata`` / ``FieldMetadata`` (already applied as warnings in
    ``_apply_field_aliases``). This helper just makes the per-field
    dispatch in ``_validate_fields`` find the value under the alias key.
    """
    del fields, parent_path
    container_aliases = self._current_field_aliases or {}
    reverse: dict[str, str] = {}
    for alias_key, canonical_key in container_aliases.items():
      if alias_key in data and canonical_key not in data:
        reverse[canonical_key] = alias_key
    return reverse

  _current_field_aliases: dict[str, str] | None = None

  def _validate_field(
    self,
    value: Any,
    field_meta: FieldMetadata,
    field_path: str,
  ) -> list[ValidationError]:
    """Dispatch validation for *value* against *field_meta*."""
    match field_meta.type:
      case "const":
        return self._validate_const(value, field_meta, field_path)
      case "string":
        return self._validate_string(value, field_meta, field_path)
      case "int":
        return self._validate_int(value, field_meta, field_path)
      case "bool":
        return self._validate_bool(value, field_meta, field_path)
      case "enum":
        return self._validate_enum(value, field_meta, field_path)
      case "object":
        return self._validate_object(value, field_meta, field_path)
      case "array":
        return self._validate_array(value, field_meta, field_path)
      case _:
        return []

  # -- scalar handlers ------------------------------------------------------

  def _validate_const(
    self, value: Any, field_meta: FieldMetadata, field_path: str
  ) -> list[ValidationError]:
    if value == field_meta.const_value:
      return []
    return [
      ValidationError(
        path=field_path,
        message="must equal constant value",
        expected=str(field_meta.const_value),
        actual=str(value),
        severity=SEVERITY_ERROR,
      )
    ]

  def _validate_string(
    self, value: Any, field_meta: FieldMetadata, field_path: str
  ) -> list[ValidationError]:
    if not isinstance(value, str):
      return [
        ValidationError(
          path=field_path,
          message="must be a string",
          expected="string",
          actual=type(value).__name__,
          severity=SEVERITY_ERROR,
        )
      ]
    if field_meta.pattern and not re.match(field_meta.pattern, value):
      return [
        ValidationError(
          path=field_path,
          message="does not match required pattern",
          expected=f"pattern: {field_meta.pattern}",
          actual=value,
          severity=SEVERITY_ERROR,
        )
      ]
    return []

  def _validate_int(
    self, value: Any, field_meta: FieldMetadata, field_path: str
  ) -> list[ValidationError]:
    del field_meta
    if isinstance(value, int) and not isinstance(value, bool):
      return []
    return [
      ValidationError(
        path=field_path,
        message="must be an integer",
        expected="int",
        actual=type(value).__name__,
        severity=SEVERITY_ERROR,
      )
    ]

  def _validate_bool(
    self, value: Any, field_meta: FieldMetadata, field_path: str
  ) -> list[ValidationError]:
    del field_meta
    if isinstance(value, bool):
      return []
    return [
      ValidationError(
        path=field_path,
        message="must be a boolean",
        expected="bool",
        actual=type(value).__name__,
        severity=SEVERITY_ERROR,
      )
    ]

  # -- enum -----------------------------------------------------------------

  def _validate_enum(
    self,
    value: Any,
    field_meta: FieldMetadata,
    field_path: str,
  ) -> list[ValidationError]:
    """Validate an enum value, honouring aliases, tolerated_aliases, did-you-mean."""
    enum_values = field_meta.enum_values or []
    aliases = field_meta.aliases or {}
    tolerated = field_meta.tolerated_aliases or {}

    if value in enum_values:
      return []
    if value in aliases:
      return self._handle_alias_rewrite(value, aliases[value], field_path)
    if value in tolerated:
      return self._handle_tolerated(value, tolerated[value], field_path)

    if not self._strict:
      return []
    hint = closest_match(str(value), enum_values) if enum_values else None
    return [
      ValidationError(
        path=field_path,
        message="must be one of allowed values",
        expected=", ".join(str(v) for v in enum_values),
        actual=str(value),
        severity=SEVERITY_ERROR,
        fix_hint=hint,
      )
    ]

  def _handle_alias_rewrite(
    self, value: Any, canonical: str, field_path: str
  ) -> list[ValidationError]:
    if not self._strict:
      return []
    return [
      ValidationError(
        path=field_path,
        message=f"value {value!r} is an alias for {canonical!r}",
        expected=canonical,
        actual=str(value),
        severity=SEVERITY_WARNING,
        fix_hint=canonical,
        fix_kind=FIX_KIND_REWRITE_VALUE,
      )
    ]

  def _handle_tolerated(
    self, value: Any, entry: Any, field_path: str
  ) -> list[ValidationError]:
    msg = (
      f"value {value!r} is a tolerated alias for "
      f"{entry.canonical!r} (sunsets at {entry.sunset_after})"
    )
    if not self._accept_tolerated:
      return [
        ValidationError(
          path=field_path,
          message=msg,
          expected=entry.canonical,
          actual=str(value),
          severity=SEVERITY_ERROR,
        )
      ]
    if self._strict:
      return [
        ValidationError(
          path=field_path,
          message=msg,
          expected=entry.canonical,
          actual=str(value),
          severity=SEVERITY_WARNING,
        )
      ]
    return []

  # -- array ----------------------------------------------------------------

  def _validate_array(
    self, value: Any, field_meta: FieldMetadata, field_path: str
  ) -> list[ValidationError]:
    if not isinstance(value, list):
      return [
        ValidationError(
          path=field_path,
          message="must be an array",
          expected="array",
          actual=type(value).__name__,
          severity=SEVERITY_ERROR,
        )
      ]

    errors: list[ValidationError] = []
    if field_meta.min_items is not None and len(value) < field_meta.min_items:
      errors.append(
        ValidationError(
          path=field_path,
          message=f"must have at least {field_meta.min_items} items",
          actual=f"{len(value)} items",
          severity=SEVERITY_ERROR,
        )
      )
    if field_meta.max_items is not None and len(value) > field_meta.max_items:
      errors.append(
        ValidationError(
          path=field_path,
          message=f"must have at most {field_meta.max_items} items",
          actual=f"{len(value)} items",
          severity=SEVERITY_ERROR,
        )
      )

    if field_meta.items:
      for idx, item in enumerate(value):
        errors.extend(
          self._validate_field(item, field_meta.items, f"{field_path}[{idx}]")
        )

    return errors

  # -- object ---------------------------------------------------------------

  def _validate_object(
    self, value: Any, field_meta: FieldMetadata, field_path: str
  ) -> list[ValidationError]:
    """Validate an object-typed field (declared + additional/strict pass)."""
    if not isinstance(value, dict):
      return [
        ValidationError(
          path=field_path,
          message="must be an object",
          expected="object",
          actual=type(value).__name__,
          severity=SEVERITY_ERROR,
        )
      ]

    errors: list[ValidationError] = []
    errors.extend(
      self._apply_field_aliases(value, field_meta.field_aliases, field_path)
    )

    declared: set[str] = set()
    if field_meta.properties:
      saved = self._current_field_aliases
      self._current_field_aliases = dict(field_meta.field_aliases or {})
      try:
        errors.extend(self._validate_fields(value, field_meta.properties, field_path))
      finally:
        self._current_field_aliases = saved
      declared = set(field_meta.properties)

    errors.extend(
      self._validate_additional_keys(value, field_meta, field_path, declared)
    )

    if field_meta.conditional_rules:
      errors.extend(
        self._apply_conditional_rules(value, field_meta.conditional_rules, field_path)
      )
    return errors

  def _validate_additional_keys(
    self,
    value: dict[str, Any],
    field_meta: FieldMetadata,
    field_path: str,
    declared: set[str],
  ) -> list[ValidationError]:
    """Validate keys not covered by declared properties (additional/strict pass).

    Keys present under declared properties (or under their alias keys) are
    already validated by ``_validate_fields``; this pass handles the rest via
    ``additional_properties`` or the strict unknown-key rejection.
    """
    declared_or_aliased = set(declared)
    for alias_key, canonical_key in (field_meta.field_aliases or {}).items():
      if canonical_key in declared:
        declared_or_aliased.add(alias_key)

    errors: list[ValidationError] = []
    for key, item in value.items():
      if key in declared_or_aliased:
        continue
      sub_path = f"{field_path}.{key}" if field_path else key
      if field_meta.additional_properties is not None:
        errors.extend(
          self._validate_field(item, field_meta.additional_properties, sub_path)
        )
      elif self._strict:
        errors.append(
          ValidationError(path=sub_path, message="unknown key", severity=SEVERITY_ERROR)
        )
    return errors

  # -- conditional rules ---------------------------------------------------

  def _apply_conditional_rules(
    self,
    obj: dict[str, Any],
    rules: list[ConditionalRule],
    path_prefix: str,
  ) -> list[ValidationError]:
    """Apply if/then rules to *obj*, prefixing error paths with *path_prefix*.

    Object-scoped: the top-level call passes ``path_prefix=""`` (so an error
    on ``origin`` reads ``origin``, no leading dot) while ``_validate_object``
    passes the array-item/nested path (so it reads ``requirements[2].origin``).
    """
    errors: list[ValidationError] = []
    for rule in rules:
      condition_value = self._get_nested_value(obj, rule.condition_field)
      if condition_value != rule.condition_value:
        continue
      for required_field in rule.requires:
        if self._has_nested_value(obj, required_field):
          continue
        expected_msg = (
          f"field present (due to: {rule.description})" if rule.description else None
        )
        condition_desc = f"{rule.condition_field}={rule.condition_value}"
        path = f"{path_prefix}.{required_field}" if path_prefix else required_field
        errors.append(
          ValidationError(
            path=path,
            message=f"is required when {condition_desc}",
            expected=expected_msg,
            severity=SEVERITY_ERROR,
          )
        )
    return errors

  def _get_nested_value(self, data: dict[str, Any], path: str) -> Any:
    """Get value from nested path (e.g., 'metadata.revision')."""
    current: Any = data
    for part in path.split("."):
      if not isinstance(current, dict) or part not in current:
        return None
      current = current[part]
    return current

  def _has_nested_value(self, data: dict[str, Any], path: str) -> bool:
    """Check if nested path exists."""
    return self._get_nested_value(data, path) is not None


__all__ = [
  "FIX_KIND_RENAME_KEY",
  "FIX_KIND_REWRITE_VALUE",
  "MetadataValidator",
  "SEVERITY_ERROR",
  "SEVERITY_WARNING",
  "ValidationError",
]

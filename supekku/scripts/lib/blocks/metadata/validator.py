"""Metadata-driven validation engine.

This module provides runtime validation of data against block metadata schemas.
The validator produces path-aware error messages for developer-friendly output.

DE-137 IP-137-P01 (DEC-137-14, DEC-137-23, F-30, F-54):

- `MetadataValidator.__init__` no longer accepts ``strict_unknown_keys``;
  strictness is controlled per call via ``validate(*, strict=..., accept_tolerated=...)``.
- Two-pass dispatch: ``BlockMetadata.field_aliases`` /
  ``FieldMetadata.field_aliases`` rename keys before per-field dispatch
  (Pass 1); ``FieldMetadata.aliases`` normalise values after dispatch (Pass 2).
- ``ValidationError`` carries ``severity`` plus ``fix_hint`` / ``fix_kind`` so
  ``validate --fix`` can dispatch on the canonical correction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from spec_driver.core.string_utils import closest_match

from .schema import BlockMetadata, FieldMetadata

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
    if errors:
      for error in errors:
        print(error)

  ``strict`` (default ``False``) flips unknown-key rejection, enum-violation
  reporting, and emits warnings for alias rewrites. ``accept_tolerated``
  (default ``True``) accepts ``FieldMetadata.tolerated_aliases`` entries
  silently; setting it to ``False`` makes those entries reject under
  ``strict``.
  """

  def __init__(self, metadata: BlockMetadata):
    self.metadata = metadata

  def validate(
    self,
    data: dict[str, Any],
    *,
    strict: bool = False,
    accept_tolerated: bool = True,
  ) -> list[ValidationError]:
    """Validate data against metadata.

    Args:
      data: Parsed YAML data to validate.
      strict: When True, unknown keys and unrecognised enum values become
        ``error``-severity diagnostics, and alias rewrites surface as
        ``warning``-severity diagnostics with ``fix_kind`` / ``fix_hint``.
      accept_tolerated: When True (default), ``tolerated_aliases`` are
        accepted silently under ``strict=False`` and surface as warnings
        under ``strict=True``. When False, tolerated aliases reject
        under strict (``--no-tolerated-aliases`` semantics).

    Returns:
      List of validation errors (empty if valid). Errors of severity
      ``warning`` do not by themselves indicate invalid data; callers
      decide whether to surface them.
    """
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

    # Pass 1: field-NAME aliasing at the top-level block.
    errors.extend(
      self._apply_field_aliases(
        data, self.metadata.field_aliases, parent_path="", strict=strict
      )
    )

    # Pass 2: per-field validation (recursive).
    errors.extend(
      self._validate_fields(
        data,
        self.metadata.fields,
        parent_path="",
        strict=strict,
        accept_tolerated=accept_tolerated,
      )
    )

    # Top-level unknown-key pass — only under strict.
    if strict:
      for key in data:
        if key not in self.metadata.fields:
          errors.append(
            ValidationError(
              path=key, message="unknown key", severity=SEVERITY_ERROR
            )
          )

    if self.metadata.conditional_rules:
      errors.extend(self._validate_conditional_rules(data))

    return errors

  def _apply_field_aliases(
    self,
    data: dict[str, Any],
    field_aliases: Any,
    parent_path: str,
    *,
    strict: bool,
  ) -> list[ValidationError]:
    """Rename alias keys in-place; report collisions and strict warnings.

    Mutates *data* by popping ``alias_key`` and writing ``canonical_key``
    when the canonical is absent. When both keys are present the alias
    stays untouched and an ``error``-severity diagnostic is appended so
    ``--fix`` declines to merge (F-54).
    """
    errors: list[ValidationError] = []
    if not field_aliases:
      return errors

    for alias_key, canonical_key in field_aliases.items():
      if alias_key not in data:
        continue
      alias_path = (
        f"{parent_path}.{alias_key}" if parent_path else alias_key
      )
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
      data[canonical_key] = data.pop(alias_key)
      if strict:
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
    *,
    strict: bool,
    accept_tolerated: bool,
  ) -> list[ValidationError]:
    """Validate fields recursively."""
    errors: list[ValidationError] = []

    for field_name, field_meta in fields.items():
      field_path = f"{parent_path}.{field_name}" if parent_path else field_name

      if field_meta.required and field_name not in data:
        errors.append(
          ValidationError(
            path=field_path, message="is required", severity=SEVERITY_ERROR
          )
        )
        continue

      if field_name not in data:
        continue  # Optional field not present

      value = data[field_name]
      errors.extend(
        self._validate_field(
          value,
          field_meta,
          field_path,
          owner=data,
          owner_key=field_name,
          strict=strict,
          accept_tolerated=accept_tolerated,
        )
      )

    return errors

  def _validate_field(
    self,
    value: Any,
    field_meta: FieldMetadata,
    field_path: str,
    *,
    owner: dict[str, Any] | None = None,
    owner_key: str | None = None,
    strict: bool,
    accept_tolerated: bool,
  ) -> list[ValidationError]:
    """Validate a single field value."""
    errors: list[ValidationError] = []

    if field_meta.type == "const":
      if value != field_meta.const_value:
        errors.append(
          ValidationError(
            path=field_path,
            message="must equal constant value",
            expected=str(field_meta.const_value),
            actual=str(value),
            severity=SEVERITY_ERROR,
          )
        )

    elif field_meta.type == "enum":
      errors.extend(
        self._validate_enum(
          value,
          field_meta,
          field_path,
          owner=owner,
          owner_key=owner_key,
          strict=strict,
          accept_tolerated=accept_tolerated,
        )
      )

    elif field_meta.type == "string":
      if not isinstance(value, str):
        errors.append(
          ValidationError(
            path=field_path,
            message="must be a string",
            expected="string",
            actual=type(value).__name__,
            severity=SEVERITY_ERROR,
          )
        )
      elif field_meta.pattern and not re.match(field_meta.pattern, value):
        errors.append(
          ValidationError(
            path=field_path,
            message="does not match required pattern",
            expected=f"pattern: {field_meta.pattern}",
            actual=value,
            severity=SEVERITY_ERROR,
          )
        )

    elif field_meta.type == "int":
      if not isinstance(value, int) or isinstance(value, bool):
        errors.append(
          ValidationError(
            path=field_path,
            message="must be an integer",
            expected="int",
            actual=type(value).__name__,
            severity=SEVERITY_ERROR,
          )
        )

    elif field_meta.type == "bool":
      if not isinstance(value, bool):
        errors.append(
          ValidationError(
            path=field_path,
            message="must be a boolean",
            expected="bool",
            actual=type(value).__name__,
            severity=SEVERITY_ERROR,
          )
        )

    elif field_meta.type == "object":
      errors.extend(
        self._validate_object(
          value,
          field_meta,
          field_path,
          strict=strict,
          accept_tolerated=accept_tolerated,
        )
      )

    elif field_meta.type == "array":
      errors.extend(
        self._validate_array(
          value,
          field_meta,
          field_path,
          strict=strict,
          accept_tolerated=accept_tolerated,
        )
      )

    return errors

  def _validate_enum(
    self,
    value: Any,
    field_meta: FieldMetadata,
    field_path: str,
    *,
    owner: dict[str, Any] | None,
    owner_key: str | None,
    strict: bool,
    accept_tolerated: bool,
  ) -> list[ValidationError]:
    """Validate an enum value, honouring aliases, tolerated_aliases, did-you-mean."""
    enum_values = field_meta.enum_values or []
    aliases = field_meta.aliases or {}
    tolerated = field_meta.tolerated_aliases or {}
    errors: list[ValidationError] = []

    if value in enum_values:
      return errors

    if value in aliases:
      canonical = aliases[value]
      if owner is not None and owner_key is not None:
        owner[owner_key] = canonical
      if strict:
        errors.append(
          ValidationError(
            path=field_path,
            message=f"value {value!r} is an alias for {canonical!r}",
            expected=canonical,
            actual=str(value),
            severity=SEVERITY_WARNING,
            fix_hint=canonical,
            fix_kind=FIX_KIND_REWRITE_VALUE,
          )
        )
      return errors

    if value in tolerated:
      entry = tolerated[value]
      if not accept_tolerated:
        errors.append(
          ValidationError(
            path=field_path,
            message=(
              f"value {value!r} is a tolerated alias for "
              f"{entry.canonical!r} (sunsets at {entry.sunset_after})"
            ),
            expected=entry.canonical,
            actual=str(value),
            severity=SEVERITY_ERROR,
          )
        )
      elif strict:
        errors.append(
          ValidationError(
            path=field_path,
            message=(
              f"value {value!r} is a tolerated alias for "
              f"{entry.canonical!r} (sunsets at {entry.sunset_after})"
            ),
            expected=entry.canonical,
            actual=str(value),
            severity=SEVERITY_WARNING,
          )
        )
      return errors

    # Unknown value.
    if strict:
      hint = closest_match(str(value), enum_values) if enum_values else None
      errors.append(
        ValidationError(
          path=field_path,
          message="must be one of allowed values",
          expected=", ".join(str(v) for v in enum_values),
          actual=str(value),
          severity=SEVERITY_ERROR,
          fix_hint=hint,
        )
      )
    return errors

  def _validate_array(
    self,
    value: Any,
    field_meta: FieldMetadata,
    field_path: str,
    *,
    strict: bool,
    accept_tolerated: bool,
  ) -> list[ValidationError]:
    """Validate an array-typed field."""
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
        item_path = f"{field_path}[{idx}]"
        errors.extend(
          self._validate_field(
            item,
            field_meta.items,
            item_path,
            owner=value,
            owner_key=idx,
            strict=strict,
            accept_tolerated=accept_tolerated,
          )
        )

    return errors

  def _validate_object(
    self,
    value: Any,
    field_meta: FieldMetadata,
    field_path: str,
    *,
    strict: bool,
    accept_tolerated: bool,
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

    # Pass 1 at this layer: field-NAME aliasing on nested object schemas
    # (mirrors the top-level pass for BlockMetadata.field_aliases).
    errors.extend(
      self._apply_field_aliases(
        value, field_meta.field_aliases, parent_path=field_path, strict=strict
      )
    )

    declared: set[str] = set()
    if field_meta.properties:
      errors.extend(
        self._validate_fields(
          value,
          field_meta.properties,
          field_path,
          strict=strict,
          accept_tolerated=accept_tolerated,
        )
      )
      declared = set(field_meta.properties)

    for key in value:
      if key in declared:
        continue
      sub_path = f"{field_path}.{key}" if field_path else key
      if field_meta.additional_properties is not None:
        errors.extend(
          self._validate_field(
            value[key],
            field_meta.additional_properties,
            sub_path,
            owner=value,
            owner_key=key,
            strict=strict,
            accept_tolerated=accept_tolerated,
          )
        )
      elif strict:
        errors.append(
          ValidationError(path=sub_path, message="unknown key", severity=SEVERITY_ERROR)
        )
    return errors

  def _validate_conditional_rules(self, data: dict[str, Any]) -> list[ValidationError]:
    """Validate conditional rules (if/then logic)."""
    errors: list[ValidationError] = []

    for rule in self.metadata.conditional_rules:
      condition_value = self._get_nested_value(data, rule.condition_field)
      if condition_value == rule.condition_value:
        for required_field in rule.requires:
          if not self._has_nested_value(data, required_field):
            expected_msg = None
            if rule.description:
              expected_msg = f"field present (due to: {rule.description})"
            condition_desc = f"{rule.condition_field}={rule.condition_value}"
            errors.append(
              ValidationError(
                path=required_field,
                message=f"is required when {condition_desc}",
                expected=expected_msg,
                severity=SEVERITY_ERROR,
              )
            )

    return errors

  def _get_nested_value(self, data: dict[str, Any], path: str) -> Any:
    """Get value from nested path (e.g., 'metadata.revision')."""
    parts = path.split(".")
    current = data
    for part in parts:
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

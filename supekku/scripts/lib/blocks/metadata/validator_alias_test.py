"""Validator tests for the two-axis alias mechanism (DE-137 IP-137-P01).

Covers:
- VT-CC-008: field-NAME alias canonicalisation + ``fix_kind='rename_key'``.
- VT-CC-009: tolerated_aliases accepted by default; rejected under
  ``accept_tolerated=False``; warning under strict.
- VT-CC-030: field-VALUE alias canonicalisation +
  ``fix_kind='rewrite_value'``.
- VT-CC-034: field-NAME alias collision -> error severity, no merge.
"""

from __future__ import annotations

import pytest

from .schema import BlockMetadata, FieldMetadata, ToleratedAlias
from .validator import (
  FIX_KIND_RENAME_KEY,
  FIX_KIND_REWRITE_VALUE,
  SEVERITY_ERROR,
  SEVERITY_WARNING,
  MetadataValidator,
)


def _enum_block_with_field_alias() -> BlockMetadata:
  return BlockMetadata(
    version=1,
    schema_id="test.nature_aware",
    fields={
      "nature": FieldMetadata(type="string"),
    },
    field_aliases={"annotation": "nature"},
  )


def _status_block(*, aliases=None, tolerated=None) -> BlockMetadata:
  return BlockMetadata(
    version=1,
    schema_id="test.status",
    fields={
      "status": FieldMetadata(
        type="enum",
        enum_values=["draft", "in-progress", "completed"],
        aliases=aliases,
        tolerated_aliases=tolerated,
      ),
    },
  )


# VT-CC-008 ----------------------------------------------------------------


def test_field_name_alias_strict_emits_warning_with_rename_fix() -> None:
  validator = MetadataValidator(_enum_block_with_field_alias())
  errors = validator.validate({"annotation": "foo"}, strict=True)
  assert len(errors) == 1
  err = errors[0]
  assert err.severity == SEVERITY_WARNING
  assert err.fix_kind == FIX_KIND_RENAME_KEY
  assert err.fix_hint == "nature"
  assert "annotation" in err.message
  assert "nature" in err.message


def test_field_name_alias_tolerant_is_silent() -> None:
  validator = MetadataValidator(_enum_block_with_field_alias())
  errors = validator.validate({"annotation": "foo"})
  assert errors == []


def test_field_name_alias_does_not_mutate_input() -> None:
  data = {"annotation": "foo"}
  validator = MetadataValidator(_enum_block_with_field_alias())
  validator.validate(data, strict=True)
  assert data == {"annotation": "foo"}, "validator must be report-only"


# VT-CC-034 (collision) ----------------------------------------------------


def test_field_name_alias_collision_is_error_severity() -> None:
  validator = MetadataValidator(_enum_block_with_field_alias())
  data = {"annotation": "foo", "nature": "bar"}
  errors = validator.validate(data, strict=True)
  collisions = [e for e in errors if "conflict" in e.message]
  assert len(collisions) == 1
  err = collisions[0]
  assert err.severity == SEVERITY_ERROR
  assert err.fix_kind is None
  assert err.fix_hint is None
  assert data == {"annotation": "foo", "nature": "bar"}, "no silent merge"


# VT-CC-030 ----------------------------------------------------------------


def test_field_value_alias_strict_emits_warning_with_rewrite_fix() -> None:
  validator = MetadataValidator(_status_block(aliases={"complete": "completed"}))
  errors = validator.validate({"status": "complete"}, strict=True)
  assert len(errors) == 1
  err = errors[0]
  assert err.severity == SEVERITY_WARNING
  assert err.fix_kind == FIX_KIND_REWRITE_VALUE
  assert err.fix_hint == "completed"


def test_field_value_alias_tolerant_is_silent() -> None:
  validator = MetadataValidator(_status_block(aliases={"complete": "completed"}))
  errors = validator.validate({"status": "complete"})
  assert errors == []


# VT-CC-009 ----------------------------------------------------------------


def test_tolerated_alias_accepted_silently_by_default() -> None:
  tolerated = {
    "wip": ToleratedAlias(
      canonical="in-progress", sunset_after="DE-140", rationale="migration window"
    )
  }
  validator = MetadataValidator(_status_block(tolerated=tolerated))
  errors = validator.validate({"status": "wip"})
  assert errors == []


def test_tolerated_alias_under_strict_emits_warning() -> None:
  tolerated = {
    "wip": ToleratedAlias(canonical="in-progress", sunset_after="DE-140", rationale="")
  }
  validator = MetadataValidator(_status_block(tolerated=tolerated))
  errors = validator.validate({"status": "wip"}, strict=True)
  assert len(errors) == 1
  assert errors[0].severity == SEVERITY_WARNING
  assert "tolerated alias" in errors[0].message


def test_tolerated_alias_under_no_tolerated_is_error() -> None:
  tolerated = {
    "wip": ToleratedAlias(canonical="in-progress", sunset_after="DE-140", rationale="")
  }
  validator = MetadataValidator(_status_block(tolerated=tolerated))
  errors = validator.validate({"status": "wip"}, strict=True, accept_tolerated=False)
  assert len(errors) == 1
  assert errors[0].severity == SEVERITY_ERROR


# Did-you-mean coverage ----------------------------------------------------


@pytest.mark.parametrize(
  ("typo", "expected_hint"),
  [
    ("draaft", "draft"),
    ("in_progres", "in-progress"),
    ("complte", "completed"),
  ],
)
def test_unknown_enum_under_strict_populates_did_you_mean(
  typo: str, expected_hint: str
) -> None:
  validator = MetadataValidator(_status_block())
  errors = validator.validate({"status": typo}, strict=True)
  assert len(errors) == 1
  assert errors[0].fix_hint == expected_hint


def test_unknown_enum_under_tolerant_is_silent() -> None:
  validator = MetadataValidator(_status_block())
  errors = validator.validate({"status": "completely_invented"})
  assert errors == []


# Relations item — block.field_aliases on nested object ---------------------


def test_nested_relations_item_field_aliases_strict_emits_warning() -> None:
  block = BlockMetadata(
    version=1,
    schema_id="test.relations_aware",
    fields={
      "relations": FieldMetadata(
        type="array",
        items=FieldMetadata(
          type="object",
          properties={
            "type": FieldMetadata(type="string"),
            "nature": FieldMetadata(type="string"),
          },
          field_aliases={"annotation": "nature"},
        ),
      ),
    },
  )
  validator = MetadataValidator(block)
  data = {
    "relations": [
      {"type": "relates_to", "annotation": "legacy alias"},
    ]
  }
  errors = validator.validate(data, strict=True)
  warnings = [
    e
    for e in errors
    if e.severity == SEVERITY_WARNING and e.fix_kind == FIX_KIND_RENAME_KEY
  ]
  assert len(warnings) == 1
  assert warnings[0].path == "relations[0].annotation"
  assert warnings[0].fix_hint == "nature"

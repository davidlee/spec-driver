"""Tests for the metadata schema dataclasses (DE-137 IP-137-P01 task 1.3).

Covers the alias-mechanism extensions:
- `ToleratedAlias`
- `FieldMetadata.aliases` / `.tolerated_aliases`
- `BlockMetadata.field_aliases`
"""

from __future__ import annotations

import dataclasses
from types import MappingProxyType

from .schema import BlockMetadata, FieldMetadata, ToleratedAlias


def _enum_field() -> FieldMetadata:
  return FieldMetadata(type="enum", enum_values=["draft", "completed"])


def test_tolerated_alias_is_frozen_dataclass() -> None:
  alias = ToleratedAlias(
    canonical="in-progress", sunset_after="DE-140", rationale="migration window"
  )
  assert alias.canonical == "in-progress"
  assert alias.sunset_after == "DE-140"
  assert alias.rationale == "migration window"
  try:
    alias.canonical = "completed"  # type: ignore[misc]
  except dataclasses.FrozenInstanceError:
    return
  msg = "ToleratedAlias must be frozen"
  raise AssertionError(msg)


def test_field_metadata_aliases_default_none() -> None:
  meta = _enum_field()
  assert meta.aliases is None
  assert meta.tolerated_aliases is None


def test_field_metadata_accepts_aliases_mapping() -> None:
  meta = FieldMetadata(
    type="enum",
    enum_values=["completed", "in-progress"],
    aliases={"complete": "completed"},
  )
  assert meta.aliases is not None
  assert meta.aliases["complete"] == "completed"


def test_field_metadata_accepts_tolerated_aliases_with_metadata_value() -> None:
  alias = ToleratedAlias(canonical="in-progress", sunset_after="DE-140", rationale="")
  meta = FieldMetadata(
    type="enum",
    enum_values=["in-progress"],
    tolerated_aliases={"wip": alias},
  )
  assert meta.tolerated_aliases is not None
  assert meta.tolerated_aliases["wip"].canonical == "in-progress"


def test_field_metadata_accepts_mappingproxytype_for_aliases() -> None:
  proxy = MappingProxyType({"complete": "completed"})
  meta = FieldMetadata(
    type="enum",
    enum_values=["completed"],
    aliases=proxy,
  )
  assert meta.aliases == proxy


def test_block_metadata_field_aliases_default_none() -> None:
  block = BlockMetadata(version=1, schema_id="t.s", fields={"f": _enum_field()})
  assert block.field_aliases is None


def test_block_metadata_accepts_field_aliases_mapping() -> None:
  block = BlockMetadata(
    version=1,
    schema_id="t.s",
    fields={"nature": FieldMetadata(type="string")},
    field_aliases={"annotation": "nature"},
  )
  assert block.field_aliases is not None
  assert block.field_aliases["annotation"] == "nature"


def test_field_metadata_field_aliases_default_none() -> None:
  meta = FieldMetadata(
    type="object", properties={"nature": FieldMetadata(type="string")}
  )
  assert meta.field_aliases is None


def test_field_metadata_accepts_field_aliases_mapping() -> None:
  """Nested object schemas (e.g. relations item) carry their own field_aliases."""
  meta = FieldMetadata(
    type="object",
    properties={"nature": FieldMetadata(type="string")},
    field_aliases={"annotation": "nature"},
  )
  assert meta.field_aliases == {"annotation": "nature"}


def test_field_metadata_replace_preserves_aliases() -> None:
  meta = FieldMetadata(
    type="enum",
    enum_values=["completed", "in-progress"],
    aliases={"complete": "completed"},
  )
  copy = dataclasses.replace(meta, required=True)
  assert copy.aliases == {"complete": "completed"}
  assert copy.required is True


def test_existing_field_metadata_construction_unchanged() -> None:
  """Pre-existing constructions without aliases continue to work."""
  meta = FieldMetadata(type="string", required=True, description="name")
  assert meta.aliases is None
  assert meta.tolerated_aliases is None

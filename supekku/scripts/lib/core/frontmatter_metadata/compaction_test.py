"""Tests for frontmatter compaction using FieldMetadata persistence annotations."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .compaction import compact_frontmatter
from .delta import DELTA_FRONTMATTER_METADATA


def _make_metadata(**field_overrides: FieldMetadata) -> BlockMetadata:
  """Build a minimal BlockMetadata with the given fields."""
  return BlockMetadata(
    version=1,
    schema_id="test.frontmatter",
    fields=field_overrides,
  )


class TestCompactFrontmatter(unittest.TestCase):
  """Core compaction logic tests."""

  def test_canonical_fields_always_kept(self) -> None:
    meta = _make_metadata(
      name=FieldMetadata(type="string", persistence="canonical"),
    )
    data = {"name": "hello"}
    result = compact_frontmatter(data, meta)
    self.assertEqual(result, {"name": "hello"})

  def test_derived_fields_omitted(self) -> None:
    meta = _make_metadata(
      name=FieldMetadata(type="string", persistence="canonical"),
      generated=FieldMetadata(type="string", persistence="derived"),
    )
    data = {"name": "hello", "generated": "some-hash"}
    result = compact_frontmatter(data, meta)
    self.assertEqual(result, {"name": "hello"})

  def test_derived_fields_kept_in_full_mode(self) -> None:
    meta = _make_metadata(
      name=FieldMetadata(type="string", persistence="canonical"),
      generated=FieldMetadata(type="string", persistence="derived"),
    )
    data = {"name": "hello", "generated": "some-hash"}
    result = compact_frontmatter(data, meta, mode="full")
    self.assertEqual(result, {"name": "hello", "generated": "some-hash"})

  def test_optional_omitted_when_absent(self) -> None:
    meta = _make_metadata(
      name=FieldMetadata(type="string", persistence="canonical"),
      summary=FieldMetadata(type="string", persistence="optional"),
    )
    data = {"name": "hello"}
    result = compact_frontmatter(data, meta)
    self.assertNotIn("summary", result)

  def test_optional_omitted_when_none(self) -> None:
    meta = _make_metadata(
      summary=FieldMetadata(type="string", persistence="optional"),
    )
    data = {"summary": None}
    result = compact_frontmatter(data, meta)
    self.assertNotIn("summary", result)

  def test_optional_with_default_omitted_when_equal(self) -> None:
    meta = _make_metadata(
      tags=FieldMetadata(
        type="array",
        persistence="optional",
        default_value=[],
        items=FieldMetadata(type="string"),
      ),
    )
    data = {"tags": []}
    result = compact_frontmatter(data, meta)
    self.assertNotIn("tags", result)

  def test_optional_kept_when_non_default(self) -> None:
    meta = _make_metadata(
      tags=FieldMetadata(
        type="array",
        persistence="optional",
        default_value=[],
        items=FieldMetadata(type="string"),
      ),
    )
    data = {"tags": ["important"]}
    result = compact_frontmatter(data, meta)
    self.assertEqual(result, {"tags": ["important"]})

  def test_optional_kept_when_present_no_default(self) -> None:
    meta = _make_metadata(
      summary=FieldMetadata(type="string", persistence="optional"),
    )
    data = {"summary": "A real summary"}
    result = compact_frontmatter(data, meta)
    self.assertEqual(result, {"summary": "A real summary"})

  def test_default_omit_stripped_when_equal(self) -> None:
    meta = _make_metadata(
      relations=FieldMetadata(
        type="array",
        persistence="default-omit",
        default_value=[],
        items=FieldMetadata(
          type="object",
          properties={
            "type": FieldMetadata(type="string"),
            "target": FieldMetadata(type="string"),
          },
        ),
      ),
    )
    data = {"relations": []}
    result = compact_frontmatter(data, meta)
    self.assertNotIn("relations", result)

  def test_default_omit_kept_when_non_default(self) -> None:
    meta = _make_metadata(
      relations=FieldMetadata(
        type="array",
        persistence="default-omit",
        default_value=[],
        items=FieldMetadata(
          type="object",
          properties={
            "type": FieldMetadata(type="string"),
            "target": FieldMetadata(type="string"),
          },
        ),
      ),
    )
    data = {"relations": [{"type": "implements", "target": "SPEC-001"}]}
    result = compact_frontmatter(data, meta)
    self.assertEqual(
      result, {"relations": [{"type": "implements", "target": "SPEC-001"}]}
    )

  def test_default_omit_dict_with_superset_keys_kept(self) -> None:
    """applies_to with prod key differs from default {specs:[], requirements:[]}."""
    meta = _make_metadata(
      applies_to=FieldMetadata(
        type="object",
        persistence="default-omit",
        default_value={"specs": [], "requirements": []},
        properties={
          "specs": FieldMetadata(
            type="array",
            items=FieldMetadata(type="string"),
          ),
          "requirements": FieldMetadata(
            type="array",
            items=FieldMetadata(type="string"),
          ),
        },
      ),
    )
    data = {"applies_to": {"specs": [], "prod": ["PROD-020"], "requirements": []}}
    result = compact_frontmatter(data, meta)
    self.assertIn("applies_to", result)
    self.assertEqual(
      result["applies_to"],
      {"specs": [], "prod": ["PROD-020"], "requirements": []},
    )

  def test_default_omit_dict_equal_to_default_stripped(self) -> None:
    meta = _make_metadata(
      applies_to=FieldMetadata(
        type="object",
        persistence="default-omit",
        default_value={"specs": [], "requirements": []},
        properties={
          "specs": FieldMetadata(
            type="array",
            items=FieldMetadata(type="string"),
          ),
          "requirements": FieldMetadata(
            type="array",
            items=FieldMetadata(type="string"),
          ),
        },
      ),
    )
    data = {"applies_to": {"specs": [], "requirements": []}}
    result = compact_frontmatter(data, meta)
    self.assertNotIn("applies_to", result)

  def test_unknown_fields_pass_through(self) -> None:
    meta = _make_metadata(
      name=FieldMetadata(type="string", persistence="canonical"),
    )
    data = {"name": "hello", "custom_field": "preserved"}
    result = compact_frontmatter(data, meta)
    self.assertEqual(result, {"name": "hello", "custom_field": "preserved"})

  def test_full_mode_keeps_everything(self) -> None:
    meta = _make_metadata(
      name=FieldMetadata(type="string", persistence="canonical"),
      derived=FieldMetadata(type="string", persistence="derived"),
      tags=FieldMetadata(
        type="array",
        persistence="optional",
        default_value=[],
        items=FieldMetadata(type="string"),
      ),
      relations=FieldMetadata(
        type="array",
        persistence="default-omit",
        default_value=[],
        items=FieldMetadata(
          type="object",
          properties={
            "type": FieldMetadata(type="string"),
            "target": FieldMetadata(type="string"),
          },
        ),
      ),
    )
    data = {
      "name": "hello",
      "derived": "hash",
      "tags": [],
      "relations": [],
    }
    result = compact_frontmatter(data, meta, mode="full")
    self.assertEqual(result, data)

  def test_empty_data_returns_empty(self) -> None:
    meta = _make_metadata(
      name=FieldMetadata(type="string", persistence="canonical"),
    )
    result = compact_frontmatter({}, meta)
    self.assertEqual(result, {})

  def test_preserves_field_order(self) -> None:
    """Compacted output preserves insertion order of surviving fields."""
    meta = _make_metadata(
      id=FieldMetadata(type="string", persistence="canonical"),
      name=FieldMetadata(type="string", persistence="canonical"),
      tags=FieldMetadata(
        type="array",
        persistence="default-omit",
        default_value=[],
        items=FieldMetadata(type="string"),
      ),
      status=FieldMetadata(type="string", persistence="canonical"),
    )
    data = {"id": "DE-001", "name": "Test", "tags": [], "status": "draft"}
    result = compact_frontmatter(data, meta)
    self.assertEqual(list(result.keys()), ["id", "name", "status"])

  def test_invalid_mode_raises(self) -> None:
    meta = _make_metadata()
    with self.assertRaises(ValueError, msg="Invalid compaction mode"):
      compact_frontmatter({}, meta, mode="invalid")


class TestDeltaCompactionRoundTrip(unittest.TestCase):
  """Round-trip tests using real DELTA_FRONTMATTER_METADATA."""

  def setUp(self) -> None:
    self.meta = DELTA_FRONTMATTER_METADATA

  def test_minimal_delta_unchanged(self) -> None:
    """Minimal delta (canonical fields only) survives compaction."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2026-03-03",
      "updated": "2026-03-03",
    }
    result = compact_frontmatter(data, self.meta)
    self.assertEqual(result, data)

  def test_empty_defaults_stripped(self) -> None:
    """Empty-default fields (aliases, relations, applies_to) are removed."""
    data = {
      "id": "DE-002",
      "name": "Delta With Defaults",
      "slug": "delta-defaults",
      "kind": "delta",
      "status": "draft",
      "created": "2026-03-03",
      "updated": "2026-03-03",
      "aliases": [],
      "relations": [],
      "applies_to": {"specs": [], "requirements": []},
    }
    result = compact_frontmatter(data, self.meta)
    self.assertNotIn("relations", result)
    self.assertNotIn("applies_to", result)
    # aliases is not in delta metadata — passes through as unknown
    self.assertIn("aliases", result)

  def test_populated_defaults_kept(self) -> None:
    """Non-default values for default-omit fields are preserved."""
    data = {
      "id": "DE-003",
      "name": "Delta With Content",
      "slug": "delta-content",
      "kind": "delta",
      "status": "in-progress",
      "created": "2026-03-03",
      "updated": "2026-03-03",
      "relations": [{"type": "implements", "target": "SPEC-101"}],
      "applies_to": {
        "specs": ["SPEC-101"],
        "prod": ["PROD-020"],
        "requirements": ["SPEC-101.FR-01"],
      },
    }
    result = compact_frontmatter(data, self.meta)
    self.assertEqual(result["relations"], data["relations"])
    self.assertEqual(result["applies_to"], data["applies_to"])

  def test_optional_fields_stripped_when_empty(self) -> None:
    """Optional fields (owners, tags, etc.) stripped when empty/default."""
    data = {
      "id": "DE-004",
      "name": "Delta Optional",
      "slug": "delta-optional",
      "kind": "delta",
      "status": "draft",
      "created": "2026-03-03",
      "updated": "2026-03-03",
      "owners": [],
      "auditers": [],
      "tags": [],
      "context_inputs": [],
      "risk_register": [],
    }
    result = compact_frontmatter(data, self.meta)
    for field in ("owners", "auditers", "tags", "context_inputs", "risk_register"):
      self.assertNotIn(field, result, f"{field} should be stripped")

  def test_optional_fields_kept_when_populated(self) -> None:
    data = {
      "id": "DE-005",
      "name": "Delta Full",
      "slug": "delta-full",
      "kind": "delta",
      "status": "in-progress",
      "lifecycle": "implementation",
      "created": "2026-03-03",
      "updated": "2026-03-03",
      "owners": ["alice"],
      "summary": "A meaningful delta",
      "tags": ["core"],
    }
    result = compact_frontmatter(data, self.meta)
    self.assertEqual(result["owners"], ["alice"])
    self.assertEqual(result["summary"], "A meaningful delta")
    self.assertEqual(result["tags"], ["core"])
    self.assertEqual(result["lifecycle"], "implementation")

  def test_applies_to_with_prod_not_stripped(self) -> None:
    """Known pitfall: applies_to with prod key != default, must be kept."""
    data = {
      "id": "DE-006",
      "name": "Delta Prod",
      "slug": "delta-prod",
      "kind": "delta",
      "status": "draft",
      "created": "2026-03-03",
      "updated": "2026-03-03",
      "applies_to": {"specs": [], "prod": ["PROD-020"], "requirements": []},
    }
    result = compact_frontmatter(data, self.meta)
    self.assertIn("applies_to", result)

  def test_full_mode_preserves_all_fields(self) -> None:
    """Full mode keeps everything, including empty defaults."""
    data = {
      "id": "DE-007",
      "name": "Full Mode Delta",
      "slug": "full-mode",
      "kind": "delta",
      "status": "draft",
      "created": "2026-03-03",
      "updated": "2026-03-03",
      "owners": [],
      "relations": [],
      "applies_to": {"specs": [], "requirements": []},
      "tags": [],
    }
    result = compact_frontmatter(data, self.meta, mode="full")
    self.assertEqual(result, data)

  def test_round_trip_semantic_equivalence(self) -> None:
    """Compacted data + defaults reconstructs original semantics."""
    original = {
      "id": "DE-008",
      "name": "Round Trip",
      "slug": "round-trip",
      "kind": "delta",
      "status": "draft",
      "created": "2026-03-03",
      "updated": "2026-03-03",
      "relations": [],
      "applies_to": {"specs": [], "requirements": []},
      "owners": [],
      "tags": [],
    }
    compacted = compact_frontmatter(original, self.meta)

    # Reconstruct: for each missing field, the reader would use defaults
    reconstructed = dict(compacted)
    for field_name, field_meta in self.meta.fields.items():
      if field_name not in reconstructed and field_meta.default_value is not None:
        reconstructed[field_name] = field_meta.default_value

    # Semantic equivalence: canonical fields identical, default fields
    # either present with original value or reconstructable from defaults
    for key, value in original.items():
      if key in compacted:
        self.assertEqual(compacted[key], value)
      else:
        field_meta = self.meta.fields.get(key)
        self.assertIsNotNone(field_meta, f"Missing field {key} not in metadata")
        assert field_meta is not None  # narrow type for linter
        self.assertEqual(
          value,
          field_meta.default_value,
          f"Omitted field {key} had non-default value",
        )


if __name__ == "__main__":
  unittest.main()

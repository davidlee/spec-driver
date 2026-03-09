"""Tests for search index builder (VT-087-002)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from supekku.scripts.lib.core.artifact_view import ArtifactEntry, ArtifactType
from supekku.tui.search.index import (
  FIELD_ID,
  FIELD_STATUS,
  FIELD_TITLE,
  SearchEntry,
  _extract_relation_targets,
  _extract_searchable_fields,
  build_search_index,
)


@dataclass
class _FakeRecord:
  """Minimal record for testing field extraction."""

  id: str = "DE-001"
  name: str = "Test delta"
  status: str = "draft"
  kind: str = "delta"
  slug: str = "test_delta"
  category: str | None = None
  c4_level: str | None = None
  tags: list[str] | None = None
  relations: list[dict[str, Any]] | None = None
  path: str = "/tmp/fake.md"


def _make_entry(
  *,
  record_id: str = "DE-001",
  title: str = "Test delta",
  status: str = "draft",
  art_type: ArtifactType = ArtifactType.DELTA,
) -> ArtifactEntry:
  return ArtifactEntry(
    id=record_id,
    title=title,
    status=status,
    path=Path("/tmp/fake.md"),
    artifact_type=art_type,
  )


class TestExtractSearchableFields:
  """Test _extract_searchable_fields."""

  def test_core_fields(self):
    ae = _make_entry()
    record = _FakeRecord()
    fields = _extract_searchable_fields(ae, record)
    assert fields[FIELD_ID] == "DE-001"
    assert fields[FIELD_TITLE] == "Test delta"
    assert fields[FIELD_STATUS] == "draft"

  def test_scalar_frontmatter_attrs(self):
    ae = _make_entry()
    record = _FakeRecord(
      kind="delta",
      slug="test_delta",
      category="unit",
      c4_level="code",
    )
    fields = _extract_searchable_fields(ae, record)
    assert fields["kind"] == "delta"
    assert fields["slug"] == "test_delta"
    assert fields["category"] == "unit"
    assert fields["c4_level"] == "code"

  def test_missing_attrs_omitted(self):
    ae = _make_entry()
    record = _FakeRecord(category=None, c4_level=None)
    fields = _extract_searchable_fields(ae, record)
    assert "category" not in fields
    assert "c4_level" not in fields

  def test_empty_string_attrs_omitted(self):
    ae = _make_entry()
    record = _FakeRecord(category="", c4_level="")
    fields = _extract_searchable_fields(ae, record)
    assert "category" not in fields
    assert "c4_level" not in fields

  def test_tags_produce_per_tag_entries(self):
    ae = _make_entry()
    record = _FakeRecord(tags=["tui", "search", "navigation"])
    fields = _extract_searchable_fields(ae, record)
    assert fields["tag.0"] == "tui"
    assert fields["tag.1"] == "search"
    assert fields["tag.2"] == "navigation"
    # No joined string key.
    assert "tags" not in fields

  def test_empty_tags_list(self):
    ae = _make_entry()
    record = _FakeRecord(tags=[])
    fields = _extract_searchable_fields(ae, record)
    assert not any(k.startswith("tag.") for k in fields)

  def test_tags_none(self):
    ae = _make_entry()
    record = _FakeRecord(tags=None)
    fields = _extract_searchable_fields(ae, record)
    assert not any(k.startswith("tag.") for k in fields)

  def test_whitespace_tags_stripped(self):
    ae = _make_entry()
    record = _FakeRecord(tags=["  tui  ", ""])
    fields = _extract_searchable_fields(ae, record)
    assert fields["tag.0"] == "tui"
    # Empty string after strip is excluded.
    assert "tag.1" not in fields

  def test_record_without_optional_attrs(self):
    """Records that lack certain attrs entirely (e.g. no .slug)."""
    ae = _make_entry()
    record = MagicMock(spec=[])  # No attributes at all.
    fields = _extract_searchable_fields(ae, record)
    # Core fields still present from ArtifactEntry.
    assert FIELD_ID in fields
    assert FIELD_TITLE in fields
    assert FIELD_STATUS in fields


class TestExtractRelationTargets:
  """Test _extract_relation_targets."""

  def test_with_relations(self):
    record = _FakeRecord(
      relations=[
        {"type": "implements", "target": "PROD-010"},
        {"type": "depends_on", "target": "DE-085"},
      ],
    )
    targets = _extract_relation_targets(record)
    assert "PROD-010" in targets
    assert "DE-085" in targets

  def test_no_relations(self):
    record = _FakeRecord(relations=None)
    assert _extract_relation_targets(record) == ()

  def test_empty_relations(self):
    record = _FakeRecord(relations=[])
    assert _extract_relation_targets(record) == ()

  def test_record_without_relations_attr(self):
    record = MagicMock(spec=[])
    assert _extract_relation_targets(record) == ()


class TestBuildSearchIndex:
  """Test build_search_index end-to-end."""

  def test_produces_entries_for_working_registries(self):
    record = _FakeRecord(id="DE-001", name="Test", status="draft")
    mock_registry = MagicMock()
    mock_registry.collect.return_value = {"DE-001": record}

    with patch(
      "supekku.tui.search.index._REGISTRY_FACTORIES",
      {ArtifactType.DELTA: lambda _root: mock_registry},
    ):
      index = build_search_index(root=Path("/tmp"))

    assert len(index) == 1
    assert isinstance(index[0], SearchEntry)
    assert index[0].entry.id == "DE-001"

  def test_skips_failing_registries(self):
    def _failing_factory(_root):
      raise RuntimeError("boom")

    record = _FakeRecord(id="ADR-001", name="Test ADR")
    ok_registry = MagicMock()
    ok_registry.collect.return_value = {"ADR-001": record}

    with patch(
      "supekku.tui.search.index._REGISTRY_FACTORIES",
      {
        ArtifactType.DELTA: _failing_factory,
        ArtifactType.ADR: lambda _root: ok_registry,
      },
    ):
      index = build_search_index(root=Path("/tmp"))

    assert len(index) == 1
    assert index[0].entry.id == "ADR-001"

  def test_skips_failing_records(self):
    """If adapt_record fails for one record, others still indexed."""

    @dataclass
    class _BadRecord:
      # Missing 'id' — adapt_record will fail.
      pass

    good = _FakeRecord(id="DE-001", name="Good", status="draft")
    bad = _BadRecord()

    mock_registry = MagicMock()
    mock_registry.collect.return_value = {"DE-001": good, "DE-BAD": bad}

    with patch(
      "supekku.tui.search.index._REGISTRY_FACTORIES",
      {ArtifactType.DELTA: lambda _root: mock_registry},
    ):
      index = build_search_index(root=Path("/tmp"))

    ids = [e.entry.id for e in index]
    assert "DE-001" in ids

  def test_empty_when_no_factories(self):
    with patch("supekku.tui.search.index._REGISTRY_FACTORIES", {}):
      index = build_search_index(root=Path("/tmp"))
    assert index == []

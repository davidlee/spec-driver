"""Tests for frontmatter_writer — canonical YAML round-trip writer."""

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from .frontmatter_writer import (
  FieldUpdateResult,
  ListUpdateResult,
  add_frontmatter_list_items,
  dump_frontmatter_yaml,
  remove_frontmatter_list_items,
  update_frontmatter,
  update_frontmatter_fields,
  update_frontmatter_status,
)
from .spec_utils import load_markdown_file

SAMPLE_FRONTMATTER = """\
---
id: DE-001
name: Example Delta
status: draft
kind: delta
created: '2026-01-01'
updated: '2026-01-01'
---

# DE-001 – Example Delta

Body content here.
"""

MEMORY_FRONTMATTER = """\
---
id: mem.fact.test
name: Test Memory
status: active
kind: memory
memory_type: fact
created: '2026-01-01'
updated: '2026-01-01'
verified: '2026-01-01'
---

# Test Memory

Body content here.
"""

TAGGED_FRONTMATTER = """\
---
id: SPEC-100
name: Test Spec
status: draft
kind: spec
created: '2026-01-01'
updated: '2026-01-01'
tags: [auth, security]
---

# SPEC-100

Body content.
"""


# ---------------------------------------------------------------------------
# CompactDumper / dump_frontmatter_yaml
# ---------------------------------------------------------------------------


class TestCompactDumper:
  """Tests for CompactDumper formatting heuristic."""

  def test_short_scalar_list_is_flow(self) -> None:
    out = dump_frontmatter_yaml({"tags": ["a", "b", "c"]})
    assert "tags: [a, b, c]" in out

  def test_empty_list_is_flow(self) -> None:
    out = dump_frontmatter_yaml({"aliases": []})
    assert "aliases: []" in out

  def test_long_scalar_list_is_block(self) -> None:
    items = [f"item-{i:03d}" for i in range(20)]
    out = dump_frontmatter_yaml({"items": items})
    assert "- item-000" in out

  def test_list_of_dicts_is_block(self) -> None:
    out = dump_frontmatter_yaml(
      {"relations": [{"type": "implements", "target": "FR-001"}]}
    )
    assert "- type: implements" in out

  def test_idempotent(self) -> None:
    import yaml

    data = {
      "id": "SPEC-100",
      "tags": ["auth", "security"],
      "relations": [{"type": "implements", "target": "FR-001"}],
      "aliases": [],
    }
    out1 = dump_frontmatter_yaml(data)
    out2 = dump_frontmatter_yaml(yaml.safe_load(out1))
    assert out1 == out2

  def test_unicode_preserved(self) -> None:
    out = dump_frontmatter_yaml({"note": "spec ⇄ delta"})
    assert "⇄" in out

  def test_date_string_quoted(self) -> None:
    out = dump_frontmatter_yaml({"created": "2025-01-15"})
    assert 'created: "2025-01-15"' in out

  def test_key_order_preserved(self) -> None:
    data = {"z": 1, "a": 2, "m": 3}
    out = dump_frontmatter_yaml(data)
    assert out.index("z:") < out.index("a:") < out.index("m:")


# ---------------------------------------------------------------------------
# update_frontmatter (core mutator)
# ---------------------------------------------------------------------------


class TestUpdateFrontmatter:
  """Tests for update_frontmatter() mutator pattern."""

  def test_applies_mutation(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter(f, lambda fm: fm.__setitem__("status", "active"))

    fm, _ = load_markdown_file(f)
    assert fm["status"] == "active"

  def test_bumps_updated_date(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    with patch("supekku.scripts.lib.core.frontmatter_writer.date") as mock_date:
      mock_date.today.return_value = date(2026, 3, 14)
      mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
      update_frontmatter(f, lambda fm: None)

    fm, _ = load_markdown_file(f)
    assert fm["updated"] == "2026-03-14"

  def test_preserves_body(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter(f, lambda fm: fm.__setitem__("status", "active"))

    _, body = load_markdown_file(f)
    assert "# DE-001 – Example Delta" in body
    assert "Body content here." in body

  def test_preserves_body_with_horizontal_rule(self, tmp_path: Path) -> None:
    content = "---\nid: X\nstatus: draft\n---\n\n# Title\n\n---\n\nAfter rule.\n"
    f = tmp_path / "test.md"
    f.write_text(content, encoding="utf-8")

    update_frontmatter(f, lambda fm: fm.__setitem__("status", "active"))

    _, body = load_markdown_file(f)
    assert "---" in body
    assert "After rule." in body

  def test_returns_mutated_dict(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    result = update_frontmatter(f, lambda fm: fm.__setitem__("status", "done"))

    assert result["status"] == "done"

  def test_raises_on_missing_file(self, tmp_path: Path) -> None:
    f = tmp_path / "missing.md"
    with pytest.raises(FileNotFoundError):
      update_frontmatter(f, lambda fm: None)

  def test_trailing_newline(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter(f, lambda fm: None)

    content = f.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert not content.endswith("\n\n\n")


# ---------------------------------------------------------------------------
# update_frontmatter_status (backward-compatible wrapper)
# ---------------------------------------------------------------------------


class TestUpdateFrontmatterStatus:
  """Tests for update_frontmatter_status()."""

  def test_updates_status_field(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    result = update_frontmatter_status(f, "in-progress")

    assert result is True
    fm, _ = load_markdown_file(f)
    assert fm["status"] == "in-progress"

  def test_updates_updated_date(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    with patch("supekku.scripts.lib.core.frontmatter_writer.date") as mock_date:
      mock_date.today.return_value = date(2026, 3, 8)
      mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
      update_frontmatter_status(f, "completed")

    fm, _ = load_markdown_file(f)
    assert fm["updated"] == "2026-03-08"

  def test_preserves_body_content(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter_status(f, "completed")

    _, body = load_markdown_file(f)
    assert "# DE-001 – Example Delta" in body
    assert "Body content here." in body

  def test_preserves_other_frontmatter_fields(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter_status(f, "completed")

    fm, _ = load_markdown_file(f)
    assert fm["id"] == "DE-001"
    assert fm["name"] == "Example Delta"
    assert fm["kind"] == "delta"
    assert fm["created"] == "2026-01-01"

  def test_returns_false_when_no_status_field(self, tmp_path: Path) -> None:
    f = tmp_path / "no-status.md"
    f.write_text("---\nid: X\nname: X\n---\n# No status\n", encoding="utf-8")

    result = update_frontmatter_status(f, "active")

    assert result is False

  def test_raises_on_nonexistent_file(self, tmp_path: Path) -> None:
    f = tmp_path / "missing.md"

    with pytest.raises(FileNotFoundError):
      update_frontmatter_status(f, "active")

  def test_raises_on_empty_status(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    with pytest.raises(ValueError, match="must not be empty"):
      update_frontmatter_status(f, "")

  def test_raises_on_whitespace_only_status(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    with pytest.raises(ValueError, match="must not be empty"):
      update_frontmatter_status(f, "   ")

  def test_idempotent_update(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter_status(f, "draft")

    content = f.read_text(encoding="utf-8")
    assert content.count("status: draft") == 1

  def test_only_modifies_frontmatter_status(self, tmp_path: Path) -> None:
    """Status-like lines in body content should not be touched."""
    content_with_body = """\
---
id: DE-001
status: draft
updated: '2026-01-01'
---

# Title

status: this should not change
"""
    f = tmp_path / "DE-001.md"
    f.write_text(content_with_body, encoding="utf-8")

    update_frontmatter_status(f, "active")

    content = f.read_text(encoding="utf-8")
    fm, body = load_markdown_file(f)
    assert fm["status"] == "active"
    assert "status: this should not change" in body

  def test_trailing_newline_preserved(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter_status(f, "completed")

    content = f.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert not content.endswith("\n\n\n")


# ---------------------------------------------------------------------------
# update_frontmatter_fields (backward-compatible wrapper)
# ---------------------------------------------------------------------------


class TestUpdateFrontmatterFields:
  """Tests for update_frontmatter_fields()."""

  def test_replaces_existing_field(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    result = update_frontmatter_fields(f, {"status": "deprecated"})

    fm, _ = load_markdown_file(f)
    assert fm["status"] == "deprecated"
    assert "status" in result.updated
    assert not result.inserted

  def test_replaces_multiple_existing_fields(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    result = update_frontmatter_fields(
      f, {"verified": "2026-03-09", "updated": "2026-03-09"}
    )

    fm, _ = load_markdown_file(f)
    assert fm["verified"] == "2026-03-09"
    assert result.updated == {"verified", "updated"}

  def test_inserts_missing_field(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    sha = "a" * 40
    result = update_frontmatter_fields(f, {"verified_sha": sha})

    fm, _ = load_markdown_file(f)
    assert fm["verified_sha"] == sha
    assert "verified_sha" in result.inserted
    assert not result.updated

  def test_mixed_replace_and_insert(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    sha = "b" * 40
    result = update_frontmatter_fields(
      f, {"verified": "2026-03-09", "verified_sha": sha}
    )

    fm, _ = load_markdown_file(f)
    assert fm["verified"] == "2026-03-09"
    assert fm["verified_sha"] == sha
    assert result.updated == {"verified"}
    assert result.inserted == {"verified_sha"}

  def test_preserves_body_content(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    update_frontmatter_fields(f, {"status": "deprecated"})

    _, body = load_markdown_file(f)
    assert "# Test Memory" in body
    assert "Body content here." in body

  def test_preserves_unmodified_fields(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    update_frontmatter_fields(f, {"status": "deprecated"})

    fm, _ = load_markdown_file(f)
    assert fm["id"] == "mem.fact.test"
    assert fm["name"] == "Test Memory"
    assert fm["kind"] == "memory"
    assert fm["created"] == "2026-01-01"

  def test_does_not_modify_body_lines_matching_field_name(self, tmp_path: Path) -> None:
    content = "---\nid: X\nstatus: active\nupdated: '2026-01-01'\n---\n\n# Title\n\nstatus: body line\n"
    f = tmp_path / "test.md"
    f.write_text(content, encoding="utf-8")

    update_frontmatter_fields(f, {"status": "deprecated"})

    fm, body = load_markdown_file(f)
    assert fm["status"] == "deprecated"
    assert "status: body line" in body

  def test_raises_on_empty_updates(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    with pytest.raises(ValueError, match="must not be empty"):
      update_frontmatter_fields(f, {})

  def test_raises_on_nonexistent_file(self, tmp_path: Path) -> None:
    f = tmp_path / "missing.md"

    with pytest.raises(FileNotFoundError):
      update_frontmatter_fields(f, {"status": "active"})

  def test_insertion_preserves_dict_order(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    update_frontmatter_fields(f, {"field_a": "val_a", "field_b": "val_b"})

    content = f.read_text(encoding="utf-8")
    assert content.index("field_a:") < content.index("field_b:")

  def test_trailing_newline_preserved(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    update_frontmatter_fields(f, {"status": "deprecated"})

    content = f.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert not content.endswith("\n\n\n")

  def test_result_type(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    result = update_frontmatter_fields(f, {"status": "active"})

    assert isinstance(result, FieldUpdateResult)


# ---------------------------------------------------------------------------
# add_frontmatter_list_items
# ---------------------------------------------------------------------------


class TestAddFrontmatterListItems:
  """Tests for add_frontmatter_list_items()."""

  def test_adds_to_existing_list(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    result = add_frontmatter_list_items(f, "tags", ["oauth2"])

    assert result.added == ["oauth2"]
    assert result.final == ["auth", "oauth2", "security"]

    fm, _ = load_markdown_file(f)
    assert fm["tags"] == ["auth", "oauth2", "security"]

  def test_deduplicates(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    result = add_frontmatter_list_items(f, "tags", ["auth", "new"])

    assert result.added == ["new"]
    assert "auth" in result.final

  def test_creates_field_when_absent(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    result = add_frontmatter_list_items(f, "tags", ["new-tag"])

    assert result.added == ["new-tag"]
    assert result.final == ["new-tag"]

    fm, _ = load_markdown_file(f)
    assert fm["tags"] == ["new-tag"]

  def test_sorts_by_default(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    result = add_frontmatter_list_items(f, "tags", ["zebra", "alpha"])

    assert result.final == ["alpha", "zebra"]

  def test_no_sort_when_disabled(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    result = add_frontmatter_list_items(f, "tags", ["zebra", "alpha"], sort=False)

    assert result.final == ["zebra", "alpha"]

  def test_idempotent(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    result = add_frontmatter_list_items(f, "tags", ["auth"])

    assert result.added == []
    assert result.final == ["auth", "security"]

  def test_preserves_body(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    add_frontmatter_list_items(f, "tags", ["new"])

    _, body = load_markdown_file(f)
    assert "Body content." in body

  def test_bumps_updated(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    with patch("supekku.scripts.lib.core.frontmatter_writer.date") as mock_date:
      mock_date.today.return_value = date(2026, 6, 15)
      mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
      add_frontmatter_list_items(f, "tags", ["new"])

    fm, _ = load_markdown_file(f)
    assert fm["updated"] == "2026-06-15"

  def test_raises_on_empty_items(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    with pytest.raises(ValueError, match="must not be empty"):
      add_frontmatter_list_items(f, "tags", [])

  def test_raises_on_missing_file(self, tmp_path: Path) -> None:
    f = tmp_path / "missing.md"
    with pytest.raises(FileNotFoundError):
      add_frontmatter_list_items(f, "tags", ["x"])

  def test_result_type(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    result = add_frontmatter_list_items(f, "tags", ["new"])

    assert isinstance(result, ListUpdateResult)
    assert result.field == "tags"

  def test_flow_style_output(self, tmp_path: Path) -> None:
    """Short tag lists should emit as flow-style [a, b, c]."""
    f = tmp_path / "test.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    add_frontmatter_list_items(f, "tags", ["alpha", "beta"])

    content = f.read_text(encoding="utf-8")
    assert "tags: [alpha, beta]" in content


# ---------------------------------------------------------------------------
# remove_frontmatter_list_items
# ---------------------------------------------------------------------------


class TestRemoveFrontmatterListItems:
  """Tests for remove_frontmatter_list_items()."""

  def test_removes_existing_item(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    result = remove_frontmatter_list_items(f, "tags", ["auth"])

    assert result.removed == ["auth"]
    assert result.final == ["security"]

    fm, _ = load_markdown_file(f)
    assert fm["tags"] == ["security"]

  def test_removes_multiple_items(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    result = remove_frontmatter_list_items(f, "tags", ["auth", "security"])

    assert set(result.removed) == {"auth", "security"}
    assert result.final == []

  def test_ignores_nonexistent_items(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    result = remove_frontmatter_list_items(f, "tags", ["nonexistent"])

    assert result.removed == []
    assert result.final == ["auth", "security"]

  def test_empty_list_after_removal(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    remove_frontmatter_list_items(f, "tags", ["auth", "security"])

    fm, _ = load_markdown_file(f)
    assert fm["tags"] == []

  def test_absent_field_returns_empty(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    result = remove_frontmatter_list_items(f, "tags", ["anything"])

    assert result.removed == []
    assert result.final == []

  def test_preserves_body(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    remove_frontmatter_list_items(f, "tags", ["auth"])

    _, body = load_markdown_file(f)
    assert "Body content." in body

  def test_raises_on_empty_items(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    with pytest.raises(ValueError, match="must not be empty"):
      remove_frontmatter_list_items(f, "tags", [])

  def test_raises_on_missing_file(self, tmp_path: Path) -> None:
    f = tmp_path / "missing.md"
    with pytest.raises(FileNotFoundError):
      remove_frontmatter_list_items(f, "tags", ["x"])

  def test_result_type(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(TAGGED_FRONTMATTER, encoding="utf-8")

    result = remove_frontmatter_list_items(f, "tags", ["auth"])

    assert isinstance(result, ListUpdateResult)
    assert result.field == "tags"

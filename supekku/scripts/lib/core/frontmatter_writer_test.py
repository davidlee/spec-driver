"""Tests for frontmatter_writer — safe line-level frontmatter field updates."""

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from .frontmatter_writer import (
  FieldUpdateResult,
  update_frontmatter_fields,
  update_frontmatter_status,
)

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


class TestUpdateFrontmatterStatus:
  """Tests for update_frontmatter_status()."""

  def test_updates_status_field(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    result = update_frontmatter_status(f, "in-progress")

    assert result is True
    content = f.read_text(encoding="utf-8")
    assert "status: in-progress" in content
    assert "status: draft" not in content

  def test_updates_updated_date(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    with patch("supekku.scripts.lib.core.frontmatter_writer.date") as mock_date:
      mock_date.today.return_value = date(2026, 3, 8)
      mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
      update_frontmatter_status(f, "completed")

    content = f.read_text(encoding="utf-8")
    assert "updated: '2026-03-08'" in content
    assert "updated: '2026-01-01'" not in content

  def test_preserves_body_content(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter_status(f, "completed")

    content = f.read_text(encoding="utf-8")
    assert "# DE-001 – Example Delta" in content
    assert "Body content here." in content

  def test_preserves_other_frontmatter_fields(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter_status(f, "completed")

    content = f.read_text(encoding="utf-8")
    assert "id: DE-001" in content
    assert "name: Example Delta" in content
    assert "kind: delta" in content
    assert "created: '2026-01-01'" in content

  def test_returns_false_when_no_status_field(self, tmp_path: Path) -> None:
    f = tmp_path / "no-status.md"
    f.write_text("---\nid: X\nname: X\n---\n# No status\n", encoding="utf-8")

    result = update_frontmatter_status(f, "active")

    assert result is False
    # File should be unchanged
    assert f.read_text(encoding="utf-8") == "---\nid: X\nname: X\n---\n# No status\n"

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

  def test_writes_status_unquoted(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter_status(f, "in-progress")

    content = f.read_text(encoding="utf-8")
    assert "status: in-progress\n" in content
    assert "status: 'in-progress'" not in content
    assert 'status: "in-progress"' not in content

  def test_only_modifies_frontmatter_status(self, tmp_path: Path) -> None:
    """Status-like lines in body content should not be touched."""
    content_with_body_status = """\
---
id: DE-001
status: draft
updated: '2026-01-01'
---

# Title

status: this should not change
"""
    f = tmp_path / "DE-001.md"
    f.write_text(content_with_body_status, encoding="utf-8")

    update_frontmatter_status(f, "active")

    content = f.read_text(encoding="utf-8")
    assert "status: active\n" in content
    assert "status: this should not change" in content

  def test_trailing_newline_preserved(self, tmp_path: Path) -> None:
    f = tmp_path / "DE-001.md"
    f.write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter_status(f, "completed")

    content = f.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert not content.endswith("\n\n")


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


class TestUpdateFrontmatterFields:
  """Tests for update_frontmatter_fields()."""

  def test_replaces_existing_field(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    result = update_frontmatter_fields(f, {"status": "deprecated"})

    content = f.read_text(encoding="utf-8")
    assert "status: deprecated" in content
    assert "status: active" not in content
    assert "status" in result.updated
    assert not result.inserted

  def test_replaces_multiple_existing_fields(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    result = update_frontmatter_fields(f, {
      "verified": "'2026-03-09'",
      "updated": "'2026-03-09'",
    })

    content = f.read_text(encoding="utf-8")
    assert "verified: '2026-03-09'" in content
    assert "updated: '2026-03-09'" in content
    assert result.updated == {"verified", "updated"}

  def test_inserts_missing_field(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    sha = "a" * 40
    result = update_frontmatter_fields(f, {"verified_sha": sha})

    content = f.read_text(encoding="utf-8")
    assert f"verified_sha: {sha}" in content
    assert "verified_sha" in result.inserted
    assert not result.updated

  def test_mixed_replace_and_insert(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    sha = "b" * 40
    result = update_frontmatter_fields(f, {
      "verified": "'2026-03-09'",
      "verified_sha": sha,
      "updated": "'2026-03-09'",
    })

    content = f.read_text(encoding="utf-8")
    assert "verified: '2026-03-09'" in content
    assert f"verified_sha: {sha}" in content
    assert "updated: '2026-03-09'" in content
    assert result.updated == {"verified", "updated"}
    assert result.inserted == {"verified_sha"}

  def test_inserted_field_appears_before_closing_marker(
    self, tmp_path: Path,
  ) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    update_frontmatter_fields(f, {"verified_sha": "c" * 40})

    content = f.read_text(encoding="utf-8")
    lines = content.splitlines()
    # Find the closing --- and the verified_sha line
    sha_idx = next(
      i for i, line in enumerate(lines) if "verified_sha:" in line
    )
    # The closing --- after frontmatter
    closing_idx = next(
      i for i, line in enumerate(lines) if line.strip() == "---" and i > 0
    )
    assert sha_idx < closing_idx

  def test_preserves_body_content(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    update_frontmatter_fields(f, {"status": "deprecated"})

    content = f.read_text(encoding="utf-8")
    assert "# Test Memory" in content
    assert "Body content here." in content

  def test_preserves_unmodified_fields(self, tmp_path: Path) -> None:
    f = tmp_path / "mem.fact.test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    update_frontmatter_fields(f, {"status": "deprecated"})

    content = f.read_text(encoding="utf-8")
    assert "id: mem.fact.test" in content
    assert "name: Test Memory" in content
    assert "kind: memory" in content
    assert "created: '2026-01-01'" in content

  def test_does_not_modify_body_lines_matching_field_name(
    self, tmp_path: Path,
  ) -> None:
    content_with_body_field = """\
---
id: X
status: active
updated: '2026-01-01'
---

# Title

status: this should not change
"""
    f = tmp_path / "test.md"
    f.write_text(content_with_body_field, encoding="utf-8")

    update_frontmatter_fields(f, {"status": "deprecated"})

    content = f.read_text(encoding="utf-8")
    assert "status: deprecated\n" in content
    assert "status: this should not change" in content

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

    update_frontmatter_fields(f, {
      "field_a": "val_a",
      "field_b": "val_b",
    })

    content = f.read_text(encoding="utf-8")
    idx_a = content.index("field_a:")
    idx_b = content.index("field_b:")
    assert idx_a < idx_b

  def test_trailing_newline_preserved(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    update_frontmatter_fields(f, {"status": "deprecated"})

    content = f.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert not content.endswith("\n\n")

  def test_result_type(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text(MEMORY_FRONTMATTER, encoding="utf-8")

    result = update_frontmatter_fields(f, {"status": "active"})

    assert isinstance(result, FieldUpdateResult)

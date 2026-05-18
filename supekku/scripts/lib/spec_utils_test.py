"""Tests for spec_utils module."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

import pytest
import yaml

from supekku.scripts.lib.core.frontmatter_schema import FrontmatterValidationError
from supekku.scripts.lib.core.spec_utils import (
  MarkdownLoadError,
  append_unique,
  dump_markdown_file_create,
  dump_markdown_file_update,
  ensure_list_entry,
  load_markdown_file,
  load_validated_markdown_file,
  validate_frontmatter,
)


class SpecUtilsTestCase(unittest.TestCase):
  """Test cases for spec_utils module functionality."""

  def test_load_markdown_file_parses_frontmatter_and_body(self) -> None:
    """Test loading markdown file parses YAML frontmatter and body."""
    content = textwrap.dedent(
      """
            ---
            id: SPEC-001
            name: Example Spec
            kind: spec
            ---

            Body line
            ---
            Extra body line
            """,
    ).lstrip("\n")

    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "spec.md"
      path.write_text(content, encoding="utf-8")

      frontmatter, body = load_markdown_file(path)

    assert frontmatter == {"id": "SPEC-001", "name": "Example Spec", "kind": "spec"}
    assert body == "Body line\n---\nExtra body line\n"

  def test_load_markdown_file_raises_friendly_error_on_malformed_yaml(self) -> None:
    """VT-DR135-001: malformed YAML raises MarkdownLoadError with path + line/col."""
    # Stray colon mid-value reproduces the ScannerError from ISSUE-054.
    content = textwrap.dedent(
      """
            ---
            id: SPEC-001
            name: bad value: with: stray: colons
            kind: spec
            ---

            Body
            """,
    ).lstrip("\n")

    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "spec.md"
      path.write_text(content, encoding="utf-8")

      with pytest.raises(MarkdownLoadError) as excinfo:
        load_markdown_file(path)

    msg = str(excinfo.value)
    assert "invalid YAML frontmatter" in msg
    assert str(path) in msg
    assert "line " in msg
    assert "column " in msg
    assert isinstance(excinfo.value.__cause__, yaml.YAMLError)
    # MarkdownLoadError must remain a ValueError so existing call-site
    # `except (ValueError, OSError)` clauses keep working.
    assert isinstance(excinfo.value, ValueError)

  def test_dump_markdown_file_round_trip(self) -> None:
    """Test dump and reload round trip preserves content."""
    frontmatter = {"id": "SPEC-010", "name": "Round Trip", "kind": "spec"}
    body = "Round trip body\n"

    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "spec.md"
      dump_markdown_file_update(path, frontmatter, body)

      reloaded_frontmatter, reloaded_body = load_markdown_file(path)

    assert reloaded_frontmatter == frontmatter
    assert reloaded_body == body

  def test_ensure_list_entry_returns_existing_list(self) -> None:
    """Test ensure_list_entry returns existing list from dict."""
    data = {"owners": ["alice"]}
    result = ensure_list_entry(data, "owners")
    assert result is data["owners"]

    result.append("bob")
    assert data["owners"] == ["alice", "bob"]

  def test_ensure_list_entry_raises_for_non_list(self) -> None:
    """Test ensure_list_entry raises TypeError for non-list values."""
    data = {"owners": "alice"}
    with pytest.raises(TypeError):
      ensure_list_entry(data, "owners")

  def test_append_unique_appends_when_missing(self) -> None:
    """Test append_unique adds item when not present."""
    values = ["alice"]
    modified = append_unique(values, "bob")
    assert modified
    assert values == ["alice", "bob"]

  def test_append_unique_skips_existing_item(self) -> None:
    """Test append_unique skips item that already exists."""
    values = ["alice", "bob"]
    modified = append_unique(values, "alice")
    assert not modified
    assert values == ["alice", "bob"]

  def test_validate_frontmatter_success(self) -> None:
    """Test frontmatter validation succeeds with valid data."""
    frontmatter = {
      "id": "SPEC-200",
      "name": "Validated Spec",
      "slug": "validated-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2024-06-01",
      "updated": "2024-07-01",
      "owners": ["alice"],
      "relations": [
        {
          "type": "implements",
          "target": "FR-100",
          "annotation": "covers primary requirement",
        },
      ],
    }

    result = validate_frontmatter(frontmatter)

    assert result.id == "SPEC-200"
    assert result.created.isoformat() == "2024-06-01"
    assert len(result.relations) == 1
    relation = result.relations[0]
    assert relation.type == "implements"
    assert relation.target == "FR-100"
    assert result.data["relations"][0]["annotation"] == "covers primary requirement"
    assert result.data is not frontmatter
    assert frontmatter["owners"] == ["alice"]

  def test_validate_frontmatter_missing_required_field(self) -> None:
    """Test validation fails when required field is missing."""
    frontmatter = {
      "name": "Missing Id",
      "slug": "missing-id",
      "kind": "spec",
      "status": "draft",
      "created": "2024-06-01",
      "updated": "2024-07-01",
    }

    with pytest.raises(FrontmatterValidationError):
      validate_frontmatter(frontmatter)

  def test_validate_frontmatter_invalid_relations(self) -> None:
    """Test validation fails for malformed relations."""
    frontmatter = {
      "id": "SPEC-201",
      "name": "Bad Relations",
      "slug": "bad-relations",
      "kind": "spec",
      "status": "draft",
      "created": "2024-06-01",
      "updated": "2024-07-01",
      "relations": ["not-a-mapping"],
    }

    with pytest.raises(FrontmatterValidationError):
      validate_frontmatter(frontmatter)

  def test_load_validated_markdown_file_round_trip(self) -> None:
    """Test loading and dumping with validation preserves data."""
    frontmatter = {
      "id": "SPEC-202",
      "name": "Load Validated",
      "slug": "load-validated",
      "kind": "spec",
      "status": "draft",
      "created": "2024-06-01",
      "updated": "2024-07-01",
    }
    body = "Some content\n"

    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "spec.md"
      dump_markdown_file_update(path, frontmatter, body)

      result, loaded_body = load_validated_markdown_file(path)

    assert result.slug == "load-validated"
    assert loaded_body == body


class DumpCreateUpdateSplitTest(unittest.TestCase):
  """IP-137-P02 task 2.5 — `_create` / `_update` semantics."""

  def test_create_renders_enum_comment_hints(self) -> None:
    fm = {
      "id": "DE-001",
      "name": "split test",
      "slug": "split-test",
      "kind": "delta",
      "status": "draft",
      "created": "2026-01-01",
      "updated": "2026-01-01",
    }
    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "DE-001.md"
      dump_markdown_file_create(path, fm, "# body\n", kind="delta")
      text = path.read_text(encoding="utf-8")
    assert "status: draft  # one of:" in text
    assert "# body" in text

  def test_create_refuses_existing_path(self) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "DE-001.md"
      path.write_text("existing", encoding="utf-8")
      with pytest.raises(FileExistsError):
        dump_markdown_file_create(path, {"id": "DE-001"}, "body\n", kind="delta")

  def test_update_preserves_existing_trailing_comments(self) -> None:
    initial = (
      "---\n"
      "id: DE-001\n"
      "status: draft  # one of: draft | completed\n"
      "kind: delta\n"
      "---\n\nbody\n"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "DE-001.md"
      path.write_text(initial, encoding="utf-8")
      dump_markdown_file_update(
        path,
        {"id": "DE-001", "status": "in-progress", "kind": "delta"},
        "body\n",
      )
      text = path.read_text(encoding="utf-8")
    assert "status: in-progress  # one of: draft | completed" in text

  def test_update_no_comments_when_none_present(self) -> None:
    initial = "---\nid: DE-001\nkind: delta\n---\n\nbody\n"
    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "DE-001.md"
      path.write_text(initial, encoding="utf-8")
      dump_markdown_file_update(path, {"id": "DE-001", "kind": "delta"}, "body\n")
      text = path.read_text(encoding="utf-8")
    assert "#" not in text

  def test_update_idempotent_round_trip(self) -> None:
    fm = {"id": "DE-001", "kind": "delta", "status": "draft"}
    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "DE-001.md"
      dump_markdown_file_create(path, fm, "body\n", kind="delta")
      first = path.read_text(encoding="utf-8")
      dump_markdown_file_update(path, fm, "body\n")
      second = path.read_text(encoding="utf-8")
    assert first == second


if __name__ == "__main__":
  unittest.main()

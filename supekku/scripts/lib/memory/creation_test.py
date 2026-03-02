"""Tests for memory creation logic."""

from __future__ import annotations

from pathlib import Path

import frontmatter
import pytest
import yaml

from supekku.scripts.lib.memory.creation import (
  MemoryAlreadyExistsError,
  MemoryCreationOptions,
  MemoryCreationResult,
  build_memory_frontmatter,
  create_memory,
)
from supekku.scripts.lib.memory.registry import MemoryRegistry


@pytest.fixture()
def memory_dir(tmp_path: Path) -> Path:
  """Create a temporary memory directory with sample files."""
  mem_dir = tmp_path / "memory"
  mem_dir.mkdir()
  return mem_dir


@pytest.fixture()
def registry(tmp_path: Path, memory_dir: Path) -> MemoryRegistry:
  """Create a MemoryRegistry rooted at tmp_path."""
  return MemoryRegistry(root=tmp_path, directory=memory_dir)


def _write_memory_file(
  directory: Path,
  mem_id: str,
  name: str = "test",
  memory_type: str = "fact",
) -> None:
  """Write a minimal valid memory file."""
  fm = {
    "id": mem_id,
    "name": name,
    "kind": "memory",
    "status": "active",
    "memory_type": memory_type,
  }
  content = f"---\n{yaml.safe_dump(fm, sort_keys=False)}---\n\n# {name}\n"
  (directory / f"{mem_id}.md").write_text(content, encoding="utf-8")


# --- build_memory_frontmatter ---


class TestBuildMemoryFrontmatter:
  """Tests for build_memory_frontmatter."""

  def test_minimal(self) -> None:
    opts = MemoryCreationOptions(
      memory_id="mem.fact.auth",
      name="Test Memory",
      memory_type="fact",
    )
    fm = build_memory_frontmatter("mem.fact.auth", opts)
    assert fm["id"] == "mem.fact.auth"
    assert fm["name"] == "Test Memory"
    assert fm["kind"] == "memory"
    assert fm["status"] == "active"
    assert fm["memory_type"] == "fact"
    assert fm["tags"] == []
    assert fm["summary"] == ""
    assert "created" in fm
    assert "updated" in fm

  def test_with_all_options(self) -> None:
    opts = MemoryCreationOptions(
      memory_id="mem.pattern.arch.registry",
      name="Architecture Pattern",
      memory_type="pattern",
      status="review",
      tags=["arch", "python"],
      summary="Key architecture pattern for registry",
    )
    fm = build_memory_frontmatter("mem.pattern.arch.registry", opts)
    assert fm["id"] == "mem.pattern.arch.registry"
    assert fm["status"] == "review"
    assert fm["memory_type"] == "pattern"
    assert fm["tags"] == ["arch", "python"]
    assert fm["summary"] == "Key architecture pattern for registry"

  def test_dates_are_iso_strings(self) -> None:
    opts = MemoryCreationOptions(
      memory_id="mem.fact.test",
      name="Test",
      memory_type="fact",
    )
    fm = build_memory_frontmatter("mem.fact.test", opts)
    assert isinstance(fm["created"], str)
    assert isinstance(fm["updated"], str)


# --- create_memory ---


class TestCreateMemory:
  """Tests for create_memory with semantic IDs."""

  def test_creates_file(
    self,
    registry: MemoryRegistry,
    memory_dir: Path,
  ) -> None:
    opts = MemoryCreationOptions(
      memory_id="mem.fact.auth",
      name="Test Memory",
      memory_type="fact",
    )
    result = create_memory(registry, opts)

    assert isinstance(result, MemoryCreationResult)
    assert result.memory_id == "mem.fact.auth"
    assert result.path.exists()
    assert result.filename == "mem.fact.auth.md"

  def test_file_has_valid_frontmatter(
    self,
    registry: MemoryRegistry,
  ) -> None:
    opts = MemoryCreationOptions(
      memory_id="mem.concept.important",
      name="Important Fact",
      memory_type="concept",
      tags=["core"],
      summary="Something important",
    )
    result = create_memory(registry, opts)
    post = frontmatter.load(str(result.path))

    assert post["id"] == "mem.concept.important"
    assert post["name"] == "Important Fact"
    assert post["memory_type"] == "concept"
    assert post["kind"] == "memory"
    assert post["tags"] == ["core"]
    assert post["summary"] == "Something important"

  def test_file_has_body(self, registry: MemoryRegistry) -> None:
    opts = MemoryCreationOptions(
      memory_id="mem.fact.body-test",
      name="Test Memory",
      memory_type="fact",
    )
    result = create_memory(registry, opts)
    text = result.path.read_text(encoding="utf-8")

    assert "# Test Memory" in text
    assert "## Summary" in text
    assert "## Context" in text

  def test_raises_on_duplicate_id(
    self,
    registry: MemoryRegistry,
    memory_dir: Path,
  ) -> None:
    _write_memory_file(memory_dir, "mem.fact.existing")
    opts = MemoryCreationOptions(
      memory_id="mem.fact.existing",
      name="Duplicate",
      memory_type="fact",
    )
    with pytest.raises(MemoryAlreadyExistsError):
      create_memory(registry, opts)

  def test_raises_on_invalid_id(self, registry: MemoryRegistry) -> None:
    opts = MemoryCreationOptions(
      memory_id="bad_id",
      name="Bad",
      memory_type="fact",
    )
    with pytest.raises(ValueError, match="invalid.*segment"):
      create_memory(registry, opts)

  def test_normalizes_id_to_lowercase(
    self,
    registry: MemoryRegistry,
  ) -> None:
    opts = MemoryCreationOptions(
      memory_id="mem.Fact.Auth",
      name="Upper",
      memory_type="fact",
    )
    result = create_memory(registry, opts)
    assert result.memory_id == "mem.fact.auth"

  def test_custom_status(self, registry: MemoryRegistry) -> None:
    opts = MemoryCreationOptions(
      memory_id="mem.thread.draft-test",
      name="Draft Memory",
      memory_type="thread",
      status="draft",
    )
    result = create_memory(registry, opts)
    post = frontmatter.load(str(result.path))
    assert post["status"] == "draft"

  def test_creates_directory_if_missing(self, tmp_path: Path) -> None:
    mem_dir = tmp_path / "memory"
    reg = MemoryRegistry(root=tmp_path, directory=mem_dir)
    opts = MemoryCreationOptions(
      memory_id="mem.fact.new",
      name="New Mem",
      memory_type="fact",
    )
    result = create_memory(reg, opts)
    assert result.path.exists()
    assert mem_dir.exists()

  def test_warns_on_type_mismatch(
    self,
    registry: MemoryRegistry,
  ) -> None:
    opts = MemoryCreationOptions(
      memory_id="mem.pattern.auth",
      name="Auth Thing",
      memory_type="fact",
    )
    with pytest.warns(UserWarning, match="type segment.*differs"):
      result = create_memory(registry, opts)
    assert result.warnings
    assert "differs" in result.warnings[0]

  def test_no_warning_when_types_match(
    self,
    registry: MemoryRegistry,
  ) -> None:
    opts = MemoryCreationOptions(
      memory_id="mem.fact.auth",
      name="Auth Fact",
      memory_type="fact",
    )
    result = create_memory(registry, opts)
    assert not result.warnings

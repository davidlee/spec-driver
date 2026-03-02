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
  generate_next_memory_id,
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


def _write_memory_file(directory: Path, mem_id: str, name: str = "test") -> None:
  """Write a minimal valid memory file."""
  fm = {
    "id": mem_id,
    "name": name,
    "kind": "memory",
    "status": "active",
    "memory_type": "fact",
  }
  content = f"---\n{yaml.safe_dump(fm, sort_keys=False)}---\n\n# {name}\n"
  slug = name.lower().replace(" ", "_")
  (directory / f"{mem_id}-{slug}.md").write_text(content, encoding="utf-8")


# --- generate_next_memory_id ---


class TestGenerateNextMemoryId:
  """Tests for generate_next_memory_id."""

  def test_empty_registry(self, registry: MemoryRegistry) -> None:
    assert generate_next_memory_id(registry) == "MEM-001"

  def test_with_existing_records(
    self, registry: MemoryRegistry, memory_dir: Path,
  ) -> None:
    _write_memory_file(memory_dir, "MEM-001")
    _write_memory_file(memory_dir, "MEM-005", "other")
    assert generate_next_memory_id(registry) == "MEM-006"

  def test_with_single_record(
    self, registry: MemoryRegistry, memory_dir: Path,
  ) -> None:
    _write_memory_file(memory_dir, "MEM-003")
    assert generate_next_memory_id(registry) == "MEM-004"


# --- build_memory_frontmatter ---


class TestBuildMemoryFrontmatter:
  """Tests for build_memory_frontmatter."""

  def test_minimal(self) -> None:
    opts = MemoryCreationOptions(name="Test Memory", memory_type="fact")
    fm = build_memory_frontmatter("MEM-001", opts)
    assert fm["id"] == "MEM-001"
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
      name="Architecture Pattern",
      memory_type="pattern",
      status="review",
      tags=["arch", "python"],
      summary="Key architecture pattern for registry",
    )
    fm = build_memory_frontmatter("MEM-042", opts)
    assert fm["id"] == "MEM-042"
    assert fm["status"] == "review"
    assert fm["memory_type"] == "pattern"
    assert fm["tags"] == ["arch", "python"]
    assert fm["summary"] == "Key architecture pattern for registry"

  def test_dates_are_iso_strings(self) -> None:
    opts = MemoryCreationOptions(name="Test", memory_type="fact")
    fm = build_memory_frontmatter("MEM-001", opts)
    # Should be ISO date strings, not date objects
    assert isinstance(fm["created"], str)
    assert isinstance(fm["updated"], str)


# --- create_memory ---


class TestCreateMemory:
  """Tests for create_memory."""

  def test_creates_file(
    self, registry: MemoryRegistry, memory_dir: Path,
  ) -> None:
    opts = MemoryCreationOptions(name="Test Memory", memory_type="fact")
    result = create_memory(registry, opts)

    assert isinstance(result, MemoryCreationResult)
    assert result.memory_id == "MEM-001"
    assert result.path.exists()
    assert result.filename == "MEM-001-test_memory.md"

  def test_file_has_valid_frontmatter(
    self, registry: MemoryRegistry, memory_dir: Path,
  ) -> None:
    opts = MemoryCreationOptions(
      name="Important Fact",
      memory_type="concept",
      tags=["core"],
      summary="Something important",
    )
    result = create_memory(registry, opts)
    post = frontmatter.load(str(result.path))

    assert post["id"] == "MEM-001"
    assert post["name"] == "Important Fact"
    assert post["memory_type"] == "concept"
    assert post["kind"] == "memory"
    assert post["tags"] == ["core"]
    assert post["summary"] == "Something important"

  def test_file_has_body(
    self, registry: MemoryRegistry, memory_dir: Path,
  ) -> None:
    opts = MemoryCreationOptions(name="Test Memory", memory_type="fact")
    result = create_memory(registry, opts)
    text = result.path.read_text(encoding="utf-8")

    assert "# Test Memory" in text
    assert "## Summary" in text
    assert "## Context" in text

  def test_increments_id(
    self, registry: MemoryRegistry, memory_dir: Path,
  ) -> None:
    _write_memory_file(memory_dir, "MEM-003")
    opts = MemoryCreationOptions(name="New Memory", memory_type="fact")
    result = create_memory(registry, opts)
    assert result.memory_id == "MEM-004"

  def test_raises_on_existing_file(
    self, registry: MemoryRegistry, memory_dir: Path,
  ) -> None:
    # Create a file that would collide
    (memory_dir / "MEM-001-test_memory.md").write_text("existing", encoding="utf-8")
    opts = MemoryCreationOptions(name="Test Memory", memory_type="fact")
    with pytest.raises(MemoryAlreadyExistsError):
      create_memory(registry, opts)

  def test_custom_status(
    self, registry: MemoryRegistry, memory_dir: Path,
  ) -> None:
    opts = MemoryCreationOptions(
      name="Draft Memory", memory_type="thread", status="draft",
    )
    result = create_memory(registry, opts)
    post = frontmatter.load(str(result.path))
    assert post["status"] == "draft"

  def test_creates_directory_if_missing(self, tmp_path: Path) -> None:
    mem_dir = tmp_path / "memory"
    reg = MemoryRegistry(root=tmp_path, directory=mem_dir)
    opts = MemoryCreationOptions(name="New Mem", memory_type="fact")
    result = create_memory(reg, opts)
    assert result.path.exists()
    assert mem_dir.exists()

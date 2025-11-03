"""Tests for standard registry module."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .registry import StandardRecord, StandardRegistry


class TestStandardRecord(unittest.TestCase):
  """Tests for StandardRecord dataclass."""

  def test_to_dict_minimal(self) -> None:
    """Test serialization with minimal fields."""
    record = StandardRecord(id="STD-001", title="Test Standard", status="default")

    result = record.to_dict(Path("/tmp"))

    assert result["id"] == "STD-001"
    assert result["title"] == "Test Standard"
    assert result["status"] == "default"
    assert result["summary"] == ""

  def test_default_status(self) -> None:
    """Test that 'default' status is supported."""
    record = StandardRecord(
      id="STD-001",
      title="Google Go Style Guide",
      status="default",
      summary="Recommended unless justified otherwise",
    )

    result = record.to_dict(Path("/tmp"))

    assert result["status"] == "default"
    assert result["summary"] == "Recommended unless justified otherwise"


class TestStandardRegistry(unittest.TestCase):
  """Tests for StandardRegistry class."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.test_dir = tempfile.mkdtemp()
    self.root = Path(self.test_dir)

    self.standards_dir = self.root / "specify" / "standards"
    self.standards_dir.mkdir(parents=True)

    self.registry_dir = self.root / "specify" / ".registry"
    self.registry_dir.mkdir(parents=True)

  def test_collect_single_standard(self) -> None:
    """Test collecting a single standard."""
    standard_content = """---
id: STD-001
title: 'STD-001: Google Go Style Guide'
status: default
created: '2024-01-01'
summary: Use Google Go style guide unless justified otherwise
tags:
  - style
  - go
---

# STD-001: Google Go Style Guide

## Statement
Follow Google Go style guide conventions.
"""
    standard_file = self.standards_dir / "STD-001-google-go-style-guide.md"
    standard_file.write_text(standard_content, encoding="utf-8")

    registry = StandardRegistry(root=self.root)
    standards = registry.collect()

    assert len(standards) == 1
    assert "STD-001" in standards

    standard = standards["STD-001"]
    assert standard.id == "STD-001"
    assert standard.status == "default"
    assert standard.tags == ["style", "go"]

  def test_iter_filtered_by_default_status(self) -> None:
    """Test filtering standards by 'default' status."""
    # Create standards with different statuses
    for i, status in enumerate(["draft", "default", "required"], 1):
      content = f"""---
id: STD-{i:03d}
title: 'STD-{i:03d}: Standard {i}'
status: {status}
---

# STD-{i:03d}
"""
      (self.standards_dir / f"STD-{i:03d}.md").write_text(content, encoding="utf-8")

    registry = StandardRegistry(root=self.root)
    default_standards = list(registry.iter(status="default"))

    assert len(default_standards) == 1
    assert default_standards[0].status == "default"


if __name__ == "__main__":
  unittest.main()

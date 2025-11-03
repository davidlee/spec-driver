"""Tests for standard creation module."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from .creation import (
  StandardCreationOptions,
  create_standard,
  generate_next_standard_id,
)
from .registry import StandardRegistry


class TestGenerateNextStandardId(unittest.TestCase):
  """Tests for generate_next_standard_id function."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.test_dir = tempfile.mkdtemp()
    self.root = Path(self.test_dir)
    self.standards_dir = self.root / "specify" / "standards"
    self.standards_dir.mkdir(parents=True)

  def test_first_standard(self) -> None:
    """Test ID generation for first standard."""
    registry = StandardRegistry(root=self.root)
    standard_id = generate_next_standard_id(registry)

    assert standard_id == "STD-001"


class TestCreateStandard(unittest.TestCase):
  """Tests for create_standard function."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.test_dir = tempfile.mkdtemp()
    self.root = Path(self.test_dir)

    self.standards_dir = self.root / "specify" / "standards"
    self.standards_dir.mkdir(parents=True)

    # Create .spec-driver/templates directory and copy standard template
    templates_dir = self.root / ".spec-driver" / "templates"
    templates_dir.mkdir(parents=True)

    # Copy the actual standard template from the package
    package_templates = Path(__file__).parent.parent.parent.parent / "templates"
    if (package_templates / "standard-template.md").exists():
      shutil.copy(
        package_templates / "standard-template.md",
        templates_dir / "standard-template.md",
      )

  def test_create_standard_with_default_status(self) -> None:
    """Test creating a standard with 'default' status."""
    registry = StandardRegistry(root=self.root)
    options = StandardCreationOptions(
      title="Google Go Style Guide",
      status="default",
    )

    result = create_standard(registry, options, sync_registry=False)

    assert result.standard_id == "STD-001"
    content = result.path.read_text(encoding="utf-8")
    assert "status: default" in content


if __name__ == "__main__":
  unittest.main()

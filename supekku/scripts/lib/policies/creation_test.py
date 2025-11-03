"""Tests for policy creation module."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .creation import (
  PolicyAlreadyExistsError,
  PolicyCreationOptions,
  build_policy_frontmatter,
  create_policy,
  create_title_slug,
  generate_next_policy_id,
)
from .registry import PolicyRegistry


class TestTitleSlug(unittest.TestCase):
  """Tests for create_title_slug function."""

  def test_simple_title(self) -> None:
    """Test slug creation from simple title."""
    assert create_title_slug("Code must have tests") == "code-must-have-tests"

  def test_with_special_chars(self) -> None:
    """Test slug creation with special characters."""
    assert create_title_slug("Don't store PII!") == "don-t-store-pii"

  def test_multiple_spaces(self) -> None:
    """Test slug creation with multiple spaces."""
    assert create_title_slug("Multiple   spaces   here") == "multiple-spaces-here"

  def test_leading_trailing_hyphens(self) -> None:
    """Test slug strips leading/trailing hyphens."""
    assert create_title_slug("--test--") == "test"


class TestGenerateNextPolicyId(unittest.TestCase):
  """Tests for generate_next_policy_id function."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.test_dir = tempfile.mkdtemp()
    self.root = Path(self.test_dir)
    self.policies_dir = self.root / "specify" / "policies"
    self.policies_dir.mkdir(parents=True)

  def test_first_policy(self) -> None:
    """Test ID generation for first policy."""
    registry = PolicyRegistry(root=self.root)
    policy_id = generate_next_policy_id(registry)

    assert policy_id == "POL-001"

  def test_incremental_ids(self) -> None:
    """Test ID generation increments correctly."""
    # Create existing policy
    policy_content = """---
id: POL-001
title: 'POL-001: Test'
status: draft
---

# POL-001
"""
    (self.policies_dir / "POL-001-test.md").write_text(
      policy_content,
      encoding="utf-8",
    )

    registry = PolicyRegistry(root=self.root)
    policy_id = generate_next_policy_id(registry)

    assert policy_id == "POL-002"


class TestBuildPolicyFrontmatter(unittest.TestCase):
  """Tests for build_policy_frontmatter function."""

  def test_minimal_frontmatter(self) -> None:
    """Test frontmatter with minimal fields."""
    fm = build_policy_frontmatter("POL-001", "Test Policy", "draft")

    assert fm["id"] == "POL-001"
    assert fm["title"] == "POL-001: Test Policy"
    assert fm["status"] == "draft"
    assert "created" in fm
    assert "updated" in fm
    assert fm["owners"] == []
    assert fm["supersedes"] == []

  def test_with_author(self) -> None:
    """Test frontmatter with author."""
    fm = build_policy_frontmatter(
      "POL-001",
      "Test Policy",
      "required",
      author="Jane Doe",
    )

    assert fm["owners"] == ["Jane Doe"]


class TestCreatePolicy(unittest.TestCase):
  """Tests for create_policy function."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.test_dir = tempfile.mkdtemp()
    self.root = Path(self.test_dir)

    # Create directory structure
    self.policies_dir = self.root / "specify" / "policies"
    self.policies_dir.mkdir(parents=True)

    # Create templates directory
    templates_dir = self.root / "supekku" / "templates"
    templates_dir.mkdir(parents=True)

    # Create a simple template
    template_content = """# {{ policy_id }}: {{ title }}

## Statement

Policy statement goes here.
"""
    (templates_dir / "policy-template.md").write_text(
      template_content,
      encoding="utf-8",
    )

  def test_create_first_policy(self) -> None:
    """Test creating the first policy."""
    registry = PolicyRegistry(root=self.root)
    options = PolicyCreationOptions(title="Code must have tests", status="required")

    result = create_policy(registry, options, sync_registry=False)

    assert result.policy_id == "POL-001"
    assert result.filename == "POL-001-code-must-have-tests.md"
    assert result.path.exists()

    # Verify file content
    content = result.path.read_text(encoding="utf-8")
    assert "id: POL-001" in content
    assert "title: 'POL-001: Code must have tests'" in content
    assert "status: required" in content
    assert "# POL-001: Code must have tests" in content

  def test_create_duplicate_raises_error(self) -> None:
    """Test that creating duplicate policy raises error."""
    registry = PolicyRegistry(root=self.root)
    options = PolicyCreationOptions(title="Test Policy", status="draft")

    # Create first policy
    create_policy(registry, options, sync_registry=False)

    # Try to create duplicate (same ID will be generated)
    with self.assertRaises(PolicyAlreadyExistsError):
      create_policy(registry, options, sync_registry=False)


if __name__ == "__main__":
  unittest.main()

"""Tests for create_spec module."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import pytest

from supekku.scripts.lib.core.paths import get_templates_dir
from supekku.scripts.lib.core.spec_utils import load_markdown_file
from supekku.scripts.lib.specs.creation import (
  CreateSpecOptions,
  RepositoryRootNotFoundError,
  create_spec,
)


class CreateSpecTest(unittest.TestCase):
  """Test cases for create_spec functionality."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _setup_repo(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    templates = get_templates_dir(root)
    templates.mkdir(parents=True)
    (root / "specify" / "tech").mkdir(parents=True)
    (root / "specify" / "product").mkdir(parents=True)
    (templates / "spec.md").write_text(
      """# {{ spec_id }} – {{ name }}\n\nSpec body content\n""",
      encoding="utf-8",
    )
    (templates / "tech-spec.testing.md").write_text(
      """# {{ spec_id }} Testing Guide\n\nTest body content\n""",
      encoding="utf-8",
    )
    os.chdir(root)
    return root

  def test_create_tech_spec_generates_spec_and_testing_doc(self) -> None:
    """Test creating a tech spec with testing documentation."""
    self._setup_repo()

    result = create_spec(
      "Search Service",
      CreateSpecOptions(spec_type="tech", include_testing=True),
    )

    assert result.spec_id == "SPEC-001"
    assert result.test_path

    frontmatter, body = load_markdown_file(result.spec_path)
    assert frontmatter["name"] == "Search Service"
    assert frontmatter["status"] == "draft"
    assert frontmatter["kind"] == "spec"
    assert frontmatter["slug"].startswith("search")
    assert "# SPEC-001 – Search Service" in body
    assert "Spec body content" in body

    test_frontmatter, test_body = load_markdown_file(result.test_path)
    assert test_frontmatter["id"].endswith(".TESTS")
    assert test_frontmatter["kind"] == "guidance"
    assert "# SPEC-001 Testing Guide" in test_body
    assert "Test body content" in test_body

  def test_create_product_spec_without_testing_doc(self) -> None:
    """Test creating a product spec without testing documentation."""
    self._setup_repo()

    result = create_spec(
      "Sync Experience",
      CreateSpecOptions(spec_type="product", include_testing=False),
    )

    assert result.spec_id == "PROD-001"
    assert result.test_path is None

  def test_missing_templates_use_fallback(self) -> None:
    """Test that missing local templates fall back to package templates."""
    root = self._setup_repo()
    local_template = get_templates_dir(root) / "spec.md"
    local_template.unlink()

    # Should succeed using package template fallback
    result = create_spec("Fallback Template Test", CreateSpecOptions())
    assert result.spec_id == "SPEC-001"
    assert result.spec_path.exists()

  def test_repository_root_not_found(self) -> None:
    """Test that operations outside a repository raise RepositoryRootNotFoundError."""
    # Create temp dir that's NOT under /tmp to avoid finding stray .spec-driver dirs
    tmpdir = tempfile.TemporaryDirectory(dir=Path.home())  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    test_dir = Path(tmpdir.name) / "nested" / "deep"
    test_dir.mkdir(parents=True)
    os.chdir(test_dir)

    with pytest.raises(RepositoryRootNotFoundError):
      create_spec("No Repo", CreateSpecOptions())

  def test_json_output_matches_structure(self) -> None:
    """Test that JSON output from create_spec has expected structure."""
    self._setup_repo()
    result = create_spec("Example", CreateSpecOptions())
    payload = json.loads(result.to_json())
    assert payload["id"] == "SPEC-001"
    assert "spec_file" in payload


if __name__ == "__main__":
  unittest.main()

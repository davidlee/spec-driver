"""Tests for create_spec module."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import pytest

from supekku.scripts.lib.core.paths import (
  PRODUCT_SPECS_SUBDIR,
  SPEC_DRIVER_DIR,
  TECH_SPECS_SUBDIR,
  get_templates_dir,
)
from supekku.scripts.lib.core.spec_utils import load_markdown_file
from supekku.scripts.lib.specs.creation import (
  CreateSpecOptions,
  RepositoryRootNotFoundError,
  build_frontmatter,
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
    (root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR).mkdir(parents=True)
    (root / SPEC_DRIVER_DIR / PRODUCT_SPECS_SUBDIR).mkdir(parents=True)
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
    from unittest.mock import patch  # noqa: PLC0415

    with (
      patch(
        "supekku.scripts.lib.specs.creation.find_repository_root",
        side_effect=RepositoryRootNotFoundError("no repo"),
      ),
      pytest.raises(RepositoryRootNotFoundError),
    ):
      create_spec("No Repo", CreateSpecOptions())

  def test_json_output_matches_structure(self) -> None:
    """Test that JSON output from create_spec has expected structure."""
    self._setup_repo()
    result = create_spec("Example", CreateSpecOptions())
    payload = json.loads(result.to_json())
    assert payload["id"] == "SPEC-001"
    assert "spec_file" in payload


class BuildFrontmatterTaxonomyTest(unittest.TestCase):
  """VT-030-002: build_frontmatter sets taxonomy defaults correctly."""

  def test_tech_spec_defaults_to_assembly(self):
    fm = build_frontmatter(
      spec_id="SPEC-001",
      slug="test",
      name="Test",
      kind="spec",
      created="2026-01-01",
    )
    assert fm["category"] == "assembly"
    assert "c4_level" not in fm

  def test_product_spec_has_no_category(self):
    fm = build_frontmatter(
      spec_id="PROD-001",
      slug="test",
      name="Test",
      kind="prod",
      created="2026-01-01",
    )
    assert "category" not in fm

  def test_guidance_has_no_category(self):
    fm = build_frontmatter(
      spec_id="SPEC-001.TESTS",
      slug="test-tests",
      name="Test Guide",
      kind="guidance",
      created="2026-01-01",
    )
    assert "category" not in fm

  def test_explicit_category_overrides_default(self):
    fm = build_frontmatter(
      spec_id="SPEC-001",
      slug="test",
      name="Test",
      kind="spec",
      created="2026-01-01",
      category="unit",
      c4_level="code",
    )
    assert fm["category"] == "unit"
    assert fm["c4_level"] == "code"

  def test_create_tech_spec_frontmatter_has_assembly(self):
    """Integration: create_spec produces a tech spec with category: assembly."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    templates = get_templates_dir(root)
    templates.mkdir(parents=True)
    (root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR).mkdir(parents=True)
    (root / SPEC_DRIVER_DIR / PRODUCT_SPECS_SUBDIR).mkdir(parents=True)
    (templates / "spec.md").write_text(
      "# {{ spec_id }} – {{ name }}\n\nBody\n",
      encoding="utf-8",
    )
    saved = Path.cwd()
    os.chdir(root)
    try:
      result = create_spec("Test Spec", CreateSpecOptions(spec_type="tech"))
      frontmatter, _ = load_markdown_file(result.spec_path)
      assert frontmatter["category"] == "assembly"
    finally:
      os.chdir(saved)


if __name__ == "__main__":
  unittest.main()

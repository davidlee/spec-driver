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
from supekku.scripts.lib.core.templates import get_package_templates_dir
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


class TemplateBlockVariablesTest(unittest.TestCase):
  """VT-DE139-TPL-001: template contains all block template variables."""

  def test_spec_template_has_block_variables(self):
    template_path = get_package_templates_dir() / "spec.md"
    content = template_path.read_text(encoding="utf-8")

    for var in (
      "spec_relationships_block",
      "spec_capabilities_block",
      "spec_verification_block",
      "spec_concerns_block",
      "spec_hypotheses_block",
      "spec_decisions_block",
    ):
      assert f"{{{{ {var} }}}}" in content, f"missing {var}"

  def test_spec_template_has_requirements_block_variable(self):
    """VT-140-020: template includes spec_requirements_block placeholder."""
    template_path = get_package_templates_dir() / "spec.md"
    content = template_path.read_text(encoding="utf-8")
    assert "{{ spec_requirements_block }}" in content, "missing spec_requirements_block"


class CreateSpecBlocksTest(unittest.TestCase):
  """VT-DE139-CREATE-001: created spec emits all block placeholders."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _setup_repo_with_blocks_template(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    templates = get_templates_dir(root)
    templates.mkdir(parents=True)
    (root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR).mkdir(parents=True)
    (root / SPEC_DRIVER_DIR / PRODUCT_SPECS_SUBDIR).mkdir(parents=True)
    (templates / "spec.md").write_text(
      "# {{ spec_id }} – {{ name }}\n\n"
      "{{ spec_relationships_block }}\n\n"
      "{{ spec_capabilities_block }}\n\n"
      "{{ spec_verification_block }}\n\n"
      "{{ spec_requirements_block }}\n\n"
      "{{ spec_concerns_block }}\n\n"
      "{{ spec_hypotheses_block }}\n\n"
      "{{ spec_decisions_block }}\n\n"
      "## 1. Intent\n\nBody.\n",
      encoding="utf-8",
    )
    os.chdir(root)
    return root

  def test_created_spec_contains_all_blocks(self):
    self._setup_repo_with_blocks_template()
    result = create_spec("Widget Parser", CreateSpecOptions(spec_type="tech"))
    content = result.spec_path.read_text(encoding="utf-8")

    assert "supekku:spec.relationships@v1" in content
    assert "supekku:spec.capabilities@v1" in content
    assert "supekku:verification.coverage@v1" in content
    assert "supekku:spec.concerns@v1" in content
    assert "supekku:spec.hypotheses@v1" in content
    assert "supekku:spec.decisions@v1" in content

  def test_created_spec_contains_requirements_block(self):
    """VT-140-019: spec creation emits empty requirements block (DEC-140-14)."""
    self._setup_repo_with_blocks_template()
    result = create_spec("Widget Parser", CreateSpecOptions(spec_type="tech"))
    content = result.spec_path.read_text(encoding="utf-8")
    assert "supekku:spec.requirements@v1" in content
    assert "requirements: []" in content

  def test_created_spec_has_no_packages(self):
    self._setup_repo_with_blocks_template()
    result = create_spec("Widget Parser", CreateSpecOptions(spec_type="tech"))
    fm, _ = load_markdown_file(result.spec_path)
    assert "packages" not in fm


class SpecRequirementsEmptyBlockTest(unittest.TestCase):
  """VT-140-030: scaffolded spec with empty block creates no registry entries."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def test_empty_requirements_block_produces_no_records(self):
    """Empty requirements block in created spec yields zero registry entries."""
    from supekku.scripts.lib.blocks.spec_requirements import (  # noqa: PLC0415
      extract_spec_requirements,
    )

    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    templates = get_templates_dir(root)
    templates.mkdir(parents=True)
    (root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR).mkdir(parents=True)
    (root / SPEC_DRIVER_DIR / PRODUCT_SPECS_SUBDIR).mkdir(parents=True)
    (templates / "spec.md").write_text(
      "# {{ spec_id }} – {{ name }}\n\n"
      "{{ spec_requirements_block }}\n\n"
      "## Body\n",
      encoding="utf-8",
    )
    os.chdir(root)

    result = create_spec("Empty Reqs", CreateSpecOptions(spec_type="tech"))
    content = result.spec_path.read_text(encoding="utf-8")

    block = extract_spec_requirements(content)
    assert block is not None, "requirements block should be present"
    reqs = block.data.get("requirements", [])
    assert reqs == [], f"expected empty requirements list, got {reqs}"


if __name__ == "__main__":
  unittest.main()

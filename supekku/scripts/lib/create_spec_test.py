"""Tests for create_spec module."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import pytest

from supekku.scripts.lib.create_spec import (
  CreateSpecOptions,
  RepositoryRootNotFoundError,
  TemplateNotFoundError,
  create_spec,
)
from supekku.scripts.lib.paths import get_templates_dir
from supekku.scripts.lib.spec_utils import load_markdown_file


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
    (templates / "tech-spec-template.md").write_text(
      """```markdown\n# Tech Body\n```\n""",
      encoding="utf-8",
    )
    (templates / "product-spec-template.md").write_text(
      """```markdown\n# Product Body\n```\n""",
      encoding="utf-8",
    )
    (templates / "tech-testing-template.md").write_text(
      """```markdown\n# Test Body\n```\n""",
      encoding="utf-8",
    )
    os.chdir(root)
    return root

  def test_create_tech_spec_generates_spec_and_testing_doc(self) -> None:
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
    assert body == "# Tech Body\n"

    test_frontmatter, test_body = load_markdown_file(result.test_path)
    assert test_frontmatter["id"].endswith(".TESTS")
    assert test_frontmatter["kind"] == "guidance"
    assert test_body == "# Test Body\n"

  def test_create_product_spec_without_testing_doc(self) -> None:
    self._setup_repo()

    result = create_spec(
      "Sync Experience",
      CreateSpecOptions(spec_type="product", include_testing=False),
    )

    assert result.spec_id == "PROD-001"
    assert result.test_path is None

  def test_missing_templates_raise_error(self) -> None:
    root = self._setup_repo()
    (get_templates_dir(root) / "tech-spec-template.md").unlink()

    with pytest.raises(TemplateNotFoundError):
      create_spec("Missing Template", CreateSpecOptions())

  def test_repository_root_not_found(self) -> None:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    os.chdir(tmpdir.name)

    with pytest.raises(RepositoryRootNotFoundError):
      create_spec("No Repo", CreateSpecOptions())

  def test_json_output_matches_structure(self) -> None:
    self._setup_repo()
    result = create_spec("Example", CreateSpecOptions())
    payload = json.loads(result.to_json())
    assert payload["id"] == "SPEC-001"
    assert "spec_file" in payload


if __name__ == "__main__":
  unittest.main()

"""Tests for create_spec module."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from supekku.scripts.lib.create_spec import (
    CreateSpecOptions,
    RepositoryRootNotFoundError,
    TemplateNotFoundError,
    create_spec,
)
from supekku.scripts.lib.spec_utils import load_markdown_file


class CreateSpecTest(unittest.TestCase):
    """Test cases for create_spec functionality."""

    def setUp(self) -> None:
        self._cwd = os.getcwd()

    def tearDown(self) -> None:
        os.chdir(self._cwd)

    def _setup_repo(self) -> Path:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        root = Path(tmpdir.name)
        (root / ".git").mkdir()
        templates = root / "supekku" / "templates"
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

        self.assertEqual(result.spec_id, "SPEC-001")
        self.assertTrue(result.test_path)

        frontmatter, body = load_markdown_file(result.spec_path)
        self.assertEqual(frontmatter["name"], "Search Service")
        self.assertEqual(frontmatter["status"], "draft")
        self.assertEqual(frontmatter["kind"], "spec")
        self.assertTrue(frontmatter["slug"].startswith("search"))
        self.assertEqual(body, "# Tech Body\n")

        test_frontmatter, test_body = load_markdown_file(result.test_path)
        self.assertTrue(test_frontmatter["id"].endswith(".TESTS"))
        self.assertEqual(test_frontmatter["kind"], "guidance")
        self.assertEqual(test_body, "# Test Body\n")

    def test_create_product_spec_without_testing_doc(self) -> None:
        self._setup_repo()

        result = create_spec(
            "Sync Experience",
            CreateSpecOptions(spec_type="product", include_testing=False),
        )

        self.assertEqual(result.spec_id, "PROD-001")
        self.assertIsNone(result.test_path)

    def test_missing_templates_raise_error(self) -> None:
        root = self._setup_repo()
        (root / "supekku" / "templates" / "tech-spec-template.md").unlink()

        with self.assertRaises(TemplateNotFoundError):
            create_spec("Missing Template", CreateSpecOptions())

    def test_repository_root_not_found(self) -> None:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        os.chdir(tmpdir.name)

        with self.assertRaises(RepositoryRootNotFoundError):
            create_spec("No Repo", CreateSpecOptions())

    def test_json_output_matches_structure(self) -> None:
        self._setup_repo()
        result = create_spec("Example", CreateSpecOptions())
        payload = json.loads(result.to_json())
        self.assertEqual(payload["id"], "SPEC-001")
        self.assertIn("spec_file", payload)


if __name__ == "__main__":
    unittest.main()

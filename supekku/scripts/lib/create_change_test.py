"""Tests for create_change module."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from supekku.scripts.lib.create_change import (
    ChangeArtifactCreated,
    create_delta,
    create_requirement_breakout,
    create_revision,
)
from supekku.scripts.lib.spec_utils import load_markdown_file


class CreateChangeTest(unittest.TestCase):
    """Test cases for create_change module functionality."""

    def setUp(self) -> None:
        self._cwd = os.getcwd()

    def tearDown(self) -> None:
        os.chdir(self._cwd)

    def _make_repo(self) -> Path:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        root = Path(tmpdir.name)
        (root / ".git").mkdir()
        spec_dir = root / "specify" / "tech" / "spec-100-example"
        spec_dir.mkdir(parents=True, exist_ok=True)
        (spec_dir / "SPEC-100.md").write_text(
            "---\nid: SPEC-100\nslug: spec-100\nname: Spec 100\ncreated: 2024-01-01\nupdated: 2024-01-01\nstatus: draft\nkind: spec\n---\n\n- FR-100: Example\n",
            encoding="utf-8",
        )
        os.chdir(root)
        return root

    def test_create_revision(self) -> None:
        root = self._make_repo()
        result = create_revision(
            "Move FR",
            source_specs=["SPEC-100"],
            destination_specs=["SPEC-101"],
            requirements=["SPEC-100.FR-100"],
            repo_root=root,
        )
        self.assertIsInstance(result, ChangeArtifactCreated)
        self.assertTrue(result.primary_path.exists())
        frontmatter, _ = load_markdown_file(result.primary_path)
        self.assertEqual(frontmatter["kind"], "revision")
        self.assertIn("SPEC-100", frontmatter.get("source_specs", []))

    def test_create_delta(self) -> None:
        root = self._make_repo()
        result = create_delta(
            "Implement ignore handling",
            specs=["SPEC-100"],
            requirements=["SPEC-100.FR-100"],
            repo_root=root,
        )
        self.assertTrue(result.primary_path.exists())
        frontmatter, _ = load_markdown_file(result.primary_path)
        self.assertEqual(frontmatter["kind"], "delta")
        plan_files = [p for p in result.extras if p.name.startswith("IP-")]
        self.assertTrue(plan_files)

    def test_create_requirement_breakout(self) -> None:
        root = self._make_repo()
        path = create_requirement_breakout(
            "SPEC-100",
            "FR-200",
            title="Handle edge cases",
            repo_root=root,
        )
        self.assertTrue(path.exists())
        frontmatter, _ = load_markdown_file(path)
        self.assertEqual(frontmatter["kind"], "requirement")
        self.assertEqual(frontmatter["spec"], "SPEC-100")


if __name__ == "__main__":
    unittest.main()

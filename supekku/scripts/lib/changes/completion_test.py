"""Tests for complete_revision in completion module."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from supekku.scripts.lib.changes.completion import complete_revision
from supekku.scripts.lib.core.spec_utils import load_markdown_file


class CompleteRevisionTest(unittest.TestCase):
  """Test cases for complete_revision functionality."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_repo(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)
    return root

  def _create_revision(
    self,
    root: Path,
    revision_id: str = "RE-001",
    status: str = "draft",
  ) -> Path:
    """Create a minimal revision file for testing."""
    revision_dir = root / "change" / "revisions" / f"{revision_id}-test"
    revision_dir.mkdir(parents=True, exist_ok=True)
    revision_path = revision_dir / f"{revision_id}.md"
    revision_path.write_text(
      f"---\nid: {revision_id}\nslug: test\nname: Test Revision\n"
      f"created: '2026-01-01'\nupdated: '2026-01-01'\n"
      f"status: {status}\nkind: revision\naliases: []\nrelations: []\n"
      f"---\n\n# {revision_id}\n",
      encoding="utf-8",
    )
    return revision_path

  def test_complete_draft_revision(self) -> None:
    """Test completing a draft revision transitions to completed."""
    root = self._make_repo()
    path = self._create_revision(root)
    exit_code = complete_revision("RE-001", repo_root=root)
    assert exit_code == 0
    frontmatter, _ = load_markdown_file(path)
    assert frontmatter["status"] == "completed"

  def test_complete_in_progress_revision(self) -> None:
    """Test completing an in-progress revision transitions to completed."""
    root = self._make_repo()
    path = self._create_revision(root, status="in-progress")
    exit_code = complete_revision("RE-001", repo_root=root)
    assert exit_code == 0
    frontmatter, _ = load_markdown_file(path)
    assert frontmatter["status"] == "completed"

  def test_complete_already_completed(self) -> None:
    """Test completing an already-completed revision is idempotent."""
    root = self._make_repo()
    self._create_revision(root, status="completed")
    exit_code = complete_revision("RE-001", repo_root=root)
    assert exit_code == 0

  def test_complete_unexpected_status_rejected(self) -> None:
    """Test unexpected status is rejected without --force."""
    root = self._make_repo()
    self._create_revision(root, status="deferred")
    exit_code = complete_revision("RE-001", repo_root=root)
    assert exit_code == 1

  def test_complete_unexpected_status_forced(self) -> None:
    """Test unexpected status accepted with --force."""
    root = self._make_repo()
    path = self._create_revision(root, status="deferred")
    exit_code = complete_revision("RE-001", force=True, repo_root=root)
    assert exit_code == 0
    frontmatter, _ = load_markdown_file(path)
    assert frontmatter["status"] == "completed"

  def test_complete_not_found(self) -> None:
    """Test error when revision does not exist."""
    root = self._make_repo()
    (root / "change" / "revisions").mkdir(parents=True, exist_ok=True)
    exit_code = complete_revision("RE-999", repo_root=root)
    assert exit_code == 1

  def test_complete_updates_date(self) -> None:
    """Test that updated date is set on completion."""
    root = self._make_repo()
    path = self._create_revision(root)
    complete_revision("RE-001", repo_root=root)
    frontmatter, _ = load_markdown_file(path)
    assert frontmatter["updated"] != "2026-01-01"


if __name__ == "__main__":
  unittest.main()

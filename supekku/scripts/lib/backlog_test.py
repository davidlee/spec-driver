"""Tests for backlog module."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from supekku.scripts.lib.backlog import (
  append_backlog_summary,
  create_backlog_entry,
  find_repo_root,
)


class BacklogLibraryTest(unittest.TestCase):
  """Test cases for backlog management functionality."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_repo(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    (root / "backlog" / "issues").mkdir(parents=True)
    (root / "backlog" / "backlog.md").write_text("", encoding="utf-8")
    os.chdir(root)
    return root

  def test_create_backlog_entry_writes_frontmatter(self) -> None:
    self._make_repo()

    path = create_backlog_entry("issue", "Investigate feature flag")

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "id: ISSUE-001" in text
    assert "name: Investigate feature flag" in text

  def test_append_backlog_summary_appends_missing_entries(self) -> None:
    root = self._make_repo()
    entry = create_backlog_entry("issue", "Investigate feature flag")

    additions = append_backlog_summary()

    assert len(additions) == 1
    summary = (root / "backlog" / "backlog.md").read_text(encoding="utf-8")
    assert "ISSUE-001" in summary
    assert entry.relative_to(root / "backlog").as_posix() in summary

  def test_find_repo_root_resolves_from_nested_path(self) -> None:
    root = self._make_repo()
    nested = root / "backlog" / "issues"
    os.chdir(nested)
    resolved = find_repo_root()
    assert resolved == root


if __name__ == "__main__":
  unittest.main()

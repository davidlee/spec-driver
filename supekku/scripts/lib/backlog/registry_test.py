"""Tests for backlog module."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import yaml

from supekku.scripts.lib.backlog.registry import (
  append_backlog_summary,
  create_backlog_entry,
  find_backlog_items_by_id,
  find_repo_root,
  load_backlog_registry,
  save_backlog_registry,
  sync_backlog_registry,
)
from supekku.scripts.lib.core.paths import BACKLOG_DIR


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
    (root / BACKLOG_DIR / "issues").mkdir(parents=True)
    (root / BACKLOG_DIR / "backlog.md").write_text("", encoding="utf-8")
    os.chdir(root)
    return root

  def test_create_backlog_entry_writes_frontmatter(self) -> None:
    """Test that creating a backlog entry writes correct frontmatter."""
    self._make_repo()

    path = create_backlog_entry("issue", "Investigate feature flag")

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "id: ISSUE-001" in text
    assert "name: Investigate feature flag" in text

  def test_append_backlog_summary_appends_missing_entries(self) -> None:
    """Test that appending to backlog summary adds missing entries."""
    root = self._make_repo()
    entry = create_backlog_entry("issue", "Investigate feature flag")

    additions = append_backlog_summary()

    assert len(additions) == 1
    summary = (root / BACKLOG_DIR / "backlog.md").read_text(encoding="utf-8")
    assert "ISSUE-001" in summary
    # Resolve paths to handle macOS /var -> /private/var symlink
    backlog_root = root.resolve() / BACKLOG_DIR
    assert entry.resolve().relative_to(backlog_root).as_posix() in summary

  def test_find_repo_root_resolves_from_nested_path(self) -> None:
    """Test that find_repo_root resolves correctly from nested directories."""
    root = self._make_repo()
    nested = root / BACKLOG_DIR / "issues"
    os.chdir(nested)
    resolved = find_repo_root()
    # Resolve both paths to handle macOS /var -> /private/var symlink
    assert resolved.resolve() == root.resolve()

  def test_load_backlog_registry_returns_empty_when_missing(self) -> None:
    """Test that load_backlog_registry returns empty list when file doesn't exist."""
    root = self._make_repo()
    ordering = load_backlog_registry(root)
    assert ordering == []

  def test_save_and_load_backlog_registry_roundtrip(self) -> None:
    """Test that save and load preserve ordering."""
    root = self._make_repo()
    expected = ["ISSUE-003", "IMPR-001", "ISSUE-001"]

    save_backlog_registry(expected, root)
    actual = load_backlog_registry(root)

    assert actual == expected

  def test_load_backlog_registry_handles_malformed_yaml(self) -> None:
    """Test that load_backlog_registry returns empty list for malformed YAML."""
    root = self._make_repo()
    registry_dir = root / ".spec-driver" / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry_file = registry_dir / "backlog.yaml"

    # Write invalid YAML
    registry_file.write_text("invalid: [unclosed", encoding="utf-8")

    # Should raise YAML error
    with self.assertRaises(yaml.YAMLError):
      load_backlog_registry(root)

  def test_load_backlog_registry_handles_wrong_structure(self) -> None:
    """Test that load_backlog_registry returns empty list for wrong structure."""
    root = self._make_repo()
    registry_dir = root / ".spec-driver" / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry_file = registry_dir / "backlog.yaml"

    # Write valid YAML but wrong structure (not a dict)
    registry_file.write_text("- item1\n- item2\n", encoding="utf-8")

    ordering = load_backlog_registry(root)
    assert ordering == []

  def test_sync_backlog_registry_initializes_empty_registry(self) -> None:
    """Test that sync creates registry from scratch with all items."""
    root = self._make_repo()

    # Create some backlog items
    create_backlog_entry("issue", "First issue")
    create_backlog_entry("issue", "Second issue")
    create_backlog_entry("improvement", "First improvement")

    stats = sync_backlog_registry(root)

    assert stats["total"] == 3
    assert stats["added"] == 3
    assert stats["removed"] == 0
    assert stats["unchanged"] == 0

    # Verify ordering (should be sorted by ID)
    ordering = load_backlog_registry(root)
    assert ordering == ["IMPR-001", "ISSUE-001", "ISSUE-002"]

  def test_sync_backlog_registry_preserves_existing_order(self) -> None:
    """Test that sync preserves order of existing items."""
    root = self._make_repo()

    # Create items
    create_backlog_entry("issue", "First issue")
    create_backlog_entry("issue", "Second issue")

    # Set custom order (reversed)
    save_backlog_registry(["ISSUE-002", "ISSUE-001"], root)

    # Sync should preserve this order
    stats = sync_backlog_registry(root)

    assert stats["total"] == 2
    assert stats["added"] == 0
    assert stats["removed"] == 0
    assert stats["unchanged"] == 2

    ordering = load_backlog_registry(root)
    assert ordering == ["ISSUE-002", "ISSUE-001"]

  def test_sync_backlog_registry_appends_new_items(self) -> None:
    """Test that sync appends new items to existing order."""
    root = self._make_repo()

    # Create initial items
    create_backlog_entry("issue", "First issue")
    save_backlog_registry(["ISSUE-001"], root)

    # Add more items
    create_backlog_entry("issue", "Second issue")
    create_backlog_entry("improvement", "First improvement")

    stats = sync_backlog_registry(root)

    assert stats["total"] == 3
    assert stats["added"] == 2
    assert stats["removed"] == 0
    assert stats["unchanged"] == 1

    ordering = load_backlog_registry(root)
    # ISSUE-001 preserved at start, new items appended sorted
    assert ordering == ["ISSUE-001", "IMPR-001", "ISSUE-002"]

  def test_sync_backlog_registry_prunes_orphaned_items(self) -> None:
    """Test that sync removes IDs for deleted items."""
    root = self._make_repo()

    # Create items
    create_backlog_entry("issue", "First issue")
    issue2 = create_backlog_entry("issue", "Second issue")

    # Set registry with both
    save_backlog_registry(["ISSUE-001", "ISSUE-002"], root)

    # Delete one item
    issue2.unlink()

    stats = sync_backlog_registry(root)

    assert stats["total"] == 1
    assert stats["added"] == 0
    assert stats["removed"] == 1
    assert stats["unchanged"] == 1

    ordering = load_backlog_registry(root)
    assert ordering == ["ISSUE-001"]

  def test_sync_backlog_registry_handles_mixed_changes(self) -> None:
    """Test sync with new items, deleted items, and preserved items."""
    root = self._make_repo()

    # Create initial items
    create_backlog_entry("issue", "First issue")
    create_backlog_entry("issue", "Second issue")

    # Set registry with custom order
    save_backlog_registry(["ISSUE-002", "ISSUE-001"], root)

    # Delete ISSUE-002 and add new items
    (root / BACKLOG_DIR / "issues" / "ISSUE-002-second_issue" / "ISSUE-002.md").unlink()
    create_backlog_entry("improvement", "First improvement")
    create_backlog_entry("issue", "Third issue")

    stats = sync_backlog_registry(root)

    assert stats["total"] == 3  # ISSUE-001, IMPR-001, ISSUE-003
    assert stats["added"] == 2  # IMPR-001, ISSUE-003
    assert stats["removed"] == 1  # ISSUE-002
    assert stats["unchanged"] == 1  # ISSUE-001

    ordering = load_backlog_registry(root)
    # ISSUE-001 preserved, ISSUE-002 removed, new items appended sorted
    assert ordering == ["ISSUE-001", "IMPR-001", "ISSUE-003"]


class FindBacklogItemsByIdTest(unittest.TestCase):
  """Tests for find_backlog_items_by_id (VT-backlog-find)."""

  def _make_repo(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    return root

  def _create_item(self, root: Path, subdir: str, item_id: str, slug: str) -> Path:
    """Create a minimal backlog item at the expected path."""
    entry_dir = root / BACKLOG_DIR / subdir / f"{item_id}-{slug}"
    entry_dir.mkdir(parents=True, exist_ok=True)
    md_file = entry_dir / f"{item_id}.md"
    kind = subdir.rstrip("s")
    fm = (
      f"---\nid: {item_id}\nname: {slug}\nkind: {kind}\nstatus: open\n---\n# {slug}\n"
    )
    md_file.write_text(fm, encoding="utf-8")
    return md_file

  def test_finds_issue_by_id(self) -> None:
    root = self._make_repo()
    self._create_item(root, "issues", "ISSUE-001", "test-issue")
    items = find_backlog_items_by_id("ISSUE-001", root)
    assert len(items) == 1
    assert items[0].id == "ISSUE-001"
    assert items[0].kind == "issue"

  def test_finds_improvement_by_id(self) -> None:
    root = self._make_repo()
    self._create_item(root, "improvements", "IMPR-001", "test-improvement")
    items = find_backlog_items_by_id("IMPR-001", root)
    assert len(items) == 1
    assert items[0].id == "IMPR-001"

  def test_finds_risk_by_id(self) -> None:
    root = self._make_repo()
    self._create_item(root, "risks", "RISK-001", "test-risk")
    items = find_backlog_items_by_id("RISK-001", root)
    assert len(items) == 1
    assert items[0].id == "RISK-001"

  def test_finds_problem_by_id(self) -> None:
    root = self._make_repo()
    self._create_item(root, "problems", "PROB-001", "test-problem")
    items = find_backlog_items_by_id("PROB-001", root)
    assert len(items) == 1
    assert items[0].id == "PROB-001"

  def test_returns_empty_for_missing_id(self) -> None:
    root = self._make_repo()
    self._create_item(root, "issues", "ISSUE-001", "test")
    items = find_backlog_items_by_id("ISSUE-999", root)
    assert items == []

  def test_returns_empty_for_no_backlog_dir(self) -> None:
    root = self._make_repo()
    items = find_backlog_items_by_id("ISSUE-001", root)
    assert items == []

  def test_kind_filter_narrows_search(self) -> None:
    root = self._make_repo()
    self._create_item(root, "issues", "ISSUE-001", "test")
    items = find_backlog_items_by_id("ISSUE-001", root, kind="problem")
    assert items == []
    items = find_backlog_items_by_id("ISSUE-001", root, kind="issue")
    assert len(items) == 1

  def test_invalid_kind_returns_empty(self) -> None:
    root = self._make_repo()
    items = find_backlog_items_by_id("ISSUE-001", root, kind="nonsense")
    assert items == []

  def test_duplicate_ids_returns_multiple(self) -> None:
    """Duplicate IDs across subdirs (or within) return all matches."""
    root = self._make_repo()
    # Same ID in two different slug dirs (simulating data quality issue)
    self._create_item(root, "issues", "ISSUE-001", "first")
    self._create_item(root, "issues", "ISSUE-001", "second")
    items = find_backlog_items_by_id("ISSUE-001", root)
    assert len(items) == 2


if __name__ == "__main__":
  unittest.main()

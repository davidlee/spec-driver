"""Tests for BundleTree widget (VT-061-01)."""

from __future__ import annotations

from pathlib import Path

import pytest

from supekku.tui.widgets.bundle_tree import BundleFileSelected, BundleTree


@pytest.fixture()
def bundle_dir(tmp_path: Path) -> Path:
  """Create a realistic delta bundle directory."""
  bd = tmp_path / "DE-061-tui_bundle_file_browser"
  bd.mkdir()
  (bd / "DE-061.md").write_text("# Delta\n", encoding="utf-8")
  (bd / "DR-061.md").write_text("# Design\n", encoding="utf-8")
  (bd / "IP-061.md").write_text("# Plan\n", encoding="utf-8")
  (bd / "notes.md").write_text("# Notes\n", encoding="utf-8")
  phases = bd / "phases"
  phases.mkdir()
  (phases / "phase-01.md").write_text("# Phase 1\n", encoding="utf-8")
  (phases / "phase-02.md").write_text("# Phase 2\n", encoding="utf-8")
  return bd


@pytest.fixture()
def empty_bundle(tmp_path: Path) -> Path:
  """Create an empty bundle directory."""
  bd = tmp_path / "DE-099-empty"
  bd.mkdir()
  return bd


class TestBundleTreePopulation:
  """BundleTree.show_bundle populates the tree from a directory."""

  def test_populates_files(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    primary = bundle_dir / "DE-061.md"
    tree.show_bundle(bundle_dir, primary)

    # Root should have children
    children = tree.root.children
    assert len(children) > 0

    # Collect all leaf names
    leaf_names = [n.label.plain for n in children if not n.children]
    assert "DE-061.md" in leaf_names
    assert "DR-061.md" in leaf_names
    assert "IP-061.md" in leaf_names
    assert "notes.md" in leaf_names

  def test_populates_subdirectories(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")

    # Find the phases directory node
    dir_nodes = [n for n in tree.root.children if n.children]
    assert len(dir_nodes) == 1
    phases_node = dir_nodes[0]
    assert phases_node.label.plain == "phases"

    phase_names = [n.label.plain for n in phases_node.children]
    assert "phase-01.md" in phase_names
    assert "phase-02.md" in phase_names

  def test_sets_root_label_to_dir_name(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")
    assert tree.root.label.plain == bundle_dir.name

  def test_empty_bundle(self, empty_bundle: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(empty_bundle, empty_bundle / "nonexistent.md")
    assert len(tree.root.children) == 0

  def test_stores_path_as_node_data(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")

    for node in tree.root.children:
      assert isinstance(node.data, Path)


class TestBundleTreeHiddenAndSymlinks:
  """BundleTree skips hidden files and symlinks."""

  def test_skips_dotfiles(self, bundle_dir: Path) -> None:
    (bundle_dir / ".hidden").write_text("hidden\n", encoding="utf-8")
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")

    names = [n.label.plain for n in tree.root.children]
    assert ".hidden" not in names

  def test_skips_dotdirs(self, bundle_dir: Path) -> None:
    hidden_dir = bundle_dir / ".secret"
    hidden_dir.mkdir()
    (hidden_dir / "file.md").write_text("secret\n", encoding="utf-8")

    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")

    names = [n.label.plain for n in tree.root.children]
    assert ".secret" not in names

  def test_skips_symlinks(self, bundle_dir: Path) -> None:
    target = bundle_dir / "DE-061.md"
    link = bundle_dir / "link.md"
    link.symlink_to(target)

    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, target)

    names = [n.label.plain for n in tree.root.children]
    assert "link.md" not in names

  def test_skips_symlink_dirs(self, bundle_dir: Path) -> None:
    target_dir = bundle_dir / "phases"
    link_dir = bundle_dir / "linked_phases"
    link_dir.symlink_to(target_dir)

    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")

    names = [n.label.plain for n in tree.root.children]
    assert "linked_phases" not in names


class TestBundleTreeDepthLimit:
  """BundleTree respects _MAX_TREE_DEPTH."""

  def test_depth_limit(self, tmp_path: Path) -> None:
    bd = tmp_path / "DE-001-deep"
    # Create nested dirs: bd/a/b/c/d/file.md (4 levels deep)
    deep = bd
    for name in ("a", "b", "c", "d"):
      deep = deep / name
    deep.mkdir(parents=True)
    (deep / "deep.md").write_text("deep\n", encoding="utf-8")
    (bd / "DE-001.md").write_text("# Delta\n", encoding="utf-8")

    tree = BundleTree(id="test-tree")
    tree.show_bundle(bd, bd / "DE-001.md")

    # Should have 'a' dir at root level
    dir_nodes = [n for n in tree.root.children if n.children]
    assert len(dir_nodes) == 1

    # Walk down: a -> b -> c (depth 3 reached, d should not appear)
    a_node = dir_nodes[0]
    assert a_node.label.plain == "a"

    b_nodes = [n for n in a_node.children if n.children]
    assert len(b_nodes) == 1
    b_node = b_nodes[0]
    assert b_node.label.plain == "b"

    c_nodes = [n for n in b_node.children if n.children]
    # c exists but d should not be populated (depth 3 = max)
    if c_nodes:
      c_node = c_nodes[0]
      # d should not appear as a child of c
      d_nodes = [n for n in c_node.children if n.label.plain == "d"]
      assert len(d_nodes) == 0


class TestBundleTreeSortOrder:
  """Sort: directories first, primary first among files, then alpha."""

  def test_directories_before_files(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")

    children = tree.root.children
    # Find first file and last dir
    first_file_idx = None
    last_dir_idx = None
    for i, node in enumerate(children):
      if node.children:
        last_dir_idx = i
      elif first_file_idx is None:
        first_file_idx = i

    if last_dir_idx is not None and first_file_idx is not None:
      assert last_dir_idx < first_file_idx

  def test_primary_file_first_among_files(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    primary = bundle_dir / "DE-061.md"
    tree.show_bundle(bundle_dir, primary)

    # Get file-only children (skip dirs)
    file_nodes = [n for n in tree.root.children if not n.children]
    assert len(file_nodes) > 0
    assert file_nodes[0].data == primary

  def test_alpha_order_among_non_primary(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")

    file_nodes = [n for n in tree.root.children if not n.children]
    # Skip primary (first), rest should be alphabetical
    rest = [n.label.plain.lower() for n in file_nodes[1:]]
    assert rest == sorted(rest)


class TestBundleTreeClear:
  """BundleTree.clear_bundle resets state."""

  def test_clear_removes_children(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")
    assert len(tree.root.children) > 0

    tree.clear_bundle()
    assert tree.bundle_dir is None
    assert tree._primary_path is None

  def test_clear_then_repopulate(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")
    tree.clear_bundle()
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")
    assert len(tree.root.children) > 0


class TestBundleTreeSelectFile:
  """BundleTree.select_file navigates to a specific file."""

  def test_select_existing_file(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")

    found = tree.select_file(bundle_dir / "DR-061.md")
    assert found is True

  def test_select_nonexistent_file(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")

    found = tree.select_file(bundle_dir / "nonexistent.md")
    assert found is False


class TestBundleTreeProperties:
  """BundleTree exposes bundle_dir property."""

  def test_bundle_dir_none_initially(self) -> None:
    tree = BundleTree(id="test-tree")
    assert tree.bundle_dir is None

  def test_bundle_dir_set_after_show(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")
    assert tree.bundle_dir == bundle_dir

  def test_bundle_dir_none_after_clear(self, bundle_dir: Path) -> None:
    tree = BundleTree(id="test-tree")
    tree.show_bundle(bundle_dir, bundle_dir / "DE-061.md")
    tree.clear_bundle()
    assert tree.bundle_dir is None


class TestBundleFileSelectedMessage:
  """BundleFileSelected message carries the file path."""

  def test_message_has_path(self) -> None:
    path = Path("/some/file.md")
    msg = BundleFileSelected(path)
    assert msg.path == path

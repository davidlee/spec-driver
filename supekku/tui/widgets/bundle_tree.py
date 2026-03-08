"""Bundle file tree widget — shows all files in a bundle directory (DEC-061-01)."""

from __future__ import annotations

from pathlib import Path

from textual.binding import Binding
from textual.message import Message
from textual.widgets import Tree
from textual.widgets._tree import TreeNode


class BundleFileSelected(Message):
  """Posted when a file is selected in the bundle tree."""

  def __init__(self, path: Path) -> None:
    super().__init__()
    self.path = path


_MAX_TREE_DEPTH = 3


class BundleTree(Tree[Path]):
  """File tree for bundle-backed artifact directories.

  Shows all files in a bundle directory with standard tree navigation.
  Skips hidden files (dotfiles) and symlinks. Depth-limited to prevent
  runaway recursion.
  """

  BINDINGS = [
    Binding("tab", "focus_artifact_table", "Table", show=False),
  ]

  def __init__(self, **kwargs) -> None:
    super().__init__("Bundle", **kwargs)
    self._bundle_dir: Path | None = None
    self._primary_path: Path | None = None

  def show_bundle(self, bundle_dir: Path, primary_path: Path) -> None:
    """Populate tree with bundle directory contents."""
    self._bundle_dir = bundle_dir
    self._primary_path = primary_path
    self.clear()
    self.root.set_label(bundle_dir.name)
    self.root.expand()
    self._populate(self.root, bundle_dir, depth=0)
    self._select_primary()

  def _populate(self, node: TreeNode[Path], directory: Path, depth: int) -> None:
    """Add files and directories, skipping hidden files and symlinks."""
    if depth >= _MAX_TREE_DEPTH:
      return
    try:
      entries = sorted(directory.iterdir(), key=self._sort_key)
    except OSError:
      return
    for entry in entries:
      if entry.name.startswith(".") or entry.is_symlink():
        continue
      if entry.is_dir():
        branch = node.add(entry.name, data=entry)
        self._populate(branch, entry, depth + 1)
        branch.expand()
      elif entry.is_file():
        node.add_leaf(entry.name, data=entry)

  def _sort_key(self, path: Path) -> tuple[int, int, str]:
    """Sort: directories first, primary file first among files, then alpha."""
    is_dir = 0 if path.is_dir() else 1
    is_primary = 0 if path == self._primary_path else 1
    return (is_dir, is_primary, path.name.lower())

  def _select_primary(self) -> None:
    """Cursor the primary file node after population."""
    for idx, node in enumerate(self.root.children):
      if node.data == self._primary_path:
        self.cursor_line = idx + 1  # +1 because root is line 0
        return

  def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
    """Emit BundleFileSelected when a file node is selected."""
    path = event.node.data
    if isinstance(path, Path) and path.is_file():
      self.post_message(BundleFileSelected(path))

  def action_focus_artifact_table(self) -> None:
    """Leave tree, focus artifact table (DEC-061-03)."""
    self.screen.query_one("#artifact-table").focus()

  def clear_bundle(self) -> None:
    """Reset to empty state."""
    self._bundle_dir = None
    self._primary_path = None
    self.clear()

  def select_file(self, file_path: Path) -> bool:
    """Select a specific file in the tree by path. Returns True if found."""
    for idx, node in enumerate(self._walk_nodes()):
      if node.data == file_path:
        self.cursor_line = idx
        return True
    return False

  def _walk_nodes(self) -> list[TreeNode[Path]]:
    """Flat list of all visible nodes for cursor indexing."""
    result: list[TreeNode[Path]] = []

    def _walk(node: TreeNode[Path]) -> None:
      result.append(node)
      if node.is_expanded:
        for child in node.children:
          _walk(child)

    _walk(self.root)
    return result

  @property
  def bundle_dir(self) -> Path | None:
    """The currently displayed bundle directory, or None."""
    return self._bundle_dir

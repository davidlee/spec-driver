# supekku.tui.widgets.bundle_tree

Bundle file tree widget — shows all files in a bundle directory (DEC-061-01).

## Classes

### BundleFileSelected

Posted when a file is selected in the bundle tree.

**Inherits from:** Message

### BundleTree

File tree for bundle-backed artifact directories.

Shows all files in a bundle directory with standard tree navigation.
Skips hidden files (dotfiles) and symlinks. Depth-limited to prevent
runaway recursion.

**Inherits from:** Tree[Path]

#### Methods

- `action_focus_tab_target(self) -> None`: Leave tree, focus the configured tab target (DEC-061-03, DEC-061-07).
- @property `bundle_dir(self) -> <BinOp>`: The currently displayed bundle directory, or None.
- `clear_bundle(self) -> None`: Reset to empty state.
- `on_tree_node_selected(self, event) -> None`: Emit BundleFileSelected when a file node is selected.
- `select_file(self, file_path) -> bool`: Select a specific file in the tree by path. Returns True if found.
- `show_bundle(self, bundle_dir, primary_path) -> None`: Populate tree with bundle directory contents.

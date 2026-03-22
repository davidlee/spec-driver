# supekku.tui.widgets.bundle_tree_test

Tests for BundleTree widget (VT-061-01).

## Functions

- `_plain(label) -> str`: Extract plain text from a tree node label.
- @pytest.fixture `bundle_dir(tmp_path) -> Path`: Create a realistic delta bundle directory.
- @pytest.fixture `empty_bundle(tmp_path) -> Path`: Create an empty bundle directory.

## Classes

### TestBundleFileSelectedMessage

BundleFileSelected message carries the file path.

#### Methods

- `test_message_has_path(self) -> None`

### TestBundleTreeClear

BundleTree.clear_bundle resets state.

#### Methods

- `test_clear_removes_children(self, bundle_dir) -> None`
- `test_clear_then_repopulate(self, bundle_dir) -> None`

### TestBundleTreeDepthLimit

BundleTree respects \_MAX_TREE_DEPTH.

#### Methods

- `test_depth_limit(self, tmp_path) -> None`

### TestBundleTreeHiddenAndSymlinks

BundleTree skips hidden files and symlinks.

#### Methods

- `test_skips_dotdirs(self, bundle_dir) -> None`
- `test_skips_dotfiles(self, bundle_dir) -> None`
- `test_skips_symlink_dirs(self, bundle_dir) -> None`
- `test_skips_symlinks(self, bundle_dir) -> None`

### TestBundleTreePopulation

BundleTree.show_bundle populates the tree from a directory.

#### Methods

- `test_empty_bundle(self, empty_bundle) -> None`
- `test_populates_files(self, bundle_dir) -> None`
- `test_populates_subdirectories(self, bundle_dir) -> None`
- `test_sets_root_label_to_dir_name(self, bundle_dir) -> None`
- `test_stores_path_as_node_data(self, bundle_dir) -> None`

### TestBundleTreeProperties

BundleTree exposes bundle_dir property.

#### Methods

- `test_bundle_dir_none_after_clear(self, bundle_dir) -> None`
- `test_bundle_dir_none_initially(self) -> None`
- `test_bundle_dir_set_after_show(self, bundle_dir) -> None`

### TestBundleTreeSelectFile

BundleTree.select_file navigates to a specific file.

#### Methods

- `test_select_existing_file(self, bundle_dir) -> None`
- `test_select_nonexistent_file(self, bundle_dir) -> None`

### TestBundleTreeSortOrder

Sort: directories first, primary first among files, then alpha.

#### Methods

- `test_alpha_order_among_non_primary(self, bundle_dir) -> None`
- `test_directories_before_files(self, bundle_dir) -> None`
- `test_primary_file_first_among_files(self, bundle_dir) -> None`

# supekku.scripts.lib.backlog.registry_test

Tests for backlog module.

## Classes

### BacklogLibraryTest

Test cases for backlog management functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_append_backlog_summary_appends_missing_entries(self) -> None`: Test that appending to backlog summary adds missing entries.
- `test_create_backlog_entry_writes_frontmatter(self) -> None`: Test that creating a backlog entry writes correct frontmatter.
- `test_find_repo_root_resolves_from_nested_path(self) -> None`: Test that find_repo_root resolves correctly from nested directories.
- `test_load_backlog_registry_handles_malformed_yaml(self) -> None`: Test that load_backlog_registry returns empty list for malformed YAML.
- `test_load_backlog_registry_handles_wrong_structure(self) -> None`: Test that load_backlog_registry returns empty list for wrong structure.
- `test_load_backlog_registry_returns_empty_when_missing(self) -> None`: Test that load_backlog_registry returns empty list when file doesn't exist.
- `test_save_and_load_backlog_registry_roundtrip(self) -> None`: Test that save and load preserve ordering.
- `test_sync_backlog_registry_appends_new_items(self) -> None`: Test that sync appends new items to existing order.
- `test_sync_backlog_registry_handles_mixed_changes(self) -> None`: Test sync with new items, deleted items, and preserved items.
- `test_sync_backlog_registry_initializes_empty_registry(self) -> None`: Test that sync creates registry from scratch with all items.
- `test_sync_backlog_registry_preserves_existing_order(self) -> None`: Test that sync preserves order of existing items.
- `test_sync_backlog_registry_prunes_orphaned_items(self) -> None`: Test that sync removes IDs for deleted items.
- `_make_repo(self) -> Path`

### BacklogRegistryTest

Tests for BacklogRegistry class (VT-057-registry).

**Inherits from:** unittest.TestCase

#### Methods

- `test_collect_returns_all_items(self) -> None` - -- collect --
- `test_collect_returns_dict_keyed_by_id(self) -> None`
- `test_constructor_accepts_keyword_root(self) -> None`
- `test_constructor_auto_discovers_root(self) -> None` - -- Constructor --
- `test_duplicate_ids_warns(self) -> None`
- `test_empty_corpus(self) -> None`
- `test_filter_by_kind(self) -> None` - -- filter --
- `test_filter_by_severity(self) -> None`
- `test_filter_returns_empty_on_no_match(self) -> None`
- `test_find_returns_item(self) -> None` - -- find --
- `test_find_returns_none_for_missing(self) -> None`
- `test_iter_combines_kind_and_status(self) -> None`
- `test_iter_filters_by_kind(self) -> None`
- `test_iter_filters_by_status(self) -> None`
- `test_iter_yields_all(self) -> None` - -- iter --
- `test_malformed_yaml_skipped_with_warning(self) -> None` - -- edge cases --
- `_create_item(self, root, subdir, item_id, slug) -> Path`
- `_make_repo(self) -> Path`

### FindBacklogItemsByIdTest

Tests for find_backlog_items_by_id (VT-backlog-find).

**Inherits from:** unittest.TestCase

#### Methods

- `test_duplicate_ids_logs_warning(self) -> None`: Duplicate IDs log a warning; registry keeps one (last wins).
- `test_finds_improvement_by_id(self) -> None`
- `test_finds_issue_by_id(self) -> None`
- `test_finds_problem_by_id(self) -> None`
- `test_finds_risk_by_id(self) -> None`
- `test_invalid_kind_returns_empty(self) -> None`
- `test_kind_filter_narrows_search(self) -> None`
- `test_returns_empty_for_missing_id(self) -> None`
- `test_returns_empty_for_no_backlog_dir(self) -> None`
- `_create_item(self, root, subdir, item_id, slug) -> Path`: Create a minimal backlog item at the expected path.
- `_make_repo(self) -> Path`

### TestFindItem

Tests for find_item() convenience function (ADR-009 surface).

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_find_item_logs_warning_on_duplicate(self) -> None`
- `test_find_item_respects_kind_filter(self) -> None`
- `test_find_item_returns_item(self) -> None`
- `test_find_item_returns_none_for_missing(self) -> None`
- `_create_item(self, root, subdir, item_id, slug) -> Path`
- `_make_repo(self) -> Path`

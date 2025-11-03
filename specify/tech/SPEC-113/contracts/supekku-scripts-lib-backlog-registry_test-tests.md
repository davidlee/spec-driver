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

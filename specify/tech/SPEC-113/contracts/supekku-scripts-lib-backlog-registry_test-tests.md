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
- `_make_repo(self) -> Path`

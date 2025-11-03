# supekku.scripts.lib.decisions.registry_test

Tests for decision_registry module.

## Classes

### TestDecisionRecord

Tests for DecisionRecord dataclass.

**Inherits from:** unittest.TestCase

#### Methods

- `test_to_dict_full(self) -> None`: Test serialization with all fields populated. - Empty lists are omitted
- `test_to_dict_minimal(self) -> None`: Test serialization with minimal fields.

### TestDecisionRegistry

Tests for DecisionRegistry class.

**Inherits from:** unittest.TestCase

#### Methods

- `test_cleanup_all_status_directories(self) -> None`: Test _cleanup_all_status_directories removes all symlinks.
- `test_collect_empty_directory(self) -> None`: Test collecting from empty directory.
- `test_collect_with_adr_files(self) -> None`: Test collecting ADR files.
- `test_edge_case_broken_symlinks_cleanup(self) -> None`: Test that broken symlinks are properly cleaned up.
- `test_edge_case_concurrent_directory_operations(self) -> None`: Test robustness when directories are modified during operations.
- `test_edge_case_empty_decisions_directory(self) -> None`: Test symlink rebuild with no ADR files.
- `test_edge_case_invalid_status_values(self) -> None`: Test handling of ADRs with invalid/non-standard status values.
- `test_edge_case_permission_errors_handling(self) -> None`: Test graceful handling when symlink creation might fail.
- `test_filter(self) -> None`: Test filtering decisions.
- `test_filter_by_standard(self) -> None`: Test filtering decisions by standard reference.
- `test_find(self) -> None`: Test finding specific decision.
- `test_init(self) -> None`: Test registry initialization.
- `test_iter_with_status_filter(self) -> None`: Test iterating with status filter.
- `test_multiple_adrs_same_status_grouping(self) -> None`: Test that multiple ADRs with same status are properly grouped.
- `test_parse_adr_file_no_frontmatter(self) -> None`: Test parsing ADR file without frontmatter.
- `test_parse_date_formats(self) -> None`: Test parsing various date formats.
- `test_rebuild_status_directory_relative_paths(self) -> None`: Test _rebuild_status_directory creates relative symlinks. - But no symlinks
- `test_rebuild_status_symlinks_cleans_existing(self) -> None`: Test that rebuild_status_symlinks cleans up existing symlinks.
- `test_rebuild_status_symlinks_creates_directories(self) -> None`: Test that rebuild_status_symlinks creates status directories and symlinks.
- `test_rebuild_status_symlinks_handles_missing_files(self) -> None`: Test that rebuild_status_symlinks skips ADRs with missing files.
- `test_status_transition_updates_symlinks(self) -> None`: Test that changing ADR status moves symlinks between directories.
- `test_sync_with_symlinks_integration(self) -> None`: Test sync_with_symlinks performs both sync and symlink rebuild.
- `test_write_and_sync(self) -> None`: Test writing registry to YAML file. - default status
- `_setup_test_repo(self, tmpdir) -> Path`: Set up a test repository with required directories.

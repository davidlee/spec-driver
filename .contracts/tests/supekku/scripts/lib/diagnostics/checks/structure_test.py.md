# supekku.scripts.lib.diagnostics.checks.structure_test

Tests for structure checks.

## Functions

- `_make_workspace(tmp_path) -> _FakeWorkspace`: Create a minimal valid workspace structure.

## Classes

### TestCheckOrphanedBundles

Tests for orphaned bundle detection.

**Inherits from:** unittest.TestCase

#### Methods

- `test_bundle_with_dr_and_ip_is_not_orphaned(self) -> None`: Bundle with DR/IP files is not orphaned.
- `test_bundle_with_non_primary_md_warns(self) -> None`: Bundle with .md files but no primary artifact warns.
- `test_empty_bundle_warns(self) -> None`: Empty bundle directory should warn.
- `test_no_orphans_in_normal_structure(self) -> None`: Normal delta bundle with DE-*.md is not orphaned.
- `test_nonexistent_parent_returns_empty(self) -> None`: Non-existent parent directory returns no results.

### TestCheckStructure

Tests for check_structure function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_missing_spec_driver_root(self) -> None`: Missing .spec-driver/ should fail and short-circuit.
- `test_missing_subdirectory_warns(self) -> None`: Missing required subdirectory should warn.
- `test_valid_workspace(self) -> None`: All directories present produces all-pass.

### _FakeWorkspace

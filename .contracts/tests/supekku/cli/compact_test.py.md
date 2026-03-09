# supekku.cli.compact_test

Tests for admin compact CLI command.

## Constants

- `BLOATED_DELTA` - Minimal delta frontmatter with empty defaults (compactable)
- `MINIMAL_DELTA` - Already minimal — nothing to compact
- `runner`

## Functions

- `_root_flag(root) -> list[str]`
- `_write_delta(root, frontmatter, body) -> Path`: Write a delta file in the expected directory structure.

## Classes

### TestCompactDelta

Tests for `spec-driver compact delta`.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_compact_preserves_body(self) -> None`
- `test_compact_removes_empty_defaults(self) -> None`
- `test_dry_run_does_not_modify_files(self) -> None`
- `test_dry_run_shows_changes(self) -> None`
- `test_no_changes_needed(self) -> None`
- `test_specific_delta_id(self) -> None`
- `test_unknown_delta_id_fails(self) -> None`

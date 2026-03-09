# supekku.cli.admin_test

Tests for admin CLI command group routing.

## Classes

### AdminGroupTest

Test that admin subcommands are routed correctly.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_admin_backfill_help(self) -> None`
- `test_admin_compact_help(self) -> None`
- `test_admin_help(self) -> None`
- `test_admin_resolve_help(self) -> None`

### OldCommandsRemovedTest

Test that old top-level commands no longer exist.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_backfill_removed(self) -> None`
- `test_compact_removed(self) -> None`
- `test_resolve_removed(self) -> None`
- `test_schema_removed(self) -> None`
- `test_skills_removed(self) -> None`

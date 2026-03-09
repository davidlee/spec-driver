# supekku.cli.complete_test

Tests for complete CLI commands.

## Classes

### CompleteRevisionCommandTest

Test cases for complete revision CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_complete_revision_not_found(self) -> None`: Test error when revision not found.
- `test_complete_revision_success(self) -> None`: Test completing a revision via CLI.
- `test_complete_revision_with_force(self) -> None`: Test completing revision with --force flag.
- `_create_revision(self, revision_id, status) -> Path`: Create a minimal revision file for testing.

### CreateAuditCommandTest

Test cases for create audit CLI command (smoke tests via create app).

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_create_audit_via_cli(self) -> None`: Test creating an audit via CLI.
- `test_create_audit_with_all_options(self) -> None`: Test creating an audit with all CLI options.

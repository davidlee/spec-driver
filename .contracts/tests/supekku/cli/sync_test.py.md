# supekku.cli.sync_test

Tests for sync CLI command.

## Classes

### SyncBacklogDryRunTest

VT-057-sync-dryrun: \_sync_backlog respects dry_run.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_dry_run_does_not_write_registry(self) -> None`: \_sync_backlog(dry_run=True) returns stats but does not write backlog.yaml.
- `test_non_dry_run_writes_registry(self) -> None`: \_sync_backlog(dry_run=False) writes backlog.yaml.

### SyncCommandTest

Test cases for sync CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `tearDown(self) -> None`: Clean up test environment.
- @patch(supekku.cli.sync.\_sync_requirements) @patch(supekku.cli.sync.\_sync_specs) @patch(supekku.cli.sync.find_repo_root) `test_sync_exits_one_when_specs_fail(self, mock_find_repo, mock_sync_specs, mock_sync_reqs) -> None`: Sync should exit 1 when spec sync returns failure.
- @patch(supekku.cli.sync.\_sync_requirements) @patch(supekku.cli.sync.\_sync_specs) @patch(supekku.cli.sync.find_repo_root) `test_sync_exits_zero_when_specs_succeed(self, mock_find_repo, mock_sync_specs, mock_sync_reqs) -> None`: Sync should exit 0 when all sync operations succeed.

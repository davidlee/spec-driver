# supekku.cli.create_test

Tests for create CLI commands.

## Classes

### CreateBacklogCommandsTest

Test cases for backlog creation CLI commands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `tearDown(self) -> None`: Clean up test environment.
- `test_create_improvement(self) -> None`: Test creating an improvement via CLI.
- `test_create_issue(self) -> None`: Test creating an issue via CLI.
- `test_create_issue_json_output(self) -> None`: Test creating an issue with --json flag returns valid JSON.
- `test_create_issue_with_spaces_in_title(self) -> None`: Test creating an issue with spaces in title creates proper slug.
- `test_create_multiple_issues_increments_id(self) -> None`: Test that creating multiple issues increments the ID.
- `test_create_problem(self) -> None`: Test creating a problem via CLI.
- `test_create_problem_json_output(self) -> None`: Test creating a problem with --json flag returns valid JSON.
- `test_create_risk(self) -> None`: Test creating a risk via CLI.
- `test_create_risk_json_output(self) -> None`: Test creating a risk with --json flag returns valid JSON.

### CreateDeltaFromBacklogTest

VT-077-from-backlog: --from-backlog as boolean flag.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_from_backlog_accepts_valid_issue_id(self) -> None`: --from-backlog ISSUE-NNN passes validation, fails on lookup.
- `test_from_backlog_accepts_valid_risk_id(self) -> None`: --from-backlog RISK-NNN passes validation.
- `test_from_backlog_no_longer_swallows_flags(self) -> None`: --from-backlog --help should show help, not validation error.

This is the root cause fix for ISSUE-043: --from-backlog is now
a boolean flag that doesn't greedily consume the next token.
- `test_from_backlog_with_non_id_name_shows_error(self) -> None`: --from-backlog with non-ID name shows format error.
- `test_from_backlog_without_name_shows_error(self) -> None`: --from-backlog without a name argument shows usage error.
- `_has_id_validation_error(self, result) -> bool`: Check output for backlog ID format error.
- `_output(self, result)`: Combine stdout and stderr for assertion.

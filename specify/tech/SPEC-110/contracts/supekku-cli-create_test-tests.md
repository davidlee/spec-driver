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

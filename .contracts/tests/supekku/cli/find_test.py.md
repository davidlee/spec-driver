# supekku.cli.find_test

Tests for find CLI commands.

## Classes

### FindAdrCommandTest

Test cases for find adr CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_find_adr_exact_match(self) -> None`: Test finding ADR with exact ID.
- `test_find_adr_wildcard(self) -> None`: Test finding ADRs with wildcard pattern.

### FindCardCommandTest

Test cases for find card CLI command (existing).

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_find_card_wildcard(self) -> None`: Test finding cards with ID pattern.

### FindDeltaCommandTest

Test cases for find delta CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_find_delta_exact_match(self) -> None`: Test finding delta with exact ID.
- `test_find_delta_wildcard(self) -> None`: Test finding deltas with wildcard pattern.

### FindNewSubcommandsTest

Integration tests for Phase 2 find subcommands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_find_audit_wildcard(self) -> None`
- `test_find_improvement_wildcard(self) -> None`
- `test_find_issue_wildcard(self) -> None`
- `test_find_plan_exact(self) -> None`
- `test_find_plan_no_match(self) -> None`
- `test_find_plan_wildcard(self) -> None`
- `test_find_requirement(self) -> None`

### FindPolicyCommandTest

Test cases for find policy CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_find_policy_wildcard(self) -> None`: Test finding policies with wildcard pattern.

### FindRevisionCommandTest

Test cases for find revision CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_find_revision_wildcard(self) -> None`: Test finding revisions with wildcard pattern.

### FindRevisionRegressionTest

Regression tests for find revision — must pass before AND after migration.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_find_revision_exact(self) -> None`: find revision RE-001 returns its path.
- `test_find_revision_no_match(self) -> None`: find revision with nonexistent pattern returns empty (exit 0).
- `test_find_revision_numeric_shorthand(self) -> None`: find revision 1 resolves to RE-001.
- `test_find_revision_wildcard(self) -> None`: find revision RE-* returns paths for all revisions.

### FindSpecCommandTest

Test cases for find spec CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_find_spec_case_insensitive(self) -> None`: Test finding specs is case-insensitive. - No output, but success
- `test_find_spec_exact_match(self) -> None`: Test finding spec with exact ID.
- `test_find_spec_no_match(self) -> None`: Test finding spec with no matches returns success (Unix find behavior).
- `test_find_spec_question_mark_pattern(self) -> None`: Test finding specs with ? pattern (single char match).
- `test_find_spec_wildcard(self) -> None`: Test finding specs with wildcard pattern.

### FindStandardCommandTest

Test cases for find standard CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_find_standard_wildcard(self) -> None`: Test finding standards with wildcard pattern.

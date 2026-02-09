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

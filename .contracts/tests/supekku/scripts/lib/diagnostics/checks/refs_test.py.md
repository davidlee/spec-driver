# supekku.scripts.lib.diagnostics.checks.refs_test

Tests for cross-reference checks.

## Classes

### TestCheckRefs

Tests for check_refs function.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- @patch(supekku.scripts.lib.diagnostics.checks.refs.validate_workspace) `test_all_results_have_refs_category(self, mock_validate) -> None`: Every result should use the refs category.
- @patch(supekku.scripts.lib.diagnostics.checks.refs.validate_workspace) `test_error_translates_to_fail(self, mock_validate) -> None`: Validator error level should translate to fail status.
- @patch(supekku.scripts.lib.diagnostics.checks.refs.validate_workspace) `test_info_translates_to_pass(self, mock_validate) -> None`: Validator info level should translate to pass status.
- @patch(supekku.scripts.lib.diagnostics.checks.refs.validate_workspace) `test_multiple_issues(self, mock_validate) -> None`: Multiple issues should produce one result per issue.
- @patch(supekku.scripts.lib.diagnostics.checks.refs.validate_workspace) `test_no_issues_passes(self, mock_validate) -> None`: No validation issues should produce a single pass result.
- @patch(supekku.scripts.lib.diagnostics.checks.refs.validate_workspace) `test_validator_exception_produces_fail(self, mock_validate) -> None`: If the validator raises, check_refs should return a fail result.
- @patch(supekku.scripts.lib.diagnostics.checks.refs.validate_workspace) `test_warning_translates_to_warn(self, mock_validate) -> None`: Validator warning level should translate to warn status.

### \_FakeWorkspace

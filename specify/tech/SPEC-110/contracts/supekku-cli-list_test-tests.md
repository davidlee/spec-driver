# supekku.cli.list_test

Tests for list CLI commands (backlog shortcuts).

## Classes

### ListBacklogShortcutsTest

Test cases for backlog listing shortcut commands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment with sample backlog entries.
- `tearDown(self) -> None`: Clean up test environment.
- `test_equivalence_with_list_backlog(self) -> None`: Test that shortcuts are equivalent to list backlog -k.
- `test_list_improvements(self) -> None`: Test listing improvements via shortcut command. - Should not show issues
- `test_list_issues(self) -> None`: Test listing issues via shortcut command.
- `test_list_issues_empty_result(self) -> None`: Test listing issues with filter that returns no results.
- `test_list_issues_json_format(self) -> None`: Test listing issues with JSON output. - doesn't match "one"
- `test_list_issues_with_status_filter(self) -> None`: Test listing issues with status filter. - Should not show issues
- `test_list_issues_with_substring_filter(self) -> None`: Test listing issues with substring filter. - resolved, not open
- `test_list_problems(self) -> None`: Test listing problems via shortcut command. - Should not show problems
- `test_list_risks(self) -> None`: Test listing risks via shortcut command. - Should not show issues
- `test_regexp_filter(self) -> None`: Test listing with regexp filter.
- `test_tsv_format(self) -> None`: Test listing with TSV format.
- `_create_sample_improvement(self, impr_id, title, status) -> None`: Helper to create a sample improvement file.
- `_create_sample_issue(self, issue_id, title, status) -> None`: Helper to create a sample issue file.
- `_create_sample_problem(self, prob_id, title, status) -> None`: Helper to create a sample problem file.
- `_create_sample_risk(self, risk_id, title, status) -> None`: Helper to create a sample risk file.

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

### ListRequirementsCategoryFilterTest

Test cases for requirements with category filtering.

VT-017-003: Category filtering tests
VT-017-004: Category display tests

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment with requirements registry including categories.
- `tearDown(self) -> None`: Clean up test environment.
- `test_category_column_in_json_output(self) -> None`: VT-017-004: Test category field in JSON format. - category should be present
- `test_category_column_in_table_output(self) -> None`: VT-017-004: Test category column appears in table output.
- `test_category_column_in_tsv_output(self) -> None`: VT-017-004: Test category column in TSV format.
- `test_category_filter_case_insensitive(self) -> None`: VT-017-003: Test --category with -i flag for case-insensitive matching.
- `test_category_filter_case_sensitive(self) -> None`: VT-017-003: Test --category filter is case-sensitive by default.
- `test_category_filter_combined_with_other_filters(self) -> None`: VT-017-003: Test --category combined with --kind filter.
- `test_category_filter_exact_match(self) -> None`: VT-017-003: Test --category filter with exact match.
- `test_category_filter_excludes_uncategorized(self) -> None`: VT-017-003: Test --category filter excludes requirements with null category.
- `test_category_filter_substring_match(self) -> None`: VT-017-003: Test --category filter with substring matching. - performance, not auth
- `test_empty_result_with_category_filter(self) -> None`: VT-017-003: Test category filter with no matches returns empty gracefully.
- `test_regexp_filter_category_case_insensitive(self) -> None`: VT-017-003: Test -r with -i flag makes category search case-insensitive. - category: security
- `test_regexp_filter_includes_category(self) -> None`: VT-017-003: Test -r regexp filter searches category field.
- `test_uncategorized_requirements_show_placeholder(self) -> None`: VT-017-004: Test uncategorized requirements display correctly.

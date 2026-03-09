# supekku.cli.list_test

Tests for list CLI commands (backlog shortcuts).

## Constants

- `runner` - noqa: E402

## Functions

- `_make_memory_record(memory_id) -> MemoryRecord`: Build a minimal MemoryRecord for list tests.

## Classes

### BacklogPrioritizationTest

Test cases for backlog prioritization feature (VT-015-005).

Tests the --prioritize flag and interactive editor workflow integration.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment with sample backlog entries and registry.
- `tearDown(self) -> None`: Clean up test environment.
- `test_list_backlog_uses_priority_order(self) -> None`: Test that list backlog displays items in priority order by default.
- `test_order_by_id_flag(self) -> None`: Test --order id flag provides chronological ordering.
- `_create_sample_improvement(self, impr_id, title, status) -> None`: Helper to create a sample improvement file.
- `_create_sample_issue(self, issue_id, title, status, severity) -> None`: Helper to create a sample issue file.

### ListBacklogSeverityFilterTest

Test cases for --severity filter on backlog list commands (VT-DE-074).

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment with backlog entries at different severities.
- `tearDown(self) -> None`
- `test_list_backlog_severity_filter(self) -> None`: --severity on list backlog filters to matching severity.
- `test_list_improvements_severity_filter(self) -> None`: --severity on list improvements filters correctly. - p3
- `test_list_issues_severity_filter(self) -> None`: --severity on list issues filters correctly. - p3
- `test_list_problems_severity_filter(self) -> None`: --severity on list problems filters correctly. - resolved, excluded by default
- `test_list_risks_severity_filter(self) -> None`: --severity on list risks filters correctly. - p3
- `test_severity_combined_with_status(self) -> None`: --severity combined with --status narrows results.
- `test_severity_filter_case_insensitive(self) -> None`: --severity matching is case-insensitive. - p2
- `test_severity_filter_no_matches(self) -> None`: --severity with no matches returns empty.
- `_create_item(self, kind, item_id, title, status, severity) -> None`

### ListBacklogShortcutsTest

Test cases for backlog listing shortcut commands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment with sample backlog entries.
- `tearDown(self) -> None`: Clean up test environment.
- `test_equivalence_with_list_backlog(self) -> None`: Test that shortcuts are equivalent to list backlog -k.
- `test_list_improvements(self) -> None`: Test listing improvements via shortcut command. - Should not show issues
- `test_list_issues(self) -> None`: Test listing issues via shortcut command.
- `test_list_issues_empty_result(self) -> None`: Test listing issues with filter that returns no results. - resolved, filtered by default
- `test_list_issues_json_format(self) -> None`: Test listing issues with JSON output. - doesn't match "one"
- `test_list_issues_with_status_filter(self) -> None`: Test listing issues with status filter. - Should not show issues
- `test_list_issues_with_substring_filter(self) -> None`: Test listing issues with substring filter. - resolved, not open
- `test_list_problems(self) -> None`: Test listing problems via shortcut command. - Should not show problems
- `test_list_risks(self) -> None`: Test listing risks via shortcut command. - Should not show issues
- `test_regexp_filter(self) -> None`: Test listing with regexp filter.
- `test_tsv_format(self) -> None`: Test listing with TSV format. - resolved, filtered by default
- `_create_sample_improvement(self, impr_id, title, status) -> None`: Helper to create a sample improvement file.
- `_create_sample_issue(self, issue_id, title, status) -> None`: Helper to create a sample issue file.
- `_create_sample_problem(self, prob_id, title, status) -> None`: Helper to create a sample problem file.
- `_create_sample_risk(self, risk_id, title, status) -> None`: Helper to create a sample risk file.

### ListDeltasRelationFilterTest

VT-085-002: --related-to, --relation, --refs on list deltas.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_refs_column_table(self) -> None`
- `test_refs_column_tsv(self) -> None`
- `test_related_to_case_insensitive(self) -> None`
- `test_related_to_finds_matching_delta(self) -> None`
- `test_related_to_no_match(self) -> None`
- `test_relation_bad_format_errors(self) -> None`
- `test_relation_type_target(self) -> None`
- `_create_deltas(self) -> None`

### ListFilterBackfillTest

Integration tests for --filter backfill on list commands (VT-list-filters).

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_list_deltas_filter_by_id(self) -> None`
- `test_list_deltas_filter_narrows(self) -> None`
- `test_list_deltas_filter_no_match(self) -> None`
- `_create_deltas(self) -> None`

### ListPlansTest

Integration tests for list plans command (VT-list-plans).

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_list_plans_basic(self) -> None`
- `test_list_plans_filter_no_match(self) -> None`
- `test_list_plans_json(self) -> None`
- `test_list_plans_status_filter(self) -> None`
- `test_list_plans_substring_filter(self) -> None`
- `_create_plan(self, delta_id, plan_id, name, status) -> None`

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

### ListSpecsCategoryFilterTest

VT-030-003: list specs --category and --c4-level filters.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_c4_level_filter(self) -> None`: --c4-level code shows only code-level tech specs.
- `test_category_all_shows_everything(self) -> None`: --category all disables category filtering for tech specs. - product → always shown
- `test_category_assembly_only(self) -> None`: --category assembly shows only assembly tech specs. - products always pass
- `test_category_multi_value(self) -> None`: --category unit,assembly shows both but excludes unknown. - unknown ≠ assembly
- `test_category_unit_only(self) -> None`: --category unit shows only unit tech specs (plus products).
- `test_default_hides_unit_specs(self) -> None`: Default listing shows assembly + unknown but hides unit specs.
- `test_kind_product_ignores_category(self) -> None`: --kind product is unaffected by --category. - kind=tech excludes products
- `test_kind_tech_with_category_filter(self) -> None`: --kind tech + default category still hides unit specs. - c4_level: unknown
- `_create_spec(self, tech_dir, spec_id, slug, name) -> None`

### ListSpecsRelationFilterTest

VT-085-002: --related-to, --relation, --refs on list specs.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_refs_column_tsv(self) -> None`
- `test_related_to_via_informed_by(self) -> None`
- `test_related_to_via_relations(self) -> None`
- `test_relation_filter(self) -> None`
- `_create_specs(self) -> None`

### TestListMemoriesStale

Tests for --stale flag on list memories command.

#### Methods

- `test_stale_flag_empty_registry(self) -> None`: --stale with no memories exits cleanly.
- `test_stale_flag_produces_tiered_output(self) -> None`: --stale flag shows tiered staleness output.

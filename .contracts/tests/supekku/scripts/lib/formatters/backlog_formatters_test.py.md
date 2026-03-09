# supekku.scripts.lib.formatters.backlog_formatters_test

Tests for backlog_formatters module.

## Classes

### TestBacklogExternalFields

Tests for ext_id/ext_url support in backlog formatters (VT-067-002).

**Inherits from:** unittest.TestCase

#### Methods

- `test_details_with_ext_id_and_url(self) -> None`: Test detail formatter shows ext_id with url.
- `test_details_with_ext_id_only(self) -> None`: Test detail formatter shows ext_id without url.
- `test_details_without_ext_id_omits_line(self) -> None`: Test detail formatter omits External line when no ext_id.
- `test_json_includes_ext_fields(self) -> None`: Test JSON output includes ext_id and ext_url when present.
- `test_json_omits_ext_fields_when_empty(self) -> None`: Test JSON output omits ext_id/ext_url when empty.
- `test_table_show_external_includes_column(self) -> None`: Test table output includes ExtID column when show_external=True.
- `test_tsv_no_external_omits_ext_id(self) -> None`: Test TSV output omits ext_id when show_external=False.
- `test_tsv_show_external_inserts_ext_id(self) -> None`: Test TSV output includes ext_id after ID when show_external=True.

### TestFormatBacklogDetails

Tests for format_backlog_details function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_full_issue(self) -> None`: Test formatting issue with all fields.
- `test_format_minimal_backlog_item(self) -> None`: Test formatting backlog item with minimal fields.
- `test_format_risk_with_likelihood(self) -> None`: Test formatting risk with likelihood field.

### TestFormatBacklogListJson

Tests for format_backlog_list_json function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_backlog_item_with_all_fields(self) -> None`: Test formatting backlog item with all possible fields.
- `test_format_minimal_backlog_item(self) -> None`: Test formatting backlog item with minimal fields.

### TestFormatBacklogListTable

Tests for format_backlog_list_table function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_empty_list_json(self) -> None`: Test formatting empty backlog list as JSON.
- `test_format_empty_list_table(self) -> None`: Test formatting empty backlog list as table.
- `test_format_empty_list_tsv(self) -> None`: Test formatting empty backlog list as TSV.
- `test_format_multiple_backlog_items(self) -> None`: Test formatting multiple backlog items of different kinds.
- `test_format_problem_without_severity(self) -> None`: Test formatting problem item without severity field.
- `test_format_single_issue_json(self) -> None`: Test formatting single issue as JSON.
- `test_format_single_issue_table(self) -> None`: Test formatting single issue as table.
- `test_format_single_issue_tsv(self) -> None`: Test formatting single issue as TSV.
- `test_format_with_timestamps(self) -> None`: Test formatting backlog item with timestamps.

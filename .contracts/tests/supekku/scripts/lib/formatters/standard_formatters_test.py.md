# supekku.scripts.lib.formatters.standard_formatters_test

Tests for standard_formatters module.

## Classes

### TestFormatStandardDetails

Tests for format_standard_details function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_default_status_standard(self) -> None`: Test formatting with 'default' status (unique to standards).
- `test_format_empty_lists_omitted(self) -> None`: Test that empty list fields are not displayed.
- `test_format_full_standard(self) -> None`: Test formatting with all fields populated.
- `test_format_minimal_standard(self) -> None`: Test formatting with minimal required fields.
- `test_format_preserves_order(self) -> None`: Test that output maintains logical field ordering.
- `test_format_with_backlinks(self) -> None`: Test formatting with backlinks.
- `test_format_with_decision_and_policy_backlinks(self) -> None`: Test formatting standards with decision and policy backlinks.
- `test_format_with_multiple_owners(self) -> None`: Test formatting with multiple owners.

### TestFormatStandardListJson

Tests for format_standard_list_json function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_multiple_standards(self) -> None`: Test JSON formatting with multiple standards.
- `test_format_single_standard(self) -> None`: Test JSON formatting with single standard.
- `test_format_standard_without_updated_date(self) -> None`: Test JSON formatting with standard missing updated date.

### TestFormatStandardListTable

Tests for format_standard_list_table function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_json_via_table_function(self) -> None`: Test JSON formatting through format_standard_list_table.
- `test_format_missing_updated_date(self) -> None`: Test formatting with missing updated date shows em dash.
- `test_format_table_basic(self) -> None`: Test table formatting with basic standards.
- `test_format_title_prefix_removal(self) -> None`: Test that STD-XXX: prefix is removed from titles in table view.
- `test_format_tsv(self) -> None`: Test TSV formatting.

### TestStandardExternalFields

Tests for ext_id/ext_url support in standard formatters (VT-067-002).

**Inherits from:** unittest.TestCase

#### Methods

- `test_details_with_ext_id_and_url(self) -> None`: Test detail formatter shows ext_id with url.
- `test_details_with_ext_id_only(self) -> None`: Test detail formatter shows ext_id without url.
- `test_details_without_ext_id_omits_line(self) -> None`: Test detail formatter omits External line when no ext_id.
- `test_json_includes_ext_fields(self) -> None`: Test JSON output includes ext_id and ext_url when present.
- `test_json_omits_ext_fields_when_empty(self) -> None`: Test JSON output omits ext_id/ext_url when empty.
- `test_table_show_external_includes_column(self) -> None`: Test table includes ExtID column when show_external=True.
- `test_tsv_no_external_omits_ext_id(self) -> None`: Test TSV omits ext_id when show_external=False.
- `test_tsv_show_external_inserts_ext_id(self) -> None`: Test TSV includes ext_id after ID when show_external=True.

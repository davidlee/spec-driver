# supekku.scripts.lib.formatters.drift_formatters_test

Tests for drift_formatters module.

## Functions

- `_make_entry(entry_id, title) -> DriftEntry`
- `_make_ledger(ledger_id, name, entries) -> DriftLedger`

## Classes

### TestFormatDriftDetails

Tests for format_drift_details.

**Inherits from:** unittest.TestCase

#### Methods

- `test_basic_details(self) -> None`
- `test_details_timestamps(self) -> None`
- `test_details_with_body(self) -> None`
- `test_details_with_delta_ref(self) -> None`
- `test_details_with_entries(self) -> None`
- `test_details_without_delta_ref(self) -> None`
- `test_entry_summary_minimal(self) -> None`: Entry summary with only id and title.

### TestFormatDriftDetailsJson

Tests for format_drift_details_json.

**Inherits from:** unittest.TestCase

#### Methods

- `test_basic_json(self) -> None`
- `test_json_includes_path(self) -> None`
- `test_json_omits_empty_optional_fields(self) -> None`
- `test_json_with_entries(self) -> None`

### TestFormatDriftListTable

Tests for format_drift_list_table.

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_list_json(self) -> None`
- `test_empty_list_table(self) -> None`
- `test_empty_list_tsv(self) -> None`
- `test_entry_count_in_table(self) -> None`
- `test_multiple_ledgers(self) -> None`
- `test_single_ledger_json(self) -> None`
- `test_single_ledger_table(self) -> None`
- `test_single_ledger_tsv(self) -> None`
- `test_truncate_option(self) -> None`

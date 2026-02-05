# supekku.scripts.lib.formatters.card_formatters_test

Tests for card formatters.

VT-021-006: list cards output formats (table/json/tsv)

## Classes

### TestCardFormatters

VT-021-006: Output format consistency.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_card_details(self) -> None`: Format card as human-readable detail view.
- `test_format_card_details_without_created(self) -> None`: Handle card without created date.
- `test_format_card_details_without_lane(self) -> None`: Handle card without lane.
- `test_format_card_list_json_valid(self) -> None`: Format cards as valid JSON array.
- `test_format_card_list_table_aligned(self) -> None`: Format cards as aligned table.
- `test_format_card_list_tsv(self) -> None`: Format cards as tab-separated values.
- `test_format_empty_card_list(self) -> None`: Handle empty card list gracefully.

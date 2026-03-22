# supekku.scripts.lib.formatters.table_utils_test

Tests for table rendering utilities.

## Classes

### TestColumnWidthCalculation

Test column width calculation.

#### Methods

- `test_calculate_column_widths_equal_distribution(self)`: Test that columns get equal width distribution.
- `test_calculate_column_widths_narrow_terminal(self)`: Test handling of very narrow terminal.
- `test_calculate_column_widths_zero_columns(self)`: Test handling of zero columns.

### TestFormatListTable

Tests for the generic format_list_table helper.

#### Methods

- `test_custom_column_widths(self)`: Custom column_widths callback is used when provided.
- `test_custom_column_widths_not_called_without_truncate(self)`: column_widths callback should not be called when truncate is False.
- `test_empty_items_json(self)` - headers still rendered
- `test_empty_items_table(self)`
- `test_empty_items_tsv(self)`
- `test_json_format_delegates_to_callback(self)`
- `test_table_format_is_default(self)`
- `test_table_format_renders_columns_and_data(self)` - type: ignore[invalid-argument-type]
- `test_title_appears_in_table(self)`
- `test_truncate_false_preserves_all_content(self)`
- `test_truncate_true_shortens_content(self)`
- `test_tsv_format_uses_tsv_row_callback(self)`
- `_call(self, items)`
- @staticmethod `_make_item(item_id, name, status) -> dict`
- @staticmethod `_prepare_row(item) -> list[str]`
- @staticmethod `_prepare_tsv_row(item) -> list[str]`
- @staticmethod `_to_json(items) -> str`

### TestJsonFormatting

Test JSON formatting.

#### Methods

- `test_format_as_json_basic(self)`: Test basic JSON formatting.
- `test_format_as_json_empty_list(self)`: Test JSON formatting with empty list.
- `test_format_as_json_with_complex_types(self)`: Test JSON formatting with dates and paths.

### TestRowAddition

Test adding rows to tables.

#### Methods

- `test_add_multiple_rows(self)`: Test adding multiple rows.
- `test_add_row_no_max_widths(self)`: Test adding row when max_widths is None.
- `test_add_row_with_truncation(self)`: Test adding row with truncation.
- `test_add_row_without_truncation(self)`: Test adding row without truncation.
- `test_empty_string_not_truncated(self)`: Empty string is handled without error. - no leaked markup
- `test_mixed_markup_and_plain_row(self)`: Row with mixed markup and plain text columns truncates correctly.
- `test_plain_text_truncation_still_works(self)`: Plain strings (no markup) are still truncated correctly.
- `test_short_markup_not_truncated(self)`: Markup string whose display text fits within max_width is not truncated.
- `test_truncation_max_width_lte_3(self)`: Edge case: max_width <= 3 truncates without ellipsis.
- `test_truncation_of_long_markup_adds_ellipsis(self)`: Long display text with markup is truncated with ellipsis. - no leaked markup tags
- `test_truncation_preserves_rich_markup_style(self)`: Truncation of Rich markup strings preserves styling on visible text.

### TestTableCreation

Test table creation.

#### Methods

- `test_create_table_basic(self)`: Test creating a basic table.
- `test_create_table_empty_columns(self)`: Test creating table with no columns.
- `test_create_table_no_header(self)`: Test creating table without header.
- `test_create_table_with_title(self)`: Test creating table with title.

### TestTableRendering

Test table rendering.

#### Methods

- `test_render_empty_table(self)`: Test rendering an empty table.
- `test_render_table_basic(self)`: Test rendering a basic table.

### TestTerminalDetection

Test terminal width and TTY detection.

#### Methods

- `test_get_terminal_width_returns_int(self)`: Test that get_terminal_width returns a positive integer.
- `test_is_tty_returns_bool(self)`: Test that is_tty returns a boolean.

### TestTsvFormatting

Test TSV formatting.

#### Methods

- `test_format_as_tsv_basic(self)`: Test basic TSV formatting.
- `test_format_as_tsv_empty(self)`: Test TSV formatting with empty list.
- `test_format_as_tsv_single_row(self)`: Test TSV formatting with single row.
- `test_format_as_tsv_with_numeric_values(self)`: Test TSV formatting with mixed types.

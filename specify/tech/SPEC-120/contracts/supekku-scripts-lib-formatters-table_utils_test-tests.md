# supekku.scripts.lib.formatters.table_utils_test

Tests for table rendering utilities.

## Classes

### TestColumnWidthCalculation

Test column width calculation.

#### Methods

- `test_calculate_column_widths_equal_distribution(self)`: Test that columns get equal width distribution.
- `test_calculate_column_widths_narrow_terminal(self)`: Test handling of very narrow terminal.
- `test_calculate_column_widths_zero_columns(self)`: Test handling of zero columns.

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

### TestTextTruncation

Test text truncation.

#### Methods

- `test_truncate_text_custom_suffix(self)`: Test truncation with custom suffix.
- `test_truncate_text_exact_width(self)`: Test text at exact max width.
- `test_truncate_text_long_text(self)`: Test truncation of long text.
- `test_truncate_text_no_truncation_needed(self)`: Test that short text is not truncated.
- `test_truncate_text_width_smaller_than_suffix(self)`: Test handling when max_width is smaller than suffix.

### TestTsvFormatting

Test TSV formatting.

#### Methods

- `test_format_as_tsv_basic(self)`: Test basic TSV formatting.
- `test_format_as_tsv_empty(self)`: Test TSV formatting with empty list.
- `test_format_as_tsv_single_row(self)`: Test TSV formatting with single row.
- `test_format_as_tsv_with_numeric_values(self)`: Test TSV formatting with mixed types.

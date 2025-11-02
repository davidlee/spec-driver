# supekku.scripts.lib.formatters.table_utils

Shared table rendering utilities using rich.

Pure formatting functions for rendering tabular data with smart truncation.

## Functions

- `add_row_with_truncation(table, row_data, max_widths, no_truncate) -> None`: Add a row to the table with optional smart truncation.

Args:
  table: Rich Table instance
  row_data: Data for each column
  max_widths: Dictionary mapping column index to max width
  no_truncate: If True, don't truncate any fields
- `calculate_column_widths(terminal_width, num_columns, reserved_padding) -> dict[Tuple[int, int]]`: Calculate maximum width for each column with equal distribution.

Args:
  terminal_width: Total available width
  num_columns: Number of columns to distribute width across
  reserved_padding: Reserved space for borders/padding per column

Returns:
  Dictionary mapping column index to max width
- `create_table(columns, title, show_header) -> Table`: Create a rich Table with standard styling.

Args:
  columns: Column names
  title: Optional table title
  show_header: Whether to show column headers (default: True)

Returns:
  Configured rich Table instance
- `format_as_json(items) -> str`: Format items as JSON array with standard structure.

Args:
  items: List of item dictionaries

Returns:
  JSON string with structure: {"items": [...]}
- `format_as_tsv(rows) -> str`: Format data as tab-separated values.

Args:
  rows: List of rows, each row is a list of column values

Returns:
  TSV string with one row per line
- `get_terminal_width() -> int`: Get current terminal width.

Returns:
  Terminal width in columns. Defaults to 80 if not a TTY.
- `is_tty() -> bool`: Check if stdout is a TTY.

Returns:
  True if stdout is a TTY, False otherwise (pipe, redirect, CI).
- `render_table(table) -> str`: Render a rich Table to string with spec-driver theme.

Args:
  table: Rich Table instance

Returns:
  Rendered table as string
- `truncate_text(text, max_width, suffix) -> str`: Truncate text to maximum width with ellipsis.

Args:
  text: Text to truncate
  max_width: Maximum width (including suffix)
  suffix: Suffix to append if truncated (default: "...")

Returns:
  Truncated text with suffix if needed, or original if within width

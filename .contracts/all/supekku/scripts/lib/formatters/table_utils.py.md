# supekku.scripts.lib.formatters.table_utils

Shared table rendering utilities using rich.

Pure formatting functions for rendering tabular data with smart truncation.

## Functions

- `add_row_with_truncation(table, row_data, max_widths) -> None`: Add a row to the table with optional markup-aware truncation.

Uses `rich.text.Text.from_markup()` to measure display width (visible
characters only), so Rich markup tags are never counted toward the width
budget. Truncated `Text` objects preserve styling on the remaining
characters.

Args:
table: Rich Table instance
row_data: Data for each column (may contain Rich markup)
max_widths: Dictionary mapping column index to max width.
When `None`, no truncation is applied.

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

- `format_list_table(items) -> str`: Generic list-table formatter with json/tsv/table dispatch.

Eliminates the repeated dispatch + table-setup boilerplate shared by all
`format_*_list_table` functions. Callers supply only the variable parts:
column definitions, per-item row preparation, and serialisation callbacks.

Args:
items: Sequence of domain objects to render.
columns: Column header names for the table.
title: Table title.
prepare*row: `(item) -> [cell, ...]` for rich-table rows (may include
markup).
prepare_tsv_row: `(item) -> [cell, ...]` for plain TSV rows (no markup).
to_json: `(items) -> str` for JSON serialisation of the full list.
format_type: Output format — `"table"` (default), `"json"`, or
`"tsv"`.
truncate: When \_True*, truncate cell content to fit terminal width.
column*widths: Optional `(terminal_width) -> {col_idx: width}` for
custom width distribution. Only called when \_truncate* is True.
Falls back to equal distribution via :func:`calculate_column_widths`.

Returns:
Formatted string in the requested format.

- `get_terminal_width() -> int`: Get current terminal width.

Returns:
Terminal width in columns. Defaults to 80 if not a TTY.

- `governance_5col_widths(terminal_width) -> dict[Tuple[int, int]]`: Column widths for the common ID / Title / Tags / Status / Updated layout.

Used by decision, policy, and standard formatters which share identical
column structure.

Args:
terminal_width: Available terminal width.

Returns:
Column-index-to-width mapping with flex space allocated to Title.

- `is_tty() -> bool`: Check if stdout is a TTY.

Returns:
True if stdout is a TTY, False otherwise (pipe, redirect, CI).

- `render_table(table) -> str`: Render a rich Table to string with spec-driver theme.

Args:
table: Rich Table instance

Returns:
Rendered table as string

"""Shared table rendering utilities using rich.

Pure formatting functions for rendering tabular data with smart truncation.
"""

from __future__ import annotations

import json
import os
import shutil
from typing import TYPE_CHECKING, Any

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from supekku.scripts.lib.formatters.theme import SPEC_DRIVER_THEME

if TYPE_CHECKING:
  from collections.abc import Callable, Sequence


def get_terminal_width() -> int:
  """Get current terminal width.

  Returns:
    Terminal width in columns. Defaults to 80 if not a TTY.
  """
  try:
    return shutil.get_terminal_size().columns
  except (AttributeError, ValueError, OSError):
    # Not a TTY or unable to determine - use default
    return 80


def is_tty() -> bool:
  """Check if stdout is a TTY.

  Returns:
    True if stdout is a TTY, False otherwise (pipe, redirect, CI).
  """
  return os.isatty(1)


def calculate_column_widths(
  terminal_width: int,
  num_columns: int,
  reserved_padding: int = 4,
) -> dict[int, int]:
  """Calculate maximum width for each column with equal distribution.

  Args:
    terminal_width: Total available width
    num_columns: Number of columns to distribute width across
    reserved_padding: Reserved space for borders/padding per column

  Returns:
    Dictionary mapping column index to max width
  """
  if num_columns <= 0:
    return {}

  # Reserve space for table borders and padding
  total_reserved = reserved_padding * num_columns
  available_width = max(terminal_width - total_reserved, num_columns * 10)

  # Distribute equally
  col_width = available_width // num_columns

  return dict.fromkeys(range(num_columns), col_width)


def create_table(
  columns: Sequence[str],
  title: str | None = None,
  show_header: bool = True,
) -> Table:
  """Create a rich Table with standard styling.

  Args:
    columns: Column names
    title: Optional table title
    show_header: Whether to show column headers (default: True)

  Returns:
    Configured rich Table instance
  """
  table = Table(
    title=title,
    show_header=show_header,
    show_lines=False,
    pad_edge=False,
    collapse_padding=True,
    box=box.ROUNDED,
    border_style="table.border",
  )

  for col in columns:
    table.add_column(col, overflow="fold")

  return table


def add_row_with_truncation(
  table: Table,
  row_data: Sequence[str],
  max_widths: dict[int, int] | None = None,
) -> None:
  """Add a row to the table with optional markup-aware truncation.

  Uses ``rich.text.Text.from_markup()`` to measure display width (visible
  characters only), so Rich markup tags are never counted toward the width
  budget.  Truncated ``Text`` objects preserve styling on the remaining
  characters.

  Args:
    table: Rich Table instance
    row_data: Data for each column (may contain Rich markup)
    max_widths: Dictionary mapping column index to max width.
      When ``None``, no truncation is applied.
  """
  if max_widths is None:
    table.add_row(*row_data)
    return

  truncated: list[Text] = []
  for i, value in enumerate(row_data):
    max_width = max_widths.get(i, 40)  # Default to 40 if not specified
    text = Text.from_markup(value)
    if max_width <= 3:
      text.truncate(max_width)
    elif len(text) > max_width:
      text.truncate(max_width - 3)
      text.append("...")
    truncated.append(text)

  table.add_row(*truncated)


def render_table(table: Table) -> str:
  """Render a rich Table to string with spec-driver theme.

  Args:
    table: Rich Table instance

  Returns:
    Rendered table as string
  """
  console = Console(theme=SPEC_DRIVER_THEME)
  with console.capture() as capture:
    console.print(table)
  return capture.get()


def format_as_json(items: Sequence[dict[str, Any]]) -> str:
  """Format items as JSON array with standard structure.

  Args:
    items: List of item dictionaries

  Returns:
    JSON string with structure: {"items": [...]}
  """
  return json.dumps({"items": list(items)}, indent=2, default=str)


def format_as_tsv(rows: Sequence[Sequence[str]]) -> str:
  """Format data as tab-separated values.

  Args:
    rows: List of rows, each row is a list of column values

  Returns:
    TSV string with one row per line
  """
  return "\n".join("\t".join(str(cell) for cell in row) for row in rows)


def format_list_table(
  items: Sequence[Any],
  *,
  columns: Sequence[str],
  title: str,
  prepare_row: Callable[[Any], Sequence[str]],
  prepare_tsv_row: Callable[[Any], Sequence[str]],
  to_json: Callable[[Sequence[Any]], str],
  format_type: str = "table",
  truncate: bool = False,
  column_widths: Callable[[int], dict[int, int]] | None = None,
) -> str:
  """Generic list-table formatter with json/tsv/table dispatch.

  Eliminates the repeated dispatch + table-setup boilerplate shared by all
  ``format_*_list_table`` functions.  Callers supply only the variable parts:
  column definitions, per-item row preparation, and serialisation callbacks.

  Args:
    items: Sequence of domain objects to render.
    columns: Column header names for the table.
    title: Table title.
    prepare_row: ``(item) -> [cell, ...]`` for rich-table rows (may include
      markup).
    prepare_tsv_row: ``(item) -> [cell, ...]`` for plain TSV rows (no markup).
    to_json: ``(items) -> str`` for JSON serialisation of the full list.
    format_type: Output format — ``"table"`` (default), ``"json"``, or
      ``"tsv"``.
    truncate: When *True*, truncate cell content to fit terminal width.
    column_widths: Optional ``(terminal_width) -> {col_idx: width}`` for
      custom width distribution.  Only called when *truncate* is True.
      Falls back to equal distribution via :func:`calculate_column_widths`.

  Returns:
    Formatted string in the requested format.
  """
  if format_type == "json":
    return to_json(items)

  if format_type == "tsv":
    return format_as_tsv([prepare_tsv_row(item) for item in items])

  # -- table format --
  table = create_table(columns=list(columns), title=title)

  max_widths: dict[int, int] | None = None
  if truncate:
    tw = get_terminal_width()
    if column_widths is not None:
      max_widths = column_widths(tw)
    else:
      max_widths = calculate_column_widths(tw, len(columns))

  for item in items:
    row = prepare_row(item)
    add_row_with_truncation(table, row, max_widths=max_widths)

  return render_table(table)


def governance_5col_widths(terminal_width: int) -> dict[int, int]:
  """Column widths for the common ID / Title / Tags / Status / Updated layout.

  Used by decision, policy, and standard formatters which share identical
  column structure.

  Args:
    terminal_width: Available terminal width.

  Returns:
    Column-index-to-width mapping with flex space allocated to Title.
  """
  reserved = 10  # borders + padding
  id_width = 10
  tags_width = 20
  status_width = 12
  updated_width = 10
  title_width = max(
    terminal_width - id_width - tags_width - status_width - updated_width - reserved,
    20,
  )
  return {
    0: id_width,
    1: title_width,
    2: tags_width,
    3: status_width,
    4: updated_width,
  }

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

from supekku.scripts.lib.formatters.theme import SPEC_DRIVER_THEME

if TYPE_CHECKING:
  from collections.abc import Sequence


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


def truncate_text(text: str, max_width: int, suffix: str = "...") -> str:
  """Truncate text to maximum width with ellipsis.

  Args:
    text: Text to truncate
    max_width: Maximum width (including suffix)
    suffix: Suffix to append if truncated (default: "...")

  Returns:
    Truncated text with suffix if needed, or original if within width
  """
  if len(text) <= max_width:
    return text

  if max_width <= len(suffix):
    return suffix[:max_width]

  return text[: max_width - len(suffix)] + suffix


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
  no_truncate: bool = False,
) -> None:
  """Add a row to the table with optional smart truncation.

  Args:
    table: Rich Table instance
    row_data: Data for each column
    max_widths: Dictionary mapping column index to max width
    no_truncate: If True, don't truncate any fields
  """
  if no_truncate or max_widths is None:
    table.add_row(*row_data)
    return

  truncated = []
  for i, value in enumerate(row_data):
    max_width = max_widths.get(i, 40)  # Default to 40 if not specified
    truncated.append(truncate_text(value, max_width))

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

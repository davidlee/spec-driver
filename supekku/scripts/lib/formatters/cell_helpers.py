"""Rich-compatible cell formatting helpers.

Pure functions for formatting common cell types (tags, dates) with Rich markup.
Reusable across CLI tables, TUI widgets, and any Rich-compatible rendering context.

No Rich Table dependency — just string output.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime


def format_tags_cell(tags: Sequence[str] | None, style: str = "#d79921") -> str:
  """Format tags as a comma-separated Rich markup string.

  Args:
    tags: Tag values to format. Empty/None returns empty string.
    style: Rich style to apply (default: gold ``#d79921``).

  Returns:
    Styled string like ``[#d79921]foo, bar[/#d79921]``, or ``""`` when empty.
  """
  if not tags:
    return ""
  joined = ", ".join(tags)
  return f"[{style}]{joined}[/{style}]"


def format_date_cell(
  value: date | datetime | None,
  missing: str = "—",
  fmt: str = "%Y-%m-%d",
) -> str:
  """Format a date for display.

  Args:
    value: Date to format. ``None`` returns the *missing* sentinel.
    missing: Placeholder when *value* is ``None`` (default: em dash).
    fmt: ``strftime`` format string (default: ISO date).

  Returns:
    Formatted date string or *missing* sentinel.
  """
  if value is None:
    return missing
  return value.strftime(fmt)

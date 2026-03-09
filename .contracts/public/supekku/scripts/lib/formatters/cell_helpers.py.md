# supekku.scripts.lib.formatters.cell_helpers

Rich-compatible cell formatting helpers.

Pure functions for formatting common cell types (tags, dates) with Rich markup.
Reusable across CLI tables, TUI widgets, and any Rich-compatible rendering context.

No Rich Table dependency — just string output.

## Functions

- `format_date_cell(value, missing, fmt) -> str`: Format a date for display.

Args:
  value: Date to format. ``None`` returns the *missing* sentinel.
  missing: Placeholder when *value* is ``None`` (default: em dash).
  fmt: ``strftime`` format string (default: ISO date).

Returns:
  Formatted date string or *missing* sentinel.
- `format_tags_cell(tags, style) -> str`: Format tags as a comma-separated Rich markup string.

Args:
  tags: Tag values to format. Empty/None returns empty string.
  style: Rich style to apply (default: gold ``#d79921``).

Returns:
  Styled string like ``[#d79921]foo, bar[/#d79921]``, or ``""`` when empty.

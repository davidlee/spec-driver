"""Utilities for formatting YAML blocks."""

from __future__ import annotations


def format_yaml_list(key: str, values: list[str] | None, level: int = 0) -> str:
  """Format a YAML list with proper indentation.

  Args:
    key: The YAML key for the list.
    values: List of string values (will be sorted).
    level: Indentation level (0 = no indent).

  Returns:
    Formatted YAML list as a string.

  Example:
    >>> format_yaml_list("items", ["b", "a"], level=0)
    'items:\\n  - a\\n  - b'
    >>> format_yaml_list("items", [], level=1)
    '  items: []'
  """
  indent = "  " * level
  items = [str(v) for v in (values or []) if v]
  if not items:
    return f"{indent}{key}: []"
  child_indent = "  " * (level + 1)
  lines = [f"{indent}{key}:"]
  lines.extend(f"{child_indent}- {item}" for item in sorted(items))
  return "\n".join(lines)


__all__ = ["format_yaml_list"]

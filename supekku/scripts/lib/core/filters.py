"""Pure filter utilities for CLI commands.

This module provides reusable filter parsing functions following the
Skinny CLI pattern (pure functions, no side effects).
"""

from __future__ import annotations

import fnmatch


def matches_pattern(artifact_id: str, pattern: str) -> bool:
  """Check if artifact ID matches an fnmatch pattern (case-insensitive).

  Args:
    artifact_id: The artifact identifier to test.
    pattern: An fnmatch-style pattern (e.g. "SPEC-*", "ADR-00?").

  Returns:
    True if the ID matches the pattern in either its original or upper-cased
    form, False otherwise.
  """
  return fnmatch.fnmatch(artifact_id, pattern) or fnmatch.fnmatch(
    artifact_id, pattern.upper()
  )


def parse_multi_value_filter(value: str | None) -> list[str]:
  """Parse comma-separated filter value into list of strings.

  Supports both single values (backward compatible) and multi-value
  comma-separated filters. Strips whitespace from each value.

  Args:
    value: Filter value - can be:
      - None or empty string → returns []
      - Single value: "draft" → ["draft"]
      - Multiple values: "draft,in-progress" → ["draft", "in-progress"]
      - With whitespace: "draft, in-progress" → ["draft", "in-progress"]

  Returns:
    List of filter values (empty if value is None/empty).

  Examples:
    >>> parse_multi_value_filter(None)
    []
    >>> parse_multi_value_filter("")
    []
    >>> parse_multi_value_filter("draft")
    ['draft']
    >>> parse_multi_value_filter("draft,in-progress")
    ['draft', 'in-progress']
    >>> parse_multi_value_filter("draft, in-progress, completed")
    ['draft', 'in-progress', 'completed']
  """
  if not value:
    return []

  # Split by comma and strip whitespace from each value
  return [v.strip() for v in value.split(",") if v.strip()]

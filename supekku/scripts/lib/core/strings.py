"""String utility functions for spec-driver."""

from __future__ import annotations

import re

__all__ = ["slugify"]


def slugify(value: str) -> str:
  """Convert value to filename-friendly slug using underscores.

  Normalizes special characters to underscores, deduplicates consecutive
  separators, and strips leading/trailing underscores.

  Args:
    value: String to slugify.

  Returns:
    Lowercase slug with underscores. Returns "item" if result would be empty.

  Examples:
    >>> slugify("ADR-001: use spec-driver")
    'adr_001_use_spec_driver'
    >>> slugify("Fix bug -- urgent")
    'fix_bug_urgent'
    >>> slugify("foo___bar")
    'foo_bar'
    >>> slugify("title: with: colons")
    'title_with_colons'
  """
  # Lowercase first
  slug = value.lower()
  # Replace any non-alphanumeric chars with underscore
  slug = re.sub(r"[^a-z0-9]+", "_", slug)
  # Strip leading/trailing underscores
  slug = slug.strip("_")
  # Return fallback if empty
  return slug or "item"

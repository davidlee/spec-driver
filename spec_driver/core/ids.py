"""Sequential ID generation for spec-driver artifacts."""

from __future__ import annotations

import re
from collections.abc import Iterable


def next_sequential_id(names: Iterable[str], prefix: str, separator: str = "-") -> str:
  """Determine the next sequential ID from existing names.

  Scans *names* for entries matching ``{prefix}{separator}{digits}``,
  finds the highest numeric value, and returns the next ID formatted
  with at least 3 zero-padded digits.

  Args:
    names: Existing artifact names or IDs to scan.
    prefix: ID prefix (e.g. ``"ADR"``, ``"DE"``).
    separator: Character(s) between prefix and number. Use ``""``
      for unseparated IDs like ``T001``.

  Returns:
    Next available ID (e.g. ``"ADR-004"``).
  """
  pattern = re.compile(rf"{re.escape(prefix)}{re.escape(separator)}(\d+)")
  highest = 0
  for name in names:
    match = pattern.search(name)
    if match:
      highest = max(highest, int(match.group(1)))
  return f"{prefix}{separator}{highest + 1:03d}"


__all__ = ["next_sequential_id"]

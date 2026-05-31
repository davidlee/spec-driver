"""Date parsing utilities for spec-driver."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any


def parse_date(date_value: Any) -> date | None:
  """Parse date from various formats.

  Args:
    date_value: Value to parse — may be None, a date, a datetime, or an
      ISO-format string.

  Returns:
    Parsed date, or None if the value is absent or unparseable.
  """
  if not date_value:
    return None

  if isinstance(date_value, datetime):
    return date_value.date()

  if isinstance(date_value, date):
    return date_value

  if isinstance(date_value, str):
    for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"]:
      try:
        return datetime.strptime(date_value, fmt).date()
      except ValueError:
        continue

  return None


__all__ = ["parse_date"]

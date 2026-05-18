"""Tests for normalize_field (DE-137 IP-137-P01 task 1.9).

VT-CC-013 parity: every entry of the legacy ``CANONICAL_STATUS_MAP``
plus its case/whitespace variants must canonicalise via
``normalize_field("delta", "status", ...)``.
"""

from __future__ import annotations

import pytest

from .aliases import normalize_field

# VT-CC-013 parity matrix (DR-137 §5.2; mirrors legacy CANONICAL_STATUS_MAP
# coverage in changes/lifecycle_test.py).
_DELTA_STATUS_PARITY = [
  ("complete", "completed"),
  ("completed", "completed"),
  ("done", "completed"),
  ("active", "in-progress"),
  ("in_progress", "in-progress"),
  ("in-progress", "in-progress"),
  ("draft", "draft"),
  ("pending", "pending"),
  ("deferred", "deferred"),
]


@pytest.mark.parametrize(("raw", "expected"), _DELTA_STATUS_PARITY)
def test_delta_status_parity(raw: str, expected: str) -> None:
  """Permanent aliases canonicalise via metadata for delta.status."""
  assert normalize_field("delta", "status", raw) == expected


def test_delta_status_case_insensitive() -> None:
  assert normalize_field("delta", "status", "DONE") == "completed"
  assert normalize_field("delta", "status", "Active") == "in-progress"


def test_delta_status_strips_whitespace() -> None:
  assert normalize_field("delta", "status", "  done  ") == "completed"


def test_unknown_value_preserved_after_normalisation() -> None:
  """Values without alias mapping return their case-folded form."""
  assert normalize_field("delta", "status", "BOGUS") == "bogus"


def test_missing_kind_returns_normalised_value() -> None:
  assert normalize_field("nonexistent_kind", "status", "DRAFT") == "draft"


def test_missing_field_returns_normalised_value() -> None:
  assert normalize_field("delta", "nonexistent_field", "WHATEVER") == "whatever"


def test_non_string_passes_through_unchanged() -> None:
  assert normalize_field("delta", "status", 42) == 42
  assert normalize_field("delta", "status", None) is None
  assert normalize_field("delta", "status", ["x"]) == ["x"]


def test_plan_status_shared_aliases() -> None:
  """plan/phase/task share the same alias matrix."""
  for kind in ("plan", "phase", "task"):
    assert normalize_field(kind, "status", "done") == "completed"
    assert normalize_field(kind, "status", "active") == "in-progress"


def test_kinds_without_aliases_just_normalise() -> None:
  """A kind with enum_values but empty aliases preserves the canonical input."""
  assert normalize_field("spec", "status", "active") == "active"
  assert normalize_field("spec", "status", "DRAFT") == "draft"

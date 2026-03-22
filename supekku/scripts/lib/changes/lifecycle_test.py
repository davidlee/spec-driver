"""Tests for change artifact lifecycle normalisation (DE-104)."""

from __future__ import annotations

import pytest

from .lifecycle import (
  CANONICAL_STATUS_MAP,
  STATUS_COMPLETED,
  STATUS_IN_PROGRESS,
  normalize_status,
)


class TestNormalizeStatus:
  """Tests for normalize_status() including observed phase variants."""

  @pytest.mark.parametrize(
    ("raw", "expected"),
    [
      ("complete", STATUS_COMPLETED),
      ("completed", STATUS_COMPLETED),
      ("done", STATUS_COMPLETED),
      ("active", STATUS_IN_PROGRESS),
      ("in_progress", STATUS_IN_PROGRESS),
      ("in-progress", STATUS_IN_PROGRESS),
      ("draft", "draft"),
      ("pending", "pending"),
      ("deferred", "deferred"),
    ],
  )
  def test_normalizes_known_variants(self, raw: str, expected: str) -> None:
    assert normalize_status(raw) == expected

  def test_preserves_unknown_values(self) -> None:
    assert normalize_status("bogus") == "bogus"

  def test_case_insensitive(self) -> None:
    assert normalize_status("DONE") == STATUS_COMPLETED
    assert normalize_status("Active") == STATUS_IN_PROGRESS

  def test_strips_whitespace(self) -> None:
    assert normalize_status("  done  ") == STATUS_COMPLETED


class TestCanonicalStatusMap:
  """Tests for CANONICAL_STATUS_MAP coverage."""

  def test_all_observed_variants_mapped(self) -> None:
    """Ensure all 6 observed phase variants are in the map."""
    observed = {
      "draft",
      "completed",
      "complete",
      "done",
      "in-progress",
      "active",
      "in_progress",
    }
    for v in observed:
      assert v in CANONICAL_STATUS_MAP, f"'{v}' missing from CANONICAL_STATUS_MAP"

  def test_all_entries_resolve_to_canonical_values(self) -> None:
    canonical = {STATUS_COMPLETED, STATUS_IN_PROGRESS, "draft", "pending", "deferred"}
    for key, value in CANONICAL_STATUS_MAP.items():
      assert value in canonical, f"'{key}' maps to non-canonical '{value}'"

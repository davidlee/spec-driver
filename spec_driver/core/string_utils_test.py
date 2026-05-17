"""Tests for spec_driver.core.string_utils (VT-CC-010)."""

from __future__ import annotations

import pytest

from spec_driver.core.string_utils import CLOSEST_MATCH_CUTOFF, closest_match

DELTA_STATUS_CANDIDATES = (
  "completed",
  "deferred",
  "draft",
  "in-progress",
  "pending",
)


@pytest.mark.parametrize(
  ("value", "expected"),
  [
    ("complete", "completed"),
    ("pendng", "pending"),
    ("in_progres", "in-progress"),
    ("defered", "deferred"),
    ("draaft", "draft"),
  ],
)
def test_closest_match_catches_canonical_typos(value: str, expected: str) -> None:
  """VT-CC-010: typo inputs return their canonical at cutoff 0.6."""
  assert closest_match(value, DELTA_STATUS_CANDIDATES) == expected


@pytest.mark.parametrize(
  "value",
  ["live", "active", "done", "wip"],
)
def test_closest_match_silent_on_semantic_alternatives(value: str) -> None:
  """Semantic alternatives miss the cutoff; they belong in FieldMetadata.aliases."""
  assert closest_match(value, DELTA_STATUS_CANDIDATES) is None


@pytest.mark.parametrize("value", ["", "a"])
def test_closest_match_short_circuits_trivial_inputs(value: str) -> None:
  """Inputs shorter than two characters never produce a match."""
  assert closest_match(value, DELTA_STATUS_CANDIDATES) is None


def test_closest_match_accepts_arbitrary_iterable() -> None:
  """Candidates may be any iterable, not just a sequence."""

  def _candidates():
    yield from DELTA_STATUS_CANDIDATES

  assert closest_match("pendng", _candidates()) == "pending"


def test_cutoff_constant_is_advertised() -> None:
  """The module exposes the cutoff value (POL-002 magic-number avoidance)."""
  assert CLOSEST_MATCH_CUTOFF == 0.6

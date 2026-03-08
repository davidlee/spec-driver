"""Tests for standard lifecycle status constants (DE-075 DEC-075-02)."""

from supekku.scripts.lib.standards.lifecycle import STANDARD_STATUSES


def test_standard_statuses_values() -> None:
  assert frozenset({
    "draft", "required", "default", "deprecated",
  }) == STANDARD_STATUSES


def test_standard_statuses_is_frozen() -> None:
  assert isinstance(STANDARD_STATUSES, frozenset)

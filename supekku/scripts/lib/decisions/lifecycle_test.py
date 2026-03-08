"""Tests for ADR lifecycle status constants (DE-075 DEC-075-04)."""

from supekku.scripts.lib.decisions.lifecycle import ADR_STATUSES


def test_adr_statuses_values() -> None:
  assert frozenset({
    "draft", "proposed", "accepted", "rejected",
    "deprecated", "superseded", "revision-required",
  }) == ADR_STATUSES


def test_adr_statuses_is_frozen() -> None:
  assert isinstance(ADR_STATUSES, frozenset)

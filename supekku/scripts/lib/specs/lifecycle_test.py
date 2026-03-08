"""Tests for spec lifecycle status constants (DE-075 DEC-075-01)."""

from supekku.scripts.lib.specs.lifecycle import SPEC_STATUSES


def test_spec_statuses_values() -> None:
  assert (
    frozenset(
      {
        "stub",
        "draft",
        "active",
        "deprecated",
        "archived",
      }
    )
    == SPEC_STATUSES
  )


def test_spec_statuses_is_frozen() -> None:
  assert isinstance(SPEC_STATUSES, frozenset)

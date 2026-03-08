"""Tests for policy lifecycle status constants (DE-075 DEC-075-02)."""

from supekku.scripts.lib.policies.lifecycle import POLICY_STATUSES


def test_policy_statuses_values() -> None:
  assert frozenset({"draft", "required", "deprecated"}) == POLICY_STATUSES


def test_policy_statuses_is_frozen() -> None:
  assert isinstance(POLICY_STATUSES, frozenset)

"""Tests for memory lifecycle status constants (DE-075 DEC-075-03)."""

from supekku.scripts.lib.memory.lifecycle import MEMORY_STATUSES


def test_memory_statuses_values() -> None:
  assert frozenset({
    "draft", "active", "review", "superseded", "archived",
  }) == MEMORY_STATUSES


def test_memory_statuses_is_frozen() -> None:
  assert isinstance(MEMORY_STATUSES, frozenset)

"""Tests for lifecycle hygiene checks."""

from __future__ import annotations

import datetime
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

from supekku.scripts.lib.diagnostics.checks.lifecycle import (
  CATEGORY,
  DEFAULT_STALENESS_DAYS,
  check_lifecycle,
)


@dataclass(frozen=True)
class _FakeDelta:
  """Minimal delta stub for lifecycle checks."""

  id: str
  status: str
  updated: str | None = None


@dataclass
class _FakeRegistry:
  items: dict = field(default_factory=dict)
  error: Exception | None = None

  def collect(self) -> dict:
    if self.error:
      raise self.error
    return self.items


@dataclass
class _FakeWorkspace:
  root: Path
  _delta_registry: _FakeRegistry = field(default_factory=_FakeRegistry)

  @property
  def delta_registry(self) -> _FakeRegistry:
    return self._delta_registry


def _today_minus(days: int) -> str:
  return (datetime.date.today() - datetime.timedelta(days=days)).isoformat()


class TestCheckLifecycle(unittest.TestCase):
  """Tests for check_lifecycle function."""

  @patch("supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config")
  def test_no_in_progress_passes(self, mock_config: object) -> None:
    """No in-progress deltas should produce a single pass."""
    mock_config.return_value = {}  # type: ignore[attr-defined]
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _delta_registry=_FakeRegistry(
        items={
          "DE-001": _FakeDelta(id="DE-001", status="completed", updated="2026-03-01"),
        }
      ),
    )
    results = check_lifecycle(ws)
    assert len(results) == 1
    assert results[0].status == "pass"
    assert "No in-progress" in results[0].message

  @patch("supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config")
  def test_fresh_delta_passes(self, mock_config: object) -> None:
    """An in-progress delta updated recently should pass."""
    mock_config.return_value = {}  # type: ignore[attr-defined]
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _delta_registry=_FakeRegistry(
        items={
          "DE-001": _FakeDelta(
            id="DE-001",
            status="in-progress",
            updated=_today_minus(2),
          ),
        }
      ),
    )
    results = check_lifecycle(ws)
    assert len(results) == 1
    assert results[0].status == "pass"
    assert "2 days ago" in results[0].message

  @patch("supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config")
  def test_stale_delta_warns(self, mock_config: object) -> None:
    """An in-progress delta older than threshold should warn."""
    mock_config.return_value = {}  # type: ignore[attr-defined]
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _delta_registry=_FakeRegistry(
        items={
          "DE-001": _FakeDelta(
            id="DE-001",
            status="in-progress",
            updated=_today_minus(10),
          ),
        }
      ),
    )
    results = check_lifecycle(ws)
    assert len(results) == 1
    assert results[0].status == "warn"
    assert "10 days" in results[0].message
    assert results[0].suggestion is not None

  @patch("supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config")
  def test_custom_threshold_from_config(self, mock_config: object) -> None:
    """Staleness threshold should be configurable via workflow config."""
    mock_config.return_value = {"doctor": {"staleness_days": 2}}  # type: ignore[attr-defined]
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _delta_registry=_FakeRegistry(
        items={
          "DE-001": _FakeDelta(
            id="DE-001",
            status="in-progress",
            updated=_today_minus(3),
          ),
        }
      ),
    )
    results = check_lifecycle(ws)
    assert len(results) == 1
    assert results[0].status == "warn"
    assert "threshold: 2" in results[0].message

  @patch("supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config")
  def test_missing_updated_date_warns(self, mock_config: object) -> None:
    """Delta with no updated date should warn."""
    mock_config.return_value = {}  # type: ignore[attr-defined]
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _delta_registry=_FakeRegistry(
        items={
          "DE-001": _FakeDelta(id="DE-001", status="in-progress", updated=None),
        }
      ),
    )
    results = check_lifecycle(ws)
    assert len(results) == 1
    assert results[0].status == "warn"
    assert "no updated date" in results[0].message

  @patch("supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config")
  def test_unparseable_date_warns(self, mock_config: object) -> None:
    """Delta with unparseable updated date should warn."""
    mock_config.return_value = {}  # type: ignore[attr-defined]
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _delta_registry=_FakeRegistry(
        items={
          "DE-001": _FakeDelta(id="DE-001", status="in-progress", updated="not-a-date"),
        }
      ),
    )
    results = check_lifecycle(ws)
    assert len(results) == 1
    assert results[0].status == "warn"
    assert "unparseable" in results[0].message

  @patch("supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config")
  def test_registry_load_error_fails(self, mock_config: object) -> None:
    """If delta registry fails to load, should produce fail."""
    mock_config.return_value = {}  # type: ignore[attr-defined]
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _delta_registry=_FakeRegistry(error=RuntimeError("corrupt")),
    )
    results = check_lifecycle(ws)
    assert len(results) == 1
    assert results[0].status == "fail"
    assert "corrupt" in results[0].message

  @patch("supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config")
  def test_mixed_statuses(self, mock_config: object) -> None:
    """Only in-progress deltas should be checked, others ignored."""
    mock_config.return_value = {}  # type: ignore[attr-defined]
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _delta_registry=_FakeRegistry(
        items={
          "DE-001": _FakeDelta(
            id="DE-001",
            status="in-progress",
            updated=_today_minus(10),
          ),
          "DE-002": _FakeDelta(
            id="DE-002",
            status="completed",
            updated=_today_minus(30),
          ),
          "DE-003": _FakeDelta(
            id="DE-003",
            status="draft",
            updated=_today_minus(20),
          ),
        }
      ),
    )
    results = check_lifecycle(ws)
    assert len(results) == 1
    assert results[0].name == "DE-001"

  @patch("supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config")
  def test_default_staleness_days_value(self, mock_config: object) -> None:
    """Default staleness threshold should be 5 days."""
    assert DEFAULT_STALENESS_DAYS == 5

  @patch("supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config")
  def test_all_results_have_lifecycle_category(self, mock_config: object) -> None:
    """Every result should use the lifecycle category."""
    mock_config.return_value = {}  # type: ignore[attr-defined]
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _delta_registry=_FakeRegistry(
        items={
          "DE-001": _FakeDelta(
            id="DE-001",
            status="in-progress",
            updated=_today_minus(1),
          ),
        }
      ),
    )
    results = check_lifecycle(ws)
    assert all(r.category == CATEGORY for r in results)


if __name__ == "__main__":
  unittest.main()

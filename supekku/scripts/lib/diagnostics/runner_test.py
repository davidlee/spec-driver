"""Tests for diagnostic runner."""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from supekku.scripts.lib.diagnostics.models import DiagnosticResult
from supekku.scripts.lib.diagnostics.runner import (
  overall_exit_code,
  run_checks,
)


@dataclass
class _FakeWorkspace:
  root: Path = Path("/fake")


def _pass_check(_ws: object) -> list[DiagnosticResult]:
  return [
    DiagnosticResult(category="test", name="ok", status="pass", message="fine")
  ]


def _warn_check(_ws: object) -> list[DiagnosticResult]:
  return [
    DiagnosticResult(category="test", name="eh", status="warn", message="hmm")
  ]


def _fail_check(_ws: object) -> list[DiagnosticResult]:
  return [
    DiagnosticResult(
      category="test", name="bad", status="fail", message="broken"
    )
  ]


class TestRunChecks(unittest.TestCase):
  """Tests for run_checks orchestrator."""

  def test_runs_all_registered_checks(self) -> None:
    """Runs all checks when no filter provided."""
    fake_registry = {"alpha": _pass_check, "beta": _warn_check}
    with patch(
      "supekku.scripts.lib.diagnostics.runner.CHECK_REGISTRY", fake_registry
    ):
      summaries = run_checks(_FakeWorkspace())

    assert len(summaries) == 2
    assert summaries[0].category == "alpha"
    assert summaries[1].category == "beta"

  def test_filters_by_category(self) -> None:
    """Only runs requested categories."""
    fake_registry = {"alpha": _pass_check, "beta": _warn_check}
    with patch(
      "supekku.scripts.lib.diagnostics.runner.CHECK_REGISTRY", fake_registry
    ):
      summaries = run_checks(_FakeWorkspace(), categories=["beta"])

    assert len(summaries) == 1
    assert summaries[0].category == "beta"

  def test_unknown_category_raises(self) -> None:
    """Requesting unknown category raises ValueError."""
    fake_registry = {"alpha": _pass_check}
    with (
      patch(
        "supekku.scripts.lib.diagnostics.runner.CHECK_REGISTRY",
        fake_registry,
      ),
      self.assertRaises(ValueError),
    ):
      run_checks(_FakeWorkspace(), categories=["nonexistent"])

  def test_preserves_order(self) -> None:
    """Summaries are returned in registry order."""
    fake_registry = {"z": _pass_check, "a": _warn_check, "m": _fail_check}
    with patch(
      "supekku.scripts.lib.diagnostics.runner.CHECK_REGISTRY", fake_registry
    ):
      summaries = run_checks(_FakeWorkspace())

    assert [s.category for s in summaries] == ["z", "a", "m"]


class TestOverallExitCode(unittest.TestCase):
  """Tests for exit code computation."""

  def test_all_pass_returns_zero(self) -> None:
    fake_registry = {"a": _pass_check}
    with patch(
      "supekku.scripts.lib.diagnostics.runner.CHECK_REGISTRY", fake_registry
    ):
      summaries = run_checks(_FakeWorkspace())
    assert overall_exit_code(summaries) == 0

  def test_warn_returns_one(self) -> None:
    fake_registry = {"a": _pass_check, "b": _warn_check}
    with patch(
      "supekku.scripts.lib.diagnostics.runner.CHECK_REGISTRY", fake_registry
    ):
      summaries = run_checks(_FakeWorkspace())
    assert overall_exit_code(summaries) == 1

  def test_fail_returns_two(self) -> None:
    fake_registry = {"a": _pass_check, "b": _fail_check}
    with patch(
      "supekku.scripts.lib.diagnostics.runner.CHECK_REGISTRY", fake_registry
    ):
      summaries = run_checks(_FakeWorkspace())
    assert overall_exit_code(summaries) == 2

  def test_empty_summaries_returns_zero(self) -> None:
    assert overall_exit_code([]) == 0


if __name__ == "__main__":
  unittest.main()

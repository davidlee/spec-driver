"""Tests for diagnostic models."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.diagnostics.models import (
  CategorySummary,
  DiagnosticResult,
  worst_status,
)


class TestWorstStatus(unittest.TestCase):
  """Tests for worst_status aggregation."""

  def test_empty_list_returns_pass(self) -> None:
    assert worst_status([]) == "pass"

  def test_all_pass(self) -> None:
    assert worst_status(["pass", "pass", "pass"]) == "pass"

  def test_warn_beats_pass(self) -> None:
    assert worst_status(["pass", "warn", "pass"]) == "warn"

  def test_fail_beats_warn(self) -> None:
    assert worst_status(["pass", "warn", "fail"]) == "fail"

  def test_all_fail(self) -> None:
    assert worst_status(["fail", "fail"]) == "fail"

  def test_single_pass(self) -> None:
    assert worst_status(["pass"]) == "pass"

  def test_single_fail(self) -> None:
    assert worst_status(["fail"]) == "fail"


class TestDiagnosticResult(unittest.TestCase):
  """Tests for DiagnosticResult dataclass."""

  def test_frozen(self) -> None:
    result = DiagnosticResult(
      category="deps", name="python", status="pass", message="OK"
    )
    with self.assertRaises(AttributeError):
      result.status = "fail"  # type: ignore[misc]

  def test_suggestion_defaults_to_none(self) -> None:
    result = DiagnosticResult(
      category="deps", name="python", status="pass", message="OK"
    )
    assert result.suggestion is None

  def test_with_suggestion(self) -> None:
    result = DiagnosticResult(
      category="deps",
      name="node",
      status="warn",
      message="not found",
      suggestion="Install Node.js",
    )
    assert result.suggestion == "Install Node.js"


class TestCategorySummary(unittest.TestCase):
  """Tests for CategorySummary aggregation."""

  def test_empty_results_is_pass(self) -> None:
    summary = CategorySummary(category="deps", results=())
    assert summary.status == "pass"

  def test_all_pass_results(self) -> None:
    results = (
      DiagnosticResult(category="deps", name="a", status="pass", message="OK"),
      DiagnosticResult(category="deps", name="b", status="pass", message="OK"),
    )
    summary = CategorySummary(category="deps", results=results)
    assert summary.status == "pass"

  def test_mixed_results_returns_worst(self) -> None:
    results = (
      DiagnosticResult(category="deps", name="a", status="pass", message="OK"),
      DiagnosticResult(category="deps", name="b", status="warn", message="hmm"),
      DiagnosticResult(category="deps", name="c", status="pass", message="OK"),
    )
    summary = CategorySummary(category="deps", results=results)
    assert summary.status == "warn"

  def test_fail_in_results(self) -> None:
    results = (
      DiagnosticResult(category="deps", name="a", status="pass", message="OK"),
      DiagnosticResult(category="deps", name="b", status="fail", message="missing"),
    )
    summary = CategorySummary(category="deps", results=results)
    assert summary.status == "fail"


if __name__ == "__main__":
  unittest.main()

"""Tests for diagnostic formatters."""

from __future__ import annotations

import json
import unittest

from supekku.scripts.lib.diagnostics.models import CategorySummary, DiagnosticResult
from supekku.scripts.lib.formatters.diagnostic_formatters import (
  format_doctor_json,
  format_doctor_text,
)


def _make_summaries() -> list[CategorySummary]:
  return [
    CategorySummary(
      category="deps",
      results=(
        DiagnosticResult(
          category="deps", name="python", status="pass", message="Python 3.12"
        ),
        DiagnosticResult(
          category="deps",
          name="node",
          status="warn",
          message="not found",
          suggestion="Install Node.js",
        ),
      ),
    ),
    CategorySummary(
      category="structure",
      results=(
        DiagnosticResult(
          category="structure",
          name="spec-driver-root",
          status="pass",
          message=".spec-driver/ exists",
        ),
      ),
    ),
  ]


class TestFormatDoctorText(unittest.TestCase):
  """Tests for text output formatting."""

  def test_header_present(self) -> None:
    output = format_doctor_text(_make_summaries())
    assert "spec-driver doctor" in output

  def test_hides_pass_by_default(self) -> None:
    output = format_doctor_text(_make_summaries())
    assert "python" not in output
    assert "node" in output

  def test_verbose_shows_pass(self) -> None:
    output = format_doctor_text(_make_summaries(), verbose=True)
    assert "python" in output
    assert "node" in output

  def test_summary_line(self) -> None:
    output = format_doctor_text(_make_summaries())
    assert "2 pass" in output
    assert "1 warn" in output
    assert "0 fail" in output

  def test_suggestion_shown(self) -> None:
    output = format_doctor_text(_make_summaries())
    assert "Install Node.js" in output

  def test_all_pass_category_shows_note(self) -> None:
    summaries = [
      CategorySummary(
        category="test",
        results=(
          DiagnosticResult(
            category="test", name="a", status="pass", message="OK"
          ),
        ),
      )
    ]
    output = format_doctor_text(summaries)
    assert "all checks passed" in output

  def test_empty_summaries(self) -> None:
    output = format_doctor_text([])
    assert "0 pass" in output


class TestFormatDoctorJson(unittest.TestCase):
  """Tests for JSON output formatting."""

  def test_valid_json(self) -> None:
    output = format_doctor_json(_make_summaries())
    data = json.loads(output)
    assert "categories" in data
    assert "summary" in data
    assert "exit_code" in data

  def test_category_count(self) -> None:
    data = json.loads(format_doctor_json(_make_summaries()))
    assert len(data["categories"]) == 2

  def test_result_fields(self) -> None:
    data = json.loads(format_doctor_json(_make_summaries()))
    result = data["categories"][0]["results"][0]
    assert "name" in result
    assert "status" in result
    assert "message" in result
    assert "suggestion" in result

  def test_summary_counts(self) -> None:
    data = json.loads(format_doctor_json(_make_summaries()))
    assert data["summary"]["pass"] == 2
    assert data["summary"]["warn"] == 1
    assert data["summary"]["fail"] == 0

  def test_exit_code_reflects_worst(self) -> None:
    data = json.loads(format_doctor_json(_make_summaries()))
    assert data["exit_code"] == 1  # warn present

  def test_all_pass_exit_code_zero(self) -> None:
    summaries = [
      CategorySummary(
        category="test",
        results=(
          DiagnosticResult(
            category="test", name="a", status="pass", message="OK"
          ),
        ),
      )
    ]
    data = json.loads(format_doctor_json(summaries))
    assert data["exit_code"] == 0


if __name__ == "__main__":
  unittest.main()

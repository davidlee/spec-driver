"""Tests for list CLI commands (backlog shortcuts)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from typer.testing import CliRunner

from supekku.cli.list import app


class ListBacklogShortcutsTest(unittest.TestCase):
  """Test cases for backlog listing shortcut commands."""

  def setUp(self) -> None:
    """Set up test environment with sample backlog entries."""
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()

    # Create sample backlog entries for testing
    self._create_sample_issue("ISSUE-001", "Test issue one", "open")
    self._create_sample_issue("ISSUE-002", "Test issue two", "resolved")
    self._create_sample_problem("PROB-001", "Test problem", "captured")
    self._create_sample_improvement("IMPR-001", "Test improvement", "idea")
    self._create_sample_risk("RISK-001", "Test risk", "identified")

  def tearDown(self) -> None:
    """Clean up test environment."""
    self.tmpdir.cleanup()

  def _create_sample_issue(self, issue_id: str, title: str, status: str) -> None:
    """Helper to create a sample issue file."""
    issue_dir = self.root / "backlog" / "issues" / issue_id
    issue_dir.mkdir(parents=True, exist_ok=True)
    issue_file = issue_dir / f"{issue_id}.md"
    content = f"""---
id: {issue_id}
name: {title}
kind: issue
status: {status}
created: '2025-11-04'
---

# {issue_id} - {title}

Test issue content.
"""
    issue_file.write_text(content, encoding="utf-8")

  def _create_sample_problem(self, prob_id: str, title: str, status: str) -> None:
    """Helper to create a sample problem file."""
    prob_dir = self.root / "backlog" / "problems" / prob_id
    prob_dir.mkdir(parents=True, exist_ok=True)
    prob_file = prob_dir / f"{prob_id}.md"
    content = f"""---
id: {prob_id}
name: {title}
kind: problem
status: {status}
created: '2025-11-04'
---

# {prob_id} - {title}

Test problem content.
"""
    prob_file.write_text(content, encoding="utf-8")

  def _create_sample_improvement(
    self, impr_id: str, title: str, status: str
  ) -> None:
    """Helper to create a sample improvement file."""
    impr_dir = self.root / "backlog" / "improvements" / impr_id
    impr_dir.mkdir(parents=True, exist_ok=True)
    impr_file = impr_dir / f"{impr_id}.md"
    content = f"""---
id: {impr_id}
name: {title}
kind: improvement
status: {status}
created: '2025-11-04'
---

# {impr_id} - {title}

Test improvement content.
"""
    impr_file.write_text(content, encoding="utf-8")

  def _create_sample_risk(self, risk_id: str, title: str, status: str) -> None:
    """Helper to create a sample risk file."""
    risk_dir = self.root / "backlog" / "risks" / risk_id
    risk_dir.mkdir(parents=True, exist_ok=True)
    risk_file = risk_dir / f"{risk_id}.md"
    content = f"""---
id: {risk_id}
name: {title}
kind: risk
status: {status}
created: '2025-11-04'
---

# {risk_id} - {title}

Test risk content.
"""
    risk_file.write_text(content, encoding="utf-8")

  def test_list_issues(self) -> None:
    """Test listing issues via shortcut command."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-002" in result.stdout
    assert "PROB-001" not in result.stdout  # Should not show problems

  def test_list_problems(self) -> None:
    """Test listing problems via shortcut command."""
    result = self.runner.invoke(
      app,
      ["problems", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "PROB-001" in result.stdout
    assert "ISSUE-001" not in result.stdout  # Should not show issues

  def test_list_improvements(self) -> None:
    """Test listing improvements via shortcut command."""
    result = self.runner.invoke(
      app,
      ["improvements", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "IMPR-001" in result.stdout
    assert "ISSUE-001" not in result.stdout  # Should not show issues

  def test_list_risks(self) -> None:
    """Test listing risks via shortcut command."""
    result = self.runner.invoke(
      app,
      ["risks", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "RISK-001" in result.stdout
    assert "ISSUE-001" not in result.stdout  # Should not show issues

  def test_list_issues_with_status_filter(self) -> None:
    """Test listing issues with status filter."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--status", "open"],
    )

    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-002" not in result.stdout  # resolved, not open

  def test_list_issues_with_substring_filter(self) -> None:
    """Test listing issues with substring filter."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--filter", "one"],
    )

    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-002" not in result.stdout  # doesn't match "one"

  def test_list_issues_json_format(self) -> None:
    """Test listing issues with JSON output."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--format", "json"],
    )

    assert result.exit_code == 0
    # JSON output should be valid and contain issue data
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-002" in result.stdout

  def test_list_issues_empty_result(self) -> None:
    """Test listing issues with filter that returns no results."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--filter", "nonexistent"],
    )

    # Should exit successfully with no output
    assert result.exit_code == 0
    assert result.stdout.strip() == ""

  def test_equivalence_with_list_backlog(self) -> None:
    """Test that shortcuts are equivalent to list backlog -k."""
    # Test issues shortcut vs backlog -k issue
    issues_result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root)],
    )
    backlog_result = self.runner.invoke(
      app,
      ["backlog", "--root", str(self.root), "-k", "issue"],
    )

    assert issues_result.exit_code == 0
    assert backlog_result.exit_code == 0
    assert issues_result.stdout == backlog_result.stdout

  def test_regexp_filter(self) -> None:
    """Test listing with regexp filter."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--regexp", "ISSUE-00[12]"],
    )

    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-002" in result.stdout

  def test_tsv_format(self) -> None:
    """Test listing with TSV format."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--format", "tsv"],
    )

    assert result.exit_code == 0
    assert "\t" in result.stdout  # TSV uses tabs
    assert "ISSUE-001" in result.stdout


if __name__ == "__main__":
  unittest.main()

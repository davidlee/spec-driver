"""Tests for create CLI commands."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from typer.testing import CliRunner

from supekku.cli.create import app


class CreateBacklogCommandsTest(unittest.TestCase):
  """Test cases for backlog creation CLI commands."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()

  def tearDown(self) -> None:
    """Clean up test environment."""
    self.tmpdir.cleanup()

  def test_create_issue(self) -> None:
    """Test creating an issue via CLI."""
    result = self.runner.invoke(
      app,
      ["issue", "Test issue", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "Issue created: ISSUE-001" in result.stdout
    assert "ISSUE-001.md" in result.stdout

    # Verify file exists
    issue_dir = self.root / "backlog" / "issues"
    assert issue_dir.exists()
    issue_files = list(issue_dir.rglob("ISSUE-001.md"))
    assert len(issue_files) == 1
    assert issue_files[0].exists()

    # Verify frontmatter
    content = issue_files[0].read_text(encoding="utf-8")
    assert "id: ISSUE-001" in content
    assert "name: Test issue" in content
    assert "kind: issue" in content
    assert "status: open" in content

  def test_create_problem(self) -> None:
    """Test creating a problem via CLI."""
    result = self.runner.invoke(
      app,
      ["problem", "Test problem", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "Problem created: PROB-001" in result.stdout
    assert "PROB-001.md" in result.stdout

    # Verify file exists
    problem_dir = self.root / "backlog" / "problems"
    assert problem_dir.exists()
    problem_files = list(problem_dir.rglob("PROB-001.md"))
    assert len(problem_files) == 1

    # Verify frontmatter
    content = problem_files[0].read_text(encoding="utf-8")
    assert "id: PROB-001" in content
    assert "name: Test problem" in content
    assert "kind: problem" in content
    assert "status: captured" in content

  def test_create_improvement(self) -> None:
    """Test creating an improvement via CLI."""
    result = self.runner.invoke(
      app,
      ["improvement", "Test improvement", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "Improvement created: IMPR-001" in result.stdout
    assert "IMPR-001.md" in result.stdout

    # Verify file exists
    improvement_dir = self.root / "backlog" / "improvements"
    assert improvement_dir.exists()
    improvement_files = list(improvement_dir.rglob("IMPR-001.md"))
    assert len(improvement_files) == 1

    # Verify frontmatter
    content = improvement_files[0].read_text(encoding="utf-8")
    assert "id: IMPR-001" in content
    assert "name: Test improvement" in content
    assert "kind: improvement" in content
    assert "status: idea" in content

  def test_create_risk(self) -> None:
    """Test creating a risk via CLI."""
    result = self.runner.invoke(
      app,
      ["risk", "Test risk", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "Risk created: RISK-001" in result.stdout
    assert "RISK-001.md" in result.stdout

    # Verify file exists
    risk_dir = self.root / "backlog" / "risks"
    assert risk_dir.exists()
    risk_files = list(risk_dir.rglob("RISK-001.md"))
    assert len(risk_files) == 1

    # Verify frontmatter
    content = risk_files[0].read_text(encoding="utf-8")
    assert "id: RISK-001" in content
    assert "name: Test risk" in content
    assert "kind: risk" in content
    assert "status: suspected" in content
    assert "likelihood: 0.2" in content

  def test_create_multiple_issues_increments_id(self) -> None:
    """Test that creating multiple issues increments the ID."""
    self.runner.invoke(app, ["issue", "First issue", "--root", str(self.root)])
    result = self.runner.invoke(
      app,
      ["issue", "Second issue", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "ISSUE-002" in result.stdout

  def test_create_issue_with_spaces_in_title(self) -> None:
    """Test creating an issue with spaces in title creates proper slug."""
    result = self.runner.invoke(
      app,
      ["issue", "Complex Issue Title With Spaces", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    issue_dir = self.root / "backlog" / "issues"
    dirs = list(issue_dir.iterdir())
    assert len(dirs) == 1
    assert "complex-issue-title-with-spaces" in dirs[0].name


if __name__ == "__main__":
  unittest.main()

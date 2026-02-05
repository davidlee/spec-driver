"""Tests for find CLI commands."""

from __future__ import annotations

import unittest

from typer.testing import CliRunner

from supekku.cli.find import app
from supekku.scripts.lib.core.repo import find_repo_root


class FindSpecCommandTest(unittest.TestCase):
  """Test cases for find spec CLI command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_find_spec_wildcard(self) -> None:
    """Test finding specs with wildcard pattern."""
    result = self.runner.invoke(app, ["spec", "SPEC-*"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    # Should output paths
    assert "specify/tech/SPEC-" in result.stdout
    assert ".md" in result.stdout

  def test_find_spec_exact_match(self) -> None:
    """Test finding spec with exact ID."""
    # Find a spec that exists
    spec_dirs = list((self.root / "specify" / "tech").glob("SPEC-*"))
    if not spec_dirs:
      self.skipTest("No specs found in repository")

    spec_id = spec_dirs[0].name
    result = self.runner.invoke(app, ["spec", spec_id])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    assert spec_id in result.stdout

  def test_find_spec_question_mark_pattern(self) -> None:
    """Test finding specs with ? pattern (single char match)."""
    result = self.runner.invoke(app, ["spec", "SPEC-11?"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    # Should match SPEC-11X where X is any single char
    lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
    for line in lines:
      # Each line should contain SPEC-11X where X is single char
      assert "SPEC-11" in line

  def test_find_spec_no_match(self) -> None:
    """Test finding spec with no matches returns success (Unix find behavior)."""
    result = self.runner.invoke(app, ["spec", "NONEXISTENT-999"])

    assert result.exit_code == 0  # No output, but success

  def test_find_spec_case_insensitive(self) -> None:
    """Test finding specs is case-insensitive."""
    # Find with lowercase pattern
    result = self.runner.invoke(app, ["spec", "spec-*"])

    assert result.exit_code == 0
    # Should still match SPEC-* files
    assert "SPEC-" in result.stdout


class FindDeltaCommandTest(unittest.TestCase):
  """Test cases for find delta CLI command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_find_delta_wildcard(self) -> None:
    """Test finding deltas with wildcard pattern."""
    result = self.runner.invoke(app, ["delta", "DE-*"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    assert "change/deltas/DE-" in result.stdout
    assert ".md" in result.stdout

  def test_find_delta_exact_match(self) -> None:
    """Test finding delta with exact ID."""
    delta_dirs = list((self.root / "change" / "deltas").glob("DE-*"))
    if not delta_dirs:
      self.skipTest("No deltas found in repository")

    delta_id = f"DE-{delta_dirs[0].name.split('-')[1]}"
    result = self.runner.invoke(app, ["delta", delta_id])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    assert delta_id in result.stdout


class FindAdrCommandTest(unittest.TestCase):
  """Test cases for find adr CLI command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_find_adr_wildcard(self) -> None:
    """Test finding ADRs with wildcard pattern."""
    result = self.runner.invoke(app, ["adr", "ADR-*"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    assert "specify/decisions/ADR-" in result.stdout
    assert ".md" in result.stdout

  def test_find_adr_exact_match(self) -> None:
    """Test finding ADR with exact ID."""
    adr_files = list((self.root / "specify" / "decisions").glob("ADR-*.md"))
    if not adr_files:
      self.skipTest("No ADRs found in repository")

    adr_id = adr_files[0].stem.split("-")[0] + "-" + adr_files[0].stem.split("-")[1]
    result = self.runner.invoke(app, ["adr", adr_id])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    assert adr_id in result.stdout


class FindRevisionCommandTest(unittest.TestCase):
  """Test cases for find revision CLI command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_find_revision_wildcard(self) -> None:
    """Test finding revisions with wildcard pattern."""
    result = self.runner.invoke(app, ["revision", "RE-*"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    # If there are revisions, they should be in the output
    if result.stdout.strip():
      assert "change/revisions/RE-" in result.stdout
      assert ".md" in result.stdout


class FindPolicyCommandTest(unittest.TestCase):
  """Test cases for find policy CLI command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()

  def test_find_policy_wildcard(self) -> None:
    """Test finding policies with wildcard pattern."""
    result = self.runner.invoke(app, ["policy", "POL-*"])

    # Should succeed even if no policies exist
    assert result.exit_code == 0, f"Command failed: {result.stderr}"


class FindStandardCommandTest(unittest.TestCase):
  """Test cases for find standard CLI command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()

  def test_find_standard_wildcard(self) -> None:
    """Test finding standards with wildcard pattern."""
    result = self.runner.invoke(app, ["standard", "STD-*"])

    # Should succeed even if no standards exist
    assert result.exit_code == 0, f"Command failed: {result.stderr}"


class FindCardCommandTest(unittest.TestCase):
  """Test cases for find card CLI command (existing)."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_find_card_wildcard(self) -> None:
    """Test finding cards with ID pattern."""
    card_files = list((self.root / "kanban").rglob("T*.md"))
    if not card_files:
      self.skipTest("No cards found in repository")

    card_id = card_files[0].stem.split("-")[0]
    result = self.runner.invoke(app, ["card", card_id])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    assert f"{card_id}-" in result.stdout


if __name__ == "__main__":
  unittest.main()

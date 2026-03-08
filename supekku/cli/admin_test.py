"""Tests for admin CLI command group routing."""

from __future__ import annotations

import unittest

from typer.testing import CliRunner

from supekku.cli.main import app


class AdminGroupTest(unittest.TestCase):
  """Test that admin subcommands are routed correctly."""

  def setUp(self) -> None:
    self.runner = CliRunner()

  def test_admin_help(self) -> None:
    result = self.runner.invoke(app, ["admin", "--help"])
    assert result.exit_code == 0
    assert "compact" in result.stdout
    assert "resolve" in result.stdout
    assert "backfill" in result.stdout

  def test_admin_compact_help(self) -> None:
    result = self.runner.invoke(app, ["admin", "compact", "--help"])
    assert result.exit_code == 0
    assert "delta" in result.stdout

  def test_admin_resolve_help(self) -> None:
    result = self.runner.invoke(app, ["admin", "resolve", "--help"])
    assert result.exit_code == 0
    assert "links" in result.stdout

  def test_admin_backfill_help(self) -> None:
    result = self.runner.invoke(app, ["admin", "backfill", "--help"])
    assert result.exit_code == 0
    assert "spec" in result.stdout


class OldCommandsRemovedTest(unittest.TestCase):
  """Test that old top-level commands no longer exist."""

  def setUp(self) -> None:
    self.runner = CliRunner()

  def test_schema_removed(self) -> None:
    result = self.runner.invoke(app, ["schema", "--help"])
    assert result.exit_code != 0

  def test_skills_removed(self) -> None:
    result = self.runner.invoke(app, ["skills", "--help"])
    assert result.exit_code != 0

  def test_compact_removed(self) -> None:
    result = self.runner.invoke(app, ["compact", "--help"])
    assert result.exit_code != 0

  def test_resolve_removed(self) -> None:
    result = self.runner.invoke(app, ["resolve", "--help"])
    assert result.exit_code != 0

  def test_backfill_removed(self) -> None:
    result = self.runner.invoke(app, ["backfill", "--help"])
    assert result.exit_code != 0


if __name__ == "__main__":
  unittest.main()

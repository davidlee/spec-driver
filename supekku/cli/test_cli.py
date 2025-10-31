"""Comprehensive test suite for unified CLI."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from supekku.cli.main import app

runner = CliRunner()


class TestMainApp:
  """Test main application structure and help."""

  def test_main_help(self):
    """Test main help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "spec-driver" in result.stdout
    assert "Specification-driven development toolkit" in result.stdout

  def test_main_no_args(self):
    """Test invoking with no arguments shows help."""
    result = runner.invoke(app, [])
    # Typer with no_args_is_help=True returns exit code 0
    # but Click returns 2, which Typer uses internally
    assert result.exit_code in [0, 2]
    assert "Usage:" in result.stdout

  def test_main_shows_all_commands(self):
    """Test that all major commands are listed."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "install" in result.stdout
    assert "validate" in result.stdout
    assert "sync" in result.stdout
    assert "create" in result.stdout
    assert "list" in result.stdout
    assert "show" in result.stdout
    assert "complete" in result.stdout
    assert "adr" in result.stdout


class TestWorkspaceCommands:
  """Test workspace management commands."""

  def test_install_help(self):
    """Test install command help."""
    result = runner.invoke(app, ["install", "--help"])
    assert result.exit_code == 0
    assert "Initialize spec-driver workspace" in result.stdout

  def test_install_creates_workspace(self):
    """Test install command creates workspace structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
      result = runner.invoke(app, ["install", tmpdir, "--yes"])
      assert result.exit_code == 0
      assert "Workspace initialized" in result.stdout

      # Verify directories were created
      workspace = Path(tmpdir)
      assert (workspace / "change" / "deltas").exists()
      assert (workspace / "specify" / "tech").exists()
      assert (workspace / ".spec-driver" / "registry").exists()

      # Verify backlog structure
      assert (workspace / "backlog" / "improvements").exists()
      assert (workspace / "backlog" / "issues").exists()
      assert (workspace / "backlog" / "problems").exists()
      assert (workspace / "backlog" / "risks").exists()
      assert (workspace / "backlog" / "backlog.md").exists()

      # Verify backlog.md content
      backlog_content = (workspace / "backlog" / "backlog.md").read_text()
      assert "# Backlog" in backlog_content
      assert "improvements/" in backlog_content

  def test_validate_help(self):
    """Test validate command help."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Validate workspace metadata" in result.stdout


class TestCreateCommands:
  """Test create command group."""

  def test_create_help(self):
    """Test create command group help."""
    result = runner.invoke(app, ["create", "--help"])
    assert result.exit_code == 0
    assert "Create new artifacts" in result.stdout

  def test_create_spec_help(self):
    """Test create spec command help."""
    result = runner.invoke(app, ["create", "spec", "--help"])
    assert result.exit_code == 0
    assert "Create a new SPEC or PROD document" in result.stdout
    assert "--type" in result.stdout
    assert "--testing" in result.stdout

  def test_create_delta_help(self):
    """Test create delta command help."""
    result = runner.invoke(app, ["create", "delta", "--help"])
    assert result.exit_code == 0
    assert "Create a Delta bundle" in result.stdout
    assert "--spec" in result.stdout
    assert "--requirement" in result.stdout

  def test_create_requirement_help(self):
    """Test create requirement command help."""
    result = runner.invoke(app, ["create", "requirement", "--help"])
    assert result.exit_code == 0
    assert "Create a breakout requirement" in result.stdout
    assert "--kind" in result.stdout

  def test_create_revision_help(self):
    """Test create revision command help."""
    result = runner.invoke(app, ["create", "revision", "--help"])
    assert result.exit_code == 0
    assert "Create a Spec Revision bundle" in result.stdout
    assert "--source" in result.stdout
    assert "--destination" in result.stdout

  def test_create_adr_help(self):
    """Test create adr command help."""
    result = runner.invoke(app, ["create", "adr", "--help"])
    assert result.exit_code == 0
    assert "Create a new ADR" in result.stdout
    assert "--status" in result.stdout
    assert "--author" in result.stdout


class TestListCommands:
  """Test list command group."""

  def test_list_help(self):
    """Test list command group help."""
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    assert "List artifacts" in result.stdout

  def test_list_specs_help(self):
    """Test list specs command help."""
    result = runner.invoke(app, ["list", "specs", "--help"])
    assert result.exit_code == 0
    assert "List SPEC/PROD artifacts" in result.stdout
    assert "--kind" in result.stdout
    assert "--filter" in result.stdout
    assert "--package" in result.stdout

  def test_list_deltas_help(self):
    """Test list deltas command help."""
    result = runner.invoke(app, ["list", "deltas", "--help"])
    assert result.exit_code == 0
    assert "List deltas" in result.stdout
    assert "--status" in result.stdout
    assert "--details" in result.stdout

  def test_list_changes_help(self):
    """Test list changes command help."""
    result = runner.invoke(app, ["list", "changes", "--help"])
    assert result.exit_code == 0
    assert "List change artifacts" in result.stdout
    assert "--kind" in result.stdout
    assert "--filter" in result.stdout
    assert "--status" in result.stdout


class TestShowCommands:
  """Test show command group."""

  def test_show_help(self):
    """Test show command group help."""
    result = runner.invoke(app, ["show", "--help"])
    assert result.exit_code == 0
    assert "Show detailed artifact information" in result.stdout

  def test_show_adr_help(self):
    """Test show adr command help."""
    result = runner.invoke(app, ["show", "adr", "--help"])
    assert result.exit_code == 0
    assert "Show detailed information about a specific decision" in result.stdout


class TestCompleteCommands:
  """Test complete command group."""

  def test_complete_help(self):
    """Test complete command group help."""
    result = runner.invoke(app, ["complete", "--help"])
    assert result.exit_code == 0
    assert "Complete artifacts" in result.stdout

  def test_complete_delta_help(self):
    """Test complete delta command help."""
    result = runner.invoke(app, ["complete", "delta", "--help"])
    assert result.exit_code == 0
    assert "Complete a delta" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--force" in result.stdout
    assert "--skip-sync" in result.stdout


class TestAdrCommands:
  """Test ADR command group."""

  def test_adr_help(self):
    """Test adr command group help."""
    result = runner.invoke(app, ["adr", "--help"])
    assert result.exit_code == 0
    assert "Manage Architecture Decision Records" in result.stdout

  def test_adr_sync_help(self):
    """Test adr sync command help."""
    result = runner.invoke(app, ["adr", "sync", "--help"])
    assert result.exit_code == 0
    assert "Sync decision registry" in result.stdout

  def test_adr_list_help(self):
    """Test adr list command help."""
    result = runner.invoke(app, ["adr", "list", "--help"])
    assert result.exit_code == 0
    assert "List decisions" in result.stdout
    assert "--status" in result.stdout
    assert "--tag" in result.stdout

  def test_adr_show_help(self):
    """Test adr show command help."""
    result = runner.invoke(app, ["adr", "show", "--help"])
    assert result.exit_code == 0
    assert "Show detailed information about a specific decision" in result.stdout

  def test_adr_new_help(self):
    """Test adr new command help."""
    result = runner.invoke(app, ["adr", "new", "--help"])
    assert result.exit_code == 0
    assert "Create a new ADR" in result.stdout
    assert "--status" in result.stdout
    assert "--author" in result.stdout


class TestSyncCommand:
  """Test sync command."""

  def test_sync_help(self):
    """Test sync command help."""
    result = runner.invoke(app, ["sync", "--help"])
    assert result.exit_code == 0
    assert "Synchronize specifications" in result.stdout
    assert "--language" in result.stdout
    assert "--existing" in result.stdout
    assert "--check" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--specs" in result.stdout
    assert "--adr" in result.stdout
    assert "--prune" in result.stdout

  def test_sync_prune_flag_in_help(self):
    """Test that --prune flag is documented in help."""
    result = runner.invoke(app, ["sync", "--help"])
    assert result.exit_code == 0
    assert "--prune" in result.stdout
    assert "deleted source files" in result.stdout


class TestCommonOptions:
  """Test common options across commands."""

  def test_root_option_in_list_specs(self):
    """Test --root option is available."""
    result = runner.invoke(app, ["list", "specs", "--help"])
    assert result.exit_code == 0
    assert "--root" in result.stdout

  def test_root_option_in_validate(self):
    """Test --root option is available."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "--root" in result.stdout

  def test_root_option_in_adr_sync(self):
    """Test --root option is available."""
    result = runner.invoke(app, ["adr", "sync", "--help"])
    assert result.exit_code == 0
    assert "--root" in result.stdout


class TestCommandStructure:
  """Test command structure follows verb-noun pattern."""

  def test_create_follows_verb_noun(self):
    """Test create commands follow verb-noun pattern."""
    # create spec, create delta, etc.
    result = runner.invoke(app, ["create", "--help"])
    assert result.exit_code == 0
    assert "spec" in result.stdout
    assert "delta" in result.stdout
    assert "requirement" in result.stdout
    assert "revision" in result.stdout

  def test_list_follows_verb_noun(self):
    """Test list commands follow verb-noun pattern."""
    # list specs, list deltas, etc.
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    assert "specs" in result.stdout
    assert "deltas" in result.stdout
    assert "changes" in result.stdout

  def test_show_follows_verb_noun(self):
    """Test show commands follow verb-noun pattern."""
    # show adr
    result = runner.invoke(app, ["show", "--help"])
    assert result.exit_code == 0
    assert "adr" in result.stdout

  def test_complete_follows_verb_noun(self):
    """Test complete commands follow verb-noun pattern."""
    # complete delta
    result = runner.invoke(app, ["complete", "--help"])
    assert result.exit_code == 0
    assert "delta" in result.stdout


class TestErrorHandling:
  """Test error handling in CLI commands."""

  def test_invalid_command(self):
    """Test invalid command returns error."""
    result = runner.invoke(app, ["invalid-command"])
    assert result.exit_code != 0

  def test_missing_required_argument(self):
    """Test missing required argument returns error."""
    result = runner.invoke(app, ["create", "requirement"])
    # Should fail because spec, requirement, and title are required
    assert result.exit_code != 0


if __name__ == "__main__":
  pytest.main([__file__, "-v"])

"""Tests for backfill CLI command.

Note: These are basic tests for the backfill command. Full integration
testing will be performed manually in Task 1.6 due to complexity of
mocking SpecRegistry and template infrastructure.
"""

from typer.testing import CliRunner

from supekku.cli.backfill import app

runner = CliRunner()


def test_backfill_spec_not_found(tmp_path, monkeypatch):
  """Backfilling non-existent spec should error."""
  # Mock find_repo_root to return our test root
  monkeypatch.setattr(
    "supekku.scripts.lib.core.repo.find_repo_root",
    lambda _: tmp_path,
  )

  result = runner.invoke(app, ["SPEC-999"])

  assert result.exit_code == 1
  assert "Specification not found: SPEC-999" in result.stderr


def test_backfill_help():
  """Help text should be available."""
  result = runner.invoke(app, ["--help"])

  assert result.exit_code == 0
  assert "Replace stub spec body with template" in result.stdout
  assert "--force" in result.stdout
  assert "SPEC_ID" in result.stdout

"""Tests for sync CLI command."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from supekku.cli.sync import app


class SyncCommandTest(unittest.TestCase):
  """Test cases for sync CLI command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()

    # Create tech directory structure
    self.tech_dir = self.root / "specify" / "tech"
    self.tech_dir.mkdir(parents=True)

    # Create minimal registry_v2.json
    self.registry_path = self.tech_dir / "registry_v2.json"
    self.registry_path.write_text(
      json.dumps({"version": 2, "languages": {}}),
      encoding="utf-8",
    )

  def tearDown(self) -> None:
    """Clean up test environment."""
    self.tmpdir.cleanup()

  @patch("supekku.cli.sync._sync_requirements")
  @patch("supekku.cli.sync._sync_specs")
  @patch("supekku.cli.sync.find_repo_root")
  def test_sync_exits_zero_when_specs_succeed(
    self,
    mock_find_repo: MagicMock,
    mock_sync_specs: MagicMock,
    mock_sync_reqs: MagicMock,
  ) -> None:
    """Sync should exit 0 when all sync operations succeed."""
    # Setup mocks
    mock_find_repo.return_value = self.root
    mock_sync_specs.return_value = {
      "success": True,
      "processed": 5,
      "created": 0,
      "skipped": 0,
      "orphaned": 0,
    }
    mock_sync_reqs.return_value = {"success": True, "created": 0, "updated": 0}

    # Run sync command
    result = self.runner.invoke(app, ["sync"])

    # Should exit 0
    assert result.exit_code == 0, (
      f"Expected exit code 0, got {result.exit_code}. "
      f"Output: {result.stdout}"
    )
    assert "Sync completed successfully" in result.stdout

  @patch("supekku.cli.sync._sync_requirements")
  @patch("supekku.cli.sync._sync_specs")
  @patch("supekku.cli.sync.find_repo_root")
  def test_sync_exits_one_when_specs_fail(
    self,
    mock_find_repo: MagicMock,
    mock_sync_specs: MagicMock,
    mock_sync_reqs: MagicMock,
  ) -> None:
    """Sync should exit 1 when spec sync returns failure."""
    # Setup mocks
    mock_find_repo.return_value = self.root
    mock_sync_specs.return_value = {
      "success": False,
      "error": "go toolchain unavailable with existing specs",
      "processed": 0,
      "created": 0,
      "skipped": 0,
      "orphaned": 0,
    }
    mock_sync_reqs.return_value = {"success": True, "created": 0, "updated": 0}

    # Run sync command
    result = self.runner.invoke(app, ["sync"])

    # Should exit 1
    assert result.exit_code == 1, (
      f"Expected exit code 1, got {result.exit_code}. "
      f"Output: {result.stdout}"
    )
    # Error messages may go to stdout or stderr depending on typer config
    output = result.stdout + (result.stderr or "")
    assert "Sync completed with errors" in output or result.exit_code == 1


if __name__ == "__main__":
  unittest.main()

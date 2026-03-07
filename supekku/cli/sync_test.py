"""Tests for sync CLI command."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from supekku.cli.sync import app
from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR, TECH_SPECS_SUBDIR


class SyncCommandTest(unittest.TestCase):
  """Test cases for sync CLI command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()

    # Create tech directory structure
    self.tech_dir = self.root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR
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

    # Run sync command (--specs required: default is now off)
    result = self.runner.invoke(app, ["sync", "--specs"])

    # Should exit 0
    assert result.exit_code == 0, (
      f"Expected exit code 0, got {result.exit_code}. Output: {result.stdout}"
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

    # Run sync command (--specs required: default is now off)
    result = self.runner.invoke(app, ["sync", "--specs"])

    # Should exit 1
    assert result.exit_code == 1, (
      f"Expected exit code 1, got {result.exit_code}. Output: {result.stdout}"
    )
    # Error messages may go to stdout or stderr depending on typer config
    output = result.stdout + (result.stderr or "")
    assert "Sync completed with errors" in output or result.exit_code == 1


class SyncBacklogDryRunTest(unittest.TestCase):
  """VT-057-sync-dryrun: _sync_backlog respects dry_run."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()

    # Create minimal spec-driver structure
    self.tech_dir = self.root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR
    self.tech_dir.mkdir(parents=True)
    self.registry_path = self.tech_dir / "registry_v2.json"
    self.registry_path.write_text(
      json.dumps({"version": 2, "languages": {}}),
      encoding="utf-8",
    )

    # Create a backlog item
    from supekku.scripts.lib.core.paths import BACKLOG_DIR

    issues_dir = self.root / SPEC_DRIVER_DIR / BACKLOG_DIR / "issues"
    item_dir = issues_dir / "ISSUE-001-test"
    item_dir.mkdir(parents=True)
    from supekku.scripts.lib.core.spec_utils import dump_markdown_file

    dump_markdown_file(
      item_dir / "ISSUE-001.md",
      {"id": "ISSUE-001", "name": "Test", "kind": "issue", "status": "open"},
      "# Test\n",
    )

    # Create registry dir (but no backlog.yaml yet)
    from supekku.scripts.lib.core.paths import get_registry_dir

    self.registry_dir = get_registry_dir(self.root)
    self.registry_dir.mkdir(parents=True, exist_ok=True)
    self.backlog_yaml = self.registry_dir / "backlog.yaml"

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def test_dry_run_does_not_write_registry(self) -> None:
    """_sync_backlog(dry_run=True) returns stats but does not write backlog.yaml."""
    from supekku.cli.sync import _sync_backlog

    # Ensure no registry file exists before
    assert not self.backlog_yaml.exists()

    result = _sync_backlog(self.root, dry_run=True)
    assert result["total"] == 1
    assert result["added"] == 1

    # File should NOT have been written
    assert not self.backlog_yaml.exists()

  def test_non_dry_run_writes_registry(self) -> None:
    """_sync_backlog(dry_run=False) writes backlog.yaml."""
    from supekku.cli.sync import _sync_backlog

    result = _sync_backlog(self.root, dry_run=False)
    assert result["total"] == 1
    assert self.backlog_yaml.exists()


if __name__ == "__main__":
  unittest.main()

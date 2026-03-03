"""Tests for complete CLI commands."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from typer.testing import CliRunner

from supekku.cli.complete import app


class CompleteRevisionCommandTest(unittest.TestCase):
  """Test cases for complete revision CLI command."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self._cwd = Path.cwd()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    os.chdir(self.root)

  def tearDown(self) -> None:
    os.chdir(self._cwd)
    self.tmpdir.cleanup()

  def _create_revision(
    self,
    revision_id: str = "RE-001",
    status: str = "draft",
  ) -> Path:
    """Create a minimal revision file for testing."""
    revision_dir = self.root / "change" / "revisions" / f"{revision_id}-test"
    revision_dir.mkdir(parents=True, exist_ok=True)
    revision_path = revision_dir / f"{revision_id}.md"
    revision_path.write_text(
      f"---\nid: {revision_id}\nslug: test\nname: Test Revision\n"
      f"created: '2026-01-01'\nupdated: '2026-01-01'\n"
      f"status: {status}\nkind: revision\naliases: []\nrelations: []\n"
      f"---\n\n# {revision_id}\n",
      encoding="utf-8",
    )
    return revision_path

  def test_complete_revision_success(self) -> None:
    """Test completing a revision via CLI."""
    self._create_revision()
    result = self.runner.invoke(app, ["revision", "RE-001"])
    assert result.exit_code == 0
    assert "completed" in result.stdout.lower()

  def test_complete_revision_not_found(self) -> None:
    """Test error when revision not found."""
    (self.root / "change" / "revisions").mkdir(parents=True, exist_ok=True)
    result = self.runner.invoke(app, ["revision", "RE-999"])
    assert result.exit_code == 1

  def test_complete_revision_with_force(self) -> None:
    """Test completing revision with --force flag."""
    self._create_revision(status="deferred")
    result = self.runner.invoke(app, ["revision", "RE-001", "--force"])
    assert result.exit_code == 0


class CreateAuditCommandTest(unittest.TestCase):
  """Test cases for create audit CLI command (smoke tests via create app)."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self._cwd = Path.cwd()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    templates_dir = self.root / ".spec-driver" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    (templates_dir / "audit.md").write_text(
      "{{ audit_verification_block }}\n\n## Observations\n",
      encoding="utf-8",
    )
    os.chdir(self.root)

  def tearDown(self) -> None:
    os.chdir(self._cwd)
    self.tmpdir.cleanup()

  def test_create_audit_via_cli(self) -> None:
    """Test creating an audit via CLI."""
    from supekku.cli.create import app as create_app

    result = self.runner.invoke(
      create_app,
      ["audit", "Test Audit", "--spec", "SPEC-100"],
    )
    assert result.exit_code == 0
    assert "Audit created: AUD-001" in result.stdout

  def test_create_audit_with_all_options(self) -> None:
    """Test creating an audit with all CLI options."""
    from supekku.cli.create import app as create_app

    result = self.runner.invoke(
      create_app,
      [
        "audit", "Full Audit",
        "--spec", "SPEC-100",
        "--prod", "PROD-016",
        "--code-scope", "supekku/cli/**",
      ],
    )
    assert result.exit_code == 0
    assert "AUD-001" in result.stdout


if __name__ == "__main__":
  unittest.main()

"""Tests for skills CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from supekku.cli.skills import app

runner = CliRunner()


def _setup_repo(tmp_path: Path) -> Path:
  """Create minimal repo for skills sync."""
  root = tmp_path
  sd = root / ".spec-driver"
  sd.mkdir()
  (sd / "skills.allowlist").write_text("boot\n", encoding="utf-8")

  skill_dir = root / ".agent" / "skills" / "boot"
  skill_dir.mkdir(parents=True)
  (skill_dir / "SKILL.md").write_text(
    "---\nname: boot\ndescription: Onboarding.\n---\n",
    encoding="utf-8",
  )
  # Git init so find_repo_root works
  (root / ".git").mkdir()
  return root


def test_skills_sync_writes_output(tmp_path: Path) -> None:
  """CLI reports number of skills written."""
  root = _setup_repo(tmp_path)
  with patch(
    "supekku.cli.skills.find_repo_root",
    return_value=root,
  ):
    result = runner.invoke(app, [])
  assert result.exit_code == 0
  assert "1 skills" in result.output


def test_skills_sync_idempotent(tmp_path: Path) -> None:
  """Second run reports no changes."""
  root = _setup_repo(tmp_path)
  with patch(
    "supekku.cli.skills.find_repo_root",
    return_value=root,
  ):
    runner.invoke(app, [])
    result = runner.invoke(app, [])
  assert result.exit_code == 0
  assert "up to date" in result.output


def test_skills_sync_warns_missing(tmp_path: Path) -> None:
  """Warns about missing allowlisted skills."""
  root = tmp_path
  sd = root / ".spec-driver"
  sd.mkdir()
  (sd / "skills.allowlist").write_text("ghost\n", encoding="utf-8")
  (root / ".git").mkdir()

  with patch(
    "supekku.cli.skills.find_repo_root",
    return_value=root,
  ):
    result = runner.invoke(app, [])
  assert result.exit_code == 0
  assert "'ghost' not found" in result.output

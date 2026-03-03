"""Tests for skills CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from supekku.cli.skills import app

runner = CliRunner()


def _make_skill(skills_dir: Path, name: str, description: str) -> None:
  """Helper to create a SKILL.md with frontmatter."""
  skill_dir = skills_dir / name
  skill_dir.mkdir(parents=True, exist_ok=True)
  (skill_dir / "SKILL.md").write_text(
    f"---\nname: {name}\ndescription: {description}\n---\n",
    encoding="utf-8",
  )


def _setup_repo(tmp_path: Path) -> tuple[Path, Path]:
  """Create minimal repo for skills sync.

  Returns (repo_root, skills_source_dir).
  """
  root = tmp_path / "repo"
  root.mkdir()
  sd = root / ".spec-driver"
  sd.mkdir()
  (sd / "skills.allowlist").write_text("boot\n", encoding="utf-8")

  # Package-like skills source
  source = tmp_path / "pkg_skills"
  _make_skill(source, "boot", "Onboarding.")

  # Git init so find_repo_root works
  (root / ".git").mkdir()
  return root, source


def test_skills_sync_writes_output(tmp_path: Path) -> None:
  """CLI reports skills written to AGENTS.md."""
  root, source = _setup_repo(tmp_path)
  with (
    patch("supekku.cli.skills.find_repo_root", return_value=root),
    patch(
      "supekku.scripts.lib.skills.sync.get_package_skills_dir",
      return_value=source,
    ),
  ):
    result = runner.invoke(app, [])
  assert result.exit_code == 0
  assert "1 skills" in result.output


def test_skills_sync_reports_target_status(tmp_path: Path) -> None:
  """CLI reports per-target install status."""
  root, source = _setup_repo(tmp_path)
  with (
    patch("supekku.cli.skills.find_repo_root", return_value=root),
    patch(
      "supekku.scripts.lib.skills.sync.get_package_skills_dir",
      return_value=source,
    ),
  ):
    result = runner.invoke(app, [])
  assert result.exit_code == 0
  assert "claude:" in result.output
  assert "codex:" in result.output


def test_skills_sync_idempotent(tmp_path: Path) -> None:
  """Second run reports up to date."""
  root, source = _setup_repo(tmp_path)
  with (
    patch("supekku.cli.skills.find_repo_root", return_value=root),
    patch(
      "supekku.scripts.lib.skills.sync.get_package_skills_dir",
      return_value=source,
    ),
  ):
    runner.invoke(app, [])
    result = runner.invoke(app, [])
  assert result.exit_code == 0
  assert "up to date" in result.output


def test_skills_sync_warns_missing(tmp_path: Path) -> None:
  """Warns about missing allowlisted skills."""
  root = tmp_path / "repo"
  root.mkdir()
  sd = root / ".spec-driver"
  sd.mkdir()
  (sd / "skills.allowlist").write_text("ghost\n", encoding="utf-8")
  (root / ".git").mkdir()

  source = tmp_path / "empty_source"
  source.mkdir()

  with (
    patch("supekku.cli.skills.find_repo_root", return_value=root),
    patch(
      "supekku.scripts.lib.skills.sync.get_package_skills_dir",
      return_value=source,
    ),
  ):
    result = runner.invoke(app, [])
  assert result.exit_code == 0
  assert "'ghost' not found" in result.output

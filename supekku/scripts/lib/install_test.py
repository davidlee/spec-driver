"""Tests for the install script."""

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest
import yaml

from supekku.scripts.install import get_package_root, initialize_workspace
from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR


def test_get_package_root() -> None:
  """Test that get_package_root returns the supekku directory."""
  root = get_package_root()
  assert root.name == "supekku"
  assert (root / "templates").exists()
  assert (root / "about").exists()


def test_initialize_workspace_creates_directories(tmp_path: Path) -> None:
  """Test that initialize_workspace creates the expected directory structure."""
  initialize_workspace(tmp_path, auto_yes=True)

  # Verify directories were created
  expected_dirs = [
    "change/audits",
    "change/deltas",
    "change/revisions",
    "specify/decisions",
    "specify/policies",
    "specify/product",
    "specify/tech",
    "backlog/improvements",
    "backlog/issues",
    "backlog/problems",
    "backlog/risks",
    f"{SPEC_DRIVER_DIR}/registry",
    f"{SPEC_DRIVER_DIR}/templates",
    f"{SPEC_DRIVER_DIR}/about",
  ]

  for dir_path in expected_dirs:
    assert (tmp_path / dir_path).is_dir(), f"Directory {dir_path} not created"

  # Verify backlog.md was created
  backlog_file = tmp_path / "backlog" / "backlog.md"
  assert backlog_file.exists(), "backlog/backlog.md not created"

  # Verify content
  content = backlog_file.read_text()
  assert "# Backlog" in content
  assert "improvements/" in content


def test_initialize_workspace_creates_registry_files(tmp_path: Path) -> None:
  """Test that initialize_workspace creates registry files with correct content."""
  initialize_workspace(tmp_path, auto_yes=True)

  registry_dir = tmp_path / SPEC_DRIVER_DIR / "registry"

  # Check each registry file
  expected_registries = {
    "deltas.yaml": {"deltas": {}},
    "revisions.yaml": {"revisions": {}},
    "audits.yaml": {"audits": {}},
    "decisions.yaml": {"decisions": {}},
    "requirements.yaml": {"requirements": {}},
  }

  for filename, expected_content in expected_registries.items():
    registry_file = registry_dir / filename
    assert registry_file.exists(), f"Registry file {filename} not created"

    content = yaml.safe_load(registry_file.read_text())
    assert content == expected_content, f"Registry {filename} has wrong content"


def test_initialize_workspace_copies_templates(tmp_path: Path) -> None:
  """Test that initialize_workspace copies template files."""
  initialize_workspace(tmp_path, auto_yes=True)

  template_dir = tmp_path / SPEC_DRIVER_DIR / "templates"
  assert template_dir.exists()

  # Check that at least some template files were copied
  template_files = list(template_dir.glob("*.md"))
  assert len(template_files) > 0, "No template files were copied"

  # Verify a specific template exists
  assert (template_dir / "ADR.md").exists()


def test_initialize_workspace_copies_about_files(tmp_path: Path) -> None:
  """Test that initialize_workspace copies about documentation."""
  initialize_workspace(tmp_path, auto_yes=True)

  about_dir = tmp_path / SPEC_DRIVER_DIR / "about"
  assert about_dir.exists()

  # Check that about files were copied
  about_files = list(about_dir.rglob("*.md"))
  assert len(about_files) > 0, "No about files were copied"


def test_initialize_workspace_copies_agents_when_claude_exists(tmp_path: Path) -> None:
  """Test that initialize_workspace copies agents if .claude exists."""
  # Create .claude directory before installing
  claude_dir = tmp_path / ".claude"
  claude_dir.mkdir()

  initialize_workspace(tmp_path, auto_yes=True)

  commands_dir = claude_dir / "commands"
  assert commands_dir.exists()

  # Check that agent files were copied
  agent_files = list(commands_dir.glob("*.md"))
  assert len(agent_files) > 0, "No agent files were copied"


def test_initialize_workspace_skips_commands_when_no_claude(tmp_path: Path) -> None:
  """Test that agent commands are not copied if .claude didn't exist before install."""
  # .claude may be created by sync_skills (for skills), but commands/ should not
  initialize_workspace(tmp_path, auto_yes=True)

  commands_dir = tmp_path / ".claude" / "commands"
  assert not commands_dir.exists()


def test_initialize_workspace_skips_existing_files(tmp_path: Path) -> None:
  """Test that initialize_workspace doesn't overwrite registry files (user data)."""
  registry_dir = tmp_path / SPEC_DRIVER_DIR / "registry"
  registry_dir.mkdir(parents=True)

  # Create a registry file with custom content
  deltas_file = registry_dir / "deltas.yaml"
  custom_content = {"deltas": {"DE-001": {"title": "Test"}}}
  deltas_file.write_text(yaml.safe_dump(custom_content))

  # Even with auto_yes, registry files should never be overwritten
  initialize_workspace(tmp_path, auto_yes=True)

  # Verify the file wasn't overwritten
  content = yaml.safe_load(deltas_file.read_text())
  assert content == custom_content


def test_initialize_workspace_fails_on_nonexistent_directory() -> None:
  """Test that initialize_workspace exits if target directory doesn't exist."""
  nonexistent = Path("/tmp/definitely-does-not-exist-12345")

  with pytest.raises(SystemExit):
    initialize_workspace(nonexistent)


def test_initialize_workspace_dry_run(tmp_path: Path, capsys) -> None:
  """Test that dry-run mode shows changes without making them."""
  original_cwd = Path.cwd()
  try:
    # Change to tmp_path so relative paths work
    os.chdir(tmp_path)

    # Create .claude directory to trigger agent file checks
    (tmp_path / ".claude").mkdir()

    # Run in dry-run mode
    initialize_workspace(tmp_path, dry_run=True)

    # Verify output mentions dry run
    captured = capsys.readouterr()
    assert "[DRY RUN]" in captured.out

    # Verify relative paths are shown in output
    assert f"./{SPEC_DRIVER_DIR}/templates/ADR.md" in captured.out
  finally:
    os.chdir(original_cwd)

  # Verify templates were NOT copied
  template_dir = tmp_path / SPEC_DRIVER_DIR / "templates"
  template_files = list(template_dir.glob("*.md"))
  assert len(template_files) == 0, "Templates should not be copied in dry-run mode"

  # Verify about files were NOT copied
  about_dir = tmp_path / SPEC_DRIVER_DIR / "about"
  about_files = list(about_dir.rglob("*.md"))
  assert len(about_files) == 0, "About files should not be copied in dry-run mode"


def test_initialize_workspace_dry_run_with_existing_files(
  tmp_path: Path, capsys
) -> None:
  """Test that dry-run mode correctly identifies updates to existing files."""
  # First, do a normal install
  initialize_workspace(tmp_path, auto_yes=True)

  # Modify a template file to simulate an update
  template_dir = tmp_path / SPEC_DRIVER_DIR / "templates"
  adr_file = template_dir / "ADR.md"
  adr_file.write_text("modified content")

  # Run dry-run again
  initialize_workspace(tmp_path, dry_run=True)

  # Verify output shows updates
  captured = capsys.readouterr()
  assert "[DRY RUN]" in captured.out
  assert "updates" in captured.out.lower() or "~" in captured.out

  # Verify the modified file wasn't restored
  assert adr_file.read_text() == "modified content"


def test_initialize_workspace_auto_yes_updates_files(tmp_path: Path) -> None:
  """Test that --yes flag automatically updates existing files."""
  # First, do a normal install
  initialize_workspace(tmp_path, auto_yes=True)

  # Modify a template file
  template_dir = tmp_path / SPEC_DRIVER_DIR / "templates"
  adr_file = template_dir / "ADR.md"
  adr_file.write_text("modified content")

  # Get the original content from the package
  package_root = get_package_root()
  original_content = (package_root / "templates" / "ADR.md").read_text()

  # Run with auto_yes=True
  initialize_workspace(tmp_path, auto_yes=True)

  # Verify the file was restored
  assert adr_file.read_text() == original_content


def test_initialize_workspace_prompts_for_updates(tmp_path: Path) -> None:
  """Test that initialize_workspace prompts for updates when files exist."""
  # First, do a normal install
  initialize_workspace(tmp_path, auto_yes=True)

  # Modify a template file
  template_dir = tmp_path / SPEC_DRIVER_DIR / "templates"
  adr_file = template_dir / "ADR.md"
  adr_file.write_text("modified content")

  # Mock user saying "no" to updates
  with mock.patch("builtins.input", return_value="n"):
    initialize_workspace(tmp_path)

  # Verify the file was NOT restored
  assert adr_file.read_text() == "modified content"

  # Get the original content from the package
  package_root = get_package_root()
  original_content = (package_root / "templates" / "ADR.md").read_text()

  # Mock user saying "yes" to updates
  with mock.patch("builtins.input", return_value="y"):
    initialize_workspace(tmp_path)

  # Verify the file WAS restored
  assert adr_file.read_text() == original_content


def test_initialize_workspace_registry_files_never_overwritten(tmp_path: Path) -> None:
  """Test that registry files are never overwritten, even with --yes."""
  registry_dir = tmp_path / SPEC_DRIVER_DIR / "registry"
  registry_dir.mkdir(parents=True)

  # Create a registry file with custom content
  deltas_file = registry_dir / "deltas.yaml"
  custom_content = {"deltas": {"DE-001": {"title": "Test"}}}
  deltas_file.write_text(yaml.safe_dump(custom_content))

  # Run with auto_yes=True
  initialize_workspace(tmp_path, auto_yes=True)

  # Verify the registry file was NOT overwritten
  content = yaml.safe_load(deltas_file.read_text())
  assert content == custom_content


def test_initialize_workspace_backlog_never_overwritten(tmp_path: Path) -> None:
  """Test that backlog.md is never overwritten, even with --yes."""
  backlog_dir = tmp_path / "backlog"
  backlog_dir.mkdir(parents=True)

  # Create backlog file with custom content
  backlog_file = backlog_dir / "backlog.md"
  custom_content = "# My Custom Backlog\n\nCustom content here."
  backlog_file.write_text(custom_content)

  # Run with auto_yes=True
  initialize_workspace(tmp_path, auto_yes=True)

  # Verify the backlog file was NOT overwritten
  assert backlog_file.read_text() == custom_content


def test_initialize_workspace_prompts_per_category(tmp_path: Path, capsys) -> None:
  """Test that initialize_workspace prompts separately for each category."""
  original_cwd = Path.cwd()
  try:
    # Change to tmp_path so relative paths work
    os.chdir(tmp_path)

    # First install
    initialize_workspace(tmp_path, auto_yes=True)

    # Modify files in different categories
    template_dir = tmp_path / SPEC_DRIVER_DIR / "templates"
    (template_dir / "ADR.md").write_text("modified")

    about_dir = tmp_path / SPEC_DRIVER_DIR / "about"
    (about_dir / "README.md").write_text("modified")

    # Mock user saying "no" to templates, "yes" to about docs,
    # "n" to agent commands (.claude/ now exists from sync_skills)
    with mock.patch("builtins.input", side_effect=["n", "y", "n"]):
      initialize_workspace(tmp_path)
      captured = capsys.readouterr()

      # Verify both categories were mentioned
      assert "Templates" in captured.out or "templates" in captured.out
      assert "About" in captured.out or "about" in captured.out

      # Verify relative paths are shown
      assert f"./{SPEC_DRIVER_DIR}/templates/ADR.md" in captured.out
      assert f"./{SPEC_DRIVER_DIR}/about/README.md" in captured.out
  finally:
    os.chdir(original_cwd)

  # Verify templates were NOT updated
  assert (template_dir / "ADR.md").read_text() == "modified"

  # Verify about docs WERE updated
  package_root = get_package_root()
  original_readme = (package_root / "about" / "README.md").read_text()
  assert (about_dir / "README.md").read_text() == original_readme


# --- Agent template rendering tests ---


def test_initialize_workspace_renders_agent_docs(tmp_path: Path) -> None:
  """With workflow.toml present, agent docs are rendered with config values."""
  # Write a workflow.toml with non-default values
  sd_dir = tmp_path / SPEC_DRIVER_DIR
  sd_dir.mkdir(parents=True)
  (sd_dir / "workflow.toml").write_text(
    'ceremony = "town_planner"\n\n[tool]\nexec = "npx"\n\n[cards]\nenabled = false\n',
    encoding="utf-8",
  )

  initialize_workspace(tmp_path, auto_yes=True)

  agents_dir = sd_dir / "agents"
  assert agents_dir.is_dir()

  # All four agent docs should exist
  for name in ("exec", "workflow", "glossary", "policy"):
    assert (agents_dir / f"{name}.md").exists(), f"agents/{name}.md missing"

  # exec.md should contain the configured tool runner
  exec_content = (agents_dir / "exec.md").read_text()
  assert "npx" in exec_content

  # workflow.md should reflect ceremony mode
  workflow_content = (agents_dir / "workflow.md").read_text()
  assert "town_planner" in workflow_content

  # cards disabled: glossary should NOT mention "Card"
  glossary_content = (agents_dir / "glossary.md").read_text()
  assert "Card" not in glossary_content


def test_initialize_workspace_renders_agent_docs_with_defaults(
  tmp_path: Path,
) -> None:
  """Without workflow.toml, agent docs are rendered using default config."""
  initialize_workspace(tmp_path, auto_yes=True)

  agents_dir = tmp_path / SPEC_DRIVER_DIR / "agents"

  for name in ("exec", "workflow", "glossary", "policy"):
    assert (agents_dir / f"{name}.md").exists(), f"agents/{name}.md missing"

  # Defaults: ceremony=pioneer, tool.exec="uv run spec-driver", cards.enabled=True
  exec_content = (agents_dir / "exec.md").read_text()
  assert "uv run spec-driver" in exec_content

  workflow_content = (agents_dir / "workflow.md").read_text()
  assert "pioneer" in workflow_content

  glossary_content = (agents_dir / "glossary.md").read_text()
  assert "Card" in glossary_content


def test_initialize_workspace_agent_docs_idempotent(tmp_path: Path) -> None:
  """Re-running produces identical agent docs."""
  initialize_workspace(tmp_path, auto_yes=True)

  agents_dir = tmp_path / SPEC_DRIVER_DIR / "agents"
  first_run = {
    name: (agents_dir / f"{name}.md").read_text()
    for name in ("exec", "workflow", "glossary", "policy")
  }

  # Re-run
  initialize_workspace(tmp_path, auto_yes=True)

  for name, content in first_run.items():
    assert (agents_dir / f"{name}.md").read_text() == content, (
      f"agents/{name}.md changed on re-run"
    )


def test_initialize_workspace_agent_fallback_to_static_copy(
  tmp_path: Path,
) -> None:
  """If agent templates are missing, fall back to static copy."""
  # Temporarily move the agent templates out of the way
  package_root = get_package_root()
  agents_template_dir = package_root / "templates" / "agents"
  backup = package_root / "templates" / "_agents_backup"

  try:
    agents_template_dir.rename(backup)

    initialize_workspace(tmp_path, auto_yes=True)

    agents_dir = tmp_path / SPEC_DRIVER_DIR / "agents"
    # Static fallback should have copied whatever is in supekku/agents/
    # At minimum the directory should exist (even if only dogma.md)
    assert agents_dir.is_dir()
  finally:
    # Restore
    if backup.exists():
      backup.rename(agents_template_dir)


# --- Skills installation integration ---


def test_initialize_workspace_installs_skills(tmp_path: Path) -> None:
  """initialize_workspace calls sync_skills to install package skills."""
  # Create allowlist
  sd = tmp_path / SPEC_DRIVER_DIR
  sd.mkdir(parents=True)
  (sd / "skills.allowlist").write_text("boot\nconsult\n", encoding="utf-8")

  initialize_workspace(tmp_path, auto_yes=True)

  # Skills should be installed to default targets
  claude_skills = tmp_path / ".claude" / "skills"
  agents_skills = tmp_path / ".agents" / "skills"

  assert claude_skills.is_dir(), ".claude/skills/ not created"
  assert agents_skills.is_dir(), ".agents/skills/ not created"

  # At least boot and consult should be present (from real package skills)
  assert (claude_skills / "boot" / "SKILL.md").is_file()
  assert (claude_skills / "consult" / "SKILL.md").is_file()
  assert (agents_skills / "boot" / "SKILL.md").is_file()
  assert (agents_skills / "consult" / "SKILL.md").is_file()


def test_initialize_workspace_dry_run_skips_skills(tmp_path: Path) -> None:
  """In dry-run mode, skills are not installed."""
  sd = tmp_path / SPEC_DRIVER_DIR
  sd.mkdir(parents=True)
  (sd / "skills.allowlist").write_text("boot\n", encoding="utf-8")

  initialize_workspace(tmp_path, dry_run=True)

  assert not (tmp_path / ".claude" / "skills").exists()
  assert not (tmp_path / ".agents" / "skills").exists()


def test_initialize_workspace_bootstraps_allowlist(tmp_path: Path) -> None:
  """When no allowlist exists, installer creates one with all package skills."""
  initialize_workspace(tmp_path, auto_yes=True)

  allowlist = tmp_path / SPEC_DRIVER_DIR / "skills.allowlist"
  assert allowlist.is_file()
  content = allowlist.read_text(encoding="utf-8")

  # Should contain at least boot and consult (known package skills)
  lines = [
    ln.strip() for ln in content.splitlines() if ln.strip() and not ln.startswith("#")
  ]
  assert "boot" in lines
  assert "consult" in lines

  # Should be sorted
  assert lines == sorted(lines)

  # Skills should actually be installed
  assert (tmp_path / ".claude" / "skills" / "boot" / "SKILL.md").is_file()


def test_initialize_workspace_preserves_existing_allowlist(tmp_path: Path) -> None:
  """Existing allowlist is never overwritten."""
  sd = tmp_path / SPEC_DRIVER_DIR
  sd.mkdir(parents=True)
  (sd / "skills.allowlist").write_text("boot\n", encoding="utf-8")

  initialize_workspace(tmp_path, auto_yes=True)

  content = (sd / "skills.allowlist").read_text(encoding="utf-8")
  assert content == "boot\n"

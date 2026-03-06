"""Tests for the install script."""

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest
import yaml

from supekku.scripts.install import (
  _classify_memory,
  _find_memory_source,
  _install_claude_config,
  _install_hooks,
  _install_memories,
  _stamp_installed_version,
  get_package_root,
  initialize_workspace,
)
from supekku.scripts.lib.core.paths import BACKLOG_DIR, MEMORY_DIR, SPEC_DRIVER_DIR


def test_get_package_root() -> None:
  """Test that get_package_root returns the supekku directory."""
  root = get_package_root()
  assert root.name == "supekku"
  assert (root / "templates").exists()
  assert (root / "about").exists()


def test_initialize_workspace_creates_directories(tmp_path: Path) -> None:
  """Test that initialize_workspace creates the expected directory structure."""
  initialize_workspace(tmp_path, auto_yes=True)

  sd = SPEC_DRIVER_DIR

  # Verify content directories under .spec-driver/ (DE-049 flat layout)
  expected_dirs = [
    f"{sd}/audits",
    f"{sd}/deltas",
    f"{sd}/revisions",
    f"{sd}/decisions",
    f"{sd}/policies",
    f"{sd}/product",
    f"{sd}/standards",
    f"{sd}/tech",
    f"{sd}/backlog/improvements",
    f"{sd}/backlog/issues",
    f"{sd}/backlog/problems",
    f"{sd}/backlog/risks",
    f"{sd}/memory",
    f"{sd}/registry",
    f"{sd}/templates",
    f"{sd}/about",
    f"{sd}/hooks",
  ]

  for dir_path in expected_dirs:
    assert (tmp_path / dir_path).is_dir(), f"Directory {dir_path} not created"

  # Verify backlog.md was created under .spec-driver/backlog/
  backlog_file = tmp_path / sd / BACKLOG_DIR / "backlog.md"
  assert backlog_file.exists(), ".spec-driver/backlog/backlog.md not created"

  # Verify content
  content = backlog_file.read_text()
  assert "# Backlog" in content
  assert "improvements/" in content


def test_initialize_workspace_creates_compat_symlinks(tmp_path: Path) -> None:
  """VT-049-symlinks: installer creates backward-compat symlinks."""
  initialize_workspace(tmp_path, auto_yes=True)
  sd = SPEC_DRIVER_DIR

  # specify/ is a real dir with targeted symlinks (DEC-049-03)
  specify = tmp_path / "specify"
  assert specify.is_dir()
  assert not specify.is_symlink()
  for subdir in ["tech", "product", "decisions", "policies", "standards"]:
    link = specify / subdir
    assert link.is_symlink(), f"specify/{subdir} should be a symlink"
    assert link.resolve() == (tmp_path / sd / subdir).resolve()

  # change/ is a real dir with targeted symlinks
  change = tmp_path / "change"
  assert change.is_dir()
  assert not change.is_symlink()
  for subdir in ["deltas", "revisions", "audits"]:
    link = change / subdir
    assert link.is_symlink(), f"change/{subdir} should be a symlink"
    assert link.resolve() == (tmp_path / sd / subdir).resolve()

  # backlog/ and memory/ are direct symlinks
  for name in ["backlog", "memory"]:
    link = tmp_path / name
    assert link.is_symlink(), f"{name} should be a symlink"
    assert link.resolve() == (tmp_path / sd / name).resolve()


def test_initialize_workspace_compat_symlinks_idempotent(
  tmp_path: Path,
) -> None:
  """VT-049-symlinks: second install doesn't error on existing symlinks."""
  initialize_workspace(tmp_path, auto_yes=True)
  initialize_workspace(tmp_path, auto_yes=True)  # Should not raise

  # Symlinks still correct
  assert (tmp_path / "specify" / "tech").is_symlink()
  assert (tmp_path / "backlog").is_symlink()


def test_initialize_workspace_compat_symlinks_resolve(
  tmp_path: Path,
) -> None:
  """VT-049-symlinks: old paths resolve to content under .spec-driver/."""
  initialize_workspace(tmp_path, auto_yes=True)
  sd = SPEC_DRIVER_DIR

  # Write a file via the new path
  spec_dir = tmp_path / sd / "tech" / "SPEC-001"
  spec_dir.mkdir(parents=True)
  (spec_dir / "SPEC-001.md").write_text("# SPEC-001\n")

  # Read it via the old compat path
  compat_path = tmp_path / "specify" / "tech" / "SPEC-001" / "SPEC-001.md"
  assert compat_path.exists()
  assert compat_path.read_text() == "# SPEC-001\n"


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


def test_initialize_workspace_no_commands_dir_created(tmp_path: Path) -> None:
  """Commands have been replaced by skills; .claude/commands/ should not be created."""
  claude_dir = tmp_path / ".claude"
  claude_dir.mkdir()

  initialize_workspace(tmp_path, auto_yes=True)

  commands_dir = claude_dir / "commands"
  assert not commands_dir.exists(), ".claude/commands/ should not be created"


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
  backlog_dir = tmp_path / BACKLOG_DIR
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

    # Mock user saying "no" to templates, "yes" to about docs
    with mock.patch("builtins.input", side_effect=["n", "y"]):
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


# --- Agent boot.md rendering tests ---


def test_initialize_workspace_renders_boot_agent_doc(tmp_path: Path) -> None:
  """initialize_workspace renders .spec-driver/agents/boot.md from template."""
  initialize_workspace(tmp_path, auto_yes=True)
  boot_md = tmp_path / SPEC_DRIVER_DIR / "agents" / "boot.md"
  assert boot_md.exists()
  assert "/boot" in boot_md.read_text(encoding="utf-8")


def test_initialize_workspace_does_not_create_boot_md(tmp_path: Path) -> None:
  """BOOT.md is no longer created — boot is rendered as an agent doc."""
  initialize_workspace(tmp_path, auto_yes=True)
  assert not (tmp_path / SPEC_DRIVER_DIR / "BOOT.md").exists()


# --- workflow.toml exec detection tests ---


def test_initialize_creates_workflow_toml_with_detected_exec(
  tmp_path: Path,
) -> None:
  """On fresh install, workflow.toml is created with detected exec command."""
  initialize_workspace(tmp_path, auto_yes=True)

  workflow_toml = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  assert workflow_toml.exists()
  content = workflow_toml.read_text(encoding="utf-8")
  assert "[tool]" in content
  assert "exec = " in content


def test_initialize_preserves_existing_workflow_toml(tmp_path: Path) -> None:
  """Existing workflow.toml is never overwritten."""
  sd_dir = tmp_path / SPEC_DRIVER_DIR
  sd_dir.mkdir(parents=True)
  (sd_dir / "workflow.toml").write_text(
    '[tool]\nexec = "custom-runner"\n',
    encoding="utf-8",
  )

  initialize_workspace(tmp_path, auto_yes=True)

  content = (sd_dir / "workflow.toml").read_text(encoding="utf-8")
  assert 'exec = "custom-runner"' in content


def test_initialize_detects_project_dep_exec(tmp_path: Path) -> None:
  """When pyproject.toml lists spec-driver, exec is 'uv run spec-driver'."""
  (tmp_path / "pyproject.toml").write_text(
    '[project]\ndependencies = ["spec-driver>=0.6"]\n',
    encoding="utf-8",
  )

  with mock.patch("supekku.scripts.lib.core.config.which", return_value="/usr/bin/uv"):
    initialize_workspace(tmp_path, auto_yes=True)

  content = (tmp_path / SPEC_DRIVER_DIR / "workflow.toml").read_text(encoding="utf-8")
  assert 'exec = "uv run spec-driver"' in content


def test_initialize_detects_global_install_exec(tmp_path: Path) -> None:
  """When binary is in a permanent location, exec is bare 'spec-driver'."""
  with mock.patch("sys.argv", ["/nix/store/abc/bin/spec-driver", "install"]):
    initialize_workspace(tmp_path, auto_yes=True)

  content = (tmp_path / SPEC_DRIVER_DIR / "workflow.toml").read_text(encoding="utf-8")
  assert 'exec = "spec-driver"' in content


def test_initialize_dry_run_does_not_create_workflow_toml(
  tmp_path: Path,
) -> None:
  """Dry-run reports but does not write workflow.toml."""
  initialize_workspace(tmp_path, dry_run=True)

  assert not (tmp_path / SPEC_DRIVER_DIR / "workflow.toml").exists()


# --- version stamping tests ---


def test_stamp_version_prepends_to_existing_toml(tmp_path: Path) -> None:
  """Stamps version at top of existing workflow.toml."""
  toml = tmp_path / "workflow.toml"
  toml.write_text('ceremony = "settler"\n', encoding="utf-8")
  _stamp_installed_version(toml)
  content = toml.read_text(encoding="utf-8")
  lines = content.splitlines()
  assert lines[0].startswith("spec_driver_installed_version = ")
  assert 'ceremony = "settler"' in content


def test_stamp_version_updates_existing_value(tmp_path: Path) -> None:
  """Updates version if already present in toml."""
  toml = tmp_path / "workflow.toml"
  toml.write_text(
    'spec_driver_installed_version = "0.0.1"\nceremony = "settler"\n',
    encoding="utf-8",
  )
  _stamp_installed_version(toml)
  content = toml.read_text(encoding="utf-8")
  assert content.count("spec_driver_installed_version") == 1
  assert '"0.0.1"' not in content


def test_stamp_version_idempotent(tmp_path: Path) -> None:
  """Running twice produces identical content."""
  toml = tmp_path / "workflow.toml"
  toml.write_text('ceremony = "settler"\n', encoding="utf-8")
  _stamp_installed_version(toml)
  first = toml.read_text(encoding="utf-8")
  _stamp_installed_version(toml)
  second = toml.read_text(encoding="utf-8")
  assert first == second


def test_stamp_version_preserves_comments(tmp_path: Path) -> None:
  """Comments in workflow.toml are preserved."""
  toml = tmp_path / "workflow.toml"
  toml.write_text(
    'ceremony = "settler" # pioneer | settler | town_planner\n',
    encoding="utf-8",
  )
  _stamp_installed_version(toml)
  content = toml.read_text(encoding="utf-8")
  assert "# pioneer | settler | town_planner" in content


def test_stamp_version_dry_run_does_not_modify(tmp_path: Path) -> None:
  """Dry-run does not modify the file."""
  toml = tmp_path / "workflow.toml"
  toml.write_text('ceremony = "settler"\n', encoding="utf-8")
  _stamp_installed_version(toml, dry_run=True)
  content = toml.read_text(encoding="utf-8")
  assert "spec_driver_installed_version" not in content


def test_initialize_stamps_version(tmp_path: Path) -> None:
  """initialize_workspace stamps version in workflow.toml."""
  initialize_workspace(tmp_path, auto_yes=True)
  toml = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  content = toml.read_text(encoding="utf-8")
  assert "spec_driver_installed_version" in content


# --- legacy workspace detection ---


def test_legacy_workspace_warns(
  tmp_path: Path,
  capsys: pytest.CaptureFixture[str],
) -> None:
  """Legacy workspace (no version stamp) prints migration warning."""
  sd = tmp_path / SPEC_DRIVER_DIR
  sd.mkdir(parents=True)
  (sd / "workflow.toml").write_text('ceremony = "settler"\n', encoding="utf-8")
  initialize_workspace(tmp_path, auto_yes=True)
  captured = capsys.readouterr()
  assert captured.out.count("Legacy workspace detected") == 2
  assert "migrate_to_consolidated_layout.sh" in captured.out


def test_fresh_workspace_no_legacy_warning(
  tmp_path: Path,
  capsys: pytest.CaptureFixture[str],
) -> None:
  """Fresh install (no pre-existing workflow.toml) has no legacy warning."""
  initialize_workspace(tmp_path, auto_yes=True)
  captured = capsys.readouterr()
  assert "Legacy workspace detected" not in captured.out


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
  """Without workflow.toml, agent docs are rendered using detected exec + defaults."""
  with mock.patch(
    "supekku.scripts.install.detect_exec_command",
    return_value="uv run spec-driver",
  ):
    initialize_workspace(tmp_path, auto_yes=True)

  agents_dir = tmp_path / SPEC_DRIVER_DIR / "agents"

  for name in ("exec", "workflow", "glossary", "policy"):
    assert (agents_dir / f"{name}.md").exists(), f"agents/{name}.md missing"

  # exec.md reflects detected command written to workflow.toml
  exec_content = (agents_dir / "exec.md").read_text()
  assert "uv run spec-driver" in exec_content

  # Other defaults: ceremony=pioneer, cards.enabled=True
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


# --- Claude config installation tests ---


class TestInstallClaudeConfig:
  """Tests for .claude/ settings and hooks installation."""

  def _make_claude_source(self, package_root: Path) -> None:
    """Create package source files for Claude config."""
    (package_root / "claude.settings.json").write_text(
      '{"hooks": {"SessionStart": [{"hooks": [{"type": "command", '
      '"command": ".claude/hooks/startup.sh"}]}]}}',
      encoding="utf-8",
    )
    hooks_dir = package_root / "claude.hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "startup.sh").write_text(
      '#!/usr/bin/env bash\necho "boot"',
      encoding="utf-8",
    )
    (hooks_dir / "prompt.sh").write_text(
      '#!/usr/bin/bash\necho "prompt"',
      encoding="utf-8",
    )

  def test_installs_settings_and_hooks(self, tmp_path: Path) -> None:
    """Fresh install creates .claude/settings.json and .claude/hooks/*."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    self._make_claude_source(pkg)
    target = tmp_path / "target"
    target.mkdir()

    _install_claude_config(pkg, target, dry_run=False)

    settings = target / ".claude" / "settings.json"
    assert settings.exists()
    assert "SessionStart" in settings.read_text()

    startup = target / ".claude" / "hooks" / "startup.sh"
    assert startup.exists()
    assert os.access(startup, os.X_OK), "startup.sh should be executable"

    prompt = target / ".claude" / "hooks" / "prompt.sh"
    assert prompt.exists()
    assert os.access(prompt, os.X_OK), "prompt.sh should be executable"

  def test_overwrites_on_reinstall(self, tmp_path: Path) -> None:
    """Settings and hooks are overwritten (installer-owned)."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    self._make_claude_source(pkg)
    target = tmp_path / "target"
    target.mkdir()

    # First install
    _install_claude_config(pkg, target, dry_run=False)

    # Modify installed files
    settings = target / ".claude" / "settings.json"
    settings.write_text('{"custom": true}')
    startup = target / ".claude" / "hooks" / "startup.sh"
    startup.write_text("#!/bin/bash\necho custom")

    # Reinstall
    _install_claude_config(pkg, target, dry_run=False)

    assert "SessionStart" in settings.read_text()
    assert "boot" in startup.read_text()

  def test_dry_run_does_not_write(self, tmp_path: Path, capsys) -> None:
    """Dry-run reports without creating files."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    self._make_claude_source(pkg)
    target = tmp_path / "target"
    target.mkdir()

    _install_claude_config(pkg, target, dry_run=True)

    assert not (target / ".claude" / "settings.json").exists()
    assert not (target / ".claude" / "hooks").exists()

    captured = capsys.readouterr()
    assert "[DRY RUN]" in captured.out

  def test_creates_directories(self, tmp_path: Path) -> None:
    """Creates .claude/ and .claude/hooks/ if they don't exist."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    self._make_claude_source(pkg)
    target = tmp_path / "target"
    target.mkdir()

    _install_claude_config(pkg, target, dry_run=False)

    assert (target / ".claude").is_dir()
    assert (target / ".claude" / "hooks").is_dir()

  def test_idempotent(self, tmp_path: Path) -> None:
    """Repeated installs produce identical results."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    self._make_claude_source(pkg)
    target = tmp_path / "target"
    target.mkdir()

    _install_claude_config(pkg, target, dry_run=False)
    first = (target / ".claude" / "settings.json").read_text()

    _install_claude_config(pkg, target, dry_run=False)
    second = (target / ".claude" / "settings.json").read_text()

    assert first == second

  def test_skips_if_no_source_settings(self, tmp_path: Path) -> None:
    """No-op when package has no claude.settings.json."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    target = tmp_path / "target"
    target.mkdir()

    _install_claude_config(pkg, target, dry_run=False)

    assert not (target / ".claude" / "settings.json").exists()

  def test_hooks_without_settings(self, tmp_path: Path) -> None:
    """Hooks are installed even if settings.json is absent."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    hooks_dir = pkg / "claude.hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "startup.sh").write_text("#!/bin/bash\necho hi")

    target = tmp_path / "target"
    target.mkdir()

    _install_claude_config(pkg, target, dry_run=False)

    startup = target / ".claude" / "hooks" / "startup.sh"
    assert startup.exists()
    assert os.access(startup, os.X_OK)


class TestInitializeWorkspaceClaudeConfig:
  """Integration: initialize_workspace installs .claude/ config."""

  def test_installs_claude_settings_and_hooks(self, tmp_path: Path) -> None:
    """initialize_workspace copies Claude settings and hooks."""
    initialize_workspace(tmp_path, auto_yes=True)

    settings = tmp_path / ".claude" / "settings.json"
    assert settings.exists(), ".claude/settings.json not installed"

    hooks_dir = tmp_path / ".claude" / "hooks"
    assert hooks_dir.is_dir(), ".claude/hooks/ not created"

    # Hooks should be executable
    for hook in hooks_dir.glob("*.sh"):
      assert os.access(hook, os.X_OK), f"{hook.name} should be executable"

  def test_dry_run_does_not_install_claude_config(self, tmp_path: Path) -> None:
    """Dry-run does not create .claude/ files."""
    initialize_workspace(tmp_path, dry_run=True)

    # .claude/ may exist from skills dry-run skipping, but settings shouldn't
    settings = tmp_path / ".claude" / "settings.json"
    assert not settings.exists()


# --- Hook file installation tests ---


class TestInstallHooks:
  """Tests for hook file installation (create-if-missing semantics)."""

  def test_installs_hooks_on_fresh_workspace(self, tmp_path: Path) -> None:
    """Fresh install creates .spec-driver/hooks/ with hook files."""
    initialize_workspace(tmp_path, auto_yes=True)

    hooks_dir = tmp_path / SPEC_DRIVER_DIR / "hooks"
    assert hooks_dir.is_dir()
    assert (hooks_dir / "doctrine.md").exists()
    assert (hooks_dir / "README.md").exists()

  def test_does_not_overwrite_existing_hooks(self, tmp_path: Path) -> None:
    """Existing hook files are never overwritten on reinstall."""
    initialize_workspace(tmp_path, auto_yes=True)

    hooks_dir = tmp_path / SPEC_DRIVER_DIR / "hooks"
    doctrine = hooks_dir / "doctrine.md"
    doctrine.write_text("# My custom doctrine\n")

    initialize_workspace(tmp_path, auto_yes=True)

    assert doctrine.read_text() == "# My custom doctrine\n"

  def test_install_hooks_creates_missing_files_only(self, tmp_path: Path) -> None:
    """_install_hooks only creates files that don't exist yet."""
    package_root = get_package_root()
    hooks_dest = tmp_path / SPEC_DRIVER_DIR / "hooks"
    hooks_dest.mkdir(parents=True)

    # Pre-create one file with custom content
    (hooks_dest / "doctrine.md").write_text("custom")

    _install_hooks(package_root, tmp_path, dry_run=False)

    # Custom file preserved
    assert (hooks_dest / "doctrine.md").read_text() == "custom"
    # Other files installed
    assert (hooks_dest / "README.md").exists()

  def test_install_hooks_dry_run(self, tmp_path: Path, capsys) -> None:
    """Dry-run shows what would be installed without creating files."""
    package_root = get_package_root()
    sd_hooks = tmp_path / SPEC_DRIVER_DIR / "hooks"
    sd_hooks.mkdir(parents=True)

    _install_hooks(package_root, tmp_path, dry_run=True)

    captured = capsys.readouterr()
    assert "[DRY RUN]" in captured.out

    # No files should have been created
    hook_files = list(sd_hooks.glob("*"))
    assert len(hook_files) == 0

  def test_install_hooks_idempotent(self, tmp_path: Path) -> None:
    """Repeated installs produce consistent results."""
    initialize_workspace(tmp_path, auto_yes=True)

    hooks_dir = tmp_path / SPEC_DRIVER_DIR / "hooks"
    first_run = {
      f.name: f.read_text() for f in sorted(hooks_dir.iterdir()) if f.is_file()
    }

    initialize_workspace(tmp_path, auto_yes=True)

    second_run = {
      f.name: f.read_text() for f in sorted(hooks_dir.iterdir()) if f.is_file()
    }
    assert first_run == second_run


# --- Memory classification tests ---


class TestClassifyMemory:
  """Tests for _classify_memory namespace classifier."""

  def test_spec_driver_concept(self) -> None:
    assert _classify_memory("mem.concept.spec-driver.delta.md") == "spec-driver"

  def test_spec_driver_pattern(self) -> None:
    assert _classify_memory("mem.pattern.spec-driver.core-loop.md") == "spec-driver"

  def test_spec_driver_signpost(self) -> None:
    assert _classify_memory("mem.signpost.spec-driver.ceremony.md") == "spec-driver"

  def test_spec_driver_fact(self) -> None:
    assert _classify_memory("mem.fact.spec-driver.status-enums.md") == "spec-driver"

  def test_seed_project_pattern(self) -> None:
    assert _classify_memory("mem.pattern.project.workflow.md") == "seed"

  def test_seed_project_completion(self) -> None:
    assert _classify_memory("mem.pattern.project.completion.md") == "seed"

  def test_unmanaged_no_namespace(self) -> None:
    assert _classify_memory("mem.pattern.cli.skinny.md") is None

  def test_unmanaged_spec_without_driver(self) -> None:
    assert _classify_memory("mem.concept.spec.assembly-only-taxonomy.md") is None

  def test_non_markdown_ignored(self) -> None:
    assert _classify_memory("mem.concept.spec-driver.delta.yaml") is None

  def test_random_file_ignored(self) -> None:
    assert _classify_memory("README.md") is None


# --- Memory source discovery tests ---


class TestFindMemorySource:
  """Tests for _find_memory_source dual discovery."""

  def test_finds_in_package_root(self, tmp_path: Path) -> None:
    mem_dir = tmp_path / MEMORY_DIR
    mem_dir.mkdir()
    (mem_dir / "mem.concept.spec-driver.delta.md").write_text("test")
    assert _find_memory_source(tmp_path) == mem_dir

  def test_falls_back_to_parent(self, tmp_path: Path) -> None:
    pkg_root = tmp_path / "supekku"
    pkg_root.mkdir()
    mem_dir = tmp_path / MEMORY_DIR
    mem_dir.mkdir()
    (mem_dir / "mem.concept.spec-driver.delta.md").write_text("test")
    assert _find_memory_source(pkg_root) == mem_dir

  def test_prefers_package_root(self, tmp_path: Path) -> None:
    """Package-level memory dir takes precedence over parent."""
    pkg_memory = tmp_path / MEMORY_DIR
    pkg_memory.mkdir()
    (pkg_memory / "mem.concept.spec-driver.delta.md").write_text("pkg")
    # Don't create parent — just verify the package path wins
    assert _find_memory_source(tmp_path) == pkg_memory

  def test_returns_none_when_absent(self, tmp_path: Path) -> None:
    assert _find_memory_source(tmp_path) is None


# --- Memory install behavior tests ---


def _make_memory_source(src_dir: Path, files: dict[str, str]) -> None:
  """Helper: populate a memory source directory."""
  src_dir.mkdir(parents=True, exist_ok=True)
  for name, content in files.items():
    (src_dir / name).write_text(content, encoding="utf-8")


class TestInstallMemoriesSeed:
  """VT-037-001: seed bucket create-only behavior."""

  def test_creates_missing_seed_memories(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.pattern.project.workflow.md": "default workflow",
        "mem.pattern.project.completion.md": "default completion",
      },
    )
    dest.mkdir()

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    wf = (dest / "mem.pattern.project.workflow.md").read_text()
    assert wf == "default workflow"
    comp = (dest / "mem.pattern.project.completion.md").read_text()
    assert comp == "default completion"

  def test_never_overwrites_customized_seed(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.pattern.project.workflow.md": "new default",
      },
    )
    dest.mkdir()
    (dest / "mem.pattern.project.workflow.md").write_text("my custom workflow")

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    content = (dest / "mem.pattern.project.workflow.md").read_text()
    assert content == "my custom workflow"

  def test_seed_dry_run_does_not_create(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.pattern.project.workflow.md": "default workflow",
      },
    )
    dest.mkdir()

    _install_memories(src, dest, dry_run=True, auto_yes=True)

    assert not (dest / "mem.pattern.project.workflow.md").exists()


class TestInstallMemoriesManaged:
  """VT-037-002: spec-driver managed bucket refresh behavior."""

  def test_creates_new_managed_memories(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.concept.spec-driver.delta.md": "delta v2",
      },
    )
    dest.mkdir()

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert (dest / "mem.concept.spec-driver.delta.md").read_text() == "delta v2"

  def test_replaces_outdated_managed_memories(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.concept.spec-driver.delta.md": "delta v2",
      },
    )
    dest.mkdir()
    (dest / "mem.concept.spec-driver.delta.md").write_text("delta v1")

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert (dest / "mem.concept.spec-driver.delta.md").read_text() == "delta v2"

  def test_skips_unchanged_managed_memories(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    content = "delta same"
    _make_memory_source(
      src,
      {
        "mem.concept.spec-driver.delta.md": content,
      },
    )
    dest.mkdir()
    (dest / "mem.concept.spec-driver.delta.md").write_text(content)

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert (dest / "mem.concept.spec-driver.delta.md").read_text() == content

  def test_prunes_managed_ids_absent_from_source(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.concept.spec-driver.delta.md": "kept",
      },
    )
    dest.mkdir()
    (dest / "mem.concept.spec-driver.delta.md").write_text("kept")
    (dest / "mem.concept.spec-driver.removed.md").write_text("should be pruned")

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert (dest / "mem.concept.spec-driver.delta.md").exists()
    assert not (dest / "mem.concept.spec-driver.removed.md").exists()

  def test_managed_dry_run_does_not_modify(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.concept.spec-driver.delta.md": "new version",
      },
    )
    dest.mkdir()
    (dest / "mem.concept.spec-driver.delta.md").write_text("old version")
    (dest / "mem.concept.spec-driver.removed.md").write_text("should survive dry run")

    _install_memories(src, dest, dry_run=True, auto_yes=True)

    assert (dest / "mem.concept.spec-driver.delta.md").read_text() == "old version"
    assert (dest / "mem.concept.spec-driver.removed.md").exists()


class TestInstallMemoriesUnmanaged:
  """VT-037-003: unmanaged user memories are preserved."""

  def test_preserves_unmanaged_memories(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.concept.spec-driver.delta.md": "managed",
        "mem.pattern.project.workflow.md": "seed",
      },
    )
    dest.mkdir()
    (dest / "mem.pattern.cli.skinny.md").write_text("user memory")
    (dest / "mem.pattern.formatters.soc.md").write_text("another user memory")

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert (dest / "mem.pattern.cli.skinny.md").read_text() == "user memory"
    assert (dest / "mem.pattern.formatters.soc.md").read_text() == "another user memory"

  def test_unmanaged_source_files_are_skipped(self, tmp_path: Path) -> None:
    """Unmanaged files in source are not installed."""
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.pattern.cli.skinny.md": "should not be installed",
        "README.md": "also not installed",
      },
    )
    dest.mkdir()

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert not (dest / "mem.pattern.cli.skinny.md").exists()
    assert not (dest / "README.md").exists()


class TestInstallMemoriesIdempotence:
  """Repeated installs produce consistent results."""

  def test_repeated_install_is_idempotent(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.concept.spec-driver.delta.md": "managed",
        "mem.pattern.project.workflow.md": "seed default",
      },
    )
    dest.mkdir()

    _install_memories(src, dest, dry_run=False, auto_yes=True)
    first_run = {f.name: f.read_text() for f in sorted(dest.glob("*.md"))}

    _install_memories(src, dest, dry_run=False, auto_yes=True)
    second_run = {f.name: f.read_text() for f in sorted(dest.glob("*.md"))}

    assert first_run == second_run


class TestInstallMemoriesReporting:
  """Output reporting for memory install."""

  def test_reports_seed_left_untouched(self, tmp_path: Path, capsys) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.pattern.project.workflow.md": "new default",
      },
    )
    dest.mkdir()
    (dest / "mem.pattern.project.workflow.md").write_text("customized")

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    captured = capsys.readouterr()
    assert "untouched" in captured.out.lower() or "skipped" in captured.out.lower()

  def test_reports_pruned_managed_files(self, tmp_path: Path, capsys) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(src, {})
    dest.mkdir()
    (dest / "mem.concept.spec-driver.removed.md").write_text("old")

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    captured = capsys.readouterr()
    assert "prun" in captured.out.lower() or "remov" in captured.out.lower()

  def test_dry_run_reports_with_prefix(self, tmp_path: Path, capsys) -> None:
    """VT-037-004: dry-run output distinguishes categories."""
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.pattern.project.workflow.md": "seed default",
        "mem.concept.spec-driver.delta.md": "managed v2",
      },
    )
    dest.mkdir()
    (dest / "mem.concept.spec-driver.delta.md").write_text("managed v1")
    (dest / "mem.concept.spec-driver.old.md").write_text("to prune")

    _install_memories(src, dest, dry_run=True, auto_yes=True)

    captured = capsys.readouterr()
    assert "[DRY RUN]" in captured.out
    assert "Seed memories" in captured.out
    assert "Managed memories" in captured.out

  def test_reports_new_managed_and_updated(
    self,
    tmp_path: Path,
    capsys,
  ) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(
      src,
      {
        "mem.concept.spec-driver.new.md": "brand new",
        "mem.concept.spec-driver.existing.md": "updated",
      },
    )
    dest.mkdir()
    (dest / "mem.concept.spec-driver.existing.md").write_text("old")

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    captured = capsys.readouterr()
    assert "1 new" in captured.out
    assert "1 updated" in captured.out


# --- Integration: initialize_workspace with memories ---


class TestInitializeWorkspaceMemories:
  """Integration tests for memory install via initialize_workspace."""

  def test_installs_memories_on_fresh_workspace(
    self,
    tmp_path: Path,
  ) -> None:
    """Fresh install creates memory directory with managed + seed files."""
    initialize_workspace(tmp_path, auto_yes=True)

    memory_dir = tmp_path / MEMORY_DIR
    assert memory_dir.is_dir()

    # Should have at least some managed memories
    managed = [
      f for f in memory_dir.glob("*.md") if _classify_memory(f.name) == "spec-driver"
    ]
    assert len(managed) > 0

    # Should have seed stubs
    seeds = [f for f in memory_dir.glob("*.md") if _classify_memory(f.name) == "seed"]
    assert len(seeds) > 0

  def test_preserves_customized_seed_on_reinstall(
    self,
    tmp_path: Path,
  ) -> None:
    initialize_workspace(tmp_path, auto_yes=True)

    # Customise a seed memory
    wf = tmp_path / MEMORY_DIR / "mem.pattern.project.workflow.md"
    assert wf.exists()
    wf.write_text("my custom workflow")

    # Reinstall
    initialize_workspace(tmp_path, auto_yes=True)

    assert wf.read_text() == "my custom workflow"

  def test_dry_run_does_not_create_memories(
    self,
    tmp_path: Path,
  ) -> None:
    initialize_workspace(tmp_path, dry_run=True)
    memory_dir = tmp_path / MEMORY_DIR
    # Memory dir might be created (mkdir), but no files copied
    md_files = list(memory_dir.glob("*.md")) if memory_dir.exists() else []
    assert len(md_files) == 0

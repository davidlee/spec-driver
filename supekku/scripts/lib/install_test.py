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
  _install_memories,
  get_package_root,
  initialize_workspace,
)
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
    mem_dir = tmp_path / "memory"
    mem_dir.mkdir()
    (mem_dir / "mem.concept.spec-driver.delta.md").write_text("test")
    assert _find_memory_source(tmp_path) == mem_dir

  def test_falls_back_to_parent(self, tmp_path: Path) -> None:
    pkg_root = tmp_path / "supekku"
    pkg_root.mkdir()
    mem_dir = tmp_path / "memory"
    mem_dir.mkdir()
    (mem_dir / "mem.concept.spec-driver.delta.md").write_text("test")
    assert _find_memory_source(pkg_root) == mem_dir

  def test_prefers_package_root(self, tmp_path: Path) -> None:
    """Package-level memory dir takes precedence over parent."""
    pkg_memory = tmp_path / "memory"
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
    _make_memory_source(src, {
      "mem.pattern.project.workflow.md": "default workflow",
      "mem.pattern.project.completion.md": "default completion",
    })
    dest.mkdir()

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    wf = (dest / "mem.pattern.project.workflow.md").read_text()
    assert wf == "default workflow"
    comp = (dest / "mem.pattern.project.completion.md").read_text()
    assert comp == "default completion"

  def test_never_overwrites_customized_seed(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(src, {
      "mem.pattern.project.workflow.md": "new default",
    })
    dest.mkdir()
    (dest / "mem.pattern.project.workflow.md").write_text("my custom workflow")

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    content = (dest / "mem.pattern.project.workflow.md").read_text()
    assert content == "my custom workflow"

  def test_seed_dry_run_does_not_create(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(src, {
      "mem.pattern.project.workflow.md": "default workflow",
    })
    dest.mkdir()

    _install_memories(src, dest, dry_run=True, auto_yes=True)

    assert not (dest / "mem.pattern.project.workflow.md").exists()


class TestInstallMemoriesManaged:
  """VT-037-002: spec-driver managed bucket refresh behavior."""

  def test_creates_new_managed_memories(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(src, {
      "mem.concept.spec-driver.delta.md": "delta v2",
    })
    dest.mkdir()

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert (dest / "mem.concept.spec-driver.delta.md").read_text() == "delta v2"

  def test_replaces_outdated_managed_memories(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(src, {
      "mem.concept.spec-driver.delta.md": "delta v2",
    })
    dest.mkdir()
    (dest / "mem.concept.spec-driver.delta.md").write_text("delta v1")

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert (dest / "mem.concept.spec-driver.delta.md").read_text() == "delta v2"

  def test_skips_unchanged_managed_memories(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    content = "delta same"
    _make_memory_source(src, {
      "mem.concept.spec-driver.delta.md": content,
    })
    dest.mkdir()
    (dest / "mem.concept.spec-driver.delta.md").write_text(content)

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert (dest / "mem.concept.spec-driver.delta.md").read_text() == content

  def test_prunes_managed_ids_absent_from_source(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(src, {
      "mem.concept.spec-driver.delta.md": "kept",
    })
    dest.mkdir()
    (dest / "mem.concept.spec-driver.delta.md").write_text("kept")
    (dest / "mem.concept.spec-driver.removed.md").write_text("should be pruned")

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert (dest / "mem.concept.spec-driver.delta.md").exists()
    assert not (dest / "mem.concept.spec-driver.removed.md").exists()

  def test_managed_dry_run_does_not_modify(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(src, {
      "mem.concept.spec-driver.delta.md": "new version",
    })
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
    _make_memory_source(src, {
      "mem.concept.spec-driver.delta.md": "managed",
      "mem.pattern.project.workflow.md": "seed",
    })
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
    _make_memory_source(src, {
      "mem.pattern.cli.skinny.md": "should not be installed",
      "README.md": "also not installed",
    })
    dest.mkdir()

    _install_memories(src, dest, dry_run=False, auto_yes=True)

    assert not (dest / "mem.pattern.cli.skinny.md").exists()
    assert not (dest / "README.md").exists()


class TestInstallMemoriesIdempotence:
  """Repeated installs produce consistent results."""

  def test_repeated_install_is_idempotent(self, tmp_path: Path) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(src, {
      "mem.concept.spec-driver.delta.md": "managed",
      "mem.pattern.project.workflow.md": "seed default",
    })
    dest.mkdir()

    _install_memories(src, dest, dry_run=False, auto_yes=True)
    first_run = {
      f.name: f.read_text() for f in sorted(dest.glob("*.md"))
    }

    _install_memories(src, dest, dry_run=False, auto_yes=True)
    second_run = {
      f.name: f.read_text() for f in sorted(dest.glob("*.md"))
    }

    assert first_run == second_run


class TestInstallMemoriesReporting:
  """Output reporting for memory install."""

  def test_reports_seed_left_untouched(self, tmp_path: Path, capsys) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(src, {
      "mem.pattern.project.workflow.md": "new default",
    })
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
    _make_memory_source(src, {
      "mem.pattern.project.workflow.md": "seed default",
      "mem.concept.spec-driver.delta.md": "managed v2",
    })
    dest.mkdir()
    (dest / "mem.concept.spec-driver.delta.md").write_text("managed v1")
    (dest / "mem.concept.spec-driver.old.md").write_text("to prune")

    _install_memories(src, dest, dry_run=True, auto_yes=True)

    captured = capsys.readouterr()
    assert "[DRY RUN]" in captured.out
    assert "Seed memories" in captured.out
    assert "Managed memories" in captured.out

  def test_reports_new_managed_and_updated(
    self, tmp_path: Path, capsys,
  ) -> None:
    src = tmp_path / "src" / "memory"
    dest = tmp_path / "dest"
    _make_memory_source(src, {
      "mem.concept.spec-driver.new.md": "brand new",
      "mem.concept.spec-driver.existing.md": "updated",
    })
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
    self, tmp_path: Path,
  ) -> None:
    """Fresh install creates memory directory with managed + seed files."""
    initialize_workspace(tmp_path, auto_yes=True)

    memory_dir = tmp_path / "memory"
    assert memory_dir.is_dir()

    # Should have at least some managed memories
    managed = [
      f for f in memory_dir.glob("*.md")
      if _classify_memory(f.name) == "spec-driver"
    ]
    assert len(managed) > 0

    # Should have seed stubs
    seeds = [
      f for f in memory_dir.glob("*.md")
      if _classify_memory(f.name) == "seed"
    ]
    assert len(seeds) > 0

  def test_preserves_customized_seed_on_reinstall(
    self, tmp_path: Path,
  ) -> None:
    initialize_workspace(tmp_path, auto_yes=True)

    # Customise a seed memory
    wf = tmp_path / "memory" / "mem.pattern.project.workflow.md"
    assert wf.exists()
    wf.write_text("my custom workflow")

    # Reinstall
    initialize_workspace(tmp_path, auto_yes=True)

    assert wf.read_text() == "my custom workflow"

  def test_dry_run_does_not_create_memories(
    self, tmp_path: Path,
  ) -> None:
    initialize_workspace(tmp_path, dry_run=True)
    memory_dir = tmp_path / "memory"
    # Memory dir might be created (mkdir), but no files copied
    md_files = list(memory_dir.glob("*.md")) if memory_dir.exists() else []
    assert len(md_files) == 0

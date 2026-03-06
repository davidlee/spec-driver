"""Tests for skills sync: allowlist, metadata, rendering, install, prune, symlinks."""

from __future__ import annotations

import warnings as _warnings
from pathlib import Path

from supekku.scripts.lib.skills.sync import (
  AGENTS_MD_REFERENCE,
  BOOT_MD_REFERENCE,
  CANONICAL_SKILLS_DIR,
  SKILL_TARGET_DIRS,
  _ensure_target_symlinks,
  _is_pre_migration_layout,
  _skill_dir_matches,
  ensure_file_reference,
  get_package_skill_names,
  install_skills_to_target,
  parse_allowlist,
  prune_skills_from_target,
  read_skill_metadata,
  render_skills_system,
  sync_skills,
)

AGENTS_MD_REF = AGENTS_MD_REFERENCE
BOOT_MD_REF = BOOT_MD_REFERENCE


# --- helpers ---


def _make_skill(
  skills_dir: Path, name: str, description: str, *, body: str = "# Instructions\n"
) -> None:
  """Helper to create a SKILL.md with frontmatter."""
  skill_dir = skills_dir / name
  skill_dir.mkdir(parents=True, exist_ok=True)
  (skill_dir / "SKILL.md").write_text(
    f"---\nname: {name}\ndescription: {description}\n---\n\n{body}",
    encoding="utf-8",
  )


def _make_source(tmp_path: Path) -> Path:
  """Create a package-like skills source directory."""
  source = tmp_path / "pkg_skills"
  _make_skill(source, "boot", "Mandatory onboarding.")
  _make_skill(source, "consult", "Obstacle handling.")
  _make_skill(source, "notes", "Session notes.")
  return source


def _setup_repo(tmp_path: Path) -> tuple[Path, Path]:
  """Create a minimal repo with skills source and allowlist.

  Returns (repo_root, skills_source_dir).
  Post-migration layout: specify/tech is a symlink (not a real dir).
  """
  root = tmp_path / "repo"
  root.mkdir()
  sd = root / ".spec-driver"
  sd.mkdir()
  (sd / "skills.allowlist").write_text("boot\nconsult\n", encoding="utf-8")

  source = _make_source(tmp_path)
  return root, source


def _make_pre_migration(root: Path) -> None:
  """Pre-migration workspace: no version stamp in workflow.toml."""
  sd = root / ".spec-driver"
  sd.mkdir(exist_ok=True)
  toml = sd / "workflow.toml"
  if not toml.exists():
    toml.write_text('[tool]\nexec = "spec-driver"\n', encoding="utf-8")


def _make_post_migration(root: Path) -> None:
  """Post-migration workspace: version stamp present in workflow.toml."""
  sd = root / ".spec-driver"
  sd.mkdir(exist_ok=True)
  toml = sd / "workflow.toml"
  toml.write_text(
    'spec_driver_installed_version = "0.1.0"\n'
    '[tool]\nexec = "spec-driver"\n',
    encoding="utf-8",
  )


# --- allowlist parsing ---


def test_parse_allowlist_basic(tmp_path: Path) -> None:
  """Reads one skill name per line."""
  allowlist = tmp_path / "skills.allowlist"
  allowlist.write_text("boot\nconsult\nnotes\n", encoding="utf-8")
  assert parse_allowlist(allowlist) == ["boot", "consult", "notes"]


def test_parse_allowlist_comments_and_blanks(tmp_path: Path) -> None:
  """Skips comment lines and blank lines."""
  allowlist = tmp_path / "skills.allowlist"
  allowlist.write_text(
    "# Project skills\nboot\n\n# another comment\nconsult\n  \n",
    encoding="utf-8",
  )
  assert parse_allowlist(allowlist) == ["boot", "consult"]


def test_parse_allowlist_strips_whitespace(tmp_path: Path) -> None:
  """Strips leading/trailing whitespace from skill names."""
  allowlist = tmp_path / "skills.allowlist"
  allowlist.write_text("  boot  \n  consult\n", encoding="utf-8")
  assert parse_allowlist(allowlist) == ["boot", "consult"]


def test_parse_allowlist_missing_file(tmp_path: Path) -> None:
  """Returns empty list when allowlist file does not exist."""
  allowlist = tmp_path / "skills.allowlist"
  assert not parse_allowlist(allowlist)


# --- skill metadata ---


def test_read_skill_metadata(tmp_path: Path) -> None:
  """Reads name and description from SKILL.md frontmatter."""
  _make_skill(tmp_path, "boot", "Mandatory onboarding.")
  meta = read_skill_metadata(tmp_path / "boot" / "SKILL.md")
  assert meta["name"] == "boot"
  assert meta["description"] == "Mandatory onboarding."


def test_read_skill_metadata_missing_file(tmp_path: Path) -> None:
  """Returns None for missing SKILL.md."""
  assert read_skill_metadata(tmp_path / "nope" / "SKILL.md") is None


def test_read_skill_metadata_no_frontmatter(tmp_path: Path) -> None:
  """Returns None when SKILL.md has no YAML frontmatter."""
  skill_dir = tmp_path / "broken"
  skill_dir.mkdir()
  (skill_dir / "SKILL.md").write_text("# Just markdown\n", encoding="utf-8")
  assert read_skill_metadata(skill_dir / "SKILL.md") is None


def test_read_skill_metadata_unquoted_colon_in_value(tmp_path: Path) -> None:
  """Handles description values containing colons (invalid strict YAML)."""
  skill_dir = tmp_path / "preflight"
  skill_dir.mkdir(parents=True)
  (skill_dir / "SKILL.md").write_text(
    "---\n"
    "name: preflight\n"
    "description: Before starting something new: understand task, intent, and context\n"
    "---\n\n# Body\n",
    encoding="utf-8",
  )
  meta = read_skill_metadata(skill_dir / "SKILL.md")
  assert meta is not None
  assert meta["name"] == "preflight"
  assert "understand task, intent, and context" in meta["description"]


def test_read_skill_metadata_multiline_literal(tmp_path: Path) -> None:
  """Handles YAML literal block (|) multiline descriptions."""
  skill_dir = tmp_path / "recall"
  skill_dir.mkdir(parents=True)
  (skill_dir / "SKILL.md").write_text(
    "---\n"
    "name: recall\n"
    "description: |\n"
    "  First line of description.\n"
    "  Second line continues here.\n"
    "---\n\n# Body\n",
    encoding="utf-8",
  )
  meta = read_skill_metadata(skill_dir / "SKILL.md")
  assert meta is not None
  assert meta["name"] == "recall"
  assert meta["description"] == "First line of description. Second line continues here."


def test_read_skill_metadata_multiline_folded(tmp_path: Path) -> None:
  """Handles YAML folded block (>) multiline descriptions."""
  skill_dir = tmp_path / "fold"
  skill_dir.mkdir(parents=True)
  (skill_dir / "SKILL.md").write_text(
    "---\n"
    "name: fold\n"
    "description: >\n"
    "  Folded line one.\n"
    "  Folded line two.\n"
    "---\n\n# Body\n",
    encoding="utf-8",
  )
  meta = read_skill_metadata(skill_dir / "SKILL.md")
  assert meta is not None
  assert meta["description"] == "Folded line one. Folded line two."


# --- rendering ---


def test_render_skills_system_basic() -> None:
  """Renders a complete skills_system XML block."""
  skills = [
    {"name": "boot", "description": "Mandatory onboarding."},
    {"name": "consult", "description": "Obstacle handling."},
  ]
  output = render_skills_system(skills)
  assert "<skills_system" in output
  assert "<name>boot</name>" in output
  assert "<description>Mandatory onboarding.</description>" in output
  assert "<location>project</location>" in output
  assert "<name>consult</name>" in output


def test_render_skills_system_empty() -> None:
  """Renders valid block even with no skills."""
  output = render_skills_system([])
  assert "<skills_system" in output
  assert "<available_skills>" in output
  assert "</available_skills>" in output


def test_render_skills_system_is_deterministic() -> None:
  """Same input produces identical output."""
  skills = [
    {"name": "a", "description": "Alpha."},
    {"name": "b", "description": "Beta."},
  ]
  assert render_skills_system(skills) == render_skills_system(skills)


# --- ensure @-reference in root files ---


def test_ensure_file_reference_creates_file(tmp_path: Path) -> None:
  """Creates file with @-reference when it does not exist."""
  target = tmp_path / "AGENTS.md"
  ensure_file_reference(target, AGENTS_MD_REF)
  content = target.read_text(encoding="utf-8")
  assert AGENTS_MD_REF in content


def test_ensure_file_reference_prepends(tmp_path: Path) -> None:
  """Prepends @-reference before existing content."""
  target = tmp_path / "AGENTS.md"
  target.write_text("# My Project Agents\n\nContent.\n", encoding="utf-8")
  ensure_file_reference(target, AGENTS_MD_REF)
  content = target.read_text(encoding="utf-8")
  lines = content.splitlines()
  assert lines[0] == AGENTS_MD_REF
  assert "Content." in content


def test_ensure_file_reference_idempotent(tmp_path: Path) -> None:
  """Does not duplicate @-reference on repeated calls."""
  target = tmp_path / "AGENTS.md"
  target.write_text(f"# Agents\n\n{AGENTS_MD_REF}\n", encoding="utf-8")
  ensure_file_reference(target, AGENTS_MD_REF)
  content = target.read_text(encoding="utf-8")
  assert content.count(AGENTS_MD_REF) == 1


# --- get_package_skill_names ---


def test_get_package_skill_names_valid(tmp_path: Path) -> None:
  """Returns names of dirs containing non-empty SKILL.md."""
  source = _make_source(tmp_path)
  names = get_package_skill_names(source)
  assert names == {"boot", "consult", "notes"}


def test_get_package_skill_names_empty_dir(tmp_path: Path) -> None:
  """Returns empty set for non-existent directory."""
  assert get_package_skill_names(tmp_path / "nope") == set()


def test_get_package_skill_names_ignores_empty_skill_md(tmp_path: Path) -> None:
  """Ignores dirs where SKILL.md is empty (0 bytes)."""
  source = tmp_path / "skills"
  _make_skill(source, "good", "Valid skill.")
  empty_dir = source / "doctrine"
  empty_dir.mkdir(parents=True)
  (empty_dir / "SKILL.md").write_text("", encoding="utf-8")
  names = get_package_skill_names(source)
  assert names == {"good"}


def test_get_package_skill_names_ignores_non_dirs(tmp_path: Path) -> None:
  """Ignores regular files at top level of source dir."""
  source = tmp_path / "skills"
  source.mkdir()
  _make_skill(source, "boot", "Valid.")
  (source / "README.md").write_text("not a skill", encoding="utf-8")
  names = get_package_skill_names(source)
  assert names == {"boot"}


# --- _skill_dir_matches ---


def test_skill_dir_matches_identical(tmp_path: Path) -> None:
  """Returns True when SKILL.md content matches."""
  src = tmp_path / "src" / "boot"
  dest = tmp_path / "dest" / "boot"
  _make_skill(tmp_path / "src", "boot", "Same.")
  _make_skill(tmp_path / "dest", "boot", "Same.")
  assert _skill_dir_matches(src, dest)


def test_skill_dir_matches_different(tmp_path: Path) -> None:
  """Returns False when SKILL.md content differs."""
  _make_skill(tmp_path / "src", "boot", "Version 1.")
  _make_skill(tmp_path / "dest", "boot", "Version 2.")
  assert not _skill_dir_matches(tmp_path / "src" / "boot", tmp_path / "dest" / "boot")


def test_skill_dir_matches_missing_dest(tmp_path: Path) -> None:
  """Returns False when destination SKILL.md doesn't exist."""
  _make_skill(tmp_path / "src", "boot", "Exists.")
  assert not _skill_dir_matches(tmp_path / "src" / "boot", tmp_path / "dest" / "boot")


# --- install_skills_to_target ---


def test_install_skills_to_target_copies(tmp_path: Path) -> None:
  """Installs allowlisted skills to target dir."""
  source = _make_source(tmp_path)
  target = tmp_path / "target"
  result = install_skills_to_target(source, target, ["boot", "consult"])
  assert set(result["installed"]) == {"boot", "consult"}
  assert (target / "boot" / "SKILL.md").is_file()
  assert (target / "consult" / "SKILL.md").is_file()


def test_install_skills_to_target_idempotent(tmp_path: Path) -> None:
  """Second run reports up_to_date, not installed."""
  source = _make_source(tmp_path)
  target = tmp_path / "target"
  install_skills_to_target(source, target, ["boot"])
  result = install_skills_to_target(source, target, ["boot"])
  assert result["installed"] == []
  assert result["up_to_date"] == ["boot"]


def test_install_skills_to_target_updates_changed(tmp_path: Path) -> None:
  """Re-installs when source SKILL.md has changed."""
  source = _make_source(tmp_path)
  target = tmp_path / "target"
  install_skills_to_target(source, target, ["boot"])

  # Modify source
  (source / "boot" / "SKILL.md").write_text(
    "---\nname: boot\ndescription: Updated.\n---\n\n# New body\n",
    encoding="utf-8",
  )
  result = install_skills_to_target(source, target, ["boot"])
  assert result["installed"] == ["boot"]
  assert "Updated." in (target / "boot" / "SKILL.md").read_text(encoding="utf-8")


def test_install_skills_to_target_creates_dir(tmp_path: Path) -> None:
  """Creates target directory if it doesn't exist."""
  source = _make_source(tmp_path)
  target = tmp_path / "deep" / "nested" / "target"
  assert not target.exists()
  install_skills_to_target(source, target, ["boot"])
  assert (target / "boot" / "SKILL.md").is_file()


def test_install_skills_to_target_skips_missing_source(tmp_path: Path) -> None:
  """Silently skips skills not in source directory."""
  source = _make_source(tmp_path)
  target = tmp_path / "target"
  result = install_skills_to_target(source, target, ["boot", "nonexistent"])
  assert result["installed"] == ["boot"]


# --- prune_skills_from_target ---


def test_prune_removes_delisted_package_skills(tmp_path: Path) -> None:
  """Removes package skills that are no longer allowlisted."""
  source = _make_source(tmp_path)
  target = tmp_path / "target"
  install_skills_to_target(source, target, ["boot", "consult", "notes"])

  # Now allowlist only boot — consult and notes should be pruned
  package_names = get_package_skill_names(source)
  pruned = prune_skills_from_target(target, package_names, ["boot"])
  assert set(pruned) == {"consult", "notes"}
  assert (target / "boot").is_dir()
  assert not (target / "consult").exists()
  assert not (target / "notes").exists()


def test_prune_ignores_user_skills(tmp_path: Path) -> None:
  """Does not remove skills that aren't in the package."""
  source = _make_source(tmp_path)
  target = tmp_path / "target"
  install_skills_to_target(source, target, ["boot"])

  # Add a user-created skill
  user_skill = target / "my-custom-skill"
  user_skill.mkdir()
  (user_skill / "SKILL.md").write_text("---\nname: custom\ndescription: Mine.\n---\n")

  package_names = get_package_skill_names(source)
  pruned = prune_skills_from_target(target, package_names, ["boot"])
  assert pruned == []
  assert user_skill.is_dir()


def test_prune_noop_when_all_allowed(tmp_path: Path) -> None:
  """No pruning when all package skills are in the allowlist."""
  source = _make_source(tmp_path)
  target = tmp_path / "target"
  install_skills_to_target(source, target, ["boot", "consult", "notes"])
  package_names = get_package_skill_names(source)
  pruned = prune_skills_from_target(
    target,
    package_names,
    ["boot", "consult", "notes"],
  )
  assert pruned == []


def test_prune_nonexistent_target_dir(tmp_path: Path) -> None:
  """Returns empty list for non-existent target directory."""
  pruned = prune_skills_from_target(
    tmp_path / "nope",
    {"boot"},
    ["boot"],
  )
  assert pruned == []


# --- _is_pre_migration_layout ---


def test_pre_migration_layout_no_version_stamp(tmp_path: Path) -> None:
  """Returns True when workflow.toml has no version stamp."""
  root = tmp_path / "repo"
  root.mkdir()
  _make_pre_migration(root)
  assert _is_pre_migration_layout(root) is True


def test_pre_migration_layout_with_version_stamp(tmp_path: Path) -> None:
  """Returns False when workflow.toml has version stamp."""
  root = tmp_path / "repo"
  root.mkdir()
  _make_post_migration(root)
  assert _is_pre_migration_layout(root) is False


def test_pre_migration_layout_no_toml(tmp_path: Path) -> None:
  """Returns True when workflow.toml does not exist."""
  root = tmp_path / "repo"
  root.mkdir()
  assert _is_pre_migration_layout(root) is True


# --- _ensure_target_symlinks (per-skill) ---


def _setup_canonical(root: Path, *skill_names: str) -> Path:
  """Create canonical skills dir with named skill subdirs."""
  canonical = root / CANONICAL_SKILLS_DIR
  for name in skill_names:
    _make_skill(canonical, name, f"{name} skill.")
  return canonical


def test_ensure_symlinks_creates_per_skill(tmp_path: Path) -> None:
  """Creates per-skill symlinks when target dir is empty."""
  root = tmp_path / "repo"
  root.mkdir()
  canonical = _setup_canonical(root, "boot", "consult")

  outcomes = _ensure_target_symlinks(
    root, ["claude"], ["boot", "consult"], {"boot", "consult"},
  )
  assert outcomes["claude"]["boot"] == "created"
  assert outcomes["claude"]["consult"] == "created"

  target = root / ".claude" / "skills"
  assert target.is_dir()
  assert not target.is_symlink()
  assert (target / "boot").is_symlink()
  assert (target / "boot").resolve() == (canonical / "boot").resolve()
  assert (target / "boot" / "SKILL.md").is_file()


def test_ensure_symlinks_ok_when_correct(tmp_path: Path) -> None:
  """Reports 'ok' when per-skill symlinks already point correctly."""
  root = tmp_path / "repo"
  root.mkdir()
  _setup_canonical(root, "boot")

  # First call creates
  _ensure_target_symlinks(
    root, ["claude"], ["boot"], {"boot"},
  )
  # Second call checks
  outcomes = _ensure_target_symlinks(
    root, ["claude"], ["boot"], {"boot"},
  )
  assert outcomes["claude"]["boot"] == "ok"


def test_ensure_symlinks_custom_when_wrong_symlink(tmp_path: Path) -> None:
  """Reports 'custom' when per-skill symlink points elsewhere."""
  root = tmp_path / "repo"
  root.mkdir()
  _setup_canonical(root, "boot")
  other = root / "other_skills" / "boot"
  other.mkdir(parents=True)

  target_dir = root / ".claude" / "skills"
  target_dir.mkdir(parents=True)
  (target_dir / "boot").symlink_to(other)

  outcomes = _ensure_target_symlinks(
    root, ["claude"], ["boot"], {"boot"},
  )
  assert outcomes["claude"]["boot"] == "custom"


def test_ensure_symlinks_custom_post_migration_real_dir(tmp_path: Path) -> None:
  """Reports 'custom' for real skill dir in post-migration workspace."""
  root = tmp_path / "repo"
  root.mkdir()
  _setup_canonical(root, "boot")
  _make_post_migration(root)

  # Real skill dir (user customisation)
  _make_skill(root / ".claude" / "skills", "boot", "Custom boot.")

  outcomes = _ensure_target_symlinks(
    root, ["claude"], ["boot"], {"boot"},
  )
  assert outcomes["claude"]["boot"] == "custom"
  # Real dir preserved
  assert (root / ".claude" / "skills" / "boot").is_dir()
  assert not (root / ".claude" / "skills" / "boot").is_symlink()


def test_ensure_symlinks_migrates_pre_migration(tmp_path: Path) -> None:
  """Replaces real skill dirs with symlinks in pre-migration workspace."""
  root = tmp_path / "repo"
  root.mkdir()
  canonical = _setup_canonical(root, "boot", "consult")
  _make_pre_migration(root)

  # Simulate old installer: real skill dirs
  target_dir = root / ".claude" / "skills"
  _make_skill(target_dir, "boot", "Mandatory onboarding.")
  _make_skill(target_dir, "consult", "Obstacle handling.")

  outcomes = _ensure_target_symlinks(
    root, ["claude"], ["boot", "consult"], {"boot", "consult"},
  )
  assert outcomes["claude"]["boot"] == "migrated"
  assert outcomes["claude"]["consult"] == "migrated"
  assert (target_dir / "boot").is_symlink()
  assert (target_dir / "boot").resolve() == (canonical / "boot").resolve()


def test_ensure_symlinks_preserves_user_skills(tmp_path: Path) -> None:
  """User-created skills in target dir are untouched."""
  root = tmp_path / "repo"
  root.mkdir()
  _setup_canonical(root, "boot")

  # Pre-existing user skill in target dir
  target_dir = root / ".claude" / "skills"
  _make_skill(target_dir, "my-custom", "User skill.")

  outcomes = _ensure_target_symlinks(
    root, ["claude"], ["boot"], {"boot"},
  )
  assert outcomes["claude"]["boot"] == "created"
  # User skill untouched (not in allowed_names, not processed)
  assert (target_dir / "my-custom").is_dir()
  assert not (target_dir / "my-custom").is_symlink()


def test_ensure_symlinks_idempotent(tmp_path: Path) -> None:
  """Second call returns all 'ok' after initial creation."""
  root = tmp_path / "repo"
  root.mkdir()
  _setup_canonical(root, "boot", "consult")

  _ensure_target_symlinks(
    root, ["claude"], ["boot", "consult"], {"boot", "consult"},
  )
  outcomes = _ensure_target_symlinks(
    root, ["claude"], ["boot", "consult"], {"boot", "consult"},
  )
  assert all(v == "ok" for v in outcomes["claude"].values())


# --- end-to-end sync ---


def test_sync_skills_writes_agents_md(tmp_path: Path) -> None:
  """sync_skills writes .spec-driver/AGENTS.md with allowlisted skills only."""
  root, source = _setup_repo(tmp_path)
  result = sync_skills(root, skills_source_dir=source)

  agents_md = root / ".spec-driver" / "AGENTS.md"
  assert agents_md.exists()
  content = agents_md.read_text(encoding="utf-8")
  assert "<name>boot</name>" in content
  assert "<name>consult</name>" in content
  assert result["written"] == 2


def test_sync_skills_installs_to_canonical(tmp_path: Path) -> None:
  """sync_skills installs skills to .spec-driver/skills/."""
  root, source = _setup_repo(tmp_path)
  result = sync_skills(root, skills_source_dir=source)

  canonical = root / CANONICAL_SKILLS_DIR
  assert (canonical / "boot" / "SKILL.md").is_file()
  assert (canonical / "consult" / "SKILL.md").is_file()
  assert set(result["canonical"]["installed"]) == {"boot", "consult"}


def test_sync_skills_creates_target_symlinks(tmp_path: Path) -> None:
  """sync_skills creates per-skill symlinks in agent target dirs."""
  root, source = _setup_repo(tmp_path)
  result = sync_skills(root, skills_source_dir=source)

  canonical = root / CANONICAL_SKILLS_DIR
  for target_name, target_path in SKILL_TARGET_DIRS.items():
    abs_target = root / target_path
    # Target dir is real, individual skills are symlinks
    assert abs_target.is_dir()
    assert not abs_target.is_symlink()
    for skill in ("boot", "consult"):
      skill_link = abs_target / skill
      assert skill_link.is_symlink(), (
        f"{skill} not a symlink in {target_name}"
      )
      assert skill_link.resolve() == (canonical / skill).resolve()
      assert (skill_link / "SKILL.md").is_file()

  assert result["symlinks"]["claude"]["boot"] == "created"
  assert result["symlinks"]["codex"]["boot"] == "created"


def test_sync_skills_prunes_from_canonical(tmp_path: Path) -> None:
  """sync_skills prunes de-listed skills from canonical dir."""
  root, source = _setup_repo(tmp_path)
  sync_skills(root, skills_source_dir=source)

  # Narrow allowlist to just boot
  sd = root / ".spec-driver"
  (sd / "skills.allowlist").write_text("boot\n", encoding="utf-8")
  result = sync_skills(root, skills_source_dir=source)

  canonical = root / CANONICAL_SKILLS_DIR
  assert (canonical / "boot").is_dir()
  assert not (canonical / "consult").exists()
  assert "consult" in result["canonical"]["pruned"]


def test_sync_skills_idempotent(tmp_path: Path) -> None:
  """Running sync twice produces identical output."""
  root, source = _setup_repo(tmp_path)
  sync_skills(root, skills_source_dir=source)
  first = (root / ".spec-driver" / "AGENTS.md").read_text(encoding="utf-8")
  result = sync_skills(root, skills_source_dir=source)
  second = (root / ".spec-driver" / "AGENTS.md").read_text(encoding="utf-8")
  assert first == second
  assert result["agents_md_changed"] is False

  # Canonical dir should report up_to_date
  assert result["canonical"]["installed"] == []
  assert result["canonical"]["pruned"] == []

  # Per-skill symlinks should report ok
  for skill_outcomes in result["symlinks"].values():
    assert all(v == "ok" for v in skill_outcomes.values())


def test_sync_skills_ensures_root_agents_reference(tmp_path: Path) -> None:
  """sync_skills ensures root AGENTS.md has skills and boot references."""
  root, source = _setup_repo(tmp_path)
  sync_skills(root, skills_source_dir=source)
  content = (root / "AGENTS.md").read_text(encoding="utf-8")
  assert AGENTS_MD_REF in content
  assert BOOT_MD_REF in content


def test_sync_skills_warns_on_missing_skill(tmp_path: Path) -> None:
  """Warns when allowlisted skill is not in source."""
  root, source = _setup_repo(tmp_path)
  sd = root / ".spec-driver"
  (sd / "skills.allowlist").write_text("boot\nmissing_skill\n", encoding="utf-8")

  result = sync_skills(root, skills_source_dir=source)
  assert "missing_skill" in result["warnings"]
  assert result["written"] == 1


def test_sync_skills_no_allowlist(tmp_path: Path) -> None:
  """When allowlist is missing, writes empty skills block."""
  root = tmp_path / "repo"
  root.mkdir()
  (root / ".spec-driver").mkdir()
  source = _make_source(tmp_path)
  result = sync_skills(root, skills_source_dir=source)
  assert result["written"] == 0
  agents_md = root / ".spec-driver" / "AGENTS.md"
  assert agents_md.exists()


# --- CLAUDE.md integration ---


def test_sync_skills_creates_claude_md_by_default(tmp_path: Path) -> None:
  """By default, CLAUDE.md is created with the boot reference."""
  root, source = _setup_repo(tmp_path)
  sync_skills(root, skills_source_dir=source)
  claude_md = root / "CLAUDE.md"
  assert claude_md.exists()
  content = claude_md.read_text(encoding="utf-8")
  assert BOOT_MD_REF in content
  assert AGENTS_MD_REF not in content


def test_sync_skills_writes_claude_md_when_opted_in(tmp_path: Path) -> None:
  """When integration.claude_md is true, CLAUDE.md gets the boot reference."""
  root, source = _setup_repo_with_config(tmp_path, claude_md=True)
  (root / "CLAUDE.md").write_text("# Project\n\nRules.\n", encoding="utf-8")
  sync_skills(root, skills_source_dir=source)
  content = (root / "CLAUDE.md").read_text(encoding="utf-8")
  lines = content.splitlines()
  assert lines[0] == BOOT_MD_REF
  assert "Rules." in content
  assert AGENTS_MD_REF not in content


# --- config gating ---


def _setup_repo_with_config(
  tmp_path: Path,
  *,
  agents_md: bool = True,
  claude_md: bool = True,
) -> tuple[Path, Path]:
  """Create repo with workflow.toml integration config."""
  root, source = _setup_repo(tmp_path)
  toml = (
    f"[integration]\nagents_md = {str(agents_md).lower()}\n"
    f"claude_md = {str(claude_md).lower()}\n"
  )
  (root / ".spec-driver" / "workflow.toml").write_text(
    toml,
    encoding="utf-8",
  )
  return root, source


def test_config_agents_md_false_skips_reference(tmp_path: Path) -> None:
  """When integration.agents_md is false, root AGENTS.md is not touched."""
  root, source = _setup_repo_with_config(tmp_path, agents_md=False)
  sync_skills(root, skills_source_dir=source)
  assert not (root / "AGENTS.md").exists()


def test_config_claude_md_false_skips_reference(tmp_path: Path) -> None:
  """When integration.claude_md is false, root CLAUDE.md is not touched."""
  root, source = _setup_repo_with_config(tmp_path, claude_md=False)
  sync_skills(root, skills_source_dir=source)
  assert not (root / "CLAUDE.md").exists()


def test_config_defaults_enable_both_agents_and_claude_md(tmp_path: Path) -> None:
  """Without config, both AGENTS.md and CLAUDE.md get references."""
  root, source = _setup_repo(tmp_path)
  sync_skills(root, skills_source_dir=source)
  assert (root / "AGENTS.md").exists()
  assert (root / "CLAUDE.md").exists()
  agents = (root / "AGENTS.md").read_text(encoding="utf-8")
  assert AGENTS_MD_REF in agents
  assert BOOT_MD_REF in agents
  claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
  assert BOOT_MD_REF in claude
  assert AGENTS_MD_REF not in claude


# --- config-driven targets ---


def test_sync_skills_respects_target_config(tmp_path: Path) -> None:
  """Only installs to targets listed in workflow.toml [skills] section."""
  root, source = _setup_repo(tmp_path)
  toml = '[skills]\ntargets = ["claude"]\n'
  (root / ".spec-driver" / "workflow.toml").write_text(toml, encoding="utf-8")

  result = sync_skills(root, skills_source_dir=source)
  assert "claude" in result["symlinks"]
  assert "codex" not in result["symlinks"]

  # Claude target has per-skill symlinks
  assert (root / ".claude" / "skills" / "boot").is_symlink()
  assert (root / ".claude" / "skills" / "boot" / "SKILL.md").is_file()
  # Codex target should not exist
  assert not (root / ".agents" / "skills").exists()


def test_sync_skills_unknown_target_warns(tmp_path: Path) -> None:
  """Unknown target name emits a warning and is skipped."""
  root, source = _setup_repo(tmp_path)
  toml = '[skills]\ntargets = ["claude", "vscode"]\n'
  (root / ".spec-driver" / "workflow.toml").write_text(toml, encoding="utf-8")

  with _warnings.catch_warnings(record=True) as caught:
    _warnings.simplefilter("always")
    result = sync_skills(root, skills_source_dir=source)

  assert "claude" in result["symlinks"]
  assert "vscode" not in result["symlinks"]
  assert any("vscode" in str(w.message) for w in caught)

"""Tests for skills sync: allowlist parsing, metadata, rendering, AGENTS.md."""

from __future__ import annotations

from pathlib import Path

from supekku.scripts.lib.skills.sync import (
  AGENTS_MD_REFERENCE,
  ensure_file_reference,
  parse_allowlist,
  read_skill_metadata,
  render_skills_system,
  sync_skills,
)

AGENTS_MD_REF = AGENTS_MD_REFERENCE


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


def _make_skill(skills_dir: Path, name: str, description: str) -> None:
  """Helper to create a SKILL.md with frontmatter."""
  skill_dir = skills_dir / name
  skill_dir.mkdir(parents=True, exist_ok=True)
  (skill_dir / "SKILL.md").write_text(
    f"---\nname: {name}\ndescription: {description}\n---\n\n# Instructions\n",
    encoding="utf-8",
  )


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


# --- end-to-end sync ---


def _setup_repo(tmp_path: Path) -> Path:
  """Create a minimal repo structure for sync tests."""
  root = tmp_path
  sd = root / ".spec-driver"
  sd.mkdir()
  (sd / "skills.allowlist").write_text("boot\nconsult\n", encoding="utf-8")

  skills_dir = root / ".agent" / "skills"
  _make_skill(skills_dir, "boot", "Mandatory onboarding.")
  _make_skill(skills_dir, "consult", "Obstacle handling.")
  _make_skill(skills_dir, "unrelated", "Not in allowlist.")
  return root


def test_sync_skills_writes_agents_md(tmp_path: Path) -> None:
  """sync_skills writes .spec-driver/AGENTS.md with allowlisted skills only."""
  root = _setup_repo(tmp_path)
  result = sync_skills(root)

  agents_md = root / ".spec-driver" / "AGENTS.md"
  assert agents_md.exists()
  content = agents_md.read_text(encoding="utf-8")
  assert "<name>boot</name>" in content
  assert "<name>consult</name>" in content
  assert "<name>unrelated</name>" not in content
  assert result["written"] == 2


def test_sync_skills_idempotent(tmp_path: Path) -> None:
  """Running sync twice produces identical output."""
  root = _setup_repo(tmp_path)
  sync_skills(root)
  first = (root / ".spec-driver" / "AGENTS.md").read_text(encoding="utf-8")
  result = sync_skills(root)
  second = (root / ".spec-driver" / "AGENTS.md").read_text(encoding="utf-8")
  assert first == second
  assert result["changed"] is False


def test_sync_skills_ensures_root_agents_reference(tmp_path: Path) -> None:
  """sync_skills ensures root AGENTS.md has @-reference."""
  root = _setup_repo(tmp_path)
  sync_skills(root)
  content = (root / "AGENTS.md").read_text(encoding="utf-8")
  assert AGENTS_MD_REF in content


def test_sync_skills_warns_on_missing_skill(tmp_path: Path) -> None:
  """Warns when allowlisted skill is not installed."""
  root = tmp_path
  sd = root / ".spec-driver"
  sd.mkdir()
  (sd / "skills.allowlist").write_text("boot\nmissing_skill\n", encoding="utf-8")
  skills_dir = root / ".agent" / "skills"
  _make_skill(skills_dir, "boot", "Onboarding.")

  result = sync_skills(root)
  assert "missing_skill" in result["warnings"]
  assert result["written"] == 1


def test_sync_skills_no_allowlist(tmp_path: Path) -> None:
  """When allowlist is missing, writes empty skills block."""
  root = tmp_path
  (root / ".spec-driver").mkdir()
  result = sync_skills(root)
  assert result["written"] == 0
  agents_md = root / ".spec-driver" / "AGENTS.md"
  assert agents_md.exists()


# --- CLAUDE.md integration ---


def test_sync_skills_ensures_claude_md_reference(tmp_path: Path) -> None:
  """sync_skills ensures root CLAUDE.md has @-reference to AGENTS.md."""
  root = _setup_repo(tmp_path)
  sync_skills(root)
  content = (root / "CLAUDE.md").read_text(encoding="utf-8")
  assert AGENTS_MD_REF in content


def test_sync_skills_prepends_in_existing_claude_md(tmp_path: Path) -> None:
  """@-reference is prepended before existing CLAUDE.md content."""
  root = _setup_repo(tmp_path)
  (root / "CLAUDE.md").write_text("# Project\n\nRules.\n", encoding="utf-8")
  sync_skills(root)
  content = (root / "CLAUDE.md").read_text(encoding="utf-8")
  lines = content.splitlines()
  assert lines[0] == AGENTS_MD_REF
  assert "Rules." in content


# --- config gating ---


def _setup_repo_with_config(
  tmp_path: Path,
  agents_md: bool = True,
  claude_md: bool = True,
) -> Path:
  """Create repo with workflow.toml integration config."""
  root = _setup_repo(tmp_path)
  toml = (
    f"[integration]\nagents_md = {str(agents_md).lower()}\n"
    f"claude_md = {str(claude_md).lower()}\n"
  )
  (root / ".spec-driver" / "workflow.toml").write_text(
    toml,
    encoding="utf-8",
  )
  return root


def test_config_agents_md_false_skips_reference(tmp_path: Path) -> None:
  """When integration.agents_md is false, root AGENTS.md is not touched."""
  root = _setup_repo_with_config(tmp_path, agents_md=False)
  sync_skills(root)
  assert not (root / "AGENTS.md").exists()


def test_config_claude_md_false_skips_reference(tmp_path: Path) -> None:
  """When integration.claude_md is false, root CLAUDE.md is not touched."""
  root = _setup_repo_with_config(tmp_path, claude_md=False)
  sync_skills(root)
  assert not (root / "CLAUDE.md").exists()


def test_config_defaults_enable_both(tmp_path: Path) -> None:
  """Without config, both AGENTS.md and CLAUDE.md get references."""
  root = _setup_repo(tmp_path)
  sync_skills(root)
  assert (root / "AGENTS.md").exists()
  assert (root / "CLAUDE.md").exists()
  agents = (root / "AGENTS.md").read_text(encoding="utf-8")
  claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
  assert AGENTS_MD_REF in agents
  assert AGENTS_MD_REF in claude

"""Allowlist-driven skills sync: install, prune, and expose skills in AGENTS.md.

Reads `.spec-driver/skills.allowlist`, installs allowlisted skills from the
package source (`supekku/skills/`) to `.spec-driver/skills/` (the canonical
workspace copy), then ensures agent target dirs (`.claude/skills/`,
`.agents/skills/`) are dir-level symlinks to the canonical location.

Prunes de-listed skills from the canonical dir only.  Writes a
`<skills_system>` block to `.spec-driver/AGENTS.md`.

Root `AGENTS.md` and `CLAUDE.md` are updated with `@`-references to the
managed file, controlled by `[integration]` in `workflow.toml`.
"""

from __future__ import annotations

import shutil
import sys
import warnings
from pathlib import Path

import yaml

from supekku.scripts.lib.core.config import load_workflow_config
from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR, get_package_skills_dir

# Canonical install location (relative to repo root)
CANONICAL_SKILLS_DIR = Path(SPEC_DRIVER_DIR) / "skills"

# Agent-specific target directories (relative to repo root).
# Post-migration these become dir-level symlinks to CANONICAL_SKILLS_DIR.
SKILL_TARGET_DIRS: dict[str, Path] = {
  "claude": Path(".claude") / "skills",
  "codex": Path(".agents") / "skills",
}

# Known compat children used to detect pre-migration workspaces.
_COMPAT_CHILDREN: dict[str, tuple[str, ...]] = {
  "specify": ("decisions", "policies", "product", "standards", "tech"),
  "change": ("audits", "deltas", "revisions"),
}

ALLOWLIST_FILE = "skills.allowlist"
MANAGED_AGENTS_FILE = "AGENTS.md"
AGENTS_MD_REFERENCE = f"@{SPEC_DRIVER_DIR}/{MANAGED_AGENTS_FILE}"
BOOT_MD_REFERENCE = f"@{SPEC_DRIVER_DIR}/agents/boot.md"

USAGE_BLOCK = """\
<usage>
When users ask you to perform tasks, check if any of the available skills \
below can help complete the task more effectively. Skills provide specialized \
capabilities and domain knowledge.

How to use skills:
- Check available skills in <available_skills> below
- Skills are loaded via slash commands or agent tooling
- Each skill contains detailed instructions for completing specific tasks

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>"""


def parse_allowlist(path: Path) -> list[str]:
  """Parse a skills allowlist file.

  Returns skill names in file order. Skips blank lines and `#` comments.
  Returns an empty list if the file does not exist.
  """
  if not path.is_file():
    return []
  names: list[str] = []
  for line in path.read_text(encoding="utf-8").splitlines():
    stripped = line.strip()
    if stripped and not stripped.startswith("#"):
      names.append(stripped)
  return names


def _extract_frontmatter_lines(text: str) -> list[str] | None:
  """Return the lines between ``---`` frontmatter delimiters, or None."""
  lines = text.splitlines()
  if not lines or lines[0].strip() != "---":
    return None

  for i, line in enumerate(lines[1:], start=1):
    if line.strip() == "---":
      return lines[1:i]
  return None


def _parse_frontmatter_naive(lines: list[str]) -> dict[str, str]:
  """Simple first-colon split parser for single-line ``key: value`` pairs.

  Handles values containing colons (e.g. ``description: foo: bar``)
  but cannot parse multiline block scalars.
  """
  meta: dict[str, str] = {}
  for line in lines:
    if ":" in line:
      key, _, value = line.partition(":")
      key = key.strip()
      value = value.strip().strip('"').strip("'")
      if key and value:
        meta[key] = value
  return meta


def _extract_frontmatter(text: str) -> dict | None:
  """Extract and parse YAML frontmatter from ``---`` delimited text.

  Tries ``yaml.safe_load`` first.  Falls back to a naive ``key: value``
  line parser when the YAML is technically invalid (e.g. unquoted values
  containing ``: ``).
  """
  fm_lines = _extract_frontmatter_lines(text)
  if fm_lines is None:
    return None

  try:
    data = yaml.safe_load("\n".join(fm_lines))
    if isinstance(data, dict):
      return data
  except yaml.YAMLError:
    pass

  # Fallback: naive parser tolerates unquoted colons in values
  naive = _parse_frontmatter_naive(fm_lines)
  return naive or None


def read_skill_metadata(skill_md_path: Path) -> dict[str, str] | None:
  """Read name and description from SKILL.md YAML frontmatter.

  Returns a dict with `name` and `description` keys, or None if the
  file is missing or has no parseable frontmatter.
  """
  if not skill_md_path.is_file():
    return None

  data = _extract_frontmatter(skill_md_path.read_text(encoding="utf-8"))
  if not data:
    return None

  name = data.get("name")
  description = data.get("description")
  if not name or not description:
    return None

  # Normalize multiline strings: collapse to single line
  return {
    "name": str(name).strip(),
    "description": " ".join(str(description).split()),
  }


def render_skills_system(skills: list[dict[str, str]]) -> str:
  """Render a complete `<skills_system>` XML block for AGENTS.md.

  Each skill dict must have `name` and `description` keys.
  All skills are rendered with `<location>project</location>`.
  """
  skill_entries = []
  for skill in skills:
    skill_entries.append(
      f"<skill>\n"
      f"<name>{skill['name']}</name>\n"
      f"<description>{skill['description']}</description>\n"
      f"<location>project</location>\n"
      f"</skill>"
    )

  skills_xml = "\n\n".join(skill_entries)
  if skills_xml:
    available = f"<available_skills>\n\n{skills_xml}\n\n</available_skills>"
  else:
    available = "<available_skills>\n</available_skills>"

  return (
    f'<skills_system priority="1">\n\n'
    f"## Available Skills\n\n"
    f"{USAGE_BLOCK}\n\n"
    f"{available}\n\n"
    f"</skills_system>\n"
  )


def ensure_file_reference(file_path: Path, reference: str) -> None:
  """Ensure a file exists and contains an @-reference line.

  Creates the file if missing. Prepends the reference before existing
  content if not already present. Idempotent.
  """
  if not file_path.exists():
    file_path.write_text(f"{reference}\n", encoding="utf-8")
    return

  content = file_path.read_text(encoding="utf-8")
  if reference in content:
    return

  # Prepend reference before existing content
  file_path.write_text(
    f"{reference}\n\n{content}",
    encoding="utf-8",
  )


# --- Package skill discovery ---


def get_package_skill_names(skills_source_dir: Path) -> set[str]:
  """List valid skill names in the package source directory.

  A valid skill is a subdirectory containing a non-empty SKILL.md.
  """
  if not skills_source_dir.is_dir():
    return set()
  names: set[str] = set()
  for child in skills_source_dir.iterdir():
    if not child.is_dir():
      continue
    skill_md = child / "SKILL.md"
    if skill_md.is_file() and skill_md.stat().st_size > 0:
      names.add(child.name)
  return names


def _skill_dir_matches(src: Path, dest: Path) -> bool:
  """Check whether a destination skill dir matches the source.

  Compares SKILL.md content byte-for-byte. Returns False if
  the destination SKILL.md is missing.
  """
  src_md = src / "SKILL.md"
  dest_md = dest / "SKILL.md"
  if not dest_md.is_file():
    return False
  return src_md.read_bytes() == dest_md.read_bytes()


def install_skills_to_target(
  skills_source_dir: Path,
  target_dir: Path,
  allowed_names: list[str],
) -> dict[str, list[str]]:
  """Copy allowlisted skills from package source to a target directory.

  Idempotent: skips skills whose SKILL.md already matches the source.
  Creates target_dir if it doesn't exist.

  Returns dict with 'installed' and 'up_to_date' lists of skill names.
  """
  target_dir.mkdir(parents=True, exist_ok=True)
  installed: list[str] = []
  up_to_date: list[str] = []

  for name in allowed_names:
    src = skills_source_dir / name
    if not src.is_dir():
      continue
    dest = target_dir / name
    if _skill_dir_matches(src, dest):
      up_to_date.append(name)
      continue
    # Copy entire skill directory
    if dest.exists():
      shutil.rmtree(dest)
    shutil.copytree(src, dest)
    installed.append(name)

  return {"installed": installed, "up_to_date": up_to_date}


def prune_skills_from_target(
  target_dir: Path,
  package_skill_names: set[str],
  allowed_names: list[str],
) -> list[str]:
  """Remove de-listed package skills from a target directory.

  Only prunes skills that exist in the package (by name) but are NOT
  in the allowlist. User-created skills (not in package) are never touched.

  Returns list of pruned skill names.
  """
  if not target_dir.is_dir():
    return []
  allowed_set = set(allowed_names)
  pruned: list[str] = []
  for child in sorted(target_dir.iterdir()):
    if not child.is_dir():
      continue
    name = child.name
    # Only prune if it's a known package skill AND not in the allowlist
    if name in package_skill_names and name not in allowed_set:
      shutil.rmtree(child)
      pruned.append(name)
  return pruned


# --- Target symlinks ---


def _is_pre_migration_layout(repo_root: Path) -> bool:
  """True if workspace has pre-DE-049 layout (real subdirs, not symlinks).

  Checks known compat children of ``specify/`` and ``change/``.  If any
  is a real directory (not a symlink), the workspace predates the
  consolidated layout and skill target dirs contain vanilla copies that
  are safe to replace with symlinks.
  """
  for parent, children in _COMPAT_CHILDREN.items():
    parent_dir = repo_root / parent
    for name in children:
      child = parent_dir / name
      if child.is_dir() and not child.is_symlink():
        return True
  return False


def _ensure_target_symlinks(
  repo_root: Path,
  target_names: list[str],
  package_skill_names: set[str],
) -> dict[str, str]:
  """Ensure agent target dirs are symlinks to the canonical skills dir.

  For each configured target:

  - Already a correct symlink → ``"ok"``
  - Does not exist → create symlink → ``"created"``
  - Real dir in pre-migration workspace → migrate (remove package-managed
    skill dirs, replace with symlink if empty) → ``"migrated"``
    or ``"kept"`` if user content remains
  - Real dir in post-migration workspace → leave alone → ``"custom"``

  Returns a dict mapping target name to outcome.
  """
  canonical = repo_root / CANONICAL_SKILLS_DIR
  pre_migration = _is_pre_migration_layout(repo_root)
  outcomes: dict[str, str] = {}

  for name in target_names:
    rel_path = SKILL_TARGET_DIRS.get(name)
    if rel_path is None:
      continue
    target = repo_root / rel_path

    # Compute relative symlink path from target's parent to canonical dir
    # e.g. .claude/skills → ../.spec-driver/skills
    link_target = Path("..") / CANONICAL_SKILLS_DIR

    if target.is_symlink():
      if target.resolve() == canonical.resolve():
        outcomes[name] = "ok"
      else:
        # Symlink points elsewhere — leave it alone
        outcomes[name] = "custom"
      continue

    if target.is_dir():
      if not pre_migration:
        # Post-migration real dir = intentional customisation
        outcomes[name] = "custom"
        continue

      # Pre-migration: remove package-managed skill dirs, then replace
      for child in sorted(target.iterdir()):
        if child.is_dir() and child.name in package_skill_names:
          shutil.rmtree(child)

      # Replace with symlink only if dir is now empty
      remaining = list(target.iterdir())
      if not remaining:
        target.rmdir()
        target.symlink_to(link_target)
        outcomes[name] = "migrated"
      else:
        outcomes[name] = "kept"
      continue

    # Does not exist — create parent and symlink
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(link_target)
    outcomes[name] = "created"

  return outcomes


# --- Orchestration ---


def _collect_skills(
  repo_root: Path,
  skills_source_dir: Path,
) -> tuple[list[dict[str, str]], list[str]]:
  """Read allowlist and resolve skill metadata from package source.

  Returns (skills, warnings) where warnings lists names of
  allowlisted skills that could not be found or read.
  """
  sd_root = repo_root / SPEC_DRIVER_DIR
  allowed = parse_allowlist(sd_root / ALLOWLIST_FILE)

  skills: list[dict[str, str]] = []
  warn_names: list[str] = []
  for name in allowed:
    meta = read_skill_metadata(skills_source_dir / name / "SKILL.md")
    if meta is None:
      warn_names.append(name)
      print(
        f"Warning: allowlisted skill '{name}' not found",
        file=sys.stderr,
      )
      continue
    skills.append(meta)
  return skills, warn_names


def _validate_target_names(target_names: list[str]) -> list[str]:
  """Filter target names, warning on unknowns. Returns valid names."""
  valid: list[str] = []
  for name in target_names:
    if name in SKILL_TARGET_DIRS:
      valid.append(name)
    else:
      warnings.warn(
        f"Unknown skill target '{name}'; skipping.",
        UserWarning,
        stacklevel=3,
      )
  return valid


def _write_agents_md(
  repo_root: Path,
  skills: list[dict[str, str]],
) -> bool:
  """Write AGENTS.md if content changed. Returns True if file was modified."""
  content = render_skills_system(skills)
  managed = repo_root / SPEC_DRIVER_DIR / MANAGED_AGENTS_FILE

  if managed.is_file() and managed.read_text(encoding="utf-8") == content:
    return False

  managed.parent.mkdir(parents=True, exist_ok=True)
  managed.write_text(content, encoding="utf-8")
  return True


def sync_skills(
  repo_root: Path,
  *,
  skills_source_dir: Path | None = None,
) -> dict:
  """Sync skills from package source to canonical dir and update AGENTS.md.

  Installs allowlisted skills to ``.spec-driver/skills/`` (once), prunes
  de-listed skills (once), then ensures each agent target dir is a
  symlink to the canonical location.  Writes the AGENTS.md skills block.

  Args:
    repo_root: Workspace root path.
    skills_source_dir: Override package skills dir (for testing).

  Returns a summary dict with keys:
    written: number of skills in AGENTS.md
    warnings: list of missing skill names
    agents_md_changed: whether .spec-driver/AGENTS.md was modified
    canonical: install/prune summary for .spec-driver/skills/
    symlinks: per-target symlink outcome
  """
  source = skills_source_dir or get_package_skills_dir()
  config = load_workflow_config(repo_root)
  target_names: list[str] = config.get("skills", {}).get(
    "targets",
    ["claude", "codex"],
  )
  valid_targets = _validate_target_names(target_names)

  allowed = parse_allowlist(repo_root / SPEC_DRIVER_DIR / ALLOWLIST_FILE)
  package_names = get_package_skill_names(source)

  # Install and prune in canonical location only
  canonical_dir = repo_root / CANONICAL_SKILLS_DIR
  install_result = install_skills_to_target(source, canonical_dir, allowed)
  pruned = prune_skills_from_target(canonical_dir, package_names, allowed)

  # Ensure agent targets are symlinks to canonical dir
  symlink_outcomes = _ensure_target_symlinks(
    repo_root,
    valid_targets,
    package_names,
  )

  skills, warn_names = _collect_skills(repo_root, source)
  agents_md_changed = _write_agents_md(repo_root, skills)

  # Insert @-references in root files per config
  integration = config.get("integration", {})
  if integration.get("agents_md", True):
    ensure_file_reference(repo_root / "AGENTS.md", AGENTS_MD_REFERENCE)
    ensure_file_reference(repo_root / "AGENTS.md", BOOT_MD_REFERENCE)
  if integration.get("claude_md", True):
    ensure_file_reference(repo_root / "CLAUDE.md", BOOT_MD_REFERENCE)

  return {
    "written": len(skills),
    "warnings": warn_names,
    "agents_md_changed": agents_md_changed,
    "canonical": {**install_result, "pruned": pruned},
    "symlinks": symlink_outcomes,
  }

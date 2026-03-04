"""Allowlist-driven skills sync: install, prune, and expose skills in AGENTS.md.

Reads `.spec-driver/skills.allowlist`, installs allowlisted skills from the
package source (`supekku/skills/`) to configured agent target dirs
(`.claude/skills/`, `.agents/skills/`), prunes de-listed skills, and writes
a `<skills_system>` block to `.spec-driver/AGENTS.md`.

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

# Agent-specific target directories (relative to repo root)
SKILL_TARGET_DIRS: dict[str, Path] = {
  "claude": Path(".claude") / "skills",
  "codex": Path(".agents") / "skills",
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


def _sync_to_targets(
  repo_root: Path,
  source: Path,
  target_names: list[str],
  allowed: list[str],
  package_names: set[str],
) -> dict[str, dict]:
  """Install and prune skills for each configured target.

  Returns per-target summary dict.
  """
  targets: dict[str, dict] = {}
  for name in target_names:
    rel_path = SKILL_TARGET_DIRS.get(name)
    if rel_path is None:
      warnings.warn(
        f"Unknown skill target '{name}'; skipping.",
        UserWarning,
        stacklevel=3,
      )
      continue
    abs_target = repo_root / rel_path
    result = install_skills_to_target(source, abs_target, allowed)
    pruned = prune_skills_from_target(abs_target, package_names, allowed)
    targets[name] = {**result, "pruned": pruned}
  return targets


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
  """Sync skills from package source to agent targets and update AGENTS.md.

  Installs allowlisted skills to each configured target dir, prunes
  de-listed package skills, and writes the AGENTS.md skills block.

  Args:
    repo_root: Workspace root path.
    skills_source_dir: Override package skills dir (for testing).

  Returns a summary dict with keys:
    written: number of skills in AGENTS.md
    warnings: list of missing skill names
    agents_md_changed: whether .spec-driver/AGENTS.md was modified
    targets: per-target install/prune summary
  """
  source = skills_source_dir or get_package_skills_dir()
  config = load_workflow_config(repo_root)
  target_names: list[str] = config.get("skills", {}).get(
    "targets",
    ["claude", "codex"],
  )

  allowed = parse_allowlist(repo_root / SPEC_DRIVER_DIR / ALLOWLIST_FILE)
  package_names = get_package_skill_names(source)
  targets = _sync_to_targets(
    repo_root,
    source,
    target_names,
    allowed,
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
    "targets": targets,
  }

"""Allowlist-driven skills sync: expose selected OpenSkills in AGENTS.md.

Reads `.spec-driver/skills.allowlist`, reads SKILL.md frontmatter from
`.agent/skills/*/SKILL.md`, and writes a self-contained `<skills_system>`
block to `.spec-driver/AGENTS.md`.

Root `AGENTS.md` and `CLAUDE.md` are updated with `@`-references to the
managed file, controlled by `[integration]` in `workflow.toml`.
"""

from __future__ import annotations

import sys
from pathlib import Path

from supekku.scripts.lib.core.config import load_workflow_config
from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR

SKILLS_CACHE_DIR = Path(".agent") / "skills"
ALLOWLIST_FILE = "skills.allowlist"
MANAGED_AGENTS_FILE = "AGENTS.md"
AGENTS_MD_REFERENCE = f"@{SPEC_DRIVER_DIR}/{MANAGED_AGENTS_FILE}"

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


def read_skill_metadata(skill_md_path: Path) -> dict[str, str] | None:
  """Read name and description from SKILL.md YAML frontmatter.

  Returns a dict with `name` and `description` keys, or None if the
  file is missing or has no parseable frontmatter.
  """
  if not skill_md_path.is_file():
    return None

  text = skill_md_path.read_text(encoding="utf-8")
  lines = text.splitlines()

  if not lines or lines[0].strip() != "---":
    return None

  # Find closing ---
  end = None
  for i, line in enumerate(lines[1:], start=1):
    if line.strip() == "---":
      end = i
      break
  if end is None:
    return None

  # Minimal YAML key: value parsing (no dependency on pyyaml for this)
  meta: dict[str, str] = {}
  for line in lines[1:end]:
    if ":" in line:
      key, _, value = line.partition(":")
      key = key.strip()
      value = value.strip().strip('"').strip("'")
      if key in ("name", "description"):
        meta[key] = value

  if "name" not in meta or "description" not in meta:
    return None
  return meta


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


def _collect_skills(
  repo_root: Path,
) -> tuple[list[dict[str, str]], list[str]]:
  """Read allowlist and resolve skill metadata.

  Returns (skills, warnings) where warnings lists names of
  allowlisted skills that could not be found or read.
  """
  sd_root = repo_root / SPEC_DRIVER_DIR
  allowed = parse_allowlist(sd_root / ALLOWLIST_FILE)
  skills_dir = repo_root / SKILLS_CACHE_DIR

  skills: list[dict[str, str]] = []
  warnings: list[str] = []
  for name in allowed:
    meta = read_skill_metadata(skills_dir / name / "SKILL.md")
    if meta is None:
      warnings.append(name)
      print(
        f"Warning: allowlisted skill '{name}' not found",
        file=sys.stderr,
      )
      continue
    skills.append(meta)
  return skills, warnings


def sync_skills(repo_root: Path) -> dict:
  """Sync allowlisted skills to .spec-driver/AGENTS.md.

  Returns a summary dict with keys:
    written: number of skills written
    warnings: list of warning strings (e.g. missing skills)
    changed: whether the output file was modified
  """
  skills, warnings = _collect_skills(repo_root)
  content = render_skills_system(skills)
  managed = repo_root / SPEC_DRIVER_DIR / MANAGED_AGENTS_FILE

  # Check for changes
  changed = True
  if managed.is_file() and managed.read_text(encoding="utf-8") == content:
    changed = False

  if changed:
    managed.parent.mkdir(parents=True, exist_ok=True)
    managed.write_text(content, encoding="utf-8")

  # Insert @-references in root files per config
  integration = load_workflow_config(repo_root).get(
    "integration",
    {},
  )
  if integration.get("agents_md", True):
    ensure_file_reference(
      repo_root / "AGENTS.md",
      AGENTS_MD_REFERENCE,
    )
  if integration.get("claude_md", True):
    ensure_file_reference(
      repo_root / "CLAUDE.md",
      AGENTS_MD_REFERENCE,
    )

  return {
    "written": len(skills),
    "warnings": warnings,
    "changed": changed,
  }

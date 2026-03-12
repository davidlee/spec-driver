"""Install spec-driver workspace structure and initial files.

This script sets up the necessary directory structure and registry files
for a new spec-driver workspace.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess as _subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from supekku.scripts.lib.core.agent_docs import render_agent_docs
from supekku.scripts.lib.core.config import (
  detect_exec_command,
  generate_default_workflow_toml,
)
from supekku.scripts.lib.core.npm_utils import (
  get_install_instructions,
  get_package_manager_info,
  is_npm_package_available,
)
from supekku.scripts.lib.core.paths import (
  AUDITS_SUBDIR,
  BACKLOG_DIR,
  DECISIONS_SUBDIR,
  DELTAS_SUBDIR,
  IMPROVEMENTS_SUBDIR,
  ISSUES_SUBDIR,
  MEMORY_DIR,
  POLICIES_SUBDIR,
  PROBLEMS_SUBDIR,
  PRODUCT_SPECS_SUBDIR,
  REVISIONS_SUBDIR,
  RISKS_SUBDIR,
  SPEC_DRIVER_DIR,
  STANDARDS_SUBDIR,
  TECH_SPECS_SUBDIR,
  get_backlog_dir,
  get_memory_dir,
)
from supekku.scripts.lib.core.templates import TemplateNotFoundError

# Import after path setup to avoid circular imports
from supekku.scripts.lib.file_ops import (
  FileChanges,
  format_change_summary,
  format_detailed_changes,
  scan_directory_changes,
)


def _classify_memory(filename: str) -> str | None:
  """Classify a memory file by ID namespace.

  Returns:
    'spec-driver' for platform-managed memories (mem.*.spec-driver.*),
    'seed' for project-owned starters (mem.*.project.*),
    or None for unmanaged/non-memory files.
  """
  if not filename.endswith(".md"):
    return None
  stem = filename.removesuffix(".md")
  parts = stem.split(".")
  # Expect at least: mem.<type>.<namespace>.<name>
  if len(parts) < 4 or parts[0] != "mem":
    return None
  # Check namespace segment(s) — join everything after type
  namespace = ".".join(parts[2:])
  if namespace.startswith("spec-driver."):
    return "spec-driver"
  if namespace.startswith("project."):
    return "seed"
  return None


def _find_memory_source(package_root: Path) -> Path | None:
  """Find memory source directory with dual discovery.

  Checks package root first (installed wheel), then parent directory
  (development repo root).

  Returns:
    Path to memory source directory, or None if not found.
  """
  pkg_memory = package_root / "memory"
  if pkg_memory.is_dir():
    return pkg_memory
  dev_memory = package_root.parent / "memory"
  if dev_memory.is_dir():
    return dev_memory
  return None


@dataclass
class _MemoryChanges:
  """Collects memory install actions for reporting."""

  seed_created: list[str] = field(default_factory=list)
  seed_skipped: list[str] = field(default_factory=list)
  managed_new: list[str] = field(default_factory=list)
  managed_updated: list[str] = field(default_factory=list)
  pruned: list[str] = field(default_factory=list)


def _install_seed_memories(
  sources: list[Path],
  dest_dir: Path,
  *,
  dry_run: bool,
) -> tuple[list[str], list[str]]:
  """Install seed memories: create if missing, never overwrite.

  Returns:
    (created, skipped) filename lists.
  """
  created, skipped = [], []
  for src in sources:
    dest = dest_dir / src.name
    if dest.exists():
      skipped.append(src.name)
    else:
      created.append(src.name)
      if not dry_run:
        shutil.copy2(src, dest)
  return created, skipped


def _refresh_managed_memories(
  sources: list[Path],
  dest_dir: Path,
  *,
  dry_run: bool,
) -> tuple[list[str], list[str]]:
  """Replace/refresh spec-driver managed memories from source.

  Returns:
    (new, updated) filename lists.
  """
  new, updated = [], []
  for src in sources:
    dest = dest_dir / src.name
    if not dest.exists():
      new.append(src.name)
      if not dry_run:
        shutil.copy2(src, dest)
    elif src.read_bytes() != dest.read_bytes():
      updated.append(src.name)
      if not dry_run:
        shutil.copy2(src, dest)
  return new, updated


def _prune_managed_memories(
  source_names: set[str],
  dest_dir: Path,
  *,
  dry_run: bool,
) -> list[str]:
  """Remove managed memory IDs from dest that are absent in source."""
  pruned = []
  for dest_file in sorted(dest_dir.glob("*.md")):
    if (
      _classify_memory(dest_file.name) == "spec-driver"
      and dest_file.name not in source_names
    ):
      pruned.append(dest_file.name)
      if not dry_run:
        dest_file.unlink()
  return pruned


def _install_memories(
  source_dir: Path,
  dest_dir: Path,
  *,
  dry_run: bool = False,
  auto_yes: bool = False,  # noqa: ARG001  # pylint: disable=unused-argument
) -> None:
  """Install/refresh memory packs from source into workspace.

  Two-bucket semantics:
    - seed (mem.*.project.*): create if missing, never overwrite
    - spec-driver (mem.*.spec-driver.*): replace/refresh from source
    - unmanaged: ignored entirely

  Managed-set pruning removes spec-driver IDs present in dest but
  absent from source.

  Args:
    source_dir: Directory containing package memory files.
    dest_dir: Workspace memory directory.
    dry_run: If True, report without modifying files.
    auto_yes: Reserved for future prompt-per-category support.
  """
  dest_dir.mkdir(parents=True, exist_ok=True)

  # Classify source files
  seed_sources: list[Path] = []
  managed_sources: list[Path] = []
  for f in sorted(source_dir.glob("*.md")):
    bucket = _classify_memory(f.name)
    if bucket == "seed":
      seed_sources.append(f)
    elif bucket == "spec-driver":
      managed_sources.append(f)

  changes = _MemoryChanges()
  changes.seed_created, changes.seed_skipped = _install_seed_memories(
    seed_sources, dest_dir, dry_run=dry_run
  )
  changes.managed_new, changes.managed_updated = _refresh_managed_memories(
    managed_sources, dest_dir, dry_run=dry_run
  )
  changes.pruned = _prune_managed_memories(
    {f.name for f in managed_sources},
    dest_dir,
    dry_run=dry_run,
  )
  _report_memory_changes(changes, dry_run=dry_run)


def _print_file_list(
  prefix: str,
  label: str,
  files: list[str],
  marker: str,
) -> None:
  """Print a labeled file list with a marker prefix per entry."""
  print(f"\n{prefix}{label}")
  for name in files:
    print(f"  {marker} {name}")


def _report_memory_changes(
  changes: _MemoryChanges,
  *,
  dry_run: bool,
) -> None:
  """Print memory install summary."""
  prefix = "[DRY RUN] " if dry_run else ""

  if changes.seed_created:
    n = len(changes.seed_created)
    _print_file_list(prefix, f"Seed memories: {n} new", changes.seed_created, "+")

  if changes.seed_skipped:
    n = len(changes.seed_skipped)
    _print_file_list(
      prefix,
      f"Seed memories: {n} skipped (left untouched)",
      changes.seed_skipped,
      "=",
    )

  if changes.managed_new or changes.managed_updated:
    parts = []
    if changes.managed_new:
      parts.append(f"{len(changes.managed_new)} new")
    if changes.managed_updated:
      parts.append(f"{len(changes.managed_updated)} updated")
    label = f"Managed memories: {', '.join(parts)}"
    print(f"\n{prefix}{label}")
    for name in changes.managed_new:
      print(f"  + {name}")
    for name in changes.managed_updated:
      print(f"  ~ {name}")

  if changes.pruned:
    n = len(changes.pruned)
    _print_file_list(
      prefix,
      f"Managed memories: {n} removed (absent from package)",
      changes.pruned,
      "-",
    )


def get_package_root() -> Path:
  """Find the root directory of the installed spec-driver package."""
  # The script is in supekku/scripts/, so package root is two levels up
  return Path(__file__).parent.parent


def prompt_for_category(
  category_name: str, changes: FileChanges, dest_dir: Path, auto_yes: bool = False
) -> bool:
  """Prompt user for confirmation to proceed with changes in a category.

  Args:
    category_name: Name of the category (e.g., "Templates", "About docs")
    changes: Scan results for this category.
    dest_dir: Destination directory to show full paths
    auto_yes: If True, automatically approve without prompting

  Returns:
    True if user wants to proceed, False otherwise
  """
  if not changes.has_changes:
    return False

  summary = format_change_summary(changes)
  print(f"\n{category_name}: {summary}")

  if auto_yes:
    print("  Auto-confirming (--yes flag)")
    return True

  # Show detailed changes with full paths
  details = format_detailed_changes(changes, dest_dir)
  if details:
    print(details)

  response = input(f"\nProceed with {category_name.lower()}? [Y/n] ").strip().lower()
  return response in ("", "y", "yes")


def copy_directory_if_changed(
  src: Path,
  dest: Path,
  *,
  pattern: str,
  category_name: str,
  dry_run: bool = False,
  auto_yes: bool = False,
  dry_run_label: str | None = None,
) -> None:
  """Copy directory contents from src to dest if changes detected.

  Args:
    src: Source directory
    dest: Destination directory
    pattern: Glob pattern for files to copy (e.g., "*.md", "**/*")
    category_name: Display name for user prompts
    dry_run: If True, show changes without copying (default: False)
    auto_yes: If True, auto-confirm without prompting (default: False)
    dry_run_label: Optional custom label for dry-run output (defaults to category_name)
  """
  if not src.exists():
    return

  changes = scan_directory_changes(src, dest, pattern)

  if dry_run:
    if changes.has_changes:
      label = dry_run_label or category_name
      print(f"\n[DRY RUN] {label}:")
      print(format_detailed_changes(changes, dest))
  elif prompt_for_category(category_name, changes, dest, auto_yes):
    for rel_path in changes.new_files + changes.existing_files:
      src_file = src / rel_path
      dest_file = dest / rel_path
      dest_file.parent.mkdir(parents=True, exist_ok=True)
      shutil.copy2(src_file, dest_file)


def _render_agent_docs(
  target_root: Path, package_root: Path, *, dry_run: bool = False
) -> None:
  """Render agent guidance templates into .spec-driver/agents/.

  Delegates to ``render_agent_docs`` from ``core.agent_docs``.
  Falls back to static copy if templates are missing from the package
  (backward compat for pre-template installs).
  """
  try:
    render_agent_docs(target_root, package_root, dry_run=dry_run)
  except TemplateNotFoundError:
    agents_dir = target_root / SPEC_DRIVER_DIR / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    copy_directory_if_changed(
      src=package_root / "agents",
      dest=agents_dir,
      pattern="**/*",
      category_name="agent documentation",
      dry_run=dry_run,
      auto_yes=True,
      dry_run_label="agent instruction",
    )


def _collect_claude_sources(
  package_root: Path,
) -> tuple[Path | None, list[Path]]:
  """Collect Claude config sources from the package.

  Returns:
    (settings_path or None, list of hook source paths).
  """
  settings = package_root / "claude.settings.json"
  settings_path = settings if settings.is_file() else None

  hooks_src = package_root / "claude.hooks"
  hook_files = (
    sorted(f for f in hooks_src.iterdir() if f.is_file()) if hooks_src.is_dir() else []
  )

  return settings_path, hook_files


def _install_claude_config(
  package_root: Path, target_root: Path, *, dry_run: bool = False
) -> None:
  """Install .claude/ settings and hooks from package source.

  Copies claude.settings.json and .claude/hooks/* into the target workspace.
  These are installer-owned and overwritten on every install. Hook scripts
  are made executable after copy.
  """
  settings_src, hook_sources = _collect_claude_sources(package_root)

  if settings_src is None and not hook_sources:
    return

  if dry_run:
    print("\n[DRY RUN] Claude config:")
    if settings_src:
      print("  + .claude/settings.json")
    for src in hook_sources:
      print(f"  + .claude/hooks/{src.name}")
    return

  claude_dir = target_root / ".claude"
  claude_dir.mkdir(parents=True, exist_ok=True)

  if settings_src:
    shutil.copy2(settings_src, claude_dir / "settings.json")

  if hook_sources:
    hooks_dest = claude_dir / "hooks"
    hooks_dest.mkdir(parents=True, exist_ok=True)
    for src in hook_sources:
      dest = hooks_dest / src.name
      shutil.copy2(src, dest)
      dest.chmod(dest.stat().st_mode | 0o111)


def _ensure_preboot_symlink(
  target_root: Path,
  *,
  dry_run: bool = False,
) -> None:
  """Create .claude/rules/ symlink to the preboot context file.

  The preboot file lives at ``.agents/spec-driver-boot.md`` and is
  generated by ``spec-driver admin preboot``.  The symlink makes it
  available as an unconditional Claude Code rule (cache-friendly
  prefix).

  Idempotent: skips if symlink already exists with the correct target.
  User can remove the symlink to disable preboot loading.
  """
  from supekku.scripts.lib.core.preboot import (  # noqa: PLC0415
    PREBOOT_OUTPUT_DIR,
    PREBOOT_OUTPUT_FILE,
  )

  agents_dir = target_root / PREBOOT_OUTPUT_DIR
  agents_dir.mkdir(parents=True, exist_ok=True)

  rules_dir = target_root / ".claude" / "rules"
  rules_dir.mkdir(parents=True, exist_ok=True)

  link_path = rules_dir / PREBOOT_OUTPUT_FILE
  link_target = Path("..") / ".." / PREBOOT_OUTPUT_DIR / PREBOOT_OUTPUT_FILE

  if dry_run:
    print("\n[DRY RUN] Preboot symlink:")
    print(f"  + .claude/rules/{PREBOOT_OUTPUT_FILE}")
    print(f"    → {link_target}")
    return

  if link_path.is_symlink():
    # Check if it already points to the right target
    try:
      expected = target_root / PREBOOT_OUTPUT_DIR / PREBOOT_OUTPUT_FILE
      if link_path.resolve() == expected.resolve():
        return
    except OSError:
      pass
    link_path.unlink()

  if link_path.exists():
    # Real file — don't overwrite
    return

  link_path.symlink_to(link_target)


def _install_hooks(
  package_root: Path, target_root: Path, *, dry_run: bool = False
) -> None:
  """Install hook files to .spec-driver/hooks/ with create-if-missing semantics.

  Hook files are user-customizable and seeded on first install only.
  Existing files are never overwritten.
  """
  hooks_src = package_root / "templates" / "hooks"
  if not hooks_src.is_dir():
    return

  hooks_dest = target_root / SPEC_DRIVER_DIR / "hooks"
  hooks_dest.mkdir(parents=True, exist_ok=True)

  for src_file in sorted(hooks_src.iterdir()):
    if not src_file.is_file():
      continue
    dest_file = hooks_dest / src_file.name
    if dest_file.exists():
      continue
    if dry_run:
      print("\n[DRY RUN] hook file:")
      print(f"  + ./{SPEC_DRIVER_DIR}/hooks/{src_file.name}")
    else:
      shutil.copy2(src_file, dest_file)


_VERSION_KEY = "spec_driver_installed_version"
_VERSION_RE = re.compile(rf'^{_VERSION_KEY}\s*=\s*".*"', re.MULTILINE)


def _get_package_version() -> str:
  """Get the installed spec-driver package version.

  Thin wrapper around :func:`supekku.scripts.lib.core.version.get_package_version`
  kept for internal backward compatibility.
  """
  from supekku.scripts.lib.core.version import get_package_version  # noqa: PLC0415

  return get_package_version()


def _stamp_installed_version(
  workflow_toml: Path,
  *,
  dry_run: bool = False,
) -> None:
  """Write or update ``spec_driver_installed_version`` in workflow.toml.

  Preserves existing content and comments.  Replaces the line if present,
  otherwise prepends it.
  """
  pkg_version = _get_package_version()
  version_line = f'{_VERSION_KEY} = "{pkg_version}"'

  if dry_run:
    print(f"\n[DRY RUN] workflow.toml: {version_line}")
    return

  if not workflow_toml.exists():
    return  # Will be created by the caller

  content = workflow_toml.read_text(encoding="utf-8")
  if _VERSION_RE.search(content):
    updated = _VERSION_RE.sub(version_line, content)
  else:
    updated = f"{version_line}\n{content}"

  if updated != content:
    workflow_toml.write_text(updated, encoding="utf-8")


def initialize_workspace(
  target_root: Path, dry_run: bool = False, auto_yes: bool = False
) -> None:  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
  """Initialize spec-driver workspace structure and files.

  Args:
    target_root: Root directory where workspace should be initialized
    dry_run: If True, show what would be done without making changes
    auto_yes: If True, automatically confirm all prompts

  """
  target_root = target_root.resolve()

  if not target_root.exists():
    sys.exit(1)

  # Detect legacy workspace (installed before DE-049 consolidation)
  _legacy_warning: str | None = None
  workflow_toml = target_root / SPEC_DRIVER_DIR / "workflow.toml"
  if workflow_toml.exists():
    content = workflow_toml.read_text(encoding="utf-8")
    if _VERSION_KEY not in content:
      script = get_package_root() / "scripts" / "migrate_to_consolidated_layout.sh"
      _legacy_warning = (
        "\033[1;31m"
        "⚠  Legacy workspace detected"
        " (no version stamp in workflow.toml).\n"
        "   Content may still live under"
        " specify/, change/, backlog/, memory/.\n"
        "   To migrate, run:\033[0m\n"
        f"     bash {script} --dry-run\n"
      )
      print(f"\n{_legacy_warning}")

  # Create directory structure — flat layout under .spec-driver/ (DE-049)
  sd = SPEC_DRIVER_DIR
  directories = [
    # Content directories (direct children of .spec-driver/)
    f"{sd}/{AUDITS_SUBDIR}",
    f"{sd}/{DELTAS_SUBDIR}",
    f"{sd}/{REVISIONS_SUBDIR}",
    f"{sd}/{DECISIONS_SUBDIR}",
    f"{sd}/{POLICIES_SUBDIR}",
    f"{sd}/{PRODUCT_SPECS_SUBDIR}",
    f"{sd}/{STANDARDS_SUBDIR}",
    f"{sd}/{TECH_SPECS_SUBDIR}",
    f"{sd}/{BACKLOG_DIR}/{IMPROVEMENTS_SUBDIR}",
    f"{sd}/{BACKLOG_DIR}/{ISSUES_SUBDIR}",
    f"{sd}/{BACKLOG_DIR}/{PROBLEMS_SUBDIR}",
    f"{sd}/{BACKLOG_DIR}/{RISKS_SUBDIR}",
    f"{sd}/{MEMORY_DIR}",
    # Internal directories
    f"{sd}/registry",
    f"{sd}/templates",
    f"{sd}/about",
    f"{sd}/agents",
    f"{sd}/hooks",
  ]

  for dir_path in directories:
    full_path = target_root / dir_path
    full_path.mkdir(parents=True, exist_ok=True)

  # Create empty backlog/backlog.md file
  backlog_file = get_backlog_dir(target_root) / "backlog.md"
  if not backlog_file.exists():
    backlog_file.write_text(
      "# Backlog\n\n"
      "Track improvements, issues, problems, and risks here.\n\n"
      "## Structure\n\n"
      "- `improvements/` - Enhancement ideas and feature requests\n"
      "- `issues/` - Known issues and bugs\n"
      "- `problems/` - Current problems requiring attention\n"
      "- `risks/` - Identified risks and mitigation strategies\n",
      encoding="utf-8",
    )

  # Initialize empty registry files
  registry_dir = target_root / SPEC_DRIVER_DIR / "registry"
  registries = {
    "deltas.yaml": {"deltas": {}},
    "revisions.yaml": {"revisions": {}},
    "audits.yaml": {"audits": {}},
    "decisions.yaml": {"decisions": {}},
    "requirements.yaml": {"requirements": {}},
  }

  for registry_file, initial_content in registries.items():
    registry_path = registry_dir / registry_file
    if not registry_path.exists():
      registry_path.write_text(
        yaml.safe_dump(initial_content, sort_keys=False),
        encoding="utf-8",
      )
    else:
      pass

  # Create workflow.toml with detected exec if it doesn't exist
  workflow_toml = target_root / SPEC_DRIVER_DIR / "workflow.toml"
  if not workflow_toml.exists():
    exec_cmd = detect_exec_command(target_root)
    if dry_run:
      print(f'\n[DRY RUN] workflow.toml: exec = "{exec_cmd}"')
    else:
      workflow_toml.write_text(
        generate_default_workflow_toml(exec_cmd),
        encoding="utf-8",
      )

  # Stamp installed version (every install, not just first)
  _stamp_installed_version(workflow_toml, dry_run=dry_run)

  # Copy templates from package to target
  package_root = get_package_root()
  copy_directory_if_changed(
    src=package_root / "templates",
    dest=target_root / SPEC_DRIVER_DIR / "templates",
    pattern="*.md",
    category_name="Templates",
    dry_run=dry_run,
    auto_yes=auto_yes,
  )

  # Copy about files from package to target
  copy_directory_if_changed(
    src=package_root / "about",
    dest=target_root / SPEC_DRIVER_DIR / "about",
    pattern="**/*",
    category_name="About documentation",
    dry_run=dry_run,
    auto_yes=auto_yes,
  )

  # Install hook files (create-if-missing, never overwrite)
  _install_hooks(package_root, target_root, dry_run=dry_run)

  # Install .claude/ settings and hooks (installer-owned, overwrite)
  _install_claude_config(package_root, target_root, dry_run=dry_run)

  # Create preboot symlink (.claude/rules/ → .agents/)
  _ensure_preboot_symlink(target_root, dry_run=dry_run)

  # Render agent guidance from templates (config-tailored)
  _render_agent_docs(target_root, package_root, dry_run=dry_run)

  # Install/refresh memory packs
  memory_source = _find_memory_source(package_root)
  if memory_source is not None:
    _install_memories(
      memory_source,
      get_memory_dir(target_root),
      dry_run=dry_run,
      auto_yes=auto_yes,
    )

  # Bootstrap skills allowlist if missing, then install to targets
  if not dry_run:
    from supekku.scripts.lib.skills.sync import sync_skills  # noqa: PLC0415, I001  # pylint: disable=import-outside-toplevel
    from supekku.scripts.lib.core.paths import get_package_skills_dir  # noqa: PLC0415, I001  # pylint: disable=import-outside-toplevel
    from supekku.scripts.lib.skills.sync import get_package_skill_names  # noqa: PLC0415, I001  # pylint: disable=import-outside-toplevel

    allowlist_path = target_root / SPEC_DRIVER_DIR / "skills.allowlist"
    if not allowlist_path.exists():
      names = sorted(get_package_skill_names(get_package_skills_dir()))
      allowlist_path.write_text(
        "# Skills allowlist — one skill name per line.\n"
        "# Remove a line to stop installing that skill.\n"
        + "".join(f"{n}\n" for n in names),
        encoding="utf-8",
      )

    result = sync_skills(target_root)
    _print_skills_summary(result)

  # Ensure .spec-driver/run/ is gitignored (runtime state, never committed)
  _ensure_gitignore_entry(target_root, f"{SPEC_DRIVER_DIR}/run/", dry_run=dry_run)

  # Check optional dependencies (informational only)
  _check_optional_dependencies(target_root, auto_yes=auto_yes)

  # Repeat legacy warning so it isn't buried in output
  if _legacy_warning:
    print(f"\n{_legacy_warning}")


def _print_skills_summary(result: dict) -> None:
  """Print a concise summary of skill sync results during install."""
  canonical = result["canonical"]
  installed = canonical["installed"]
  pruned = canonical["pruned"]

  parts: list[str] = []
  if installed:
    parts.append(f"installed {len(installed)}")
  if pruned:
    parts.append(f"pruned {len(pruned)}")
  if parts:
    print(f"Skills: {', '.join(parts)}")
  else:
    print("Skills: up to date")

  if result["warnings"]:
    for name in result["warnings"]:
      print(f"  Warning: skill '{name}' not found")


def _ensure_gitignore_entry(
  target_root: Path, entry: str, *, dry_run: bool = False
) -> None:
  """Append an entry to .gitignore if not already present. Idempotent."""
  gitignore = target_root / ".gitignore"
  if gitignore.exists():
    content = gitignore.read_text(encoding="utf-8")
    if entry in content:
      return
  if dry_run:
    print(f"[DRY RUN] Would add '{entry}' to .gitignore")
    return
  with open(gitignore, "a", encoding="utf-8") as f:
    # Ensure we start on a new line
    if gitignore.exists():
      existing = gitignore.read_text(encoding="utf-8")
      if existing and not existing.endswith("\n"):
        f.write("\n")
    f.write(f"{entry}\n")


def _check_optional_dependencies(target_root: Path, *, auto_yes: bool = False) -> None:
  """Check for missing optional dependencies and offer to install them.

  Detects TypeScript/JavaScript projects and offers to install
  ts-doc-extract if not available.
  """
  # Detect TypeScript project presence
  has_tsconfig = any(target_root.glob("**/tsconfig.json"))
  if not has_tsconfig:
    has_ts_files = any(target_root.glob("**/*.ts"))
    if not has_ts_files:
      return

  # Check if ts-doc-extract is available
  if is_npm_package_available("ts-doc-extract", target_root):
    return

  pm_info = get_package_manager_info(target_root)

  print(
    "\nTypeScript project detected but ts-doc-extract is not installed.\n"
    "  Contract generation for TypeScript will be skipped during sync."
  )

  local_cmd = [*pm_info.install_local_command, "ts-doc-extract"]
  global_cmd = ["npx", "--yes", "ts-doc-extract", "--help"]

  if auto_yes:
    choice = "l"
  else:
    print(
      f"\n  [l] Install locally: {' '.join(local_cmd)}"
      f"\n  [g] Install via npx (downloads on demand)"
      "\n  [s] Skip"
    )
    choice = input("\n  Install ts-doc-extract? [l/g/s] ").strip().lower()

  if choice == "l":
    print(f"  Running: {' '.join(local_cmd)}")
    _subprocess.run(local_cmd, cwd=target_root, check=False)
  elif choice == "g":
    print("  Verifying npx can fetch ts-doc-extract...")
    _subprocess.run(global_cmd, cwd=target_root, check=False)
  else:
    instructions = get_install_instructions("ts-doc-extract", pm_info)
    print(f"\n  To install later:\n  {instructions}")


def main() -> None:
  """Main entry point for spec-driver-install command."""
  parser = argparse.ArgumentParser(
    description="Initialize spec-driver workspace structure",
  )
  parser.add_argument(
    "target_dir",
    nargs="?",
    default=".",
    help="Target directory to initialize (default: current directory)",
  )
  parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Show what would be done without making changes",
  )
  parser.add_argument(
    "--yes",
    "-y",
    action="store_true",
    help="Automatically confirm all prompts",
  )

  args = parser.parse_args()
  target_path = Path(args.target_dir)

  initialize_workspace(target_path, dry_run=args.dry_run, auto_yes=args.yes)


if __name__ == "__main__":
  main()

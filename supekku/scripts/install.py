"""Install spec-driver workspace structure and initial files.

This script sets up the necessary directory structure and registry files
for a new spec-driver workspace.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from supekku.scripts.lib.core.config import load_workflow_config
from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR
from supekku.scripts.lib.core.templates import TemplateNotFoundError, render_template

# Import after path setup to avoid circular imports
from supekku.scripts.lib.file_ops import (
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
  sources: list[Path], dest_dir: Path, *, dry_run: bool,
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
  sources: list[Path], dest_dir: Path, *, dry_run: bool,
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
  source_names: set[str], dest_dir: Path, *, dry_run: bool,
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
  changes.seed_created, changes.seed_skipped = (
    _install_seed_memories(seed_sources, dest_dir, dry_run=dry_run)
  )
  changes.managed_new, changes.managed_updated = (
    _refresh_managed_memories(managed_sources, dest_dir, dry_run=dry_run)
  )
  changes.pruned = _prune_managed_memories(
    {f.name for f in managed_sources}, dest_dir, dry_run=dry_run,
  )
  _report_memory_changes(changes, dry_run=dry_run)


def _print_file_list(
  prefix: str, label: str, files: list[str], marker: str,
) -> None:
  """Print a labeled file list with a marker prefix per entry."""
  print(f"\n{prefix}{label}")
  for name in files:
    print(f"  {marker} {name}")


def _report_memory_changes(
  changes: _MemoryChanges, *, dry_run: bool,
) -> None:
  """Print memory install summary."""
  prefix = "[DRY RUN] " if dry_run else ""

  if changes.seed_created:
    n = len(changes.seed_created)
    _print_file_list(prefix, f"Seed memories: {n} new", changes.seed_created, "+")

  if changes.seed_skipped:
    n = len(changes.seed_skipped)
    _print_file_list(
      prefix, f"Seed memories: {n} skipped (left untouched)",
      changes.seed_skipped, "=",
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
      prefix, f"Managed memories: {n} removed (absent from package)",
      changes.pruned, "-",
    )


def _discover_agent_templates(package_root: Path) -> list[str]:
  """Discover agent template names from supekku/templates/agents/*.md."""
  agents_tpl_dir = package_root / "templates" / "agents"
  if not agents_tpl_dir.is_dir():
    return []
  return sorted(p.stem for p in agents_tpl_dir.glob("*.md"))


def get_package_root() -> Path:
  """Find the root directory of the installed spec-driver package."""
  # The script is in supekku/scripts/, so package root is two levels up
  return Path(__file__).parent.parent


def prompt_for_category(
  category_name: str, changes, dest_dir: Path, auto_yes: bool = False
) -> bool:
  """Prompt user for confirmation to proceed with changes in a category.

  Args:
    category_name: Name of the category (e.g., "Templates", "About docs")
    changes: FileChanges object with scan results
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

  Loads workflow config, renders each agent template with it, and writes
  the result. Falls back to static copy if templates are missing from
  the package (backward compat for pre-template installs).
  """
  config = load_workflow_config(target_root)
  agents_dir = target_root / SPEC_DRIVER_DIR / "agents"
  agents_dir.mkdir(parents=True, exist_ok=True)

  template_names = _discover_agent_templates(package_root)
  try:
    for name in template_names:
      content = render_template(
        f"agents/{name}.md",
        {"config": config},
        repo_root=target_root,
      )
      dest = agents_dir / f"{name}.md"
      if dry_run:
        print("\n[DRY RUN] agent instruction:")
        print(f"  + ./{SPEC_DRIVER_DIR}/agents/{name}.md")
      else:
        dest.write_text(content, encoding="utf-8")
  except TemplateNotFoundError:
    # Fallback: static copy for pre-template package installs
    copy_directory_if_changed(
      src=package_root / "agents",
      dest=agents_dir,
      pattern="**/*",
      category_name="agent documentation",
      dry_run=dry_run,
      auto_yes=True,
      dry_run_label="agent instruction",
    )


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

  # Create directory structure
  directories = [
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
    f"{SPEC_DRIVER_DIR}/agents",
  ]

  for dir_path in directories:
    full_path = target_root / dir_path
    full_path.mkdir(parents=True, exist_ok=True)

  # Create empty backlog/backlog.md file
  backlog_file = target_root / "backlog" / "backlog.md"
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

  # Render agent guidance from templates (config-tailored)
  _render_agent_docs(target_root, package_root, dry_run=dry_run)

  # Install/refresh memory packs
  memory_source = _find_memory_source(package_root)
  if memory_source is not None:
    _install_memories(
      memory_source,
      target_root / "memory",
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

    sync_skills(target_root)


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

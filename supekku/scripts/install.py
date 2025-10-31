"""Install spec-driver workspace structure and initial files.

This script sets up the necessary directory structure and registry files
for a new spec-driver workspace.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR

# Import after path setup to avoid circular imports
from supekku.scripts.lib.file_ops import (
  format_change_summary,
  format_detailed_changes,
  scan_directory_changes,
)


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
  template_src = package_root / "templates"
  template_dest = target_root / SPEC_DRIVER_DIR / "templates"

  if template_src.exists():
    # Scan for changes
    template_changes = scan_directory_changes(template_src, template_dest, "*.md")

    if dry_run:
      if template_changes.has_changes:
        print("\n[DRY RUN] Templates:")
        print(format_detailed_changes(template_changes, template_dest))
    elif prompt_for_category("Templates", template_changes, template_dest, auto_yes):
      # Copy new and updated files
      for rel_path in template_changes.new_files + template_changes.existing_files:
        src_file = template_src / rel_path
        dest_file = template_dest / rel_path
        shutil.copy2(src_file, dest_file)

  # Copy about files from package to target
  about_src = package_root / "about"
  about_dest = target_root / SPEC_DRIVER_DIR / "about"

  if about_src.exists():
    # Scan for changes (use ** to include subdirectories)
    about_changes = scan_directory_changes(about_src, about_dest, "**/*")

    if dry_run:
      if about_changes.has_changes:
        print("\n[DRY RUN] About documentation:")
        print(format_detailed_changes(about_changes, about_dest))
    elif prompt_for_category(
      "About documentation", about_changes, about_dest, auto_yes
    ):
      # Copy new and updated files
      for rel_path in about_changes.new_files + about_changes.existing_files:
        src_file = about_src / rel_path
        dest_file = about_dest / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)

  # Copy agent files to .claude/commands/ if .claude exists
  claude_dir = target_root / ".claude"
  if claude_dir.exists() and claude_dir.is_dir():
    commands_dir = claude_dir / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    agents_src = package_root / "agents"
    if agents_src.exists():
      # Scan for changes
      agent_changes = scan_directory_changes(agents_src, commands_dir, "*.md")

      if dry_run:
        if agent_changes.has_changes:
          print("\n[DRY RUN] Agent commands:")
          print(format_detailed_changes(agent_changes, commands_dir))
      elif prompt_for_category("Agent commands", agent_changes, commands_dir, auto_yes):
        # Copy new and updated files
        for rel_path in agent_changes.new_files + agent_changes.existing_files:
          src_file = agents_src / rel_path
          dest_file = commands_dir / rel_path
          shutil.copy2(src_file, dest_file)


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

#!/usr/bin/env python3
"""Complete a delta and transition associated requirements to active status."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

# pylint: disable=wrong-import-position
from supekku.scripts.lib.changes.completion import create_completion_revision
from supekku.scripts.lib.changes.coverage_check import (
  check_coverage_completeness,
  display_coverage_error,
  is_coverage_enforcement_enabled,
)
from supekku.scripts.lib.changes.discovery import find_requirement_sources
from supekku.scripts.lib.changes.updater import (
  RevisionUpdateError,
  update_requirement_lifecycle_status,
)
from supekku.scripts.lib.requirements.lifecycle import STATUS_ACTIVE
from supekku.scripts.lib.workspace import Workspace


def run_spec_sync() -> bool:
  """Run spec sync command and return success status."""
  try:
    result = subprocess.run(
      ["just", "supekku::sync-all"],
      cwd=ROOT,
      capture_output=True,
      text=True,
      check=False,
    )
    return result.returncode == 0
  except Exception:  # pylint: disable=broad-except
    return False


def prompt_yes_no(question: str, default: bool = False) -> bool:
  """Prompt user for yes/no answer."""
  suffix = "[Y/n]" if default else "[y/N]"
  while True:
    response = input(f"{question} {suffix} ").strip().lower()
    if not response:
      return default
    if response in ("y", "yes"):
      return True
    if response in ("n", "no"):
      return False


def validate_delta_status(
  delta_id: str,
  delta,
  force: bool,
  dry_run: bool,
) -> tuple[bool, bool]:
  """Validate delta status is appropriate for completion.

  Returns tuple of (should_continue, already_completed).
  """
  if delta.status == "completed":
    return True, True

  # Accept draft and in-progress as valid completion states
  valid_statuses = {"draft", "in-progress"}
  if delta.status not in valid_statuses and not force and not dry_run:
    # Unexpected status - prompt with explanation
    print(f"Warning: Delta {delta_id} has unexpected status '{delta.status}'")
    print("Expected status: draft or in-progress")
    if not prompt_yes_no("Complete anyway?", default=False):
      return False, False

  return True, False


def collect_requirements_to_update(_delta_id: str, delta, workspace):
  """Collect and validate requirements associated with the delta.

  Returns tuple of (requirements_to_update, error_occurred).
  """
  req_ids = delta.applies_to.get("requirements", [])
  if not req_ids:
    pass

  requirements_registry = workspace.requirements
  requirements_to_update = []

  for req_id in req_ids:
    req = requirements_registry.records.get(req_id)
    if not req:
      continue
    if req.status == "retired":
      return None, True
    requirements_to_update.append((req_id, req))

  return requirements_to_update, False


def display_preview(
  _delta_id: str,
  _delta,
  requirements_to_update,
  dry_run: bool,
) -> None:
  """Display preview of changes to be made."""
  if dry_run:
    pass

  if requirements_to_update:
    for _req_id, _req in requirements_to_update:
      pass


def prompt_spec_sync(skip_sync: bool, dry_run: bool, force: bool) -> bool:
  """Prompt for spec sync and optionally run it.

  Returns True if successful or skipped, False if sync failed.
  """
  if skip_sync or dry_run:
    return True

  if not force:
    sync_now = prompt_yes_no("Sync specs now?", default=False)
    if sync_now and not run_spec_sync():
      return False
  return True


def display_actions(_delta, requirements_to_update, update_requirements: bool) -> None:
  """Display actions that will be performed."""
  if update_requirements and requirements_to_update:
    len(requirements_to_update)
  elif requirements_to_update:
    pass


def display_dry_run_requirements(
  requirements_to_update,
  update_requirements: bool,
) -> None:
  """Display requirements that would be updated in dry-run mode."""
  if not requirements_to_update:
    return

  if update_requirements:
    for _req_id, _req in requirements_to_update:
      pass
  else:
    for _req_id, _req in requirements_to_update:
      pass


def update_delta_frontmatter(delta_path: Path, _delta_id: str) -> bool:
  """Update delta status in frontmatter to 'completed'.

  Returns True if successful, False otherwise.
  """
  if not delta_path.exists():
    return False

  content = delta_path.read_text(encoding="utf-8")
  lines = content.splitlines()

  # Find and update status in frontmatter
  in_frontmatter = False
  updated_lines = []
  status_updated = False

  for line in lines:
    if line.strip() == "---":
      in_frontmatter = not in_frontmatter
      updated_lines.append(line)
      continue

    if in_frontmatter and line.startswith("status:"):
      updated_lines.append("status: completed")
      status_updated = True
    else:
      updated_lines.append(line)

  if not status_updated:
    return False

  # Write updated delta file
  delta_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
  return True


def update_requirements_status(
  requirements_to_update,
  requirements_registry,
  silent=False,
) -> None:
  """Update requirement statuses to active (registry only - ephemeral)."""
  for req_id, _req in requirements_to_update:
    requirements_registry.set_status(req_id, STATUS_ACTIVE)

  requirements_registry.save()
  if requirements_to_update and not silent:
    pass


# pylint: disable=too-many-locals,too-many-branches
# Rationale: Complex workflow with discovery, categorization,
# user interaction, and updates
def update_requirements_in_revision_sources(
  delta_id: str,
  requirement_ids: list[str],
  workspace,
  *,
  dry_run: bool = False,
  force: bool = False,
) -> bool:
  """Update requirement lifecycle status in revision source files (persistent).

  Returns True if successful, False on error.
  """
  # Discover requirement sources
  revision_dirs = [workspace.root / "change" / "revisions"]
  sources = find_requirement_sources(requirement_ids, revision_dirs)

  # Categorize
  tracked = {req_id for req_id in requirement_ids if req_id in sources}
  untracked = set(requirement_ids) - tracked

  # Display plan
  if tracked:
    # Group by file for cleaner display
    files_map: dict[Path, list[str]] = {}
    for req_id in sorted(tracked):
      source = sources[req_id]
      if source.revision_file not in files_map:
        files_map[source.revision_file] = []
      files_map[source.revision_file].append(req_id)

    for _rev_file, reqs in sorted(files_map.items(), key=lambda x: x[0].name):
      for _req_id in reqs:
        pass

  if untracked:
    for _req_id in sorted(untracked):
      pass

  if dry_run:
    return True

  if not force and not prompt_yes_no(
    "Update requirement lifecycle status in revision files?",
    default=True,
  ):
    return False

  # Update tracked requirements in revision files
  if tracked:
    try:
      for req_id in sorted(tracked):
        source = sources[req_id]
        changed = update_requirement_lifecycle_status(
          source.revision_file,
          req_id,
          STATUS_ACTIVE,
          block_index=source.block_index,
          requirement_index=source.requirement_index,
        )
        if changed:
          pass
    except RevisionUpdateError:
      return False

    if tracked:
      pass

  # Create completion revision for untracked requirements
  if untracked:
    try:
      revision_id = create_completion_revision(
        delta_id=delta_id,
        requirements=sorted(untracked),
        workspace=workspace,
      )
      # Display revision info
      revision_slug = delta_id.lower() + "-completion"
      revision_dir = f"{revision_id}-{revision_slug}"
      revision_path = workspace.root / "change" / "revisions" / revision_dir
      print(f"\n✓ Created completion revision: {revision_id}")
      print(f"  {revision_path.relative_to(workspace.root)}")
    except (ValueError, OSError) as e:
      print(f"\nError creating completion revision: {e}", file=sys.stderr)
      return False

  return True


# pylint: disable=too-many-arguments,too-many-positional-arguments
# Rationale: Workflow orchestration requires multiple control flags
def handle_already_completed_delta(
  delta_id: str,
  requirements_to_update,
  workspace,
  dry_run: bool,
  force: bool,
  update_requirements: bool,
) -> int:
  """Handle the case where delta is already completed.

  Ensures requirements are in the correct state (idempotent operation).
  Returns exit code.
  """
  # Check if requirements need fixing
  needs_fixing = [
    (req_id, req)
    for req_id, req in requirements_to_update
    if req.status != STATUS_ACTIVE
  ]

  if not needs_fixing:
    return 0

  for _req_id, _req in needs_fixing:
    pass

  if dry_run:
    return 0

  if not force and not prompt_yes_no(
    "Update requirements to 'active' status?",
    default=True,
  ):
    return 0

  # Use persistent updates if flag is set, otherwise registry-only
  if update_requirements:
    requirement_ids = [req_id for req_id, _ in needs_fixing]
    success = update_requirements_in_revision_sources(
      delta_id=delta_id,
      requirement_ids=requirement_ids,
      workspace=workspace,
      dry_run=dry_run,
      force=True,  # Already confirmed above
    )
    if not success:
      return 1

    # Sync from source files
    workspace.sync_requirements()
  else:
    # Old behavior: registry-only (ephemeral)
    update_requirements_status(needs_fixing, workspace.requirements, silent=True)

  return 0


# pylint: disable=too-many-locals,too-many-return-statements,too-many-branches
# Rationale: Main workflow orchestration with multiple validation/error-handling paths
def complete_delta(
  delta_id: str,
  *,
  dry_run: bool = False,
  force: bool = False,
  skip_sync: bool = False,
  update_requirements: bool = True,
) -> int:
  """Complete a delta and transition requirements to active status.

  Args:
      delta_id: Delta identifier (e.g., DE-004)
      dry_run: Preview changes without applying them
      force: Skip all prompts
      skip_sync: Skip spec sync prompt/check
      update_requirements: If True (default), update requirements to 'active' status
                         in revision source files (persistent). Creates completion
                         revision for untracked requirements. If False, only marks
                         delta as completed without updating requirements.

  Returns:
      Exit code (0 for success, non-zero for errors)

  """
  workspace = Workspace.from_cwd()

  # Load and validate delta
  delta_registry = workspace.delta_registry
  delta_artifacts = delta_registry.collect()

  if delta_id not in delta_artifacts:
    ", ".join(sorted(delta_artifacts.keys()))
    return 1

  delta = delta_artifacts[delta_id]

  # Validate delta status
  should_continue, already_completed = validate_delta_status(
    delta_id,
    delta,
    force,
    dry_run,
  )
  if not should_continue:
    return 1

  # Collect requirements to update
  requirements_to_update, error = collect_requirements_to_update(
    delta_id,
    delta,
    workspace,
  )
  if error:
    return 1

  # Handle already-completed delta (idempotent mode)
  if already_completed:
    return handle_already_completed_delta(
      delta_id,
      requirements_to_update,
      workspace,
      dry_run,
      force,
      update_requirements,
    )

  # Display preview
  display_preview(delta_id, delta, requirements_to_update, dry_run)

  # Prompt for spec sync
  if not prompt_spec_sync(skip_sync, dry_run, force):
    return 1

  # Show actions
  display_actions(delta, requirements_to_update, update_requirements)

  # Handle dry-run
  if dry_run:
    display_dry_run_requirements(requirements_to_update, update_requirements)
    return 0

  # Coverage enforcement check (before confirmation)
  if is_coverage_enforcement_enabled():
    if not force:
      is_complete, missing = check_coverage_completeness(delta_id, workspace)
      if not is_complete:
        display_coverage_error(delta_id, missing, workspace.root)
        return 1
  else:
    # Log that enforcement is disabled
    print("Note: Coverage enforcement is disabled via SPEC_DRIVER_ENFORCE_COVERAGE")

  # Confirm unless force mode
  if not force and not prompt_yes_no("Mark delta as completed?", default=False):
    return 1

  # Update requirement statuses if flag is set
  # NEW: Persist to revision source files instead of just registry
  if update_requirements:
    requirement_ids = [req_id for req_id, _ in requirements_to_update]
    success = update_requirements_in_revision_sources(
      delta_id=delta_id,
      requirement_ids=requirement_ids,
      workspace=workspace,
      dry_run=dry_run,
      force=force,
    )
    if not success:
      return 1

    # Sync requirements from source files to pick up changes
    workspace.sync_requirements()

  # Perform delta updates
  if not update_delta_frontmatter(delta.path, delta_id):
    return 1

  # Sync delta registry to reflect changes
  delta_registry.sync()

  if update_requirements:
    pass
  else:
    pass

  return 0


def build_parser() -> argparse.ArgumentParser:
  """Build argument parser."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("delta_id", help="Delta ID (e.g., DE-004)")
  parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Preview changes without applying them",
  )
  parser.add_argument(
    "--force",
    action="store_true",
    help="Skip all prompts (non-interactive mode)",
  )
  parser.add_argument(
    "--skip-sync",
    action="store_true",
    help="Skip spec sync prompt/check",
  )
  parser.add_argument(
    "--skip-update-requirements",
    action="store_false",
    dest="update_requirements",
    help="Skip updating requirements (only mark delta as completed)",
  )
  return parser


def main(argv: list[str] | None = None) -> int:
  """Main entry point."""
  parser = build_parser()
  args = parser.parse_args(argv)

  return complete_delta(
    args.delta_id,
    dry_run=args.dry_run,
    force=args.force,
    skip_sync=args.skip_sync,
    update_requirements=args.update_requirements,
  )


if __name__ == "__main__":
  raise SystemExit(main())

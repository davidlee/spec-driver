#!/usr/bin/env python3
"""Complete a delta and transition associated requirements to live status."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# pylint: disable=wrong-import-position
from supekku.scripts.lib.completion_revision import create_completion_revision
from supekku.scripts.lib.lifecycle import STATUS_LIVE
from supekku.scripts.lib.revision_discovery import find_requirement_sources
from supekku.scripts.lib.revision_updater import (
    RevisionUpdateError,
    update_requirement_lifecycle_status,
)
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
        if result.returncode == 0:
            print("✓ Spec sync complete")
            return True
        print(f"✗ Spec sync failed:\n{result.stderr}", file=sys.stderr)
        return False
    except Exception as exc:  # pylint: disable=broad-except
        print(f"✗ Spec sync error: {exc}", file=sys.stderr)
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
        print("Please answer 'y' or 'n'")


def validate_delta_status(
    delta_id: str, delta, force: bool, dry_run: bool,
) -> tuple[bool, bool]:
    """Validate delta status is appropriate for completion.

    Returns tuple of (should_continue, already_completed).
    """
    if delta.status == "completed":
        return True, True

    if delta.status != "draft":
        print(
            f"Warning: Delta {delta_id} has status '{delta.status}' (expected 'draft')",
            file=sys.stderr,
        )
        if not force and not dry_run:
            if not prompt_yes_no("Continue anyway?", default=False):
                print("Aborted.", file=sys.stderr)
                return False, False
    return True, False


def collect_requirements_to_update(delta_id: str, delta, workspace):
    """Collect and validate requirements associated with the delta.

    Returns tuple of (requirements_to_update, error_occurred).
    """
    req_ids = delta.applies_to.get("requirements", [])
    if not req_ids:
        print(
            f"Warning: Delta {delta_id} has no associated requirements",
            file=sys.stderr,
        )

    requirements_registry = workspace.requirements
    requirements_to_update = []

    for req_id in req_ids:
        req = requirements_registry.records.get(req_id)
        if not req:
            print(
                f"Warning: Requirement {req_id} not found in registry", file=sys.stderr,
            )
            continue
        if req.status == "retired":
            print(
                f"Error: Requirement {req_id} is retired and cannot be updated",
                file=sys.stderr,
            )
            return None, True
        requirements_to_update.append((req_id, req))

    return requirements_to_update, False


def display_preview(delta_id: str, delta, requirements_to_update, dry_run: bool):
    """Display preview of changes to be made."""
    print()
    if dry_run:
        print("[Preview only - no changes will be made]")
        print()

    print(f"Delta: {delta_id} - {delta.name}")
    print(f"Current status: {delta.status}")
    print()

    if requirements_to_update:
        print("This delta implements:")
        for req_id, req in requirements_to_update:
            print(f"  - {req_id} ({req.status})")
        print()


def prompt_spec_sync(skip_sync: bool, dry_run: bool, force: bool) -> bool:
    """Prompt for spec sync and optionally run it.

    Returns True if successful or skipped, False if sync failed.
    """
    if skip_sync or dry_run:
        return True

    print("Pre-completion checklist:")
    print("  [ ] Have you synced specs to ensure contracts match implementation?")
    print("      Run: just supekku::sync-specs")
    print()

    if not force:
        sync_now = prompt_yes_no("Sync specs now?", default=False)
        if sync_now:
            print("\nSyncing specifications...")
            if not run_spec_sync():
                print("\nError: Spec sync failed. Aborting.", file=sys.stderr)
                return False
            print()
    return True


def display_actions(delta, requirements_to_update, update_requirements: bool):
    """Display actions that will be performed."""
    print("Actions:")
    print(f"  ✓ Update delta status: {delta.status} → completed")
    if update_requirements and requirements_to_update:
        count = len(requirements_to_update)
        print(f"  ✓ Update {count} requirement(s) → live")
    elif requirements_to_update:
        print(f"  ✓ Sync {len(requirements_to_update)} requirement(s) in registry")
    print()


def display_dry_run_requirements(requirements_to_update, update_requirements: bool):
    """Display requirements that would be updated in dry-run mode."""
    if not requirements_to_update:
        return

    if update_requirements:
        print("Requirements to update:")
        for req_id, req in requirements_to_update:
            print(f"  - {req_id}: {req.status} → live")
    else:
        print("Requirements to sync in registry:")
        for req_id, req in requirements_to_update:
            print(f"  - {req_id} (current: {req.status})")


def update_delta_frontmatter(delta_path: Path, delta_id: str) -> bool:
    """Update delta status in frontmatter to 'completed'.

    Returns True if successful, False otherwise.
    """
    if not delta_path.exists():
        print(f"Error: Delta file not found: {delta_path}", file=sys.stderr)
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
        print(
            f"Warning: Could not find 'status:' field in {delta_path}", file=sys.stderr,
        )
        return False

    # Write updated delta file
    delta_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    print(f"✓ Updated delta {delta_id} → completed")
    return True


def update_requirements_status(
    requirements_to_update, requirements_registry, silent=False,
):
    """Update requirement statuses to live (registry only - ephemeral)."""
    for req_id, _req in requirements_to_update:
        requirements_registry.set_status(req_id, STATUS_LIVE)

    requirements_registry.save()
    if requirements_to_update and not silent:
        print(f"✓ Updated {len(requirements_to_update)} requirement(s) → live")


# pylint: disable=too-many-locals,too-many-branches
# Rationale: Complex workflow with discovery, categorization, user interaction, and updates
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

        print("\nRequirements in existing revisions:")
        for rev_file, reqs in sorted(files_map.items(), key=lambda x: x[0].name):
            print(f"  {rev_file.name}:")
            for req_id in reqs:
                current_status = workspace.requirements.records[req_id].status
                print(f"    - {req_id}: {current_status} → live")

    if untracked:
        print(f"\n{len(untracked)} requirement(s) without lifecycle tracking:")
        for req_id in sorted(untracked):
            print(f"  - {req_id}")
        print(f"\nWill create new revision documenting {delta_id} completion")

    print()

    if dry_run:
        print("[Dry-run mode] No changes will be made.")
        return True

    if not force and not prompt_yes_no("Proceed with updates?", default=True):
        print("Aborted.")
        return False

    print()

    # Update tracked requirements in revision files
    if tracked:
        try:
            for req_id in sorted(tracked):
                source = sources[req_id]
                changed = update_requirement_lifecycle_status(
                    source.revision_file,
                    req_id,
                    STATUS_LIVE,
                    block_index=source.block_index,
                    requirement_index=source.requirement_index,
                )
                if changed:
                    print(f"  ✓ Updated {req_id} in {source.revision_file.name}")
        except RevisionUpdateError as exc:
            print(f"\n✗ Error updating revision files: {exc}", file=sys.stderr)
            return False

        if tracked:
            print(f"✓ Updated {len(tracked)} requirement(s) in revision files")

    # Create completion revision for untracked requirements
    if untracked:
        try:
            new_revision_id = create_completion_revision(
                delta_id=delta_id,
                requirements=sorted(untracked),
                workspace=workspace,
            )
            print(f"✓ Created {new_revision_id} for {len(untracked)} requirement(s)")
        except (ValueError, OSError) as exc:
            print(
                f"\n✗ Error creating completion revision: {exc}",
                file=sys.stderr,
            )
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
    print(f"Delta {delta_id} is already completed.")
    print()

    # Check if requirements need fixing
    needs_fixing = [
        (req_id, req)
        for req_id, req in requirements_to_update
        if req.status != STATUS_LIVE
    ]

    if not needs_fixing:
        print("All requirements are already in 'live' status.")
        print("Nothing to do.")
        return 0

    print(f"Found {len(needs_fixing)} requirement(s) not in 'live' status:")
    for req_id, req in needs_fixing:
        print(f"  - {req_id}: {req.status}")
    print()

    if dry_run:
        print("[Dry-run mode] Would update requirements to 'live' status.")
        return 0

    if not force:
        if not prompt_yes_no("Update requirements to 'live' status?", default=True):
            print("No changes made.")
            return 0
        print()

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
            print("\n✗ Failed to update revision sources", file=sys.stderr)
            return 1

        # Sync from source files
        print("\nSyncing requirements from source files...")
        workspace.sync_requirements()
        print("✓ Requirements synchronized from revision sources")
    else:
        # Old behavior: registry-only (ephemeral)
        update_requirements_status(needs_fixing, workspace.requirements, silent=True)
        print(f"✓ Updated {len(needs_fixing)} requirement(s) → live (registry only)")
        print()
        print("Requirements synchronized successfully.")

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
    """Complete a delta and transition requirements to live status.

    Args:
        delta_id: Delta identifier (e.g., DE-004)
        dry_run: Preview changes without applying them
        force: Skip all prompts
        skip_sync: Skip spec sync prompt/check
        update_requirements: If True (default), update requirements to 'live' status
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
        print(f"Error: Delta {delta_id} not found", file=sys.stderr)
        available = ", ".join(sorted(delta_artifacts.keys()))
        print(f"Available deltas: {available}", file=sys.stderr)
        return 1

    delta = delta_artifacts[delta_id]

    # Validate delta status
    should_continue, already_completed = validate_delta_status(
        delta_id, delta, force, dry_run,
    )
    if not should_continue:
        return 1

    # Collect requirements to update
    requirements_to_update, error = collect_requirements_to_update(
        delta_id, delta, workspace,
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

    # Confirm unless force mode
    if not force:
        if not prompt_yes_no("Proceed with completion?", default=False):
            print("Aborted.", file=sys.stderr)
            return 1
        print()

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
            print("\n✗ Failed to update revision sources", file=sys.stderr)
            return 1

        # Sync requirements from source files to pick up changes
        print("\nSyncing requirements from source files...")
        workspace.sync_requirements()
        print("✓ Requirements synchronized from revision sources")
        print()

    # Perform delta updates
    if not update_delta_frontmatter(delta.path, delta_id):
        return 1

    # Sync delta registry to reflect changes
    delta_registry.sync()
    print("✓ Validated workspace consistency")
    print()

    if update_requirements:
        print(f"Delta {delta_id} completed successfully.")
        print("All requirement lifecycle changes persisted to revision files.")
    else:
        print(f"Delta {delta_id} marked as completed (requirements not updated).")

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

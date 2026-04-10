"""Utilities for completing and creating completion revisions.

Documenting delta lifecycle transitions and completing revisions.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from supekku.scripts.lib.changes.audit_check import (
  check_audit_completeness,
  display_audit_error,
  display_audit_warnings,
)
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
from supekku.scripts.lib.core.config import is_strict_mode, load_workflow_config
from supekku.scripts.lib.core.events import record_artifact
from supekku.scripts.lib.core.frontmatter_writer import update_frontmatter_status
from supekku.scripts.lib.core.paths import get_revisions_dir
from supekku.scripts.lib.requirements.lifecycle import STATUS_ACTIVE
from supekku.scripts.lib.workspace import Workspace

from .creation import create_revision
from .lifecycle import STATUS_COMPLETED, STATUS_DRAFT, STATUS_IN_PROGRESS
from .registry import ChangeRegistry

if TYPE_CHECKING:
  pass


def _render_revision_change_block(
  revision_id: str,
  delta_id: str,
  requirements: list[tuple[str, str, str]],  # (req_id, spec_id, summary)
) -> str:
  """Render a revision.change YAML block.

  Documenting requirement lifecycle transitions.

  Args:
      revision_id: Revision ID (e.g., RE-042)
      delta_id: Delta ID that implemented the requirements
      requirements: List of (requirement_id, spec_id, summary) tuples

  Returns:
      Formatted YAML block as a string

  """
  # Group requirements by spec
  specs_data: dict[str, dict] = {}
  requirements_data: list[dict] = []

  for req_id, spec_id, summary in requirements:
    # Track which specs are affected
    if spec_id not in specs_data:
      specs_data[spec_id] = {
        "spec_id": spec_id,
        "action": "updated",
        "summary": f"Requirements implemented by {delta_id}",
      }

    # Build requirement entry
    req_kind = "functional" if ".FR-" in req_id else "non-functional"
    requirements_data.append(
      {
        "requirement_id": req_id,
        "kind": req_kind,
        "action": "modify",
        "summary": summary,
        "destination": {
          "spec": spec_id,
          "requirement_id": req_id,
        },
        "lifecycle": {
          "introduced_by": delta_id,
          "implemented_by": [delta_id],
          "status": STATUS_ACTIVE,
        },
      },
    )

  # Build complete block structure
  block_data = {
    "schema": "supekku.revision.change",
    "version": 1,
    "metadata": {
      "revision": revision_id,
      "prepared_by": "complete-delta",
      "generated_at": datetime.now().isoformat(),
    },
    "specs": sorted(specs_data.values(), key=lambda x: x["spec_id"]),
    "requirements": sorted(requirements_data, key=lambda x: x["requirement_id"]),
  }

  # Format as YAML
  yaml_content = yaml.safe_dump(
    block_data,
    sort_keys=False,
    indent=2,
    default_flow_style=False,
  )

  # Wrap in fenced code block with marker
  lines = [
    "```yaml supekku:revision.change@v1",
    yaml_content.rstrip(),
    "```",
  ]

  return "\n".join(lines)


# pylint: disable=too-many-locals
# Rationale: Revision creation requires gathering data from multiple sources
def create_completion_revision(
  delta_id: str,
  requirements: list[str],
  workspace: Workspace,
  *,
  revision_name: str | None = None,
) -> str:
  """Create a completion revision documenting delta lifecycle transitions.

  This revision documents requirements that were implemented by a delta
  but didn't have prior lifecycle tracking in revision files.

  Args:
      delta_id: Delta ID (e.g., DE-003)
      requirements: List of requirement IDs to document
      workspace: Workspace for accessing registries
      revision_name: Optional custom revision name
          (defaults to "Delta {delta_id} completion")

  Returns:
      New revision ID (e.g., RE-042)

  Raises:
      ValueError: If requirements not found in registry

  """
  # Default name
  if not revision_name:
    revision_name = f"Delta {delta_id} completion"

  # Gather requirement data from workspace
  req_registry = workspace.requirements
  req_data: list[tuple[str, str, str]] = []
  specs_set: set[str] = set()

  for req_id in requirements:
    req = req_registry.records.get(req_id)
    if not req:
      msg = f"Requirement {req_id} not found in registry"
      raise ValueError(msg)

    spec_id = req.primary_spec or (req.specs[0] if req.specs else "")
    if not spec_id:
      msg = f"Requirement {req_id} has no associated spec"
      raise ValueError(msg)

    specs_set.add(spec_id)
    req_data.append((req_id, spec_id, req.title))

  # Create base revision
  result = create_revision(
    name=revision_name,
    source_specs=None,
    destination_specs=sorted(specs_set),
    requirements=requirements,
    repo_root=workspace.root,
  )

  revision_id = result.artifact_id
  revision_file = result.primary_path

  # Update status to completed (not draft)
  content = revision_file.read_text(encoding="utf-8")
  content = content.replace("status: draft", "status: completed")

  # Add relation to delta in frontmatter
  # Insert relation before the closing "---"
  frontmatter_end = content.find("---", 3)
  if frontmatter_end != -1:
    relation_line = f"  - type: documents\n    target: {delta_id}\n"
    # Find relations: [] and replace with populated version
    if "relations: []" in content:
      content = content.replace("relations: []", f"relations:\n{relation_line}")
    elif "relations:\n" in content:
      # Already has relations, append to the list
      insert_pos = content.find("relations:\n") + len("relations:\n")
      content = content[:insert_pos] + relation_line + content[insert_pos:]

  # Append revision change block
  yaml_block = _render_revision_change_block(revision_id, delta_id, req_data)

  # Add block before the Notes section or at the end
  if "## 6. Notes" in content:
    insert_pos = content.find("## 6. Notes")
    content = (
      content[:insert_pos]
      + "\n## 5.1. Revision Change Block\n\n"
      + yaml_block
      + "\n\n"
      + content[insert_pos:]
    )
  else:
    content = content.rstrip() + "\n\n" + yaml_block + "\n"

  # Write updated content
  revision_file.write_text(content, encoding="utf-8")

  return revision_id


def _update_artifact_frontmatter_status(
  path: Path,
  status: str,
) -> bool:
  """Update status and updated date in artifact frontmatter.

  Delegates to the shared primitive in ``core.frontmatter_writer``.
  """
  if not path.exists():
    return False
  return update_frontmatter_status(path, status)


COMPLETABLE_STATUSES = {STATUS_DRAFT, STATUS_IN_PROGRESS}


def complete_revision(
  revision_id: str,
  *,
  force: bool = False,
  repo_root: Path | None = None,
) -> int:
  """Complete a revision by transitioning its status to completed.

  Args:
    revision_id: Revision identifier (e.g., RE-015).
    force: If True, complete even from unexpected statuses.
    repo_root: Optional repository root. Auto-detected if not provided.

  Returns:
    Exit code (0 for success, non-zero for errors).
  """
  registry = ChangeRegistry(root=repo_root, kind="revision")
  artifacts = registry.collect()

  if revision_id not in artifacts:
    print(f"Error: Revision {revision_id} not found")
    return 1

  revision = artifacts[revision_id]

  if revision.status == STATUS_COMPLETED:
    print(f"Revision {revision_id} is already completed")
    return 0

  if revision.status not in COMPLETABLE_STATUSES and not force:
    print(
      f"Error: Revision {revision_id} has status '{revision.status}'; "
      f"expected {', '.join(sorted(COMPLETABLE_STATUSES))}. "
      f"Use --force to override."
    )
    return 1

  if not _update_artifact_frontmatter_status(revision.path, STATUS_COMPLETED):
    print(f"Error: Failed to update frontmatter in {revision.path}")
    return 1

  registry.sync()
  print(f"Revision {revision_id} completed")
  return 0


## ---------------------------------------------------------------------------
## complete_delta support functions (relocated from scripts/complete_delta.py)
## ---------------------------------------------------------------------------

_ROOT = Path(__file__).resolve().parents[4]


def run_spec_sync() -> bool:
  """Run spec sync command and return success status."""
  try:
    result = subprocess.run(
      ["just", "supekku::sync-all"],
      cwd=_ROOT,
      capture_output=True,
      text=True,
      check=False,
    )
    return result.returncode == 0
  except Exception:  # pylint: disable=broad-except
    return False


def _is_interactive_input_available() -> bool:
  """Return True when stdin is interactive and can accept prompts."""
  try:
    return sys.stdin.isatty()
  except Exception:  # pylint: disable=broad-except
    return False


def prompt_yes_no(
  question: str,
  default: bool = False,
  *,
  non_interactive_default: bool | None = None,
) -> bool:
  """Prompt user for yes/no answer, with non-interactive fallback."""
  if non_interactive_default is None:
    non_interactive_default = default

  if not _is_interactive_input_available():
    return non_interactive_default

  suffix = "[Y/n]" if default else "[y/N]"
  while True:
    try:
      response = input(f"{question} {suffix} ").strip().lower()
    except EOFError:
      return non_interactive_default
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

  if delta.status not in COMPLETABLE_STATUSES and not force and not dry_run:
    print(f"Warning: Delta {delta_id} has unexpected status '{delta.status}'")
    print(f"Expected status: {', '.join(sorted(COMPLETABLE_STATUSES))}")
    if not prompt_yes_no(
      "Complete anyway?",
      default=False,
      non_interactive_default=False,
    ):
      return False, False

  return True, False


def collect_requirements_to_update(_delta_id: str, delta, workspace):
  """Collect and validate requirements associated with the delta.

  Returns tuple of (requirements_to_update, error_occurred).
  """
  req_ids = delta.applies_to.get("requirements", [])

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


def prompt_spec_sync(skip_sync: bool, dry_run: bool, force: bool) -> bool:
  """Prompt for spec sync and optionally run it.

  Returns True if successful or skipped, False if sync failed.
  """
  if skip_sync or dry_run:
    return True

  if not force:
    sync_now = prompt_yes_no(
      "Sync specs now?",
      default=False,
      non_interactive_default=False,
    )
    if sync_now and not run_spec_sync():
      return False
  return True


def update_delta_frontmatter(delta_path: Path, _delta_id: str) -> bool:
  """Update delta status in frontmatter to 'completed'.

  Delegates to the shared primitive in ``core.frontmatter_writer``.
  Returns True if successful, False otherwise.
  """
  if not delta_path.exists():
    return False
  return update_frontmatter_status(delta_path, "completed")


def update_requirements_status(
  requirements_to_update,
  requirements_registry,
  silent=False,
) -> None:
  """Update requirement statuses to active (registry only - ephemeral)."""
  for req_id, _req in requirements_to_update:
    requirements_registry.set_status(req_id, STATUS_ACTIVE)

  requirements_registry.save()


# pylint: disable=too-many-locals,too-many-branches
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
  revision_dirs = [get_revisions_dir(workspace.root)]
  sources = find_requirement_sources(requirement_ids, revision_dirs)

  tracked = {req_id for req_id in requirement_ids if req_id in sources}
  untracked = set(requirement_ids) - tracked

  if dry_run:
    return True

  if not force and not prompt_yes_no(
    "Update requirement lifecycle status in revision files?",
    default=True,
    non_interactive_default=True,
  ):
    return False

  if tracked:
    try:
      for req_id in sorted(tracked):
        source = sources[req_id]
        update_requirement_lifecycle_status(
          source.revision_file,
          req_id,
          STATUS_ACTIVE,
          block_index=source.block_index,
          requirement_index=source.requirement_index,
        )
    except RevisionUpdateError as e:
      print(
        f"Error: Failed to update requirements in revision files: {e}",
        file=sys.stderr,
      )
      return False

  if untracked:
    try:
      revision_id = create_completion_revision(
        delta_id=delta_id,
        requirements=sorted(untracked),
        workspace=workspace,
      )
      record_artifact(revision_id)
      revision_slug = delta_id.lower() + "-completion"
      revision_dir = f"{revision_id}-{revision_slug}"
      revision_path = get_revisions_dir(workspace.root) / revision_dir
      print(f"\n✓ Created completion revision: {revision_id}")
      print(f"  {revision_path.relative_to(workspace.root)}")
    except (ValueError, OSError) as e:
      print(f"\nError creating completion revision: {e}", file=sys.stderr)
      return False

  return True


# pylint: disable=too-many-arguments,too-many-positional-arguments
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
  needs_fixing = [
    (req_id, req)
    for req_id, req in requirements_to_update
    if req.status != STATUS_ACTIVE
  ]

  if not needs_fixing:
    return 0

  if dry_run:
    return 0

  if not force and not prompt_yes_no(
    "Update requirements to 'active' status?",
    default=True,
    non_interactive_default=True,
  ):
    return 0

  if update_requirements:
    requirement_ids = [req_id for req_id, _ in needs_fixing]
    success = update_requirements_in_revision_sources(
      delta_id=delta_id,
      requirement_ids=requirement_ids,
      workspace=workspace,
      dry_run=dry_run,
      force=True,
    )
    if not success:
      print(
        f"Error: Failed to fix requirement statuses for {delta_id}",
        file=sys.stderr,
      )
      return 1

    workspace.sync_requirements()
  else:
    update_requirements_status(needs_fixing, workspace.requirements, silent=True)

  return 0


# pylint: disable=too-many-locals,too-many-return-statements,too-many-branches
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

  # Strict-mode enforcement: block bypass flags (DEC-039-01, DEC-039-04)
  config = load_workflow_config(workspace.root)
  if is_strict_mode(config):
    if force:
      print("Error: --force is not permitted in strict mode", file=sys.stderr)
      return 1
    if not update_requirements:
      print(
        "Error: --skip-update-requirements is not permitted in strict mode",
        file=sys.stderr,
      )
      return 1
    if skip_sync:
      print("Error: --skip-sync is not permitted in strict mode", file=sys.stderr)
      return 1

  # Load and validate delta
  delta_registry = workspace.delta_registry
  delta_artifacts = delta_registry.collect()

  if delta_id not in delta_artifacts:
    available = ", ".join(sorted(delta_artifacts.keys()))
    print(
      f"Error: Delta {delta_id} not found. Available: {available}",
      file=sys.stderr,
    )
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
    print(
      f"Error: Cannot complete {delta_id}: retired requirements found",
      file=sys.stderr,
    )
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

  # Prompt for spec sync
  if not prompt_spec_sync(skip_sync, dry_run, force):
    print("Error: Spec sync failed", file=sys.stderr)
    return 1

  # Handle dry-run
  if dry_run:
    return 0

  # Coverage enforcement check (before confirmation)
  if is_coverage_enforcement_enabled():
    if not force:
      is_complete, missing = check_coverage_completeness(delta_id, workspace)
      if not is_complete:
        display_coverage_error(delta_id, missing, workspace.root)
        return 1
  else:
    if is_strict_mode(config):
      print(
        "Error: disabling coverage enforcement via"
        " SPEC_DRIVER_ENFORCE_COVERAGE is not permitted in strict mode",
        file=sys.stderr,
      )
      return 1
    print("Note: Coverage enforcement is disabled via SPEC_DRIVER_ENFORCE_COVERAGE")

  # Audit completeness check (DEC-079-003, DEC-079-011)
  if not force:
    audit_result = check_audit_completeness(delta_id, workspace)
    if not audit_result.is_complete:
      display_audit_error(delta_id, audit_result)
      return 1
    if audit_result.warning_findings or audit_result.collisions:
      display_audit_warnings(audit_result)

  # Confirm unless force mode
  if not force and not prompt_yes_no(
    "Mark delta as completed?",
    default=False,
    non_interactive_default=True,
  ):
    return 1

  # Update requirement statuses if flag is set
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
      print(
        f"Error: Failed to update requirement lifecycle for {delta_id}",
        file=sys.stderr,
      )
      return 1

    workspace.sync_requirements()

  # Perform delta updates
  if not update_delta_frontmatter(delta.path, delta_id):
    print(
      f"Error: Failed to update delta frontmatter for {delta_id}",
      file=sys.stderr,
    )
    return 1

  delta_registry.sync()

  return 0


__all__ = [
  "complete_delta",
  "complete_revision",
  "create_completion_revision",
]

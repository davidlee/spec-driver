"""Utilities for completing and creating completion revisions.

Documenting delta lifecycle transitions and completing revisions.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from supekku.scripts.lib.core.frontmatter_writer import update_frontmatter_status
from supekku.scripts.lib.requirements.lifecycle import STATUS_ACTIVE

from .creation import create_revision
from .lifecycle import STATUS_COMPLETED, STATUS_DRAFT, STATUS_IN_PROGRESS
from .registry import ChangeRegistry

if TYPE_CHECKING:
  from .workspace import Workspace


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


__all__ = ["complete_revision", "create_completion_revision"]

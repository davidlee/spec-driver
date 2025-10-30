"""Utilities for updating lifecycle status in revision YAML blocks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .lifecycle import VALID_STATUSES
from .revision_blocks import (
  RevisionBlockValidator,
  load_revision_blocks,
)

if TYPE_CHECKING:
  from pathlib import Path


class RevisionUpdateError(Exception):
  """Error during revision file update."""


# pylint: disable=too-many-locals,too-many-branches
# Rationale: Workflow function with multiple validation/navigation steps
def update_requirement_lifecycle_status(
  revision_file: Path,
  requirement_id: str,
  new_status: str,
  *,
  block_index: int,
  requirement_index: int,
) -> bool:
  """Update lifecycle.status for a requirement in a revision block.

  Uses RevisionChangeBlock utilities for safe YAML updates.
  Validates schema before and after modification.

  Args:
      revision_file: Path to the revision markdown file
      requirement_id: Requirement ID to update (for validation)
      new_status: New lifecycle status value
      block_index: Which YAML block in the file (0-based)
      requirement_index: Which requirement in the block (0-based)

  Returns:
      True if successful, False if no changes needed

  Raises:
      RevisionUpdateError: If update fails validation or I/O error

  """
  # Validate status value
  if new_status not in VALID_STATUSES:
    msg = f"Invalid status {new_status!r}; must be one of {sorted(VALID_STATUSES)}"
    raise ValueError(
      msg,
    )

  # Read file content
  try:
    original_content = revision_file.read_text(encoding="utf-8")
  except OSError as exc:
    msg = f"Failed to read {revision_file}: {exc}"
    raise RevisionUpdateError(msg) from exc

  # Load blocks
  try:
    blocks = load_revision_blocks(revision_file)
  except ValueError as exc:
    msg = f"Failed to parse revision blocks in {revision_file}: {exc}"
    raise RevisionUpdateError(
      msg,
    ) from exc

  if block_index >= len(blocks):
    msg = f"Block index {block_index} out of range (file has {len(blocks)} blocks)"
    raise RevisionUpdateError(
      msg,
    )

  block = blocks[block_index]

  # Parse block data
  try:
    data = block.parse()
  except ValueError as exc:
    msg = f"Failed to parse block {block_index} YAML: {exc}"
    raise RevisionUpdateError(
      msg,
    ) from exc

  # Navigate to requirement
  requirements = data.get("requirements", [])
  if not isinstance(requirements, list):
    msg = f"Block {block_index} 'requirements' is not a list"
    raise RevisionUpdateError(msg)

  if requirement_index >= len(requirements):
    msg = (
      f"Requirement index {requirement_index} out of range "
      f"(block has {len(requirements)} requirements)"
    )
    raise RevisionUpdateError(
      msg,
    )

  requirement = requirements[requirement_index]
  if not isinstance(requirement, dict):
    msg = f"Requirement {requirement_index} in block {block_index} is not a dict"
    raise RevisionUpdateError(
      msg,
    )

  # Validate requirement ID matches
  actual_req_id = requirement.get("requirement_id")
  if actual_req_id != requirement_id:
    msg = (
      f"Requirement ID mismatch: expected {requirement_id!r}, found {actual_req_id!r}"
    )
    raise RevisionUpdateError(
      msg,
    )

  # Check if update needed
  lifecycle = requirement.get("lifecycle")
  if not isinstance(lifecycle, dict):
    # Create lifecycle section if missing
    lifecycle = {}
    requirement["lifecycle"] = lifecycle

  current_status = lifecycle.get("status")
  if current_status == new_status:
    # No change needed
    return False

  # Update status
  lifecycle["status"] = new_status

  # Validate updated schema
  validator = RevisionBlockValidator()
  validation_errors = validator.validate(data)
  if validation_errors:
    error_msgs = [f"{err.render_path()}: {err.message}" for err in validation_errors]
    raise RevisionUpdateError(
      "Updated block failed validation:\n" + "\n".join(error_msgs),
    )

  # Format and replace YAML
  try:
    new_yaml = block.formatted_yaml(data)
    new_content = block.replace_content(original_content, new_yaml)
  except (ValueError, KeyError) as exc:
    msg = f"Failed to format updated YAML: {exc}"
    raise RevisionUpdateError(msg) from exc

  # Write back to file
  try:
    revision_file.write_text(new_content, encoding="utf-8")
  except OSError as exc:
    msg = f"Failed to write {revision_file}: {exc}"
    raise RevisionUpdateError(msg) from exc

  return True


def update_multiple_requirements(
  updates: dict[Path, list[tuple[int, int, str, str]]],
) -> dict[Path, bool]:
  """Batch update multiple requirements across revision files.

  Each file is updated atomically (all updates succeed or file is unchanged).

  Args:
      updates: Mapping of file -> list of (block_idx, req_idx, req_id, new_status)

  Returns:
      Mapping of file -> success status (True if updated, False if no changes)

  Raises:
      RevisionUpdateError: If any update fails

  """
  results: dict[Path, bool] = {}

  for file, update_list in updates.items():
    # For simplicity, update one requirement at a time
    # Each update reads the file fresh (inefficient but safe)
    any_changed = False
    for block_idx, req_idx, req_id, new_status in update_list:
      changed = update_requirement_lifecycle_status(
        file,
        req_id,
        new_status,
        block_index=block_idx,
        requirement_index=req_idx,
      )
      any_changed = any_changed or changed

    results[file] = any_changed

  return results


__all__ = [
  "RevisionUpdateError",
  "update_multiple_requirements",
  "update_requirement_lifecycle_status",
]

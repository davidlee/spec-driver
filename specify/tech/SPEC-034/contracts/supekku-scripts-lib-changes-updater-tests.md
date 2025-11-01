# supekku.scripts.lib.changes.updater

Utilities for updating lifecycle status in revision YAML blocks.

## Constants

- `__all__`

## Functions

- `update_multiple_requirements(updates) -> dict[Tuple[Path, bool]]`: Batch update multiple requirements across revision files.

Each file is updated atomically (all updates succeed or file is unchanged).

Args:
    updates: Mapping of file -> list of (block_idx, req_idx, req_id, new_status)

Returns:
    Mapping of file -> success status (True if updated, False if no changes)

Raises:
    RevisionUpdateError: If any update fails
- `update_requirement_lifecycle_status(revision_file, requirement_id, new_status) -> bool`: Update lifecycle.status for a requirement in a revision block.

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
    RevisionUpdateError: If update fails validation or I/O error - Rationale: Workflow function with multiple validation/navigation steps

## Classes

### RevisionUpdateError

Error during revision file update.

**Inherits from:** Exception

# supekku.scripts.lib.deletion

Deletion infrastructure for specs, deltas, revisions, and ADRs.

Provides safe deletion with validation, dry-run support, and proper cleanup
of registries, symlinks, and cross-references.

## Constants

- `__all__`

## Classes

### DeletionExecutor

Executes deletion with proper cleanup.

Handles deletion of specs, deltas, revisions, and ADRs with proper
registry updates, symlink cleanup, and cross-reference handling.

#### Methods

- `delete_spec(self, spec_id) -> DeletionPlan`: Delete a spec with full cleanup.

Args:
    spec_id: Spec ID (e.g., "SPEC-001")
    dry_run: If True, only validate and return plan without deleting

Returns:
    DeletionPlan describing what was (or would be) deleted
- `__init__(self, repo_root) -> None`: Initialize executor.

Args:
    repo_root: Repository root directory
- `_rebuild_spec_indices(self) -> None`: Rebuild spec symlink indices after deletion.
- `_remove_from_registry(self, spec_id) -> None`: Remove spec from registry_v2.json.

Args:
    spec_id: Spec ID to remove

### DeletionPlan

Describes what would be deleted without executing.

Attributes:
    artifact_id: ID of the artifact to delete (e.g., "SPEC-001")
    artifact_type: Type of artifact ("spec", "delta", "revision", "adr")
    files_to_delete: List of file paths that would be deleted
    symlinks_to_remove: List of symlink paths that would be removed
    registry_updates: Registry files and entries to remove
    cross_references: Other artifacts that reference this one
    is_safe: Whether deletion is safe (no blocking issues)
    warnings: List of warning messages

#### Methods

- `add_cross_reference(self, from_id, to_id) -> None`: Add a cross-reference.
- `add_file(self, path) -> None`: Add a file to delete.
- `add_registry_update(self, registry_file, entry) -> None`: Add a registry entry to remove.
- `add_symlink(self, path) -> None`: Add a symlink to remove.
- `add_warning(self, message) -> None`: Add a warning message to the plan.

### DeletionValidator

Validates deletion safety and identifies cleanup requirements.

Checks if artifact exists, finds cross-references, detects orphaned
symlinks, and validates that deletion is safe to proceed.

#### Methods

- `validate_spec_deletion(self, spec_id) -> DeletionPlan`: Validate deletion of a spec.

Args:
    spec_id: Spec ID (e.g., "SPEC-001")

Returns:
    DeletionPlan describing what would be deleted
- `__init__(self, repo_root) -> None`: Initialize validator.

Args:
    repo_root: Repository root directory
- `_find_spec_symlinks(self, spec_id) -> list[Path]`: Find all symlinks pointing to a spec directory.

Args:
    spec_id: Spec ID (e.g., "SPEC-001")

Returns:
    List of symlink paths

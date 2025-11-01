# supekku.scripts.lib.deletion.executor

Deletion infrastructure for specs, deltas, revisions, and ADRs.

Provides safe deletion with validation, dry-run support, and proper cleanup
of registries, symlinks, and cross-references.

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
    orphaned_specs: Set of spec IDs known to be orphaned (for context).
                   If provided, cross-references from other orphaned specs
                   will not block deletion.

Returns:
    DeletionPlan describing what would be deleted

### RegistryScanner

Scans YAML registries for cross-references to specs.

Loads and parses requirements, deltas, revisions, and decisions registries
to find which artifacts reference a given spec.

#### Methods

- `find_spec_references(self, spec_id) -> dict[Tuple[str, list[str]]]`: Find all artifacts that reference a spec.

Args:
    spec_id: Spec ID to search for (e.g., "SPEC-001")

Returns:
    Dictionary mapping artifact type to list of artifact IDs:
    {
      "requirements": ["SPEC-001.FR-001", "SPEC-001.NFR-002"],
      "deltas": ["DE-005"],
      "revisions": ["RE-003"],
      "decisions": ["ADR-042"]
    }

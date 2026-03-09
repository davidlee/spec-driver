# supekku.scripts.lib.deletion.executor

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
    orphaned_specs: Set of spec IDs known to be orphaned (for context).
                   If provided, cross-references from other orphaned specs
                   will not block deletion.

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
- `__init__(self, repo_root) -> None`: Initialize scanner.

Args:
    repo_root: Repository root directory
- @staticmethod `_extract_spec_from_requirement(req_id) -> <BinOp>`: Extract spec ID from requirement ID.

Args:
    req_id: Requirement ID (e.g., "SPEC-042.FR-001")

Returns:
    Spec ID (e.g., "SPEC-042") or None if no match
- `_load_registry(self, filename) -> <BinOp>`: Load a registry YAML file.

Args:
    filename: Name of the registry file (e.g., "requirements.yaml")

Returns:
    Parsed YAML data or None if file missing/malformed
- `_scan_decisions(self, spec_id, references) -> None`: Scan decisions.yaml for references to spec_id.

Args:
    spec_id: Spec ID to search for
    references: Dictionary to populate with found references - Only add revision once even if multiple relations
- `_scan_deltas(self, spec_id, references) -> None`: Scan deltas.yaml for references to spec_id.

Args:
    spec_id: Spec ID to search for
    references: Dictionary to populate with found references
- `_scan_requirements(self, spec_id, references) -> None`: Scan requirements.yaml for references to spec_id.

Args:
    spec_id: Spec ID to search for
    references: Dictionary to populate with found references
- `_scan_revisions(self, spec_id, references) -> None`: Scan revisions.yaml for references to spec_id.

Args:
    spec_id: Spec ID to search for
    references: Dictionary to populate with found references

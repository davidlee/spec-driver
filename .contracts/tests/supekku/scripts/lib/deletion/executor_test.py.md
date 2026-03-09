# supekku.scripts.lib.deletion.executor_test

Tests for deletion infrastructure.

## Classes

### TestCrossReferenceValidation

Test cross-reference validation in DeletionValidator.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `tearDown(self) -> None`: Clean up test environment.
- `test_blocked_by_decision(self) -> None`: Test deletion blocked by decision reference.
- `test_blocked_by_delta(self) -> None`: Test deletion blocked by delta reference.
- `test_blocked_by_multiple_references(self) -> None`: Test deletion blocked by multiple types of references.
- `test_blocked_by_requirement(self) -> None`: Test deletion blocked by requirement reference.
- `test_blocked_by_revision(self) -> None`: Test deletion blocked by revision reference.
- `test_no_cross_references(self) -> None`: Test deletion when there are no cross-references.
- `test_orphaned_specs_parameter_accepted(self) -> None`: Test that orphaned_specs parameter is accepted.
- `_create_spec(self, spec_id) -> None`: Create a minimal spec directory.
- `_write_registry(self, filename, data) -> None`: Write a registry YAML file.

### TestDeletionExecutor

Test DeletionExecutor functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `tearDown(self) -> None`: Clean up test fixtures.
- `test_delete_spec_actual_deletion(self) -> None`: Test actual deletion of spec files and directory.
- `test_delete_spec_dry_run_existing(self) -> None`: Test dry-run deletion of existing spec.
- `test_delete_spec_dry_run_nonexistent(self) -> None`: Test dry-run deletion of nonexistent spec.
- `test_delete_spec_handles_already_deleted_files(self) -> None`: Test deletion handles race conditions where files are already deleted. - Nothing should be deleted (nothing exists anyway, but plan should block)
- `test_delete_spec_handles_broken_symlinks(self) -> None`: Test deletion removes broken symlinks.
- `test_delete_spec_handles_missing_registry(self) -> None`: Test that deletion handles missing registry gracefully.
- `test_delete_spec_rebuilds_indices(self) -> None`: Test that deletion rebuilds spec indices.
- `test_delete_spec_removes_from_registry(self) -> None`: Test that deletion removes spec from registry_v2.json.
- `test_delete_spec_removes_symlinks(self) -> None`: Test deletion removes associated symlinks.
- `test_delete_spec_unsafe_deletion_not_executed(self) -> None`: Test that unsafe deletions are not executed.
- `test_delete_spec_with_multiple_files(self) -> None`: Test deletion of spec with multiple markdown files.
- `test_initialization(self) -> None`: Test DeletionExecutor initialization.
- `_create_spec_with_frontmatter(self, spec_id, frontmatter) -> Path`: Create a spec directory and file with given frontmatter.
- `_create_symlink(self, link_path, target) -> None`: Create a symlink, creating parent directories as needed.

### TestDeletionPlan

Test DeletionPlan data class.

**Inherits from:** unittest.TestCase

#### Methods

- `test_add_cross_reference(self) -> None`: Test adding cross-references.
- `test_add_file(self) -> None`: Test adding files to delete.
- `test_add_registry_update(self) -> None`: Test adding registry updates.
- `test_add_symlink(self) -> None`: Test adding symlinks to remove.
- `test_add_warning(self) -> None`: Test adding warnings to a plan.
- `test_creation_defaults(self) -> None`: Test creating a DeletionPlan with defaults.

### TestDeletionValidator

Test DeletionValidator functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `tearDown(self) -> None`: Clean up test fixtures.
- `test_find_spec_symlinks_multiple_indices(self) -> None`: Test finding symlinks across multiple index directories.
- `test_find_spec_symlinks_nested_in_spec_dir(self) -> None`: Test finding symlinks that point to files within spec directory.
- `test_find_spec_symlinks_no_indices(self) -> None`: Test finding symlinks when index directories don't exist.
- `test_initialization(self) -> None`: Test DeletionValidator initialization.
- `test_validate_spec_deletion_existing_spec(self) -> None`: Test validating deletion of an existing spec.
- `test_validate_spec_deletion_nonexistent_spec(self) -> None`: Test validating deletion of a spec that doesn't exist.
- `test_validate_spec_deletion_with_broken_symlinks(self) -> None`: Test validator handles broken symlinks gracefully.
- `test_validate_spec_deletion_with_multiple_files(self) -> None`: Test validating deletion of spec with multiple markdown files.
- `test_validate_spec_deletion_with_symlinks(self) -> None`: Test validating deletion detects symlinks to spec.
- `_create_spec_with_frontmatter(self, spec_id, frontmatter) -> Path`: Create a spec directory and file with given frontmatter.
- `_create_symlink(self, link_path, target) -> None`: Create a symlink, creating parent directories as needed.

### TestRegistryScanner

Test RegistryScanner cross-reference detection.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `tearDown(self) -> None`: Clean up test environment.
- `test_extract_spec_from_requirement(self) -> None`: Test extracting spec ID from requirement ID.
- `test_find_spec_in_decisions_requirements_list(self) -> None`: Test finding spec extracted from requirements in decisions.
- `test_find_spec_in_decisions_specs_list(self) -> None`: Test finding spec in decisions specs list.
- `test_find_spec_in_deltas(self) -> None`: Test finding spec referenced in deltas.
- `test_find_spec_in_requirements(self) -> None`: Test finding spec referenced in requirements.
- `test_find_spec_in_revisions(self) -> None`: Test finding spec referenced in revisions.
- `test_find_spec_multiple_registries(self) -> None`: Test finding spec referenced across multiple registries.
- `test_find_spec_references_empty_registries(self) -> None`: Test finding references in empty registries.
- `test_find_spec_references_no_registries(self) -> None`: Test finding references when no registries exist.
- `test_malformed_yaml_handled_gracefully(self) -> None`: Test that malformed YAML is handled without errors.
- `_write_registry(self, filename, data) -> None`: Write a registry YAML file.

# supekku.scripts.lib.validation.validator_spec_requirements_test

Spec requirements block validation in WorkspaceValidator (DE-140).

## Classes

### OperationalGuardTest

VT-140-029: strict flip blocked when unmigrated files remain.

**Inherits from:** RepoTestCase

#### Methods

- `test_all_migrated_returns_empty(self) -> None`: Guard returns empty list when all specs have blocks.
- `test_malformed_block_counts_as_unmigrated(self) -> None`: Spec with malformed requirements block is unmigrated.
- `test_no_specs_returns_empty(self) -> None`: Guard returns empty list when workspace has no specs.
- `test_unmigrated_returns_ids(self) -> None`: Guard returns IDs of specs without blocks.
- `_create_repo(self)`
- `_write_spec_with_block(self, root, spec_id) -> None`
- `_write_spec_without_block(self, root, spec_id) -> None`

### SpecRequirementsValidationTest

VT-140-015, VT-140-016, VT-140-022: spec requirements block validation.

**Inherits from:** RepoTestCase

#### Methods

- `test_malformed_yaml_block_errors(self) -> None`: Malformed YAML in requirements block produces an error.
- `test_missing_required_field_errors(self) -> None`: Block missing required field produces schema validation error.
- `test_no_block_no_issues(self) -> None`: Spec without requirements block produces no issues (pre-flip).
- `test_non_strict_permits_empty_fields(self) -> None`: Non-strict mode permits empty description and acceptance_criteria.
- `test_prod_spec_cross_validated(self) -> None`: PROD spec requirements block also cross-validates spec field.
- `test_spec_field_match_no_cross_validation_error(self) -> None`: spec field matching artifact ID produces no cross-validation error.
- `test_spec_field_mismatch_errors(self) -> None`: spec field not matching artifact ID produces an error. - -- VT-140-016: WorkspaceValidator — spec field cross-validated --
- `test_strict_rejects_blank_acceptance_criteria_items(self) -> None`: Strict mode rejects blank items in acceptance_criteria.
- `test_strict_rejects_empty_acceptance_criteria_list(self) -> None`: Strict mode rejects empty acceptance_criteria list.
- `test_strict_rejects_trimmed_empty_description(self) -> None`: Strict mode rejects trimmed-empty description field. - -- VT-140-022: Trimmed-empty/blank-item rejection --
- `test_valid_requirements_block_no_issues(self) -> None`: Valid requirements block produces no validation issues. - -- VT-140-015: WorkspaceValidator — requirements block validated --
- `_create_repo(self)`
- `_render_valid_block(self, spec_id) -> str`
- `_write_spec_with_requirements_block(self, root, spec_id, block_content) -> None`

### StrictMissingBlockTest

VT-140-017: strict mode — missing block → error.

**Inherits from:** RepoTestCase

#### Methods

- `test_non_strict_missing_block_no_error(self) -> None`: Non-strict mode: spec without requirements block is tolerated.
- `test_strict_missing_block_errors(self) -> None`: Strict mode: spec without requirements block produces error.
- `test_strict_prod_missing_block_errors(self) -> None`: Strict mode: PROD spec without block also errors.
- `_create_repo(self)`
- `_write_spec_without_block(self, root, spec_id) -> None`

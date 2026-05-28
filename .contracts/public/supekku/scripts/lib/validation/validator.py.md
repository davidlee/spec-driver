# supekku.scripts.lib.validation.validator

Validation utilities for workspace and artifact consistency.

## Functions

- `check_requirements_migration_complete(workspace) -> list[str]`: Return IDs of specs/prods missing a ``spec.requirements`` block.

Used as an operational guard (DEC-140-13): the strict flip must not
proceed while any spec/prod artifact lacks a requirements block.
- `validate_workspace(workspace, strict) -> list[ValidationIssue]`: Validate the given workspace and return a list of validation issues.

## Classes

### ValidationIssue

Represents a validation issue with severity level and context.

### WorkspaceValidator

Validates workspace consistency and artifact relationships.

#### Methods

- `validate(self) -> list[ValidationIssue]`: Validate workspace for missing references and inconsistencies.

# supekku.scripts.lib.validation.validator

Validation utilities for workspace and artifact consistency.

## Functions

- `validate_workspace(workspace, strict) -> list[ValidationIssue]`: Validate the given workspace and return a list of validation issues.

## Classes

### ValidationIssue

Represents a validation issue with severity level and context.

### WorkspaceValidator

Validates workspace consistency and artifact relationships.

#### Methods

- `validate(self) -> list[ValidationIssue]`: Validate workspace for missing references and inconsistencies.

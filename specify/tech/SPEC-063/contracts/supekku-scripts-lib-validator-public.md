# supekku.scripts.lib.validator

Validation utilities for workspace and artifact consistency.

## Functions

- `validate_workspace(workspace, strict) -> list[ValidationIssue]`

## Classes

### ValidationIssue

Represents a validation issue with severity level and context.

### WorkspaceValidator

Validates workspace consistency and artifact relationships.

#### Methods

- `validate(self) -> list[ValidationIssue]`

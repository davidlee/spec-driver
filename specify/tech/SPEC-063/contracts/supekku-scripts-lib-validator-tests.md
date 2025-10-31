# supekku.scripts.lib.validator

Validation utilities for workspace and artifact consistency.

## Constants

- `__all__`

## Functions

- `validate_workspace(workspace, strict) -> list[ValidationIssue]`

## Classes

### ValidationIssue

Represents a validation issue with severity level and context.

### WorkspaceValidator

Validates workspace consistency and artifact relationships.

#### Methods

- `validate(self) -> list[ValidationIssue]`
- `__init__(self, workspace, strict) -> None`
- `_error(self, artifact, message) -> None`
- `_validate_change_relations(self, artifacts, requirement_ids) -> None` - --------------------------------------------------------------
- `_validate_decision_references(self, decisions, decision_ids) -> None`: Validate that all related_decisions references point to existing ADRs.
- `_validate_decision_status_compatibility(self, decisions) -> None`: Warn if active ADR references deprecated or superseded ADRs.

Only applies in strict mode.
- `_warning(self, artifact, message) -> None`

# supekku.scripts.lib.validation.validator

Validation utilities for workspace and artifact consistency.

## Constants

- `__all__`

## Functions

- `validate_workspace(workspace, strict) -> list[ValidationIssue]`: Validate the given workspace and return a list of validation issues.

## Classes

### ValidationIssue

Represents a validation issue with severity level and context.

### WorkspaceValidator

Validates workspace consistency and artifact relationships.

#### Methods

- `validate(self) -> list[ValidationIssue]`: Validate workspace for missing references and inconsistencies.
- `__init__(self, workspace, strict) -> None`
- `_build_conformance_audit_index(self) -> dict[Tuple[str, list[tuple[Tuple[str, dict]]]]]`: Index completed conformance audits by delta_ref.
- `_check_finding_id_collisions(self, delta_id, audits) -> None`: Warn if finding IDs collide across multi-audit union.
- `_error(self, artifact, message) -> None`
- `_info(self, artifact, message) -> None`
- `_validate_audit_disposition(self, audit_registry) -> None`: Validate finding dispositions in completed audits.

For each completed audit, checks every finding for:
- Missing disposition → warning
- Invalid status×kind pair → error
- Invalid outcome×kind pair → error
- closure_override without rationale → error
- `_validate_audit_gate_coverage(self, delta_registry) -> None`: Validate audit gate coverage for qualifying deltas.

For each delta, resolves audit_gate. If required and no completed
conformance audit exists → warning. If multiple audits have
colliding finding IDs → warning.
- `_validate_change_relations(self, artifacts, requirement_ids) -> None` - --------------------------------------------------------------
- `_validate_decision_references(self, decisions, decision_ids) -> None`: Validate that all related_decisions references point to existing ADRs.
- `_validate_decision_status_compatibility(self, decisions) -> None`: Warn if active ADR references deprecated or superseded ADRs.

Only applies in strict mode.
- `_validate_phase_statuses(self) -> None`: Validate phase frontmatter statuses across all delta bundles. - -----------------------------------------------------------
- `_validate_single_phase(self, phase_file, valid_statuses) -> None`: Validate a single phase file's frontmatter and structure.
- `_validate_spec_taxonomy(self) -> None`: Warn when tech specs are missing taxonomy or have inconsistent values.

Scoped to tech specs (SPEC-*) only. PROD specs are excluded.
Emits warnings only — never errors.
- `_validate_unresolved_references(self) -> None`: Validate that frontmatter references resolve to known artifacts.

Uses ``build_reference_graph`` to get the full edge set, then checks
each edge target against the node index. Non-canonical forms that
resolve via normalization produce warnings. Targets that don't
resolve at all produce warnings (or errors in strict mode).

Design reference: DR-097 §4.4.
- `_warning(self, artifact, message) -> None`

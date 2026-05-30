# supekku.scripts.lib.validation.validator

Validation utilities for workspace and artifact consistency.

## Constants

- `_BARE_REQUIREMENT_PATTERN` - Compiled patterns for requirement/spec ID shape detection (POL-002).
- `_SPEC_ID_PATTERN` - Compiled patterns for requirement/spec ID shape detection (POL-002).
- `__all__`

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
- `__init__(self, workspace, strict) -> None`
- `_block_issue(self, artifact, block_label, err) -> None`: Dispatch a block ValidationError into a ValidationIssue at its severity.
- `_build_conformance_audit_index(self) -> dict[Tuple[str, list[tuple[Tuple[str, dict, str]]]]]`: Index completed conformance audits by delta_ref.
- `_check_finding_id_collisions(self, delta_id, audits) -> None`: Check finding ID collisions across multi-audit union.

Severity gated on strict (DR-141 §4).
- `_check_strict_content_requirements(self, artifact, data) -> None`: Reject trimmed-empty description and blank acceptance_criteria (VT-140-022).
- `_error(self, artifact, message) -> None`
- `_info(self, artifact, message) -> None`
- `_validate_audit_disposition(self, audit_registry) -> None`: Validate finding dispositions in completed audits.

Checks per finding (DR-141 §4):
- Invalid outcome enum → error (strict) / warn (non-strict)
- Missing disposition on completed audit → error (strict) / warn
- Invalid status×kind pair → error
- Invalid outcome×kind pair → error
- closure_override without rationale → error (strict) / warn
- closure_override.effect escalation → error (strict)
- Undisposed finding on completed audit → error (strict)
- `_validate_audit_gate_coverage(self, delta_registry) -> None`: Validate audit gate coverage for qualifying deltas.

For each delta, resolves audit_gate. If required and no completed
conformance audit exists → warning. If multiple audits have
colliding finding IDs → warning.
- `_validate_change_relations(self, artifacts, requirement_ids) -> None` - --------------------------------------------------------------
- `_validate_decision_references(self, decisions, decision_ids) -> None`: Validate that all related_decisions references point to existing ADRs.
- `_validate_decision_status_compatibility(self, decisions) -> None`: Warn if active ADR references deprecated or superseded ADRs.

Only applies in strict mode.
- `_validate_delta_blocks(self, delta_registry) -> None`: Validate per-delta context_inputs and risk_register block schemas.

Tolerated alias entries become errors when ``self.accept_tolerated`` is
False (DEC-138-14, F-138-23). Diagnostics are dispatched at the severity
reported by the underlying ``MetadataValidator`` so warnings stay warnings
unless ``--strict`` promotes them at the exit-code layer.
- `_validate_kind_frontmatter(self, model_cls, label, directories, glob) -> None`: Validate frontmatter files against a Pydantic model.

Walks *directories*, globs for *glob*, parses frontmatter, and
attempts ``model_cls(**fm)``.  Failures emit a warning using *label*
(e.g. "Memory", "Backlog", "Drift"). - -- Kind-aware frontmatter validation (DE-112) -------------------------
- `_validate_phase_frontmatter(self, fm, artifact) -> None`: Validate canonical phase frontmatter fields via PhaseSheet model.
- `_validate_phase_statuses(self) -> None`: Validate phase frontmatter statuses across all delta bundles. - -----------------------------------------------------------
- `_validate_single_phase(self, phase_file, valid_statuses) -> None`: Validate a single phase file's frontmatter and structure.
- `_validate_spec_blocks(self) -> None`: Validate per-spec concerns, hypotheses, and decisions block schemas.

Mirrors ``_validate_delta_blocks`` for spec-kind artefacts.
- `_validate_spec_requirements_blocks(self) -> None`: Validate per-spec requirements block schemas (DE-140 P03).

Follows ``_validate_spec_blocks`` pattern: extract → schema validate →
semantic checks. Adds spec field cross-validation and strict-mode
trimmed-empty/blank-item rejection per DR-140 §7.
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

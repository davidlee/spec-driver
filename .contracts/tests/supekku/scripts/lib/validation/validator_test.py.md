# supekku.scripts.lib.validation.validator_test

Tests for validator module.

## Classes

### WorkspaceValidatorTest

Test cases for workspace validation functionality.

**Inherits from:** RepoTestCase

#### Methods

- `test_audit_disposition_errors_closure_override_no_rationale(self) -> None`: closure_override without rationale emits an error.
- `test_audit_disposition_errors_invalid_outcome_kind(self) -> None`: Invalid outcome×kind pair emits an error.
- `test_audit_disposition_errors_invalid_status_kind(self) -> None`: Invalid status×kind pair emits an error.
- `test_audit_disposition_skips_draft_audits(self) -> None`: Draft audits are not checked for disposition validity.
- `test_audit_disposition_valid_finding_no_issues(self) -> None`: Valid disposition produces no audit-related issues.
- `test_audit_disposition_warns_missing_disposition(self) -> None`: Completed audit finding without disposition emits a warning.
- `test_audit_gate_no_warn_for_non_qualifying_delta(self) -> None`: Delta without requirements (auto → non-gating) gets no audit warning.
- `test_audit_gate_no_warn_when_conformance_audit_exists(self) -> None`: Delta with required gate and matching conformance audit is clean.
- `test_audit_gate_warns_finding_id_collisions(self) -> None`: Finding ID collision across multi-audit union emits a warning.
- `test_audit_gate_warns_missing_conformance_audit(self) -> None`: Delta with required gate but no conformance audit emits a warning.
- `test_existing_specs_remain_valid_after_taxonomy_validation(self) -> None`: Existing specs/paths remain valid when taxonomy validation is active. - -- Non-breaking regression (VT-030-006) --
- `test_taxonomy_never_emits_errors(self) -> None`: Taxonomy validation only emits warnings, never errors.
- `test_taxonomy_no_warn_assembly_component(self) -> None`: category: assembly with c4_level: component is fine — no warning.
- `test_taxonomy_no_warn_for_prod_spec(self) -> None`: PROD spec missing taxonomy must not trigger warnings.
- `test_taxonomy_no_warn_unit_code(self) -> None`: category: unit with c4_level: code is consistent — no warning.
- `test_taxonomy_warns_both_missing(self) -> None`: Tech spec missing both category and c4_level emits two warnings.
- `test_taxonomy_warns_inconsistent_unit_non_code(self) -> None`: category: unit with c4_level != code emits a warning.
- `test_taxonomy_warns_missing_c4_level(self) -> None`: Tech spec without c4_level emits a warning.
- `test_taxonomy_warns_missing_category(self) -> None`: Tech spec without category emits a warning.
- `test_validator_accepts_backlog_item_in_applies_to(self) -> None`: Delta referencing a backlog item in applies_to.requirements is valid.
- `test_validator_adr_mixed_validation_scenarios(self) -> None`: Test validator with mix of valid and invalid ADR scenarios in strict mode.
- `test_validator_adr_validation_no_issues_when_valid(self) -> None`: Test that validator finds no issues with valid ADR references.
- `test_validator_adr_with_empty_related_decisions(self) -> None`: Test that validator handles ADRs with no related_decisions correctly.
- `test_validator_checks_adr_reference_validation(self) -> None`: Test that validator detects broken ADR references.
- `test_validator_checks_adr_status_compatibility(self) -> None`: Test validator warns about deprecated/superseded ADRs in strict.
- `test_validator_checks_change_relations(self) -> None`: Test validator verifies change relations point to valid requirements.
- `test_validator_no_warning_deprecated_referencing_deprecated(self) -> None`: Test deprecated ADRs referencing deprecated don't warn.
- `test_validator_rejects_unknown_applies_to_requirement(self) -> None`: Delta referencing a nonexistent ID in applies_to.requirements is an error.
- `test_validator_reports_missing_relation_targets(self) -> None`: Test validator detects relation targets referencing missing artifacts.
- `test_validator_warns_coverage_without_baseline_status(self) -> None`: Test validator handles coverage evidence based on requirement status (VT-912).
- `_create_repo(self) -> Path`
- `_write_adr(self, root, adr_id, status, related_decisions) -> Path`: Helper to create ADR files for testing.
- `_write_audit(self, root, audit_id, requirement_uid) -> Path`
- `_write_backlog_item(self, root, item_id) -> None`: Create a backlog issue on disk and register it. - -- Backlog item acceptance (applies_to.requirements) --
- `_write_completed_audit(self, root, audit_id) -> Path`: Write a completed audit with mode, delta_ref, and findings. - -- Audit disposition validation (DE-079 phase 3) --
- `_write_delta(self, root, delta_id, requirement_uid) -> Path`
- `_write_prod_spec(self, root, spec_id) -> None`: Write a product spec (no taxonomy expected).
- `_write_revision(self, root, revision_id, requirement_uid) -> Path`
- `_write_spec(self, root, spec_id, requirement_label) -> None`
- `_write_tech_spec(self, root, spec_id) -> None`: Write a tech spec with optional taxonomy fields. - -- Taxonomy validation tests (VT-030-005) --

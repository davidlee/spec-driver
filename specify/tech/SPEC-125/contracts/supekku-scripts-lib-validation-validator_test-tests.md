# supekku.scripts.lib.validation.validator_test

Tests for validator module.

## Classes

### WorkspaceValidatorTest

Test cases for workspace validation functionality.

**Inherits from:** RepoTestCase

#### Methods

- `test_validator_adr_mixed_validation_scenarios(self) -> None`: Test validator with mix of valid and invalid ADR scenarios in strict mode.
- `test_validator_adr_validation_no_issues_when_valid(self) -> None`: Test that validator finds no issues with valid ADR references.
- `test_validator_adr_with_empty_related_decisions(self) -> None`: Test that validator handles ADRs with no related_decisions correctly.
- `test_validator_checks_adr_reference_validation(self) -> None`: Test that validator detects broken ADR references.
- `test_validator_checks_adr_status_compatibility(self) -> None`: Test validator warns about deprecated/superseded ADRs in strict.
- `test_validator_checks_change_relations(self) -> None`: Test validator verifies change relations point to valid requirements.
- `test_validator_no_warning_deprecated_referencing_deprecated(self) -> None`: Test deprecated ADRs referencing deprecated don't warn.
- `test_validator_reports_missing_relation_targets(self) -> None`: Test validator detects relation targets referencing missing artifacts.
- `test_validator_warns_coverage_without_baseline_status(self) -> None`: Test validator handles coverage evidence based on requirement status (VT-912).
- `_create_repo(self) -> Path`
- `_write_adr(self, root, adr_id, status, related_decisions) -> Path`: Helper to create ADR files for testing.
- `_write_audit(self, root, audit_id, requirement_uid) -> Path`
- `_write_delta(self, root, delta_id, requirement_uid) -> Path`
- `_write_revision(self, root, revision_id, requirement_uid) -> Path`
- `_write_spec(self, root, spec_id, requirement_label) -> None`

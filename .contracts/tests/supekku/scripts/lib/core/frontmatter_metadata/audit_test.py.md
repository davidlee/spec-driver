# supekku.scripts.lib.core.frontmatter_metadata.audit_test

Dual-validation tests for audit frontmatter metadata.

Tests that the metadata-driven validator handles audit-specific fields
correctly, including the per-finding disposition contract (DEC-079-001).

## Constants

- `_BASE`

## Functions

- `_new_errors(data) -> list[str]`: Run metadata validator and return error strings.

## Classes

### AuditFrontmatterValidationTest

Test metadata validator for audit-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_audit_window_missing_end(self) -> None`
- `test_audit_window_missing_start(self) -> None`
- `test_closure_override_invalid_effect(self) -> None`
- `test_closure_override_missing_rationale(self) -> None`
- `test_disposition_invalid_kind(self) -> None`
- `test_disposition_invalid_status(self) -> None`
- `test_disposition_missing_kind(self) -> None`
- `test_disposition_missing_status(self) -> None`
- `test_finding_invalid_outcome(self) -> None`
- `test_finding_missing_required_fields(self) -> None`
- `test_invalid_delta_ref_format(self) -> None`
- `test_invalid_mode(self) -> None` - -- Invalid cases --
- `test_ref_missing_kind(self) -> None`
- `test_ref_missing_ref(self) -> None`
- `test_valid_audit_window(self) -> None`
- `test_valid_audit_with_discovery_mode(self) -> None`
- `test_valid_audit_with_mode_and_delta_ref(self) -> None`
- `test_valid_disposition_follow_up_delta_accepted(self) -> None`
- `test_valid_disposition_tolerated_drift(self) -> None`
- `test_valid_disposition_with_closure_override(self) -> None`
- `test_valid_finding_aligned(self) -> None`
- `test_valid_finding_with_full_disposition(self) -> None`
- `test_valid_finding_with_linked_fields(self) -> None`
- `test_valid_findings_without_disposition(self) -> None`: Findings without disposition are valid (backward compat).
- `test_valid_minimal_audit(self) -> None` - -- Valid cases --
- `_assert_both_valid(self, data) -> None`
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`

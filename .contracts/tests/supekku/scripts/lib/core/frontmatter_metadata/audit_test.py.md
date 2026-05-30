# supekku.scripts.lib.core.frontmatter_metadata.audit_test

Dual-validation tests for audit frontmatter metadata.

Tests that the metadata-driven validator handles audit-specific fields
correctly. Finding/disposition validation moved to block-level tests
(audit_findings_test.py) after DE-141 P04.

## Constants

- `_BASE`

## Functions

- `_new_errors(data) -> list[str]`: Run metadata validator (strict mode) and return error strings.

## Classes

### AuditFrontmatterValidationTest

Test metadata validator for audit-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_audit_window_missing_end(self) -> None`
- `test_audit_window_missing_start(self) -> None`
- `test_findings_in_fm_rejected_strict(self) -> None`: After DE-141, findings in FM is an unknown key under strict.
- `test_invalid_delta_ref_format(self) -> None`
- `test_invalid_mode(self) -> None` - -- Invalid cases --
- `test_valid_audit_window(self) -> None`
- `test_valid_audit_with_code_scope(self) -> None`
- `test_valid_audit_with_discovery_mode(self) -> None`
- `test_valid_audit_with_mode_and_delta_ref(self) -> None`
- `test_valid_audit_with_spec_refs(self) -> None`
- `test_valid_minimal_audit(self) -> None` - -- Valid cases --
- `_assert_both_valid(self, data) -> None`
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`

# supekku.scripts.lib.core.frontmatter_metadata.audit_test

Dual-validation tests for audit frontmatter metadata.

## Classes

### AuditFrontmatterValidationTest

Test metadata validator for audit-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_audit_window_missing_end(self) -> None`: New validator rejects audit_window missing end.
- `test_audit_window_missing_start(self) -> None`: New validator rejects audit_window missing start. - Invalid cases (new validator only)
- `test_finding_invalid_outcome(self) -> None`: New validator rejects finding with invalid outcome.
- `test_finding_missing_required_fields(self) -> None`: New validator rejects finding missing required fields.
- `test_next_action_missing_required_fields(self) -> None`: New validator rejects next_action missing required fields.
- `test_patch_level_missing_required_fields(self) -> None`: New validator rejects patch_level missing required fields.
- `test_valid_audit_window(self) -> None`: Both validators accept audit_window with start and end.
- `test_valid_audit_with_all_fields(self) -> None`: Both validators accept audit with all optional fields.
- `test_valid_findings_array(self) -> None`: Both validators accept findings array.
- `test_valid_minimal_audit(self) -> None`: Both validators accept minimal audit (base fields only). - Valid cases
- `test_valid_next_actions_array(self) -> None`: Both validators accept next_actions array.
- `test_valid_patch_level_array(self) -> None`: Both validators accept patch_level array.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).

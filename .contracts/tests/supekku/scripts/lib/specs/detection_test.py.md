# supekku.scripts.lib.specs.detection_test

Tests for stub spec detection.

## Functions

- `test_is_stub_spec_accepted_long(tmp_path)`: Spec with status='accepted' and >30 lines should not be stub.
- `test_is_stub_spec_draft_long(tmp_path)`: Spec with status='draft' and >30 lines should not be stub.
- `test_is_stub_spec_line_count(tmp_path)`: Spec with ≤30 lines should be detected as stub (fallback).
- `test_is_stub_spec_missing_file(tmp_path)`: Non-existent spec file should raise FileNotFoundError.
- `test_is_stub_spec_modified(tmp_path)`: Spec with >30 lines and status!='stub' should not be detected as stub.
- `test_is_stub_spec_status_stub(tmp_path)`: Spec with status='stub' should be detected as stub.
- `test_is_stub_spec_stub_status_overrides_line_count(tmp_path)`: Spec with status='stub' should be stub even if >30 lines (edge case).

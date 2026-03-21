# supekku.scripts.lib.workflow.handoff_io_test

Tests for handoff I/O (DR-102 §3.2, §5).

## Functions

- `_minimal_handoff() -> dict`: Return minimal valid handoff dict.

## Classes

### BuildHandoffTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_build_omits_empty_optionals(self) -> None`
- `test_build_validates_on_write(self) -> None`: Built handoff must be writable.
- `test_build_with_boundary(self) -> None`
- `test_build_with_git_state(self) -> None`
- `test_build_with_open_items(self) -> None`
- `test_build_with_verification(self) -> None`
- `test_minimal_build(self) -> None`
- `test_next_activity_kind_for_reviewer(self) -> None`

### HandoffPathTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_default(self) -> None`

### ReadHandoffTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_read_missing_raises(self) -> None`
- `test_read_valid(self) -> None`

### WriteHandoffTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_atomic_no_temp_files(self) -> None`
- `test_write_rejects_invalid(self) -> None`
- `test_write_valid(self) -> None`

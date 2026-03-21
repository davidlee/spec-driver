# supekku.scripts.lib.workflow.state_io_test

Tests for workflow state.yaml reading/writing (DR-102 §3.1, §5).

Validates schema validation on read/write, atomic writes,
init_state construction, and update_state_workflow mutations.

## Functions

- `_minimal_state() -> dict`: Return minimal valid state dict.

## Classes

### InitStateTest

init_state constructs valid state dicts.

**Inherits from:** unittest.TestCase

#### Methods

- `test_full_init(self) -> None`
- `test_init_respects_config(self) -> None`
- `test_init_validates_on_write(self) -> None`: init_state output must be writable (schema-valid).
- `test_minimal_init(self) -> None`

### ReadStateTest

Read with validation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_read_invalid_file_raises(self) -> None`
- `test_read_missing_file_raises(self) -> None`
- `test_read_valid_state(self) -> None`

### StatePathTest

state_path returns expected path.

**Inherits from:** unittest.TestCase

#### Methods

- `test_custom_dir(self) -> None`
- `test_default_dir(self) -> None`

### UpdateStateWorkflowTest

update_state_workflow mutations.

**Inherits from:** unittest.TestCase

#### Methods

- `test_clear_claimed_by(self) -> None`
- `test_clear_previous_state(self) -> None`
- `test_ellipsis_sentinel_preserves_existing(self) -> None`: Not passing claimed_by should not touch existing value.
- `test_set_claimed_by(self) -> None`
- `test_set_previous_state(self) -> None`
- `test_update_active_role(self) -> None`
- `test_update_next_role(self) -> None`
- `test_update_status(self) -> None`
- `test_updates_timestamp(self) -> None`

### WriteStateTest

Atomic write with schema validation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_write_creates_directory(self) -> None`
- `test_write_is_atomic_no_partial_file(self) -> None`
- `test_write_rejects_invalid_data(self) -> None`
- `test_write_valid_state(self) -> None`

# supekku.scripts.lib.standards.registry_test

Tests for standard registry module.

## Classes

### TestStandardRecord

Tests for StandardRecord dataclass.

**Inherits from:** unittest.TestCase

#### Methods

- `test_default_status(self) -> None`: Test that 'default' status is supported.
- `test_to_dict_minimal(self) -> None`: Test serialization with minimal fields.

### TestStandardRegistry

Tests for StandardRegistry class.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_collect_single_standard(self) -> None`: Test collecting a single standard.
- `test_iter_filtered_by_default_status(self) -> None`: Test filtering standards by 'default' status.

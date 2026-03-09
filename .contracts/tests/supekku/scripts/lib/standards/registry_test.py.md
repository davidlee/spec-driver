# supekku.scripts.lib.standards.registry_test

Tests for standard registry module.

## Classes

### TestStandardRecord

Tests for StandardRecord dataclass.

**Inherits from:** unittest.TestCase

#### Methods

- `test_default_status(self) -> None`: Test that 'default' status is supported.
- `test_to_dict_ext_id_ext_url(self) -> None`: Test ext_id/ext_url appear in serialized dict when populated. - Empty ext_url omitted
- `test_to_dict_ext_url_only(self) -> None`: Test ext_url without ext_id — only ext_url appears.
- `test_to_dict_minimal(self) -> None`: Test serialization with minimal fields.

### TestStandardRegistry

Tests for StandardRegistry class.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_collect_single_standard(self) -> None`: Test collecting a single standard.
- `test_iter_filtered_by_default_status(self) -> None`: Test filtering standards by 'default' status.

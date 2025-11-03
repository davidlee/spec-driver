# supekku.scripts.lib.policies.registry_test

Tests for policy registry module.

## Classes

### TestPolicyRecord

Tests for PolicyRecord dataclass.

**Inherits from:** unittest.TestCase

#### Methods

- `test_to_dict_full(self) -> None`: Test serialization with all fields populated. - Empty lists are omitted
- `test_to_dict_minimal(self) -> None`: Test serialization with minimal fields.

### TestPolicyRegistry

Tests for PolicyRegistry class.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_collect_empty(self) -> None`: Test collecting policies from empty directory.
- `test_collect_single_policy(self) -> None`: Test collecting a single policy.
- `test_filter_by_tag(self) -> None`: Test filtering policies by tag.
- `test_find(self) -> None`: Test finding a specific policy by ID.
- `test_init(self) -> None`: Test registry initialization.
- `test_iter_all(self) -> None`: Test iterating over all policies.
- `test_iter_filtered_by_status(self) -> None`: Test iterating with status filter.
- `test_write_registry(self) -> None`: Test writing registry to YAML.

# supekku.cli.drift_test

Tests for drift ledger CLI commands (create, list, show).

## Classes

### CreateDriftTest

Tests for `create drift` CLI command.

**Inherits from:** _DriftTestBase

#### Methods

- `test_create_drift_ledger(self) -> None`
- `test_create_drift_sequential_ids(self) -> None`
- `test_create_drift_with_delta(self) -> None`

### InferredShowDriftTest

Tests for ID inference dispatch to drift ledgers.

**Inherits from:** _DriftTestBase

#### Methods

- `test_show_inferred_dl_prefix(self) -> None`: show DL-001 should resolve via prefix inference.

### ListDriftTest

Tests for `list drift` CLI command.

**Inherits from:** _DriftTestBase

#### Methods

- `test_list_empty(self) -> None`
- `test_list_filter(self) -> None`
- `test_list_json(self) -> None`
- `test_list_status_filter(self) -> None`
- `test_list_with_ledgers(self) -> None`

### ShowDriftTest

Tests for `show drift` CLI command.

**Inherits from:** _DriftTestBase

#### Methods

- `test_show_drift_json(self) -> None`
- `test_show_drift_ledger(self) -> None`
- `test_show_drift_not_found(self) -> None`
- `test_show_drift_path(self) -> None`
- `test_show_drift_raw(self) -> None`

### _DriftTestBase

Shared setup for drift CLI tests.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `_create_ledger(self, name, delta) -> Path`: Create a ledger file directly for test setup.

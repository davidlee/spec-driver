# supekku.scripts.lib.diagnostics.checks.lifecycle_test

Tests for lifecycle hygiene checks.

## Functions

- `_today_minus(days) -> str`

## Classes

### TestCheckLifecycle

Tests for check_lifecycle function.

**Inherits from:** unittest.TestCase

#### Methods

- @patch(supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config) `test_all_results_have_lifecycle_category(self, mock_config) -> None`: Every result should use the lifecycle category.
- @patch(supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config) `test_custom_threshold_from_config(self, mock_config) -> None`: Staleness threshold should be configurable via workflow config.
- @patch(supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config) `test_default_staleness_days_value(self, mock_config) -> None`: Default staleness threshold should be 5 days.
- @patch(supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config) `test_fresh_delta_passes(self, mock_config) -> None`: An in-progress delta updated recently should pass.
- @patch(supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config) `test_missing_updated_date_warns(self, mock_config) -> None`: Delta with no updated date should warn.
- @patch(supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config) `test_mixed_statuses(self, mock_config) -> None`: Only in-progress deltas should be checked, others ignored.
- @patch(supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config) `test_no_in_progress_passes(self, mock_config) -> None`: No in-progress deltas should produce a single pass.
- @patch(supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config) `test_registry_load_error_fails(self, mock_config) -> None`: If delta registry fails to load, should produce fail.
- @patch(supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config) `test_stale_delta_warns(self, mock_config) -> None`: An in-progress delta older than threshold should warn.
- @patch(supekku.scripts.lib.diagnostics.checks.lifecycle.load_workflow_config) `test_unparseable_date_warns(self, mock_config) -> None`: Delta with unparseable updated date should warn.

### \_FakeDelta

Minimal delta stub for lifecycle checks.

### \_FakeRegistry

#### Methods

- `collect(self) -> dict`

### \_FakeWorkspace

#### Methods

- @property `delta_registry(self) -> _FakeRegistry`

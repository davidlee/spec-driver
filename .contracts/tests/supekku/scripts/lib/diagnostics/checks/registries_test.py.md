# supekku.scripts.lib.diagnostics.checks.registries_test

Tests for registry integrity checks.

## Classes

### TestCheckRegistries

Tests for check_registries function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_registries_load_pass(self) -> None`: All registries loading successfully should produce pass results.
- `test_all_results_have_registries_category(self) -> None`: Every result should use the registries category.
- `test_empty_registry_passes(self) -> None`: An empty registry should still pass (0 items).
- `test_item_count_in_message(self) -> None`: Pass results should report item counts.
- `test_one_broken_others_still_checked(self) -> None`: A failure in one registry should not prevent checking others.
- `test_registry_error_produces_fail(self) -> None`: A registry that raises on collect() should produce a fail result.

### _FakeRegistry

Minimal registry stub with collect().

#### Methods

- `collect(self) -> dict`

### _FakeWorkspace

#### Methods

- @property `audit_registry(self) -> _FakeRegistry`
- @property `decisions(self) -> _FakeRegistry`
- @property `delta_registry(self) -> _FakeRegistry`
- @property `revision_registry(self) -> _FakeRegistry`
- @property `specs(self) -> _FakeRegistry`

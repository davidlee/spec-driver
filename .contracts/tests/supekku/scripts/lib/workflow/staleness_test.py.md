# supekku.scripts.lib.workflow.staleness_test

Tests for staleness evaluation (DR-102 §8).

## Functions

- `_cached_index() -> dict`: Return a cached review-index for testing.

## Classes

### CheckDomainMapFilesTest

Test domain_map file existence check.

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_exist(self) -> None`
- `test_empty_domain_map(self) -> None`
- `test_some_deleted(self) -> None`

### EvaluateStalenessTest

Test staleness evaluation per DR-102 §8.

**Inherits from:** unittest.TestCase

#### Methods

- `test_invalid_on_schema_id_mismatch(self) -> None`
- `test_invalid_on_schema_version_mismatch(self) -> None`
- `test_multiple_triggers(self) -> None`
- `test_no_surface_expansion_for_known_files(self) -> None`
- `test_not_reusable_on_phase_crossing(self) -> None`: Phase boundary crossing prevents reusability.
- `test_not_reusable_on_surface_expansion(self) -> None`: Dependency surface expansion prevents reusability.
- `test_reusable_on_commit_drift_only(self) -> None`: Commit drift alone makes cache reusable, not stale.
- `test_reusable_with_subset_changed_files(self) -> None`: Changed files within cached domain_map are reusable.
- `test_stale_on_commit_drift(self) -> None`
- `test_stale_on_dependency_surface_expansion(self) -> None`
- `test_stale_on_major_scope_change(self) -> None`
- `test_stale_on_phase_boundary_crossing(self) -> None`
- `test_warm_when_nothing_changed(self) -> None`

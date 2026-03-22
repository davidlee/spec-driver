# supekku.scripts.lib.specs.registry_test

Tests for spec_registry module.

## Classes

### SpecRegistryTest

Test cases for spec_registry functionality.

**Inherits from:** RepoTestCase

#### Methods

- `test_file_to_package_resolution(self) -> None`: VT-004: Test file-to-package resolution for spec queries.

Verifies that files in a package resolve to the correct package-level
spec, supporting --for-path queries at various depths.
- `test_find_by_package(self) -> None`: Test finding specs by package name.
- `test_registry_loads_specs(self) -> None`: Test that registry correctly loads both tech and product specs.
- `test_reload_refreshes_registry(self) -> None`: Test that reloading the registry picks up newly added specs.
- `_make_repo(self) -> Path`

### TestSpecRegistryReverseQueries

Test reverse relationship query methods for SpecRegistry.

**Inherits from:** RepoTestCase

#### Methods

- `test_find_by_informed_by_case_sensitive(self) -> None`: Test that ADR ID matching is case-sensitive.
- `test_find_by_informed_by_empty_string(self) -> None`: Test find_by_informed_by with empty string returns empty list.
- `test_find_by_informed_by_multiple_specs_same_adr(self) -> None`: Test finding multiple specs informed by same ADR.
- `test_find_by_informed_by_none(self) -> None`: Test find_by_informed_by with None returns empty list.
- `test_find_by_informed_by_nonexistent_adr(self) -> None`: Test finding specs for non-existent ADR returns empty list.
- `test_find_by_informed_by_returns_spec_objects(self) -> None`: Test that find_by_informed_by returns proper Spec objects.
- `test_find_by_informed_by_single_adr(self) -> None`: Test finding specs informed by a specific ADR.
- `test_find_by_informed_by_spec_without_informed_by_field(self) -> None`: Test that specs without informed_by field are not returned.
- `test_find_by_informed_by_works_with_prod_specs(self) -> None`: Test finding PROD specs by ADR.
- `_make_repo(self) -> Path`
- `_write_spec_with_adrs(self, root, spec_id, adr_ids) -> None`: Write a spec that references specific ADRs.

### TestSpecRegistryStandardSurface

Tests for ADR-009 standard registry surface: find, collect, iter, filter.

**Inherits from:** RepoTestCase

#### Methods

- `test_collect_empty_registry(self) -> None`
- `test_collect_returns_copy(self) -> None`
- `test_collect_returns_dict(self) -> None` - -- collect() ------------------------------------------------------------
- `test_filter_and_logic(self) -> None`
- `test_filter_by_category(self) -> None`
- `test_filter_by_kind(self) -> None`
- `test_filter_by_status(self) -> None` - -- filter() -------------------------------------------------------------
- `test_filter_by_tag(self) -> None`
- `test_filter_no_matches_returns_empty(self) -> None`
- `test_filter_no_params_returns_all(self) -> None`
- `test_find_returns_none_for_missing(self) -> None`
- `test_find_returns_spec(self) -> None` - -- find() ---------------------------------------------------------------
- `test_get_delegates_to_find(self) -> None` - -- get() deprecation ----------------------------------------------------
- `test_iter_filters_by_status(self) -> None`
- `test_iter_no_matches(self) -> None`
- `test_iter_yields_all(self) -> None` - -- iter() ---------------------------------------------------------------
- `_make_repo(self) -> Path`
- `_write_spec(self, root, spec_id) -> None`

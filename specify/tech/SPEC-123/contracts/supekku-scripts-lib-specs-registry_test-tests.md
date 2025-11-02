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

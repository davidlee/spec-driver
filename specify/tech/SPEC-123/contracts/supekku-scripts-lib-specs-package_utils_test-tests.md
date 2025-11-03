# supekku.scripts.lib.specs.package_utils_test

Tests for package detection utilities (VT-001).

Verification Target: PROD-005.FR-001 - Leaf Python Package Identification

Test Coverage:
- Leaf package identification across real supekku/ structure
- Non-leaf package detection (parent packages)
- Non-package path validation
- File-to-package resolution at various depths
- Edge cases: single-file packages, deeply nested structures

## Constants

- `KNOWN_LEAF_PACKAGES` - Known leaf packages in supekku/ (as of 2025-11-03)
- `KNOWN_PARENT_PACKAGES` - Known parent packages (not leaves)

## Classes

### TestEdgeCases

Test edge cases and boundary conditions.

#### Methods

- `test_deeply_nested_package(self) -> None`: Test handling of deeply nested packages.
- `test_package_with_test_only_files(self) -> None`: Test packages containing only test files are still leaf packages.
- `test_relative_vs_absolute_paths(self) -> None`: Test that both relative and absolute paths work. - Covered by real package tests
- `test_single_file_package_is_leaf(self) -> None`: Test that a package with only __init__.py is a leaf package.

### TestFindAllLeafPackages

Test find_all_leaf_packages() function.

#### Methods

- `test_excludes_parent_packages(self) -> None`: Test that parent packages are not included in results.
- `test_finds_all_18_leaf_packages_in_supekku(self) -> None`: Test that all 18 known leaf packages are discovered.
- `test_handles_nonexistent_root(self) -> None`: Test that non-existent root returns empty list.
- `test_handles_single_leaf_package_tree(self) -> None`: Test discovery in a subtree with one leaf package.
- `test_handles_tree_with_multiple_levels(self) -> None`: Test discovery in complex nested structure.
- `test_returns_sorted_results(self) -> None`: Test that results are sorted for deterministic output.

### TestFindPackageForFile

Test find_package_for_file() function.

#### Methods

- `test_handles_directory_input(self) -> None`: Test that directory paths work (returns the directory if it's a package).
- `test_resolves_file_in_leaf_package(self) -> None`: Test resolution of file to its leaf package.
- `test_resolves_file_in_nested_package(self) -> None`: Test resolution of file in deeply nested package.
- `test_resolves_init_file_to_package(self) -> None`: Test that __init__.py resolves to its containing package.
- `test_resolves_test_file_to_package(self) -> None`: Test resolution of test file to package.
- `test_returns_none_for_file_outside_package(self) -> None`: Test that files outside packages return None.

### TestIntegrationScenarios

Integration tests covering real-world workflows.

#### Methods

- `test_discover_all_then_validate_workflow(self) -> None`: Test workflow: discover all packages -> validate each.
- `test_file_to_package_to_validation_workflow(self) -> None`: Test complete workflow: file -> package -> validation.
- `test_multiple_files_resolve_to_same_package(self) -> None`: Test that multiple files in same package resolve correctly.

### TestIsLeafPackage

Test is_leaf_package() function.

#### Methods

- `test_identifies_all_known_leaf_packages(self) -> None`: Test that all 16 known leaf packages are correctly identified.
- `test_rejects_files(self) -> None`: Test that file paths are rejected.
- `test_rejects_non_package_directories(self) -> None`: Test that directories without __init__.py are rejected.
- `test_rejects_nonexistent_paths(self) -> None`: Test that non-existent paths are rejected.
- `test_rejects_parent_packages(self) -> None`: Test that parent packages are not identified as leaf packages.

### TestValidatePackagePath

Test validate_package_path() function.

#### Methods

- `test_accepts_valid_leaf_package(self) -> None`: Test that valid leaf packages pass validation.
- `test_accepts_valid_parent_package(self) -> None`: Test that parent packages also pass validation. - Should not raise
- `test_raises_for_directory_without_init(self) -> None`: Test that directories without __init__.py raise ValueError.
- `test_raises_for_file_path(self) -> None`: Test that file paths raise ValueError.
- `test_raises_for_nonexistent_path(self) -> None`: Test that non-existent paths raise FileNotFoundError. - Should not raise

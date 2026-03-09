# supekku.scripts.lib.docs.python.variants_test

Tests for deterministic contract generation (VT-002).

Verification Target: PROD-005.FR-002 - Deterministic File Ordering

Test Coverage:
- Contract generation produces identical output across multiple runs
- File ordering is deterministic within packages
- Byte-identical output for same package state
- Platform-independent ordering (Linux verified, macOS compatible)

## Classes

### TestDeterministicOrdering

Test that contract generation produces deterministic output.

#### Methods

- `test_contract_generation_is_deterministic(self) -> None`: Test that generating contracts multiple times produces identical output.

This is the core VT-002 test: run contract generation 10 times
and verify byte-identical output.
- `test_different_packages_have_different_output(self) -> None`: Sanity check: different packages should produce different contracts.
- `test_file_discovery_order_is_sorted(self) -> None`: Test that VariantSpec.get_files() returns sorted results.

### TestFileOrdering

Test file ordering behavior for various package structures.

#### Methods

- `test_package_with_many_files_ordering(self) -> None`: Test ordering for package with many files.
- `test_single_file_package_ordering(self) -> None`: Test ordering for package with single Python file.
- `test_tests_variant_filters_correctly(self) -> None`: Test that tests variant only includes test files.

### TestPlatformIndependence

Test that ordering is platform-independent.

#### Methods

- `test_path_sorting_is_lexicographic(self) -> None`: Test that path sorting follows expected lexicographic order.
- `test_sorted_ordering_is_stable(self) -> None`: Test that Python's sorted() produces stable results.

This validates the assumption that sorted(Path.rglob())
produces deterministic results across platforms.

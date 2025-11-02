# supekku.scripts.lib.formatters.spec_formatters_test

Tests for spec_formatters module.

## Classes

### TestFormatPackageList

Tests for format_package_list function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_list(self) -> None`: Test formatting empty package list.
- `test_multiple_packages(self) -> None`: Test formatting multiple packages.
- `test_single_package(self) -> None`: Test formatting single package.

### TestFormatSpecDetails

Tests for format_spec_details function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_complete_spec(self) -> None`: Test formatting spec with all fields populated.
- `test_minimal_spec(self) -> None`: Test formatting spec with minimal fields.
- `test_product_spec(self) -> None`: Test formatting product spec.
- `test_spec_with_packages(self) -> None`: Test formatting spec with packages.
- `test_spec_with_path(self) -> None`: Test formatting spec with file path.
- `test_spec_without_packages(self) -> None`: Test formatting spec with no packages.
- `test_spec_without_root(self) -> None`: Test formatting spec without root shows absolute path.
- `_create_mock_spec(self, spec_id, name, slug, kind, status, packages, path) -> Mock`: Create a mock Spec object with all fields.

### TestFormatSpecListItem

Tests for format_spec_list_item function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_options(self) -> None`: Test formatting with all options enabled.
- `test_basic_format(self) -> None`: Test basic format with id and slug.
- `test_format_with_empty_packages(self) -> None`: Test format with empty package list.
- `test_format_with_packages(self) -> None`: Test format with package list.
- `test_format_with_path(self) -> None`: Test format with path instead of slug.
- `test_format_with_path_and_packages(self) -> None`: Test format with both path and packages.
- `test_format_with_path_no_root_raises(self) -> None`: Test that include_path without root raises ValueError.
- `test_format_with_path_outside_root(self) -> None`: Test path formatting when spec path is outside root.
- `test_product_spec(self) -> None`: Test formatting product spec.
- `_create_mock_spec(self, spec_id, slug, packages, path) -> Mock`: Create a mock Spec object.

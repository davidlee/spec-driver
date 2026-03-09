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
- `test_spec_with_category_only(self) -> None`: Test formatting spec with category but no c4_level.
- `test_spec_with_packages(self) -> None`: Test formatting spec with packages.
- `test_spec_with_path(self) -> None`: Test formatting spec with file path.
- `test_spec_with_taxonomy_fields(self) -> None`: Test formatting spec displays category and c4_level.
- `test_spec_without_packages(self) -> None`: Test formatting spec with no packages.
- `test_spec_without_root(self) -> None`: Test formatting spec without root shows absolute path.
- `test_spec_without_taxonomy(self) -> None`: Test formatting spec without taxonomy fields omits them.
- `_create_mock_spec(self, spec_id, name, slug) -> Mock`: Create a mock Spec object with all fields.

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

### TestSpecExternalFields

Tests for ext_id/ext_url support in spec formatters (VT-067-002).

**Inherits from:** unittest.TestCase

#### Methods

- `test_details_with_ext_id_and_url(self) -> None`: Test detail formatter shows ext_id with url.
- `test_details_with_ext_id_only(self) -> None`: Test detail formatter shows ext_id without url.
- `test_details_without_ext_id_omits_line(self) -> None`: Test detail formatter omits External line when no ext_id.
- `test_json_includes_ext_fields(self) -> None`: Test JSON output includes ext_id and ext_url when present.
- `test_json_omits_ext_fields_when_empty(self) -> None`: Test JSON output omits ext_id/ext_url when empty.
- `test_table_no_external_omits_column(self) -> None`: Test table output omits ExtID column when show_external=False.
- `test_table_show_external_includes_column(self) -> None`: Test table output includes ExtID column when show_external=True.
- `test_tsv_no_external_omits_ext_id(self) -> None`: Test TSV output omits ext_id when show_external=False.
- `test_tsv_show_external_inserts_ext_id(self) -> None`: Test TSV output includes ext_id after ID when show_external=True.
- `_create_mock_spec(self, spec_id, name, slug) -> Mock`

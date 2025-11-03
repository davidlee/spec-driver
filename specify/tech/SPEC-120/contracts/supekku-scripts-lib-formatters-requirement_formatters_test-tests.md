# supekku.scripts.lib.formatters.requirement_formatters_test

Tests for requirement_formatters module.

## Classes

### TestFormatRequirementDetails

Tests for format_requirement_details function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_full_requirement(self) -> None`: Test formatting requirement with all fields.
- `test_format_minimal_requirement(self) -> None`: Test formatting requirement with minimal fields.
- `test_format_requirement_with_coverage_evidence(self) -> None`: Test formatting requirement with coverage_evidence field.

### TestFormatRequirementListJson

Tests for format_requirement_list_json function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_minimal_requirement(self) -> None`: Test formatting requirement with minimal fields.
- `test_format_requirement_with_coverage_evidence(self) -> None`: Test formatting requirement with coverage_evidence in JSON.
- `test_format_requirement_with_path(self) -> None`: Test formatting requirement with path.

### TestFormatRequirementListTable

Tests for format_requirement_list_table function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_empty_list_json(self) -> None`: Test formatting empty requirement list as JSON.
- `test_format_empty_list_table(self) -> None`: Test formatting empty requirement list as table.
- `test_format_empty_list_tsv(self) -> None`: Test formatting empty requirement list as TSV.
- `test_format_multiple_requirements(self) -> None`: Test formatting multiple requirements. - status
- `test_format_single_requirement_json(self) -> None`: Test formatting single requirement as JSON.
- `test_format_single_requirement_table(self) -> None`: Test formatting single requirement as table.
- `test_format_single_requirement_tsv(self) -> None`: Test formatting single requirement as TSV.
- `test_format_with_lifecycle_fields(self) -> None`: Test formatting requirement with lifecycle fields.
- `test_format_with_no_primary_spec(self) -> None`: Test formatting requirement without primary spec.
- `test_format_with_no_specs(self) -> None`: Test formatting requirement with no specs.

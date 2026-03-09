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

### TestRequirementExternalFields

Tests for ext_id/ext_url support in requirement formatters (VT-067-002).

**Inherits from:** unittest.TestCase

#### Methods

- `test_details_with_ext_id_and_url(self) -> None`: Test detail formatter shows ext_id with url.
- `test_details_with_ext_id_only(self) -> None`: Test detail formatter shows ext_id without url.
- `test_details_without_ext_id_omits_line(self) -> None`: Test detail formatter omits External line when no ext_id.
- `test_json_includes_ext_fields(self) -> None`: Test JSON output includes ext_id and ext_url when present.
- `test_json_omits_ext_fields_when_empty(self) -> None`: Test JSON output omits ext_id/ext_url when empty.
- `test_table_show_external_includes_column(self) -> None`: Test table includes ExtID column when show_external=True. - category
- `test_tsv_no_external_omits_ext_id(self) -> None`: Test TSV omits ext_id when show_external=False. - ext_id
- `test_tsv_show_external_inserts_ext_id(self) -> None`: Test TSV includes ext_id after Label when show_external=True.

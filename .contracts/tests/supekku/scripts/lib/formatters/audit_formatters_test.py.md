# supekku.scripts.lib.formatters.audit_formatters_test

Tests for audit list formatting.

Covers VT-141-LIST-001, -004, -005.

## Constants

- `EMPTY_SUMMARY`
- `SAMPLE_SUMMARY`

## Functions

- `_mock_audit() -> MagicMock`

## Classes

### TestFormatAuditListJson

VT-141-LIST-004

#### Methods

- `test_json_includes_enriched_fields(self) -> None`

### TestFormatAuditListRow

VT-141-LIST-001

#### Methods

- `test_all_columns_present(self) -> None`
- `test_delta_ref_em_dash_when_none(self) -> None`
- `test_delta_ref_shown(self) -> None`
- `test_disposed_cell(self) -> None`
- `test_findings_cell(self) -> None`
- `test_mode_em_dash_when_none(self) -> None`
- `test_mode_glyph_conformance(self) -> None`
- `test_mode_glyph_discovery(self) -> None`
- `test_name_strips_prefix(self) -> None`

### TestFormatAuditListTsv

VT-141-LIST-005

#### Methods

- `test_tsv_includes_enriched_columns(self) -> None`

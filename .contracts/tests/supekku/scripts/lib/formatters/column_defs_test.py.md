# supekku.scripts.lib.formatters.column_defs_test

Tests for shared column definitions (VT-053-column-defs).

## Constants

- `ALL_COLUMN_SETS`

## Classes

### TestAllColumnSetsExist

Every artifact type has a column definition.

#### Methods

- `test_all_sets_have_id_or_label(self)`: Every column set should have an identifying column.
- `test_all_sets_non_empty(self)`
- `test_column_labels_match_existing_formatters(self)`: Regression: labels must match what existing formatters use.

### TestColumnDef

ColumnDef is a simple metadata container.

#### Methods

- `test_creation(self)`
- `test_frozen(self)`
- `test_style_key_optional(self)`

### TestColumnLabels

column_labels extracts label list.

#### Methods

- `test_adr_labels(self)`
- `test_backlog_labels(self)`
- `test_card_labels(self)`
- `test_change_labels(self)`
- `test_memory_labels(self)`
- `test_policy_labels(self)`
- `test_requirement_labels(self)`
- `test_spec_labels(self)`
- `test_standard_labels(self)`

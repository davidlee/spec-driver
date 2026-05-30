# supekku.scripts.lib.formatters.column_defs

Shared column metadata per artifact type.

Single source of truth for "what columns to show" in list views.
Consumed by both CLI formatters and TUI list views (DEC-053-02).

Each definition maps an artifact type to its list-view columns.
Column order is display order.

## Constants

- `ADR_COLUMNS`
- `AUDIT_COLUMNS`
- `BACKLOG_COLUMNS`
- `CARD_COLUMNS`
- `CHANGE_COLUMNS`
- `DELTA_COLUMNS` - for default (``auto``) but the column header is always present.
- `DELTA_TAGS_COLUMN`
- `DRIFT_COLUMNS`
- `EXT_ID_COLUMN` - Shared optional columns (used with flags like --external, --refs)
- `MEMORY_COLUMNS`
- `PHASE_COLUMNS`
- `PLAN_COLUMNS`
- `POLICY_COLUMNS`
- `REFS_COLUMN` - Shared optional columns (used with flags like --external, --refs)
- `REQUIREMENT_COLUMNS`
- `REVISION_COLUMNS` - full field set.
- `SPEC_COLUMNS` - --- Per-artifact-type column definitions ---
- `SPEC_TAGS_COLUMN`
- `STANDARD_COLUMNS`

## Functions

- `column_labels(columns) -> list[str]`: Extract label list from column definitions.

## Classes

### ColumnDef

Column definition for a list view.

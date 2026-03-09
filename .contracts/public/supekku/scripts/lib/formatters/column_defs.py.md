# supekku.scripts.lib.formatters.column_defs

Shared column metadata per artifact type.

Single source of truth for "what columns to show" in list views.
Consumed by both CLI formatters and TUI list views (DEC-053-02).

Each definition maps an artifact type to its list-view columns.
Column order is display order.

## Constants

- `ADR_COLUMNS`
- `BACKLOG_COLUMNS`
- `CARD_COLUMNS`
- `CHANGE_COLUMNS`
- `DRIFT_COLUMNS`
- `EXT_ID_COLUMN` - Shared optional columns (used with flags like --external, --packages)
- `MEMORY_COLUMNS`
- `PACKAGES_COLUMN` - Shared optional columns (used with flags like --external, --packages)
- `PHASE_COLUMNS`
- `PLAN_COLUMNS`
- `POLICY_COLUMNS`
- `REFS_COLUMN`
- `REQUIREMENT_COLUMNS`
- `SPEC_COLUMNS` - --- Per-artifact-type column definitions ---
- `STANDARD_COLUMNS`

## Functions

- `column_labels(columns) -> list[str]`: Extract label list from column definitions.

## Classes

### ColumnDef

Column definition for a list view.

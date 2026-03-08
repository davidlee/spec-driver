# Notes for DE-069

## Phase 1 — Foundation (completed)

- Created `cell_helpers.py` with `format_tags_cell` and `format_date_cell` (12 tests)
- Added `governance_5col_widths` to `table_utils.py` (replaces 3 identical implementations)
- Removed `no_truncate` from `add_row_with_truncation` (public API reduction)
- Added `PACKAGES_COLUMN` to `column_defs.py`
- Backported helpers into decision, policy, standard, memory formatters (net -62 lines)

## Phase 2 — Migrate remaining formatters (completed)

- **change_formatters**: straightforward; extracted row helpers
- **backlog_formatters**: factory function `_backlog_column_widths` for dynamic `show_external` widths
- **requirement_formatters**: same factory pattern `_requirement_column_widths`
- **spec_formatters**: closures for `show_external` + `include_packages` dynamic columns (DEC-069-02)
- Net -13 lines (246 added, 259 removed)

## Observations

- Closure approach for dynamic columns worked cleanly — no `format_list_table` signature change needed
- Factory functions for width calculators (backlog, requirement) are slightly heavier than the governance pattern but necessary for column-count-varying layouts
- All 10 list-table formatters now use `format_list_table`

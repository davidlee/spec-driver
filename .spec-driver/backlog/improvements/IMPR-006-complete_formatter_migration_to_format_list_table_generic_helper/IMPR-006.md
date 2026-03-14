---
id: IMPR-006
name: Complete formatter migration to format_list_table generic helper
created: '2026-03-05'
updated: '2026-03-09'
status: resolved
kind: improvement
---

# Complete formatter migration to format_list_table generic helper

## Context

DE-041 introduced `format_list_table()` in `table_utils.py` — a generic helper
that eliminates the repeated dispatch + table-setup boilerplate shared by all
`format_*_list_table()` functions. 6 of 10 formatters are already migrated
(plan, decision, memory, policy, standard, card).

## Remaining work

### 1. Moderate migrations (extract helpers first, then rewire)

| Formatter                | Effort  | Notes                                                                               |
| ------------------------ | ------- | ----------------------------------------------------------------------------------- |
| `spec_formatters`        | ~30 min | Inline logic; `include_packages` dynamic columns; rename `no_truncate` → `truncate` |
| `change_formatters`      | ~20 min | Inline row logic; rename `no_truncate` → `truncate`                                 |
| `backlog_formatters`     | ~30 min | All inline; 3 helpers to extract                                                    |
| `requirement_formatters` | ~30 min | All inline; 3 helpers to extract                                                    |

### 2. DRY helpers to extract

- **`format_tags_cell(tags)`** — `", ".join(tags)` + `[#d79921]` markup repeated 9x
- **`format_date_cell(date, missing="N/A")`** — `strftime` + fallback repeated 6x
- **Consolidate identical column width calculators** — decision/policy/standard share identical `_calculate_column_widths`

### 3. Naming cleanup

- Standardize `no_truncate` → `truncate` in spec_formatters and change_formatters (2 files)

## Estimated effort

~3 hours total for all remaining migrations + DRY helpers.

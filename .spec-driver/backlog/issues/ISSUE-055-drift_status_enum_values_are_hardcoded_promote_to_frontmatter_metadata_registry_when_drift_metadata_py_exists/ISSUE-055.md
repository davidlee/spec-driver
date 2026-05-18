---
id: ISSUE-055
name: drift.status enum_values are hardcoded; promote to FRONTMATTER_METADATA_REGISTRY when drift_metadata.py exists
created: "2026-05-18"
updated: "2026-05-18"
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# drift.status enum_values are hardcoded; promote to FRONTMATTER_METADATA_REGISTRY when drift_metadata.py exists

## Context

DR-137 §5.2 Category B notes that `drift.status` lacks a
`FRONTMATTER_METADATA_REGISTRY` entry today (drift-ledger files have
frontmatter but no registered metadata module). DE-137 keeps the
hardcoded `lambda: sorted(LEDGER_STATUSES)` provider in
`spec_driver/orchestration/enums.py` to avoid expanding the per-kind
metadata surface in this delta.

`improvement.status` and `backlog.status` share the same situation —
both alias `BACKLOG_BASE_STATUSES` and stay hardcoded for now.

## Resolution path

When a future delta adds `drift_metadata.py` (and similarly
`improvement_metadata.py` / a backlog umbrella) under
`supekku/scripts/lib/core/frontmatter_metadata/`, promote these entries
to the derived Category-A view (`_kind_status(kind)`) and remove the
hardcoded `lambda` provider from `ENUM_REGISTRY`. Add the new key to
`enums_test.PRE_SPLIT_SNAPSHOT` to extend VT-CC-012 parity coverage.

## References

- DR-137 §5.2 (Category A/B split, F-17)
- `spec_driver/orchestration/enums.py` Category B section
- `supekku/scripts/lib/drift/models.py::LEDGER_STATUSES`

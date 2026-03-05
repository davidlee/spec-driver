---
id: ISSUE-038
name: list memories --truncate renders status column with file path
created: '2026-03-05'
updated: '2026-03-05'
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# list memories --truncate renders status column with file path

## Summary

`uv run spec-driver list memories --truncate` renders the Status column as
`active[/memory....` — the file path is leaking into the status field, making
the truncated table nearly unreadable.

## Evidence

```
│mem.pattern │active[/memo │pattern  │Project     │high       │p... │2026-03-04│
│.project.wo │ry....       │         │Developm... │           │     │          │
│rkfl...     │             │         │            │           │     │          │
```

The `[/memo` suffix on `active` is the start of a file path that shouldn't be in the
status column at all.

## Impact

- `--truncate` is unusable for the memories table
- Likely a Rich markup/styling issue where the path or styled text is not being
  properly stripped before column width calculation

## Related

- ISSUE-035 (noted as observation)

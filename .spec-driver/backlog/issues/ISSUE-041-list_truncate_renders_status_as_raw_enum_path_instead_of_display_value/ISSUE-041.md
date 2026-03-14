---
id: ISSUE-041
name: list --truncate renders status as raw enum path instead of display value
created: '2026-03-06'
updated: '2026-03-06'
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# list --truncate renders status as raw enum path instead of display value

## Reproduction

```
spec-driver list specs --truncate
```

## Observed

Status column renders as `[spec.status....` — the raw enum/model path is
leaking through truncation instead of the resolved display string.

```
╭────────┬─────────────────┬─────┬────────────────╮
│ID      │Name             │Tags │Status          │
├────────┼─────────────────┼─────┼────────────────┤
│PROD... │streamline sp... │     │[spec.status....│
```

## Expected

Status should render as the resolved value (`draft`, `active`, etc.) and
then truncate normally if the column is too narrow.

## Likely cause

The truncation pass is operating on the raw status object/enum repr rather
than its string display value. The status field is probably being converted
to string _after_ truncation rather than before.

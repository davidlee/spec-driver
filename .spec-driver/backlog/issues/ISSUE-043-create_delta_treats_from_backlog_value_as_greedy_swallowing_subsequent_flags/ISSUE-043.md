---
id: ISSUE-043
name: create delta treats --from-backlog value as greedy, swallowing subsequent flags
created: '2026-03-06'
updated: '2026-03-06'
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# create delta treats --from-backlog value as greedy, swallowing subsequent flags

## Reproduction

```
spec-driver create delta --from-backlog --help
# Error: backlog item '--help' not found
```

`--help` is consumed as the value for `--from-backlog` instead of being
treated as a flag.

## Expected

`--help` should take precedence (standard CLI convention), or at minimum
the `--from-backlog` option should validate that its argument looks like a
backlog item ID before attempting a lookup.

## Notes

This is a Typer/Click limitation with eager options. Low severity since
`create delta --help` works and `--from-backlog` is typically given a real
ID, but it makes the command less discoverable when exploring.


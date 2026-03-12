---
id: ISSUE-052
name: create phase appends duplicate entry to IP phases list and uses inconsistent
  ID format
created: '2026-03-11'
updated: '2026-03-11'
status: open
kind: issue
categories: []
severity: p2
impact: user
---

# create phase appends duplicate entry to IP phases list and uses inconsistent ID format

## Observed

When an IP already has manually-written phase entries (e.g. `IP-004-P01` through
`IP-004-P04`), running `spec-driver create phase` on that IP:

1. Generates a phase with a different ID format (`IP-004.PHASE-01` vs `IP-004-P01`)
2. Appends the new ID to the IP's `phases:` list without detecting the existing
   entries, resulting in duplicates

The agent then has to manually reconcile the phases list every time.

## Expected

- `create phase` should use a single canonical ID format (decide: dotted or hyphenated)
- If the IP already has phase entries, `create phase` should either detect and
  reuse the existing convention or warn about the conflict
- Should not append if an equivalent phase already exists

## Provenance

Observed in [davidlee/ligma](https://github.com/davidlee/ligma) during DE-004
IP-004 phase creation. Reported as recurring ("happens every time").

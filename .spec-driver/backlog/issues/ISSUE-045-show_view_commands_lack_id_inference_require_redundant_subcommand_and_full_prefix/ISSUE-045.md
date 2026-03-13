---
id: ISSUE-045
name: "show/view commands lack ID inference \u2014 require redundant subcommand and full prefix"
created: '2026-03-07'
updated: '2026-03-12'
status: resolved
kind: issue
categories:
  - usability
  - cli
severity: p2
impact: user
---

# show/view commands lack ID inference — require redundant subcommand and full prefix

## Problem

`show` and `view` require the user to specify both the artifact kind as a
subcommand and the full prefixed ID. The ID prefix already encodes the kind,
making the subcommand redundant and the interaction needlessly verbose.

Additionally, bare numeric IDs (without the prefix) are rejected even when
the subcommand already disambiguates the kind.

## Reproduction

```
# These fail — should work
spec-driver show ISSUE-009          # "No such command 'ISSUE-009'"
spec-driver show backlog ISSUE-009  # "No such command 'backlog'"
spec-driver show issue 009          # "issue not found: 009"
spec-driver view ISSUE-009          # "No such command 'ISSUE-009'"

# These work — but are verbose
spec-driver show issue ISSUE-009
spec-driver view issue ISSUE-009
```

## Desired Behaviour

1. **ID-only dispatch**: `show ISSUE-009` / `view ISSUE-009` should infer the
   kind from the ID prefix and route to the correct handler. The prefix-to-kind
   mapping is already known (ISSUE→issue, IMPR→improvement, DE→delta, SPEC→spec,
   ADR→adr, PROD→prod, PROB→problem, RISK→risk, RE→revision, AUD→audit, etc.).

2. **Bare number with subcommand**: `show issue 009` should prepend the prefix
   implied by the subcommand (issue → ISSUE-009).

3. **`show backlog`**: should be an alias that accepts any backlog item ID
   (ISSUE, IMPR, PROB, RISK) — since `list backlog` exists, users expect
   `show backlog` to work symmetrically.

## Scope

Affected commands: `show`, `view`, and potentially `edit` if it has the same
pattern.

The artifact resolver from DE-050 (`supekku/scripts/lib/core/resolve.py` or
equivalent) may already have the ID-to-kind mapping needed. The fix is likely
a thin dispatch layer at the `show`/`view` command group level.

## Related

- DE-050: Registry API normalisation (added `find()` across registries)
- ISSUE-019: Registry API drift (resolved by DE-050)

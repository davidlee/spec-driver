---
id: ISSUE-028
name: 'Inconsistent ID prefix inference across CLI commands (view/show/find)'
created: '2026-02-06'
updated: '2026-02-06'
status: done
kind: issue
categories:
  - cli
  - ux
severity: p3
impact: user
---

# Inconsistent ID prefix inference across CLI commands

## Problem

Some commands intelligently infer artifact prefixes, others require exact IDs:

```bash
s view adr 003   # works - infers ADR-003
s show adr 003   # Error: Decision not found: 003
s find adr 003   # no results
```

## Expected

All commands should consistently infer prefixes when context is unambiguous:
- `show adr 003` → lookup `ADR-003`
- `find adr 003` → search for `ADR-003`
- Same for SPEC, PROD, ISSUE, DE, etc.

## Acceptance Criteria

- [x] `show` command infers prefix from artifact type
- [x] `find` command infers prefix from artifact type
- [x] Consistent behavior across all artifact types (adr, delta, revision, policy, standard)
- [x] Existing exact-ID lookups still work

## Implementation Notes

1. Identify where `view` does prefix inference
2. Extract to shared utility in `core/`
3. Apply to `show` and `find` commands
4. Pattern: if ID is numeric-only or missing expected prefix, prepend it

## References

- `supekku/cli/view.py` - has working prefix inference
- `supekku/cli/show.py` - needs update
- `supekku/cli/find.py` - needs update

---
id: ISSUE-026
name: 'Make sync dry-run/check semantics consistent for ADR/backlog/requirements'
created: '2026-02-06'
updated: '2026-02-06'
status: open
kind: issue
categories:
  - cli
  - sync
severity: p3
impact: user
---

# Make sync dry-run/check semantics consistent for ADR/backlog/requirements

## Summary

Sync mode semantics are inconsistent: `--dry-run` and `--check` flags work for spec sync but are ignored for ADR/backlog/requirements paths.

## Problem

- Core ADR sync works correctly.
- But `sync --dry-run` still mutates files for ADR/backlog/requirements paths.
- There is no `--check` drift-detection path for ADR sync (non-mutating CI mode).

## Current Behavior (Bug)

`sync.py` calls registry sync functions without forwarding `dry_run`:

```python
# sync.py:160
adr_result = _sync_adr(root=root)  # dry_run not passed
```

Same issue for `_sync_backlog()` and `_sync_requirements()`.

**Result**: "dry run" is not dry for these registries.

## Expected Behavior

- `--dry-run` must produce zero writes across all sync targets.
- `--check` must:
  - Detect drift (file/registry mismatch)
  - Exit non-zero when drift exists
  - Emit actionable diff summary
  - Perform no writes

## Acceptance Criteria

- [ ] `sync --dry-run` leaves git tree unchanged for ADR/backlog/requirements
- [ ] `sync --check` exits 0 when clean, non-zero when drift exists
- [ ] `sync --check` output names specific artifacts/fields out of sync
- [ ] Existing `sync` (without flags) behavior unchanged

## Implementation Notes

1. Thread `dry_run` through `_sync_adr`, `_sync_backlog`, `_sync_requirements`
2. Add a check-only execution path (or shared planner) so detection and apply use same logic
3. Add regression tests covering:
   - dry-run no-write guarantee
   - check exit codes
   - representative ADR metadata drift case (summary, tags, new ADR addition)

## References

- `supekku/cli/sync.py` - CLI command implementation
- `supekku/scripts/lib/decisions/registry.py` - DecisionRegistry

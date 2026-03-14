---
id: ISSUE-033
name: sync overwrites requirement status when coverage entries contain unknown statuses
created: '2026-03-05'
updated: '2026-03-09'
status: resolved
kind: issue
categories: [bug, data-integrity]
severity: p2
impact: user
tags: [sync, requirements, coverage, validation]
---

# sync overwrites requirement status when coverage entries contain unknown statuses

## Summary

`_apply_coverage_blocks()` in `RequirementsRegistry` parses coverage entries
without validation. When an entry contains a status not in `VALID_STATUSES`
(e.g. `deferred`), the unknown value flows into `_compute_status_from_coverage()`
where it triggers the mixed-status fallback (`len(statuses) > 1`), silently
downgrading the requirement to `in-progress`.

This happens on every `sync` and `complete delta` invocation, overwriting any
manual correction.

## Root Cause

`VerificationCoverageValidator` correctly rejects unknown statuses, but it is
never invoked during the sync path. The data flow is:

```
_apply_coverage_blocks()
  → load_coverage_blocks()          # parse only, no validation
  → _compute_status_from_coverage() # unknown status corrupts derivation
  → record.status = computed        # silent overwrite
```

## Affected Code

- `supekku/scripts/lib/requirements/registry.py`
  - `_apply_coverage_blocks()` (line ~574): no validation
  - `_compute_status_from_coverage()` (line ~534): no filtering of unknown statuses
- `supekku/scripts/lib/blocks/verification.py`
  - `VALID_STATUSES` (line 24): `{planned, in-progress, verified, failed, blocked}`
  - `VerificationCoverageValidator`: exists but unused during sync

## Impact

- **Data corruption**: derived requirement status silently wrong after every sync
- **Validator contradiction**: `validate` then warns that the (wrongly-derived)
  status doesn't match coverage evidence
- **Closure friction**: `complete delta` calls sync, so the overwrite happens
  during the closure flow

## Proposed Fix

Two layers of defence:

1. **Validate during sync**: `_apply_coverage_blocks()` should run
   `VerificationCoverageValidator` (or at minimum check entry statuses against
   `VALID_STATUSES`). Warn on invalid entries and **exclude them** from status
   derivation.

2. **Defensive filtering**: `_compute_status_from_coverage()` should filter
   entries to only those with statuses in `VALID_STATUSES` before applying
   precedence rules. Unknown statuses must never influence derived state.

## Reported By

External usage report from `../test-driver/` project, observed during DE-003
closure (2026-03-05).

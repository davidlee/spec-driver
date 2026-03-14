---
id: ISSUE-032
name: Requirements registry sync should reconcile coverage_evidence, not just accumulate
created: '2026-03-03'
updated: '2026-03-09'
status: resolved
kind: issue
categories: []
severity: p2
impact: developer
specs: [SPEC-122]
---

# Requirements registry sync should reconcile coverage_evidence, not just accumulate

## Problem

`RequirementsRegistry._apply_coverage_blocks()` unions new coverage artifact IDs into `coverage_evidence` but never removes artifacts that were deleted or invalidated in the source spec's `verification.coverage` block.

This means stale/invalidated verification artifacts persist in the registry indefinitely, causing false warnings from the workspace validator (e.g. "has coverage evidence but status is in-progress").

## Current behavior

```python
# registry.py:675
record.coverage_evidence = sorted(set(record.coverage_evidence) | artefacts)
```

Append-only. Once an artifact ID enters `coverage_evidence`, only manual registry edits can remove it.

## Expected behavior

On sync, `coverage_evidence` should be **replaced** with the current set of artifact IDs from the spec's coverage block — not unioned with the previous set. Artifacts removed from the coverage block should be removed from the registry.

## Impact

- Stale coverage causes validator false positives
- Manual registry edits required to fix (fragile, easy to forget)
- Discovered during routine `spec-driver validate` cleanup

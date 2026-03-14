---
id: IP-087.PHASE-03
slug: 087-cross_artifact_tui_fuzzy_search_with_relational_weighting-phase-03
name: Verification, edge cases, and closure
created: '2026-03-10'
updated: '2026-03-10'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-087.PHASE-03
plan: IP-087
delta: DE-087
objective: >-
  Execute VA-087-001 walkthrough, address edge cases, update verification
  coverage entries, and prepare delta for closure.
entrance_criteria:
  - Phase 02 complete — overlay functional, just check green
exit_criteria:
  - VA-087-001 documented with pass/fail evidence
  - All VT artefacts passing
  - IP-087 verification.coverage entries updated to verified
  - spec-driver complete delta DE-087 succeeds (or force-reason documented)
verification:
  tests:
    - VT-087-001
    - VT-087-002
    - VT-087-003
  evidence:
    - VA-087-001
tasks:
  - id: "3.1"
    summary: VA-087-001 manual walkthrough
  - id: "3.2"
    summary: Edge case review and fixes
  - id: "3.3"
    summary: Update verification coverage and delta artefacts
  - id: "3.4"
    summary: Delta closure
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-087.PHASE-03
```

# Phase 03 — Verification, edge cases, and closure

## 1. Objective

Execute the manual verification walkthrough, address any edge cases found, update verification coverage, and close the delta.

## 2. Links & References

- **Delta**: [DE-087](../DE-087.md)
- **Design Revision**: [DR-087](../DR-087.md)
- **IP**: [IP-087](../IP-087.md)
- **Phase 01**: [phase-01.md](./phase-01.md)
- **Phase 02**: [phase-02.md](./phase-02.md)

## 3. Entrance Criteria

- [ ] Phase 02 complete — overlay functional, `just check` green

## 4. Exit Criteria / Done When

- [ ] VA-087-001 walkthrough documented in notes.md
- [ ] All VT artefacts passing
- [ ] IP-087 `verification.coverage` entries updated to `status: verified`
- [ ] `spec-driver complete delta DE-087` succeeds
- [ ] No outstanding lint warnings on new code

## 5. Verification

- `just check` — full suite
- VA-087-001 walkthrough scenarios:
  - Type partial ID → correct artifact surfaces regardless of type
  - Type tag name → matching artifacts surface
  - Type referenced artifact ID → referencing artifacts surface (below own-ID matches)
  - Empty query → no results (or all results, TBD)
  - Escape → overlay dismisses cleanly
  - Enter on result → browser navigates correctly
  - `Ctrl+F` → per-type search still works

## 7. Tasks & Progress

| Status | ID  | Description                  | Parallel? | Notes                   |
| ------ | --- | ---------------------------- | --------- | ----------------------- |
| [ ]    | 3.1 | VA-087-001 walkthrough       | [ ]       |                         |
| [ ]    | 3.2 | Edge case fixes              | [ ]       | Depends on 3.1 findings |
| [ ]    | 3.3 | Update verification coverage | [P]       |                         |
| [ ]    | 3.4 | Delta closure                | [ ]       | Depends on 3.1-3.3      |

### Task Details

- **3.1 VA-087-001 manual walkthrough**
  - Run the TUI, exercise all walkthrough scenarios from §5
  - Document pass/fail in notes.md with evidence

- **3.2 Edge case fixes**
  - Address any issues found during walkthrough
  - Potential edge cases: empty registries, broken records, very long titles, special characters in tags

- **3.3 Update verification coverage**
  - Set `status: verified` on VT-087-001/002/003 and VA-087-001 in IP-087
  - Update PROD-010/PROD-015 coverage blocks if applicable

- **3.4 Delta closure**
  - `spec-driver complete delta DE-087`
  - If `--force` needed, document reason and create follow-up

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] All verification evidence stored
- [ ] IP-087 progress tracking updated
- [ ] Delta closed

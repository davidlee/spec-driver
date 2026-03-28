---
id: IP-129-P02
slug: "129-requirement_authoring_and_validation_hardening-phase-02"
name: "IP-129 Phase 02 — Sync pruning and summary"
created: "2026-03-28"
updated: "2026-03-28"
status: in-progress
kind: phase
plan: IP-129
delta: DE-129
---

# Phase 2 — Sync Pruning and Summary

## 1. Objective

Add post-relation stale requirement pruning to sync, stamp `source_type = "revision"` on placeholder records, extend `SyncStats`, and add sync summary line with log-level discipline. Pass `SyncStats` into parser functions for warning counting.

## 2. Links & References

- **Delta**: DE-129
- **Design Revision Sections**: DR-129 §1.3, §1.8
- **Specs / PRODs**: SPEC-122.FR-003 (registry load/save), SPEC-122.NF-002 (idempotency)
- **Support Docs**: `supekku/scripts/lib/requirements/sync.py`, `supekku/scripts/lib/requirements/registry.py`

## 3. Entrance Criteria

- [ ] Phase 1 complete (parser hardening)
- [ ] All parser tests passing

## 4. Exit Criteria / Done When

- [ ] `SyncStats.pruned` and `SyncStats.warnings` fields added
- [ ] `spec_extractions: dict[str, set[str]]` collected during both extraction paths
- [ ] Post-relation pruning pass implemented (after step 5)
- [ ] `source_type = "revision"` stamped in `_create_placeholder_record()`
- [ ] `SyncStats` passed into parser functions; warning counter incremented
- [ ] Summary line emitted at end of sync (warning level when issues exist, info otherwise)
- [ ] Per-item diagnostics at `logger.info()` level
- [ ] Idempotency preserved (re-run produces no changes)
- [ ] All sync tests pass, lint clean

## 5. Verification

- `uv run pytest supekku/scripts/lib/requirements/sync_test.py -v`
- `uv run pytest supekku/scripts/lib/requirements/models_test.py -v`
- `just check`

## 6. Assumptions & STOP Conditions

- Assumptions: The five-step sync ordering (spec extraction → relationships → delta relations → revision blocks → coverage) is stable and matches current code.
- STOP when: If sync flow has changed since DR was written, re-verify ordering before implementing pruning pass.

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 2.1 | Add `pruned` and `warnings` to `SyncStats` | [P] | models.py, trivial |
| [ ] | 2.2 | Stamp `source_type = "revision"` in `_create_placeholder_record()` | [P] | sync.py, 2 lines |
| [ ] | 2.3 | Collect `spec_extractions` during both extraction paths | | sync.py / registry.py |
| [ ] | 2.4 | Post-relation pruning pass | | After 2.3; DR §1.3 |
| [ ] | 2.5 | Pass `SyncStats` into parser functions | | Wire warning counting |
| [ ] | 2.6 | Sync summary line with log-level discipline | | After 2.4 + 2.5 |
| [ ] | 2.7 | Code comments: `seen` vs `spec_extractions` distinction | | Per ext. review F10 |
| [ ] | 2.8 | Unit tests | | After 2.1–2.7 |
| [ ] | 2.9 | Lint + existing test pass | | Final gate |

### Task Details

- **2.3 Collect `spec_extractions`**
  - **Files**: `supekku/scripts/lib/requirements/sync.py` (and/or `registry.py` depending on where extraction loops live)
  - **Approach**: Both the `spec_registry` path and `spec_dirs` fallback path must populate `spec_extractions[spec_id] = set(extracted_uids)`. Respect the existing `yielded_ids` dedup guard.
  - **Key concern**: Verify which file owns the extraction loop. If `registry.py:sync()`, changes go there. The DR targets sync.py but the actual loop location needs confirmation at implementation time.

- **2.4 Post-relation pruning pass**
  - **Files**: Same as 2.3
  - **Approach**: After all five sync stages, iterate `spec_extractions`. For each `(spec_id, extracted_uids)`, find records where `primary_spec == spec_id AND uid not in extracted_uids AND not rec.introduced`. Delete and count.
  - **Testing**: (a) deleted requirement → pruned; (b) revision-introduced → preserved; (c) revision-moved → not pruned from old spec (primary_spec already updated by step 4); (d) backlog-sourced → not pruned; (e) re-run → idempotent

- **2.6 Summary line**
  - **Files**: sync.py
  - **Approach**: After all steps including pruning, emit summary: `Sync complete: N created, N updated, N pruned, N warnings`. If warnings > 0, emit at `logger.warning()`; otherwise `logger.info()`.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| Pruning race with revision moves | Post-relation ordering (DR §1.3, ext. review F1) | Mitigated by design |
| Both extraction paths missed | Task 2.3 explicitly covers both; ext. review F9 | Open |

## 9. Decisions & Outcomes

- 2026-03-28 — Auto-prune (no flag), `introduced` guard, post-relation ordering

## 10. Findings / Research Notes

(To be filled during implementation — verify sync flow ordering against actual code)

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to phase 3

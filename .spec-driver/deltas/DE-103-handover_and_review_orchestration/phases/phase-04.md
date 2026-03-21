---
id: IP-103.PHASE-04
slug: "103-handover_and_review_orchestration-phase-04"
name: "IP-103 Phase 04 — Review commands"
created: "2026-03-21"
updated: "2026-03-21"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-103.PHASE-04
plan: IP-103
delta: DE-103
objective: >-
  Implement review prime, review complete, and review teardown CLI commands
  with staleness/invalidation lifecycle per DR-102 §3.3, §3.4, §5, §8.
entrance_criteria:
  - Phase 03 complete (handoff commands working, 96 workflow tests passing)
exit_criteria:
  - review prime generates review-index.yaml + review-bootstrap.md
  - review complete writes review-findings.yaml and transitions state
  - review teardown deletes reviewer state files respecting session_scope policy
  - staleness/invalidation lifecycle enforced per DR-102 §8
  - all new code lint-clean (ruff)
  - all existing tests still passing
verification:
  tests:
    - VT-103-005 staleness/invalidation/reusability lifecycle
  evidence: []
tasks:
  - id: "4.1"
    summary: "Review I/O module (review_io.py) — read/write/build for review-index and review-findings"
  - id: "4.2"
    summary: "Git diff helper — get_changed_files(from_ref, to_ref)"
  - id: "4.3"
    summary: "Staleness evaluator — evaluate bootstrap_status from cache_key vs current state"
  - id: "4.4"
    summary: "CLI: review prime command"
  - id: "4.5"
    summary: "CLI: review complete command"
  - id: "4.6"
    summary: "CLI: review teardown command"
risks:
  - id: R1
    summary: "review prime complexity — domain_map assembly, staleness, bootstrap markdown"
    mitigation: "Split into small testable functions; test each independently"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-103.PHASE-04
```

# Phase 04 — Review Commands

## 1. Objective

Implement `review prime`, `review complete`, and `review teardown` CLI
commands with staleness/invalidation lifecycle per DR-102 §3.3, §3.4, §5, §8.

## 2. Links & References

- **Delta**: DE-103
- **Design Revision Sections**: DR-102 §3.3 (review-index), §3.4 (review-findings), §5 (CLI commands), §8 (lifecycle/invalidation), §9 (workflow.toml)
- **Specs / PRODs**: PROD-011
- **Existing patterns**: `handoff_io.py` (I/O module pattern), `workflow.py` (CLI pattern)

## 3. Entrance Criteria

- [x] Phase 03 complete (handoff commands working)
- [x] 77 workflow tests passing (96 total including schema tests)
- [x] review-index and review-findings schemas already registered (Phase 01)

## 4. Exit Criteria / Done When

- [x] `review prime` generates `review-index.yaml` + `review-bootstrap.md`
- [x] `review complete` writes `review-findings.yaml` and transitions state
- [x] `review teardown` deletes reviewer state files respecting policy
- [x] Staleness evaluation works per DR-102 §8
- [x] All tests passing, ruff clean

## 5. Verification

- `uv run python -m pytest supekku/scripts/lib/workflow/ supekku/cli/workflow_review_test.py -q`
- `uv run ruff check supekku/scripts/lib/workflow/ supekku/cli/workflow.py`

## 6. Assumptions & Design Decisions

**Resolved from notes assessment:**

1. **review prime complexity** — Split into: (a) `review_io.py` for I/O, (b) `staleness.py` for cache evaluation, (c) `bootstrap.py` for markdown generation. Each independently testable.

2. **review complete findings I/O** — Follow handoff_io pattern. Round number read from existing findings file (default 1 if none). Finding IDs are round-scoped (`R3-001`) per DEC-103-001.

3. **review teardown policy gating** — Read `[review].session_scope` and `[review].teardown_on` from config. Delete review-index, review-findings, review-bootstrap.md. Only teardown when conditions match policy.

4. **operations.py** — Continue the current pattern (domain logic in dedicated modules, CLI as thin orchestration). Not blocking.

5. **Placeholder renderers** — Not needed for Phase 04. review commands write YAML directly via I/O modules, don't need block renderers.

**Diff-base selection for review prime:**
- New cache: use current HEAD (reviewer sees all files in the delta's touched areas)
- Existing stale cache: diff from `staleness.cache_key.head` to current HEAD
- This avoids merge-base complexity. The domain_map lists files the reviewer should know about, not a diff. For the initial implementation, `review prime` accepts explicit `--files` or assembles from state/handoff context. Full git-diff-based domain_map construction is a refinement that can be added incrementally.

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
| ------ | --- | ----------- | ----- |
| [x]    | 4.1 | Review I/O module | 24 tests — read/write/build for review-index + review-findings |
| [x]    | 4.2 | Staleness evaluator | 16 tests — evaluate bootstrap_status from cache_key |
| [x]    | 4.3 | CLI: review prime | generates review-index.yaml + review-bootstrap.md |
| [x]    | 4.4 | CLI: review complete | writes review-findings.yaml, transitions state |
| [x]    | 4.5 | CLI: review teardown | deletes reviewer state files |
| [x]    | 4.6 | Integration verification | 21 CLI tests cover full lifecycle |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| review prime complexity | Split into small testable functions | active |
| Schema validation edge cases | Reuse existing validator; test boundary cases | active |

## 9. Decisions & Outcomes

- `2026-03-21` — Diff-base: use HEAD for new cache, cache_key.head→HEAD diff for stale cache. Avoid merge-base complexity.
- `2026-03-21` — Domain map: accept explicit files list for initial impl; git-diff-based assembly deferred.
- `2026-03-21` — Continue dedicated I/O module pattern (not operations.py).

## 10. Findings / Research Notes

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to next phase

---
id: IP-027.PHASE-02
slug: 027-contract_mirror_tree_index-phase-02
name: IP-027 Phase 02 - Sync integration and polish
created: '2026-02-20'
updated: '2026-02-20'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-027.PHASE-02
plan: IP-027
delta: DE-027
objective: >-
  Wire ContractMirrorTreeBuilder into sync CLI, add .gitignore entry, write
  VT-CONTRACT-MIRROR-003 tests for write confinement and stale view cleanup.
entrance_criteria:
  - Phase 1 complete (builder + mapping + tests)
exit_criteria:
  - sync CLI invokes mirror builder after index rebuild
  - .contracts/ in .gitignore
  - VT-CONTRACT-MIRROR-003 tests passing
  - Full test suite green, linters clean
verification:
  tests:
    - VT-CONTRACT-MIRROR-003
  evidence: []
tasks:
  - id: "2.1"
    description: Wire mirror builder into sync CLI
    status: complete
  - id: "2.2"
    description: Add .contracts/ to .gitignore
    status: complete
  - id: "2.3"
    description: Write VT-CONTRACT-MIRROR-003 tests
    status: complete
  - id: "2.4"
    description: Final lint and test
    status: complete
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-027.PHASE-02
```

# Phase 2 - Sync integration and polish

## 1. Objective

Wire `ContractMirrorTreeBuilder` into `sync` CLI, ensure `.contracts/` is gitignored,
and add write-confinement verification tests.

## 2. Links & References

- **Delta**: [DE-027](../DE-027.md)
- **Design Revision**: [DR-027](../DR-027.md) — sync integration (code_impacts)
- **Specs**: PROD-014.FR-005 (rebuild cleans stale), PROD-014.NF-002 (.gitignore safe)
- **Phase 1**: [phase-01.md](./phase-01.md)

## 3. Entrance Criteria

- [x] Phase 1 complete (builder + mapping + 44 tests)

## 4. Exit Criteria / Done When

- [x] `sync` CLI invokes `ContractMirrorTreeBuilder.rebuild()` after index rebuild
- [x] `.contracts/` entry in `.gitignore`
- [x] VT-CONTRACT-MIRROR-003 tests (write confinement, stale view cleanup)
- [x] Full test suite green (1648 pass)
- [x] Linters clean (ruff + pylint 10/10 on new files)

## 5. Verification

- `just test` — 1648 pass, 3 skipped, 0 failures
- `just lint` — ruff clean
- `just pylint` — 10/10 on new files; sync.py pre-existing warnings unchanged
- VT-CONTRACT-MIRROR-003: `test_write_confinement`, `test_rebuild_removes_all_stale_views`

## 6. Assumptions & STOP Conditions

- None; straightforward integration.

## 7. Tasks & Progress

| Status | ID  | Description                        | Parallel? | Notes                           |
| ------ | --- | ---------------------------------- | --------- | ------------------------------- |
| [x]    | 2.1 | Wire mirror builder into sync CLI  |           | 6 lines in \_sync_specs         |
| [x]    | 2.2 | Add .contracts/ to .gitignore      | [P]       |                                 |
| [x]    | 2.3 | Write VT-CONTRACT-MIRROR-003 tests |           | write confinement + stale views |
| [x]    | 2.4 | Final lint and test                |           | 1648 pass, linters clean        |

## 8. Risks & Mitigations

None materialised.

## 9. Decisions & Outcomes

- 2026-02-20 — Lazy import in `_sync_specs` follows existing pattern (other imports in same function are also lazy).

## 10. Findings / Research Notes

- sync.py pylint warnings are all pre-existing (complexity, too-many-arguments, etc.).

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] No further phases needed

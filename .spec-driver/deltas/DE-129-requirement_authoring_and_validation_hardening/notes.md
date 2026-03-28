# Notes for DE-129

## Summary

Requirement authoring and validation hardening — 9 changes across parser, sync, validator, show, and memory to catch requirement authoring errors at sync/validate time instead of months downstream.

Motivated by a client-repo postmortem (138-requirement migration, 60 validation errors). DR-129 approved after two passes of external adversarial review.

## Progress

- **Phase 1 — Parser hardening**: ✅ Complete
  - `_has_frontmatter_requirement_definitions()` — detects definition-shaped arrays in frontmatter
  - Collision tracking via `seen_uids` in `_records_from_content()`
  - Mismatch threshold relaxed: `== 0` → `<`
  - `count_requirement_like_lines()` public API
  - 15 new tests, 45/45 passing, lint clean
  - Commit: `feat(DE-129): parser hardening`

- **Phase 2 — Sync pruning + summary**: 🔲 Next
- **Phase 3 — Validator, show, memory**: 🔲 Pending

## Key Design Decisions (from DR-129)

- **Pruning runs post-relation** — after all 5 sync stages, not inside per-spec loop. Critical to avoid race with revision moves (ext. review F1).
- **`source_type = "revision"` stamp** — prerequisite for §1.6 validator check. 2-line change in `_create_placeholder_record()`.
- **Both extraction paths** must populate `spec_extractions` dict (ext. review F9).
- **`seen` vs `spec_extractions`** serve different purposes — code comment needed (ext. review F10).
- **Per-item diagnostics at `logger.info()`**, summary at `logger.warning()` (ext. review F3).
- **Bare-ID check fires for all artifact types** — no `expected_type` gate (ext. review F11).
- **Stats passing**: `SyncStats` passed into parser functions for warning counting.

## Open Concerns for Phase 2

- Verify the 5-step sync ordering matches current code before implementing pruning pass.
- Confirm which file owns the extraction loop — sync.py vs registry.py.
- `source_type` field must be persisted to registry YAML — confirm this during implementation.

---

## New Agent Instructions

### Task Card

**Delta**: DE-129 — Requirement authoring and validation hardening
**Notes**: `.spec-driver/deltas/DE-129-requirement_authoring_and_validation_hardening/notes.md` (this file)
**Delta file**: `.spec-driver/deltas/DE-129-requirement_authoring_and_validation_hardening/DE-129.md`

### Required Reading (in order)

1. DR-129 — `.spec-driver/deltas/DE-129-requirement_authoring_and_validation_hardening/DR-129.md`
   - §1.3 (sync pruning — post-relation ordering, safety invariants)
   - §1.8 (summary line, log-level discipline, stats passing)
   - §6 (adversarial review findings — especially F1, F8, F9, F10)
2. Phase 2 sheet — `.spec-driver/deltas/DE-129-requirement_authoring_and_validation_hardening/phases/phase-02.md`
3. Phase 1 sheet — `.spec-driver/deltas/DE-129-requirement_authoring_and_validation_hardening/phases/phase-01.md` (for context on what's done)

### Key Files

- `supekku/scripts/lib/requirements/sync.py` — main implementation target
- `supekku/scripts/lib/requirements/registry.py` — may own the extraction loop; verify before implementing
- `supekku/scripts/lib/requirements/models.py` — `SyncStats` dataclass (add `pruned`, `warnings`)
- `supekku/scripts/lib/requirements/parser.py` — phase 1 changes landed here; parser functions will receive `SyncStats` for warning counting
- `supekku/scripts/lib/requirements/sync_test.py` — test target

### Relevant Memories

- `mem.concept.spec-driver.requirement-lifecycle` — canonical requirement lifecycle guidance
- `mem.fact.spec-driver.requirement-bundle-files` — supplemental files not consumed by sync

### Relevant Doctrines

- POL-001 (reuse), POL-003 (module boundaries), ADR-008 (normative vs observed)
- Commit policy: frequent small commits, `.spec-driver/**` changes can go with code or separately

### User Decisions Already Made

- Auto-prune on sync (no flag), `introduced` field is exemption guard
- Post-relation pruning ordering (after all 5 sync stages)
- `source_type = "revision"` stamp in `_create_placeholder_record()`
- `SyncStats` passed into parser functions for warning counting (option b from structural observation)
- Per-item diagnostics at `logger.info()`, summary at `logger.warning()`

### Pending Commit State

- All `.spec-driver/**` changes committed
- All code changes committed
- Worktree is clean

### Advice for Next Agent

- The extraction loop location is the first thing to verify. `sync.py` has `_sync_backlog_requirements` and helper functions, but the main spec-extraction loop may be in `registry.py`. Read both before implementing.
- The 5-step sync ordering (spec extraction → relationships → delta relations → revision blocks → coverage) is the foundation of the pruning design. If the ordering has changed, stop and consult.
- The revision-move test (phase 2, task 2.4 test case (c)) is the most important test — it directly validates the ext. review F1 fix.

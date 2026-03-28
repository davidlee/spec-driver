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

- **Phase 2 — Sync pruning + summary**: ✅ Complete
  - `SyncStats.pruned` and `SyncStats.warnings` fields added to models.py
  - `source_type = "revision"` stamped in `_create_placeholder_record()`
  - `spec_extractions` collected during both extraction paths in `registry.py`
  - Post-relation pruning pass after coverage blocks (not inside per-spec loop)
  - `SyncStats` passed into parser functions for warning counting
  - Summary line with log-level discipline (info when clean, warning when issues)
  - Code comments: `seen` vs `spec_extractions` distinction (ext. review F10)
  - 14 new tests, 51 total sync tests, 4614 full suite passing, lint clean
  - Key finding: extraction loop lives in `registry.py`, not `sync.py`
  - Commit: `feat(DE-129): sync pruning, source_type stamp, summary line, stats wiring`

- **Phase 3 — Validator, show, memory**: 🔲 Next

## Key Design Decisions (from DR-129)

- **Pruning runs post-relation** — after all 5 sync stages, not inside per-spec loop. Critical to avoid race with revision moves (ext. review F1).
- **`source_type = "revision"` stamp** — prerequisite for §1.6 validator check. 2-line change in `_create_placeholder_record()`.
- **Both extraction paths** must populate `spec_extractions` dict (ext. review F9).
- **`seen` vs `spec_extractions`** serve different purposes — code comment needed (ext. review F10).
- **Per-item diagnostics at `logger.info()`**, summary at `logger.warning()` (ext. review F3).
- **Bare-ID check fires for all artifact types** — no `expected_type` gate (ext. review F11).
- **Stats passing**: `SyncStats` passed into parser functions for warning counting.

## Phase 2 Resolved Concerns

- ✅ **5-step sync ordering confirmed** — matches DR. Actual flow: spec extraction → relationships → delta relations → revision relations + blocks → audit relations → backlog → coverage. Audit + backlog are intermediate steps that don't affect `primary_spec`.
- ✅ **Extraction loop lives in `registry.py`** (`RequirementsRegistry.sync()`), not `sync.py`. Both extraction paths (spec_registry and spec_dirs) are in `sync()`.
- ✅ **`source_type` already persisted** to YAML via `to_dict()`/`from_dict()` — no additional work needed.

## Open Concerns for Phase 3

- Validator checks go in `WorkspaceValidator` (DE-119 hasn't landed).
- `re` import needed in validator.py for compiled regex constants.
- Show zero-entry hint: confirm how `show spec` currently computes registry counts.

---

## New Agent Instructions

Invoke `/execute-phase` for DE-129 Phase 3 (Validator, show, memory).

### Task Card

**Delta**: DE-129 — Requirement authoring and validation hardening
**Notes**: `.spec-driver/deltas/DE-129-requirement_authoring_and_validation_hardening/notes.md` (this file)
**Delta file**: `.spec-driver/deltas/DE-129-requirement_authoring_and_validation_hardening/DE-129.md`

### Required Reading (in order)

1. DR-129.md §1.4 (bare-ID warning), §1.5 (implements-target-kind), §1.6 (revision-introduced invariant), §1.7 (show zero-entry hint), §1.9 (memory update)
   - Path: `.spec-driver/deltas/DE-129-requirement_authoring_and_validation_hardening/DR-129.md`
2. Phase 3 sheet — `.spec-driver/deltas/DE-129-requirement_authoring_and_validation_hardening/phases/phase-03.md`
3. This file — "Open Concerns for Phase 3" section above

### Key Files

- `supekku/scripts/lib/validation/validator.py` — bare-ID warning, implements-target-kind, revision-introduced invariant
- `supekku/cli/show.py` + `supekku/scripts/lib/formatters/spec_formatters.py` — zero-entry hint
- `.spec-driver/memory/mem.concept.spec-driver.requirement-lifecycle.md` — memory to update with Common Pitfalls section

### Relevant Memories

- `mem.concept.spec-driver.requirement-lifecycle` — canonical requirement lifecycle guidance (target for §1.9 update)
- `mem.fact.spec-driver.requirement-bundle-files` — supplemental files not consumed by sync

### Relevant Doctrines

- POL-001 (reuse), POL-002 (no magic strings — compiled regex constants), POL-003 (module boundaries)
- D9: New validator checks go in `WorkspaceValidator`, not `diagnostics/checks/` (DE-119 hasn't landed)

### User Decisions Already Made

- Bare-ID check is warning, not error; targets FR/NF-shaped IDs only; fires for all artifact types (D5, ext. review F11)
- Implements-target-kind fires *instead of* generic "not found" for spec-shaped targets (D5)
- Revision-introduced invariant uses `source_type == "revision"` (stamped in Phase 2) + `not record.introduced` (D6, ext. review F7/F8)
- Show zero-entry hint is simple info note, no body parsing, no threshold (D7, ext. review F2)
- Compiled constants: `_BARE_REQUIREMENT_PATTERN`, `_SPEC_ID_PATTERN` (POL-002)

### Pending Commit State

- Worktree is clean. All Phase 2 code and `.spec-driver/**` changes committed.
- Phase 2 handoff emitted via `spec-driver phase complete DE-129`.

### Incomplete Work / Loose Ends

- None from Phase 2. All 9 tasks complete, all exit criteria met.
- Phase 3 is the final phase. After Phase 3, DE-129 is ready for audit and closure.

### Advice for Next Agent

- The `_validate_change_relations()` method in `validator.py` is the main target for tasks 3.2 and 3.3. Read it carefully before implementing — the applies_to loop and relation loop are separate code paths.
- For task 3.4 (revision-introduced invariant): this iterates `requirements.records`, not change relations. It's a separate loop in `WorkspaceValidator.validate()`.
- For task 3.5 (show zero-entry hint): check how `show spec` currently sources requirement counts. The formatter may already receive registry data — the hint may be a simple conditional in the formatter.
- The `source_type = "revision"` stamp is confirmed working (Phase 2 test `TestPlaceholderRecordSourceType`). Task 3.4 can rely on it.
- Phase 3 is the final phase. After completing it, proceed to `/audit-change` then `/close-change`.

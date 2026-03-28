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

- **Phase 3 — Validator, show, memory**: ✅ Complete
  - `_BARE_REQUIREMENT_PATTERN` and `_SPEC_ID_PATTERN` compiled regex constants (POL-002)
  - Bare-ID warning in `_validate_change_relations()` applies_to loop — fires for all artifact types
  - Implements-target-kind check: `implements → SPEC-012` emits specific guidance instead of generic error
  - Revision-introduced invariant: `source_type=revision` + no `introduced` → warning
  - Zero-entry hint in `show spec` via `_format_requirements_summary(registry_empty_hint=True)`
  - Memory updated: Common Pitfalls section in `mem.concept.spec-driver.requirement-lifecycle`
  - 14 new tests (4 bare-ID, 3 implements-target, 3 revision-invariant, 3 show-hint, 1 NF bare-ID)
  - 4711 full suite passing, ruff + pylint clean (no new issues)
  - Commit: `feat(DE-129): validator checks, show zero-entry hint, memory pitfalls (phase 3)`

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

## Next Steps

All 3 phases complete. DE-129 is ready for `/audit-change` then `/close-change`.

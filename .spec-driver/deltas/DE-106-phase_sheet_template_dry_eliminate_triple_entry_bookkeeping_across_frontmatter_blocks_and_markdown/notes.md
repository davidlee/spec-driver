# Notes for DE-106

## New Agent Instructions

### Task Card

**DE-106** — Phase sheet template DRY: eliminate triple-entry bookkeeping across frontmatter, blocks, and markdown.

Status: `in-progress`. Phase 1 complete. Phase 2 next.

### Required Reading (in order)

1. [notes.md](./notes.md) — this file
2. [IP-106](./IP-106.md) — implementation plan with 3 phases, verification coverage
3. [DR-106](./DR-106.md) — approved design revision (3 review passes, 14 findings integrated). **Start with §3a (field analysis) and §9 (rollout sequencing).**
4. [Phase 01](./phases/phase-01.md) — completed phase, read §9 Decisions for Pydantic go decision

### Related Documents

- [DE-106](./DE-106.md) — delta scope
- [IMPR-022](../../backlog/improvements/IMPR-022-phase_sheet_template_dry_eliminate_triple_entry_bookkeeping_across_frontmatter_blocks_and_markdown/IMPR-022.md) — source backlog item
- [DE-107](../DE-107-spike_evaluate_pydantic_for_model_layer/DE-107.md) — Pydantic spike (Phase 1 served as its feasibility test; go decision made)
- [autobahn.md](/workspace/spec-driver/autobahn.md) — orchestration layer brief that informed field analysis

### Key Files (implementation surface)

| File | Role | Phase 1 status |
|---|---|---|
| `supekku/scripts/lib/changes/phase_model.py` | **NEW** — PhaseSheet Pydantic model | ✅ Done |
| `supekku/scripts/lib/changes/phase_model_test.py` | Model tests (9 tests incl. corpus) | ✅ Done |
| `supekku/scripts/lib/changes/creation.py` | `create_phase()` — emits canonical frontmatter fields | ✅ Done |
| `supekku/scripts/lib/changes/artifacts.py` | Phase loading — prefers frontmatter, falls back to blocks | ✅ Done |
| `supekku/templates/phase.md` | Phase template — **needs block scaffolding removed (Phase 2)** | Pending |
| `supekku/scripts/lib/formatters/change_formatters.py` | `_enrich_phase_data()` — **verify regex fallback after block removal (Phase 2)** | Pending |
| `supekku/scripts/lib/validation/validator.py` | Phase validation — **remove overview-block warning for new phases (Phase 3)** | Pending |
| `supekku/scripts/lib/core/frontmatter_schema.py` | Frontmatter validation — **wire phase-specific validation (Phase 3)** | Pending |
| `supekku/skills/execute-phase/SKILL.md` | Skill — **audit for block references (Phase 3)** | Pending |
| `supekku/skills/plan-phases/SKILL.md` | Skill — **audit for block references (Phase 3)** | Pending |
| `supekku/skills/update-delta-docs/SKILL.md` | Skill — **audit for block references (Phase 3)** | Pending |
| `supekku/skills/notes/SKILL.md` | Skill — **audit for block references (Phase 3)** | Pending |

### Relevant Memories

- `mem.pattern.spec-driver.create-phase-convention` — phase creation ID handling
- `mem.pattern.spec-driver.frontmatter-compaction` — FieldMetadata persistence annotations
- `mem.concept.spec-driver.plan` — IP/phase structure and commands

### Relevant Doctrine

- **ADR-004**: delta-first canonical loop; spec reconciliation after implementation
- **ADR-009**: no speculative structure for future registries
- **POL-001**: maximise reuse, minimise sprawl
- **POL-002**: no magic strings
- **STD-002**: lint compliance

### Key User Decisions

- **Pydantic go**: 37ms import, all legacy phases parse cleanly. PhaseSheet model is production-ready.
- **Canonical field set (DEC-005)**: `plan`, `delta`, `objective`, `entrance_criteria`, `exit_criteria`. Verification, tasks, risks are markdown-only. See "Accepted Structured Data Losses" below.
- **Contract vs progress (DEC-006)**: frontmatter = planning contract; markdown checkboxes = execution progress. Never conflate in structured data.
- **Tracking block dropped (DEC-007)**: regex checkbox fallback handles task stats. Criteria enrichment is dead code (no display consumer).
- **Compatibility (OQ-001)**: frontmatter wins, block fallback for legacy, never merge. No bulk migration.
- **Spec reconciliation (OQ-003)**: PROD-006 updated within DE-106 after implementation, before closure. Bounded but semantic (not mechanical).

### What Phase 1 Delivered

- `PhaseSheet` Pydantic model (`phase_model.py`)
- `create_phase()` emits `plan`, `delta`, `objective`, `entrance_criteria`, `exit_criteria` in frontmatter
- `artifacts.py` reads phase data from frontmatter first, falls back to `phase.overview` blocks
- `show delta` works for both new-format and legacy phases
- 13 new tests, 591 total passing, lint clean

### Phase 2 Scope (next)

**Template + formatter + remaining compatibility.** Per IP-106 and DR-106 §9:

1. Update `supekku/templates/phase.md` — remove `{{ phase_overview_block }}` and `{{ phase_tracking_block }}` template variables. Template should emit frontmatter + markdown body only.
2. Update `creation.py` — stop calling `render_phase_overview_block()` and `render_phase_tracking_block()`. The frontmatter population (done in Phase 1) replaces them.
3. Verify `change_formatters.py` regex fallback works end-to-end after block removal.
4. Verify `list_changes` reads canonical frontmatter fields.
5. Update `validator.py` — suppress the "Missing phase.overview block" warning for new-format phases (those with `plan`+`delta` in frontmatter).

### Phase 3 Scope (after Phase 2)

Validation + ADR + skills + spec reconciliation + memories + backlog items.

### Loose Ends / Watch Items

- `create_phase()` still emits both blocks AND frontmatter (Phase 1 was additive). Phase 2 removes the block emission.
- Phase 01's phase sheet itself has both blocks and frontmatter (written before the code change). This is fine — it's a legacy-format phase that works via the frontmatter path since we manually added canonical fields.
- The existing `test_create_phase_copies_criteria_from_plan` test checks for block content in the phase body. It will need updating in Phase 2 when blocks are removed.

### Commit State

Worktree is clean. All `.spec-driver/**` changes committed. No pending commits needed.

---

## Accepted Structured Data Losses

These fields lose structured (YAML) representation. All are intentional per DR-106 DEC-005/DEC-006/DEC-007. If orchestration or tooling later needs any of these, it gets modeled as a deliberate feature with proper schema — not recovered by reinstating the blocks.

| Field | Was in | Loss | Why acceptable |
|---|---|---|---|
| Task status (per-task `pending`/`in_progress`/`completed`/`blocked`) | `phase.tracking` | Per-task granularity; regex fallback gives aggregate `[x]`/`[ ]` counts only | Highest-volatility field; primary drift source. Display table already renders aggregates — richer data was maintained but never surfaced. |
| Criteria progress (`completed: true/false` per criterion) | `phase.tracking` | Structured criterion-level completion | `_enrich_phase_data()` materializes this but no display surface reads it — dead code from a display perspective. |
| Verification (test commands, evidence items) | `phase.overview` | Structured test-command and evidence lists | No requirement linkage — IP-level `verification.coverage` owns formal VT/VA/VH traceability. Phase verification is an ad-hoc checklist with no consumer or status model. |
| Tasks (summary list) | `phase.overview` | Structured task list in YAML | Redundant with markdown §7 table + detail blocks that agents actually maintain. |
| Risks (summary list) | `phase.overview` | Structured risk list in YAML | No machine consumer. No gate-checking value. Delta-level risks are the structured surface. |
| Files (references, added, modified) | `phase.tracking` | Structured file-change tracking per task | Agent working notes with no consumer. |

## Design Review Summary

- **OQ-001**: Compatibility now, opportunistic migration later
- **OQ-002**: Canonical fields: `plan`, `delta`, `objective`, `entrance_criteria`, `exit_criteria`
- **OQ-003**: Follow ADR-004 — spec reconciliation after implementation
- **OQ-004**: Phase model is the Pydantic spike (DEC-008); go decision made
- **Internal review**: 8 findings (R1-R8), all integrated
- **External review**: 6 findings (E1-E6), all integrated
- **Doctrine outputs planned**: ADR (placement heuristic), 3 memories, 4 skill updates

# Notes for DE-106

## Phase 3 Completion Summary

Phase 3 delivered all exit criteria:

1. **Validation wired**: PhaseSheet Pydantic model validates new-format phase frontmatter in `validator.py`
2. **ADR-010 landed**: Default placement heuristic for structured artifact metadata (accepted)
3. **Skills audited**: All 4 target skills already clean of block references — no updates needed
4. **PROD-006 reconciled**: FR-001, FR-005, capabilities, data contracts, verification coverage updated
5. **3 memories created**: `mem.pattern.phase.contract-vs-progress`, `mem.pattern.phase.canonical-fields`, `mem.pattern.phase.frontmatter-block-precedence`
6. **2 backlog items captured**: IMPR-023 (bulk migration), IMPR-024 (kind-aware validation)
7. **636 relevant tests passing**, lint clean

All 3 phases complete. Delta ready for audit and closure.

---

## Phase 2 Completion Summary

Phase 2 delivered all 5 exit criteria:

1. **Template cleaned**: `phase.md` no longer contains `{{ phase_overview_block }}` or `{{ phase_tracking_block }}`
2. **Creation cleaned**: `create_phase()` no longer calls block rendering functions; frontmatter is sole structured source
3. **Regex fallback verified**: `_enrich_phase_data()` regex handles new-format phases (412 formatter tests pass)
4. **list_changes verified**: delegates to `PhaseSheet` via `load_change_artifact()` (Phase 1 work)
5. **Validator updated**: no warning for phases with `plan`+`delta` in frontmatter (11 phase validator tests pass)

**Files changed**: `supekku/templates/phase.md`, `supekku/scripts/lib/changes/creation.py`, `supekku/scripts/lib/changes/creation_test.py`, `supekku/scripts/lib/validation/validator.py`, `supekku/scripts/lib/validation/validator_test.py`

**Tests**: 635 relevant tests passing (31 creation, 412 formatter, 179 changes, 11 phase validation, + others). 1 pre-existing unrelated failure in `package_utils_test.py`.

---

## New Agent Instructions

### Task Card

**DE-106** — Phase sheet template DRY: eliminate triple-entry bookkeeping across frontmatter, blocks, and markdown.

Status: `in-progress`. All 3 phases complete. Ready for audit and closure.

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
| `supekku/templates/phase.md` | Phase template — block scaffolding removed | ✅ Done (Phase 2) |
| `supekku/scripts/lib/formatters/change_formatters.py` | `_enrich_phase_data()` — regex fallback verified | ✅ Done (Phase 2) |
| `supekku/scripts/lib/validation/validator.py` | Phase validation — overview-block warning suppressed for new phases | ✅ Done (Phase 2) |
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

### Phase 2 (complete)

All 5 deliverables done. See "Phase 2 Completion Summary" above.

### Phase 3 Scope (next)

Validation + ADR + skills + spec reconciliation + memories + backlog items. Per IP-106:

1. Wire phase frontmatter validation via Pydantic model or inline fallback
2. Land ADR (scoped to DE-106-derived placement heuristic)
3. Audit and update skills: `execute-phase`, `plan-phases`, `update-delta-docs`, `notes`
4. Reconcile PROD-006 requirements with new representation
5. Create memories: contract-vs-progress, canonical fields, frontmatter-block-precedence
6. Create follow-up backlog items: bulk migration, broader kind-aware validation

### Loose Ends / Watch Items

- Phase 01 and 02 sheets themselves have embedded blocks (written before code changes). They work via the frontmatter path since canonical fields are present. This is the expected legacy compatibility behavior.
- `render_phase_overview_block` and `render_phase_tracking_block` remain in `plan.py` — they're used by the legacy reading path (`extract_phase_tracking` in `_enrich_phase_data`) and `plan_render_test.py`. Not dead code yet.
- Validator now only reads phase file content for legacy phases (optimization: skip file read when frontmatter has canonical fields).

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
